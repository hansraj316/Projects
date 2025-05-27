import Foundation
import Combine

class AppState: ObservableObject {
    @Published var isLoggedIn: Bool = false
    @Published var currentLearningPlan: LearningPlan?
    @Published var timeSpentToday: Double = 0.0
    @Published var totalTimeSpent: Double = 0.0
    @Published var apiKey: String = ""
    @Published var theme: AppTheme = .dark
    @Published var subscriptionTier: SubscriptionTier = .freemium
    @Published var hasCompletedOnboarding: Bool = false
    
    private var cancellables = Set<AnyCancellable>()
    
    init() {
        loadPersistedState()
    }
    
    func loadPersistedState() {
        // Load saved state from UserDefaults or iCloud
        // This is a placeholder - we'll implement this later
        if let savedApiKey = UserDefaults.standard.string(forKey: "apiKey") {
            self.apiKey = savedApiKey
        }
        
        if let savedThemeValue = UserDefaults.standard.string(forKey: "theme"),
           let savedTheme = AppTheme(rawValue: savedThemeValue) {
            self.theme = savedTheme
        }
        
        if let savedTierValue = UserDefaults.standard.string(forKey: "subscriptionTier"),
           let savedTier = SubscriptionTier(rawValue: savedTierValue) {
            self.subscriptionTier = savedTier
        }
        
        self.hasCompletedOnboarding = UserDefaults.standard.bool(forKey: "hasCompletedOnboarding")
    }
    
    func saveApiKey(_ key: String) {
        self.apiKey = key
        UserDefaults.standard.set(key, forKey: "apiKey")
        
        // Post notification for components that need to update their API key
        NotificationCenter.default.post(
            name: NSNotification.Name("APIKeyChanged"),
            object: nil,
            userInfo: ["apiKey": key]
        )
        
        // Verify the key validity
        verifyApiKey(key)
    }
    
    func verifyApiKey(_ key: String) {
        // This function can be expanded to make a minimal API call to verify the key
        if key.isEmpty {
            return
        }
        
        guard let url = URL(string: "https://api.openai.com/v1/models") else {
            return
        }
        
        var request = URLRequest(url: url)
        request.httpMethod = "GET"
        request.addValue("Bearer \(key)", forHTTPHeaderField: "Authorization")
        
        URLSession.shared.dataTask(with: request) { data, response, error in
            DispatchQueue.main.async {
                let isValid = data != nil && error == nil && (response as? HTTPURLResponse)?.statusCode == 200
                UserDefaults.standard.set(isValid, forKey: "isAPIKeyValid")
                
                // Post notification about API key validation result
                NotificationCenter.default.post(
                    name: NSNotification.Name("APIKeyValidated"),
                    object: nil,
                    userInfo: ["isValid": isValid]
                )
            }
        }.resume()
    }
    
    func setTheme(_ theme: AppTheme) {
        self.theme = theme
        UserDefaults.standard.set(theme.rawValue, forKey: "theme")
    }
    
    func updateSubscriptionTier(_ tier: SubscriptionTier) {
        self.subscriptionTier = tier
        UserDefaults.standard.set(tier.rawValue, forKey: "subscriptionTier")
    }
} 