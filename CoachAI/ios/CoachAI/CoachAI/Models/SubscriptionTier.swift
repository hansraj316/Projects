import Foundation

enum SubscriptionTier: String, CaseIterable {
    case freemium = "freemium"
    case premium = "premium"
    
    var displayName: String {
        switch self {
        case .freemium:
            return "Freemium"
        case .premium:
            return "Premium"
        }
    }
    
    var dailyPlans: Int {
        switch self {
        case .freemium:
            return 1
        case .premium:
            return 10
        }
    }
    
    var resourcesPerPlan: Int {
        switch self {
        case .freemium:
            return 3
        case .premium:
            return 10
        }
    }
    
    var emailNotificationsEnabled: Bool {
        switch self {
        case .freemium:
            return false
        case .premium:
            return true
        }
    }
    
    var price: Double {
        switch self {
        case .freemium:
            return 0.0
        case .premium:
            return 9.99
        }
    }
} 