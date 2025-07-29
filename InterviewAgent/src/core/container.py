"""
Dependency Injection Container for InterviewAgent

Provides centralized service registration and resolution with automatic dependency injection.
"""

from typing import Dict, Type, Any, Callable, Optional, TypeVar, Protocol, get_type_hints
import inspect
import threading
from dataclasses import dataclass
from enum import Enum

T = TypeVar('T')

class ServiceLifetime(Enum):
    SINGLETON = "singleton"
    TRANSIENT = "transient"
    SCOPED = "scoped"

@dataclass
class ServiceDescriptor:
    interface: Type
    implementation: Type
    lifetime: ServiceLifetime
    factory: Optional[Callable] = None

class ServiceContainer:
    """
    Dependency injection container with support for:
    - Singleton, Transient, and Scoped lifetimes
    - Automatic constructor dependency resolution
    - Thread-safe operations
    - Service validation
    """
    
    def __init__(self):
        self._services: Dict[str, ServiceDescriptor] = {}
        self._singletons: Dict[str, Any] = {}
        self._scoped_instances: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.RLock()
        self._current_scope: Optional[str] = None
    
    def register_singleton(self, interface: Type[T], implementation: Type[T]) -> 'ServiceContainer':
        """Register a singleton service (one instance for application lifetime)"""
        return self._register_service(interface, implementation, ServiceLifetime.SINGLETON)
    
    def register_transient(self, interface: Type[T], implementation: Type[T]) -> 'ServiceContainer':
        """Register a transient service (new instance each time)"""
        return self._register_service(interface, implementation, ServiceLifetime.TRANSIENT)
    
    def register_scoped(self, interface: Type[T], implementation: Type[T]) -> 'ServiceContainer':
        """Register a scoped service (one instance per scope)"""
        return self._register_service(interface, implementation, ServiceLifetime.SCOPED)
    
    def register_factory(self, interface: Type[T], factory: Callable[[], T], lifetime: ServiceLifetime = ServiceLifetime.TRANSIENT) -> 'ServiceContainer':
        """Register a service with custom factory function"""
        with self._lock:
            descriptor = ServiceDescriptor(interface, interface, lifetime, factory)
            self._services[interface.__name__] = descriptor
        return self
    
    def _register_service(self, interface: Type[T], implementation: Type[T], lifetime: ServiceLifetime) -> 'ServiceContainer':
        """Internal service registration"""
        self._validate_service_registration(interface, implementation)
        
        with self._lock:
            descriptor = ServiceDescriptor(interface, implementation, lifetime)
            self._services[interface.__name__] = descriptor
        
        return self
    
    def get(self, interface: Type[T]) -> T:
        """Get service instance with automatic dependency resolution"""
        with self._lock:
            service_name = interface.__name__
            
            if service_name not in self._services:
                raise ServiceNotRegisteredException(f"Service {service_name} is not registered")
            
            descriptor = self._services[service_name]
            
            # Handle different lifetimes
            if descriptor.lifetime == ServiceLifetime.SINGLETON:
                return self._get_singleton(descriptor)
            elif descriptor.lifetime == ServiceLifetime.SCOPED:
                return self._get_scoped(descriptor)
            else:  # TRANSIENT
                return self._create_instance(descriptor)
    
    def _get_singleton(self, descriptor: ServiceDescriptor) -> Any:
        """Get or create singleton instance"""
        service_name = descriptor.interface.__name__
        
        if service_name not in self._singletons:
            self._singletons[service_name] = self._create_instance(descriptor)
        
        return self._singletons[service_name]
    
    def _get_scoped(self, descriptor: ServiceDescriptor) -> Any:
        """Get or create scoped instance"""
        if not self._current_scope:
            raise ScopeNotActiveException("No active scope for scoped service resolution")
        
        service_name = descriptor.interface.__name__
        
        if self._current_scope not in self._scoped_instances:
            self._scoped_instances[self._current_scope] = {}
        
        scope_instances = self._scoped_instances[self._current_scope]
        
        if service_name not in scope_instances:
            scope_instances[service_name] = self._create_instance(descriptor)
        
        return scope_instances[service_name]
    
    def _create_instance(self, descriptor: ServiceDescriptor) -> Any:
        """Create new service instance with dependency injection"""
        if descriptor.factory:
            return descriptor.factory()
        
        return self._auto_wire(descriptor.implementation)
    
    def _auto_wire(self, implementation: Type) -> Any:
        """Automatically resolve and inject constructor dependencies"""
        try:
            # Get constructor signature
            signature = inspect.signature(implementation.__init__)
            type_hints = get_type_hints(implementation.__init__)
            
            # Resolve dependencies
            dependencies = {}
            for param_name, param in signature.parameters.items():
                if param_name == 'self':
                    continue
                
                # Get type annotation
                param_type = type_hints.get(param_name, param.annotation)
                
                if param_type == inspect.Parameter.empty:
                    if param.default == inspect.Parameter.empty:
                        raise DependencyResolutionException(
                            f"Cannot resolve parameter '{param_name}' for {implementation.__name__}: no type annotation"
                        )
                    continue
                
                # Resolve dependency
                try:
                    dependencies[param_name] = self.get(param_type)
                except (ServiceNotRegisteredException, DependencyResolutionException):
                    if param.default != inspect.Parameter.empty:
                        # Use default value if available
                        continue
                    raise DependencyResolutionException(
                        f"Cannot resolve dependency '{param_name}' of type {param_type.__name__} for {implementation.__name__}"
                    )
            
            return implementation(**dependencies)
            
        except Exception as e:
            raise DependencyResolutionException(f"Failed to create instance of {implementation.__name__}: {str(e)}") from e
    
    def _validate_service_registration(self, interface: Type, implementation: Type) -> None:
        """Validate service registration"""
        if not inspect.isclass(interface):
            raise InvalidServiceRegistrationException(f"Interface must be a class: {interface}")
        
        if not inspect.isclass(implementation):
            raise InvalidServiceRegistrationException(f"Implementation must be a class: {implementation}")
        
        # Check if implementation can be assigned to interface (basic inheritance check)
        if not issubclass(implementation, interface) and interface != implementation:
            # Allow if interface is a Protocol
            if not (hasattr(interface, '_is_protocol') and interface._is_protocol):
                raise InvalidServiceRegistrationException(
                    f"Implementation {implementation.__name__} does not implement interface {interface.__name__}"
                )
    
    def create_scope(self, scope_id: Optional[str] = None) -> 'ServiceScope':
        """Create a new dependency injection scope"""
        if not scope_id:
            scope_id = f"scope_{id(object())}"
        
        return ServiceScope(self, scope_id)
    
    def _enter_scope(self, scope_id: str) -> None:
        """Internal method to enter a scope"""
        with self._lock:
            self._current_scope = scope_id
            if scope_id not in self._scoped_instances:
                self._scoped_instances[scope_id] = {}
    
    def _exit_scope(self, scope_id: str) -> None:
        """Internal method to exit a scope and cleanup scoped instances"""
        with self._lock:
            if scope_id in self._scoped_instances:
                # Cleanup scoped instances
                scoped_instances = self._scoped_instances.pop(scope_id)
                for instance in scoped_instances.values():
                    if hasattr(instance, 'dispose'):
                        try:
                            instance.dispose()
                        except Exception:
                            pass  # Ignore disposal errors
            
            if self._current_scope == scope_id:
                self._current_scope = None
    
    def is_registered(self, interface: Type) -> bool:
        """Check if a service is registered"""
        return interface.__name__ in self._services
    
    def get_registered_services(self) -> Dict[str, ServiceDescriptor]:
        """Get all registered services (for debugging)"""
        return self._services.copy()

class ServiceScope:
    """Context manager for dependency injection scopes"""
    
    def __init__(self, container: ServiceContainer, scope_id: str):
        self._container = container
        self._scope_id = scope_id
    
    def __enter__(self) -> 'ServiceScope':
        self._container._enter_scope(self._scope_id)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self._container._exit_scope(self._scope_id)

# Custom Exceptions
class ServiceContainerException(Exception):
    """Base exception for service container errors"""
    pass

class ServiceNotRegisteredException(ServiceContainerException):
    """Raised when requesting a service that is not registered"""
    pass

class DependencyResolutionException(ServiceContainerException):
    """Raised when dependency resolution fails"""
    pass

class InvalidServiceRegistrationException(ServiceContainerException):
    """Raised when service registration is invalid"""
    pass

class ScopeNotActiveException(ServiceContainerException):
    """Raised when trying to resolve scoped service without active scope"""
    pass

# Global container instance
_global_container: Optional[ServiceContainer] = None
_container_lock = threading.Lock()

def get_container() -> ServiceContainer:
    """Get the global service container instance"""
    global _global_container
    
    if _global_container is None:
        with _container_lock:
            if _global_container is None:
                _global_container = ServiceContainer()
    
    return _global_container

def configure_container(configurator: Callable[[ServiceContainer], None]) -> None:
    """Configure the global service container"""
    container = get_container()
    configurator(container)