import Foundation
import Combine
import StoreKit

class SettingsViewModel: ObservableObject {
    // API Key
    @Published var apiKey: String = ""
    @Published var isAPIKeySaved: Bool = false
    
    // Theme
    @Published var selectedTheme: AppTheme = .dark
    
    // Subscription
    @Published var currentSubscription: SubscriptionTier = .freemium
    @Published var isLoadingSubscription: Bool = false
    @Published var subscriptionEndDate: String = ""
    
    // State
    @Published var error: String? = nil
    var selectedTab: Int {
        get {
            return UserDefaults.standard.integer(forKey: "settingsTab")
        }
    }
    
    // App State
    private var appState: AppState
    private var cancellables = Set<AnyCancellable>()
    
    init(appState: AppState) {
        self.appState = appState
        self.apiKey = appState.apiKey
        self.isAPIKeySaved = !appState.apiKey.isEmpty
        self.selectedTheme = appState.theme
        self.currentSubscription = appState.subscriptionTier
        self.subscriptionEndDate = formatSubscriptionEndDate()
        
        setupBindings()
    }
    
    private func setupBindings() {
        appState.$apiKey
            .sink { [weak self] newValue in
                self?.apiKey = newValue
                self?.isAPIKeySaved = !newValue.isEmpty
            }
            .store(in: &cancellables)
        
        appState.$theme
            .sink { [weak self] newValue in
                self?.selectedTheme = newValue
            }
            .store(in: &cancellables)
        
        appState.$subscriptionTier
            .sink { [weak self] newValue in
                self?.currentSubscription = newValue
            }
            .store(in: &cancellables)
    }
    
    func saveAPIKey() {
        guard !apiKey.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty else {
            error = "API key cannot be empty"
            return
        }
        
        appState.saveApiKey(apiKey)
        isAPIKeySaved = true
        error = nil
    }
    
    func setTheme(_ theme: AppTheme) {
        appState.setTheme(theme)
    }
    
    func subscriptionFeatures(for tier: SubscriptionTier) -> [String] {
        switch tier {
        case .freemium:
            return [
                "\(tier.dailyPlans) learning plans per day",
                "\(tier.resourcesPerPlan) resources per plan",
                "Email notifications: \(tier.emailNotificationsEnabled ? "Yes" : "No")",
                "Time tracking & dashboard",
                "Price: Free"
            ]
        case .premium:
            return [
                "\(tier.dailyPlans) learning plans per day",
                "\(tier.resourcesPerPlan) resources per plan",
                "Email notifications: \(tier.emailNotificationsEnabled ? "Yes" : "No")",
                "Time tracking & dashboard",
                "Priority support",
                "Price: $\(String(format: "%.2f", tier.price))/month"
            ]
        }
    }
    
    func initiateSubscriptionPurchase() {
        // In a real app, we would connect to App Store's in-app purchases here
        isLoadingSubscription = true
        
        // This is a placeholder. In a real app, you'd use StoreKit
        DispatchQueue.main.asyncAfter(deadline: .now() + 1.5) { [weak self] in
            self?.isLoadingSubscription = false
            
            // Simulate successful purchase for demo
            self?.appState.updateSubscriptionTier(.premium)
            self?.currentSubscription = .premium
        }
    }
    
    func restorePurchases() {
        // In a real app, we would call StoreKit's restoreCompletedTransactions here
        isLoadingSubscription = true
        
        // This is a placeholder. In a real app, you'd use StoreKit
        DispatchQueue.main.asyncAfter(deadline: .now() + 1.5) { [weak self] in
            self?.isLoadingSubscription = false
            
            // Just for demo purposes
            if Bool.random() {
                self?.appState.updateSubscriptionTier(.premium)
                self?.currentSubscription = .premium
                self?.subscriptionEndDate = self?.formatSubscriptionEndDate() ?? ""
            } else {
                self?.error = "No purchases found to restore"
            }
        }
    }
    
    // MARK: - Stripe Integration Methods
    
    func initiateStripeSubscription() {
        isLoadingSubscription = true
        error = nil
        
        // In a real implementation, you would:
        // 1. Create a Stripe customer
        // 2. Create a subscription with Stripe
        // 3. Handle payment confirmation
        // 4. Update local subscription status
        
        // Simulating Stripe payment flow
        DispatchQueue.main.asyncAfter(deadline: .now() + 2.0) { [weak self] in
            self?.isLoadingSubscription = false
            
            // Simulate successful Stripe subscription
            self?.appState.updateSubscriptionTier(.premium)
            self?.currentSubscription = .premium
            self?.subscriptionEndDate = self?.formatSubscriptionEndDate() ?? ""
            
            // In a real app, you would save the Stripe subscription ID and customer ID
            UserDefaults.standard.set(true, forKey: "hasActiveStripeSubscription")
            UserDefaults.standard.set(Date().addingTimeInterval(30 * 24 * 60 * 60), forKey: "subscriptionEndDate") // 30 days from now
        }
    }
    
    func openStripeCustomerPortal() {
        // In a real implementation, you would:
        // 1. Create a Stripe customer portal session
        // 2. Open the portal URL in Safari or in-app browser
        
        guard let url = URL(string: "https://billing.stripe.com/p/login/test_customer_portal") else { return }
        
        #if canImport(UIKit)
        if #available(iOS 10.0, *) {
            UIApplication.shared.open(url)
        }
        #endif
    }
    
    func cancelSubscription() {
        isLoadingSubscription = true
        error = nil
        
        // In a real implementation, you would:
        // 1. Cancel the Stripe subscription
        // 2. Update local subscription status
        
        DispatchQueue.main.asyncAfter(deadline: .now() + 1.5) { [weak self] in
            self?.isLoadingSubscription = false
            
            // Simulate subscription cancellation
            self?.appState.updateSubscriptionTier(.freemium)
            self?.currentSubscription = .freemium
            self?.subscriptionEndDate = ""
            
            UserDefaults.standard.set(false, forKey: "hasActiveStripeSubscription")
            UserDefaults.standard.removeObject(forKey: "subscriptionEndDate")
        }
    }
    
    private func formatSubscriptionEndDate() -> String {
        if let endDate = UserDefaults.standard.object(forKey: "subscriptionEndDate") as? Date {
            let formatter = DateFormatter()
            formatter.dateStyle = .medium
            return formatter.string(from: endDate)
        }
        
        // Default to 30 days from now for demo
        let endDate = Date().addingTimeInterval(30 * 24 * 60 * 60)
        let formatter = DateFormatter()
        formatter.dateStyle = .medium
        return formatter.string(from: endDate)
    }
} 