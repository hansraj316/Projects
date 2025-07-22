"""
Async Utilities for Streamlit Integration
Provides helpers for running async functions in Streamlit context
"""

import asyncio
import threading
from typing import Any, Awaitable, Callable
from concurrent.futures import ThreadPoolExecutor
import streamlit as st


def run_async_in_streamlit(coro: Awaitable[Any]) -> Any:
    """
    Run an async function in Streamlit context
    
    Args:
        coro: The coroutine to run
        
    Returns:
        The result of the coroutine
    """
    try:
        # Try to get existing event loop
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # If loop is already running, use a thread pool
            with ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run, coro)
                return future.result()
        else:
            # If no loop is running, run directly
            return loop.run_until_complete(coro)
    except RuntimeError:
        # No event loop exists, create one
        return asyncio.run(coro)


def run_async_task(task_func: Callable[..., Awaitable[Any]], *args, **kwargs) -> Any:
    """
    Run an async task function with arguments
    
    Args:
        task_func: The async function to run
        *args: Positional arguments
        **kwargs: Keyword arguments
        
    Returns:
        The result of the task
    """
    coro = task_func(*args, **kwargs)
    return run_async_in_streamlit(coro)


class AsyncTaskRunner:
    """
    Helper class for managing async tasks in Streamlit
    """
    
    def __init__(self):
        self.running_tasks = {}
        self.task_results = {}
        
    def start_task(self, task_id: str, coro: Awaitable[Any]) -> None:
        """
        Start an async task in the background
        
        Args:
            task_id: Unique identifier for the task
            coro: The coroutine to run
        """
        def run_in_thread():
            try:
                result = asyncio.run(coro)
                self.task_results[task_id] = {"success": True, "result": result}
            except Exception as e:
                self.task_results[task_id] = {"success": False, "error": str(e)}
            finally:
                if task_id in self.running_tasks:
                    del self.running_tasks[task_id]
        
        thread = threading.Thread(target=run_in_thread)
        thread.daemon = True
        self.running_tasks[task_id] = thread
        thread.start()
    
    def is_task_running(self, task_id: str) -> bool:
        """Check if a task is still running"""
        return task_id in self.running_tasks and self.running_tasks[task_id].is_alive()
    
    def get_task_result(self, task_id: str) -> Any:
        """Get the result of a completed task"""
        return self.task_results.get(task_id)
    
    def cancel_task(self, task_id: str) -> bool:
        """Cancel a running task (best effort)"""
        if task_id in self.running_tasks:
            # Note: This doesn't actually cancel the async operation,
            # just removes it from tracking
            del self.running_tasks[task_id]
            return True
        return False


# Global task runner for Streamlit sessions
@st.cache_resource
def get_async_task_runner():
    """Get a cached async task runner for the session"""
    return AsyncTaskRunner()