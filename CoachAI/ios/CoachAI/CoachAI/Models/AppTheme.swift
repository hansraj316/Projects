import Foundation

enum AppTheme: String, CaseIterable {
    case light = "light"
    case dark = "dark"
    
    var displayName: String {
        switch self {
        case .light:
            return "Light"
        case .dark:
            return "Dark"
        }
    }
} 