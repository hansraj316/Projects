import SwiftUI

enum ButtonSize {
    case small, medium, large
    
    var horizontalPadding: CGFloat {
        switch self {
        case .small: return 8
        case .medium: return 12
        case .large: return 16
        }
    }
    
    var verticalPadding: CGFloat {
        switch self {
        case .small: return 4
        case .medium: return 8
        case .large: return 8
        }
    }
    
    var cornerRadius: CGFloat {
        switch self {
        case .small: return 8
        case .medium: return 10
        case .large: return 12
        }
    }
}

extension View {
    func liquidGlassButton(size: ButtonSize = .large) -> some View {
        self
            .padding(.horizontal, size.horizontalPadding)
            .padding(.vertical, size.verticalPadding)
            .background {
                RoundedRectangle(cornerRadius: size.cornerRadius)
                    .fill(.ultraThinMaterial)
                    .overlay {
                        RoundedRectangle(cornerRadius: size.cornerRadius)
                            .stroke(.white.opacity(0.2), lineWidth: 1)
                    }
                    .shadow(color: .black.opacity(0.1), radius: 2, x: 0, y: 1)
            }
    }
    
    func liquidGlassContainer(cornerRadius: CGFloat = 16, padding: CGFloat = 16) -> some View {
        self
            .padding(padding)
            .background {
                RoundedRectangle(cornerRadius: cornerRadius)
                    .fill(.ultraThinMaterial)
                    .overlay {
                        RoundedRectangle(cornerRadius: cornerRadius)
                            .stroke(.white.opacity(0.2), lineWidth: 1)
                    }
            }
            .shadow(color: .black.opacity(0.05), radius: 8, x: 0, y: 4)
    }
    
    func liquidGlassCard(isSelected: Bool = false, cornerRadius: CGFloat = 16) -> some View {
        self
            .background {
                RoundedRectangle(cornerRadius: cornerRadius)
                    .fill(.ultraThinMaterial)
                    .overlay {
                        RoundedRectangle(cornerRadius: cornerRadius)
                            .stroke(isSelected ? .blue.opacity(0.6) : .white.opacity(0.2), lineWidth: isSelected ? 2 : 1)
                    }
            }
            .shadow(color: .black.opacity(0.05), radius: 8, x: 0, y: 4)
            .scaleEffect(isSelected ? 1.02 : 1.0)
            .animation(.spring(response: 0.3, dampingFraction: 0.8), value: isSelected)
    }
} 