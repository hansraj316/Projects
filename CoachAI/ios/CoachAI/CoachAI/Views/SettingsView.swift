import SwiftUI

struct SettingsView: View {
    @EnvironmentObject private var appState: AppState
    @State private var selectedTab: Int = 0
    private var viewModel: SettingsViewModel {
        SettingsViewModel(appState: appState)
    }
    
    var body: some View {
        NavigationView {
            VStack {
                // Header
                Text("Settings")
                    .font(.largeTitle)
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .padding(.horizontal)
                
                // Tab selection
                Picker("Settings", selection: $selectedTab) {
                    Text("API Settings").tag(0)
                    Text("Subscription").tag(1)
                    Text("Appearance").tag(2)
                }
                .pickerStyle(SegmentedPickerStyle())
                .padding(.horizontal)
                
                // Tab content
                ScrollView {
                    VStack {
                        if selectedTab == 0 {
                            apiSettingsTab
                        } else if selectedTab == 1 {
                            subscriptionTab
                        } else if selectedTab == 2 {
                            appearanceTab
                        }
                    }
                    .padding()
                }
            }
            .padding(.vertical)
            .navigationBarHidden(true)
            .onAppear {
                selectedTab = UserDefaults.standard.integer(forKey: "settingsTab")
            }
            .onChange(of: selectedTab) { newValue in
                UserDefaults.standard.set(newValue, forKey: "settingsTab")
            }
            .alert(item: Binding<AlertItem?>(
                get: { viewModel.error != nil ? AlertItem(message: viewModel.error!) : nil },
                set: { _ in /* No-op since viewModel is recreated */ }
            )) { alertItem in
                Alert(
                    title: Text("Error"),
                    message: Text(alertItem.message),
                    dismissButton: .default(Text("OK"))
                )
            }
        }
    }
    
    // API Settings tab
    private var apiSettingsTab: some View {
        VStack(alignment: .leading, spacing: 20) {
            Text("OpenAI API Key Configuration")
                .font(.title2)
            
            VStack(alignment: .leading, spacing: 10) {
                Text("To use CoachAI, you need an OpenAI API key with GPT-4 access. If you don't have one:")
                    .font(.body)
                
                VStack(alignment: .leading, spacing: 8) {
                    Text("1. Go to OpenAI API Keys website")
                    Text("2. Create a new secret key")
                    Text("3. Copy and paste it below")
                }
                .padding(.leading)
                
                Link("Get your API key here", destination: URL(string: "https://platform.openai.com/api-keys")!)
                    .font(.headline)
                    .foregroundColor(.blue)
                    .padding(.vertical, 5)
            }
            
            if viewModel.isAPIKeySaved {
                HStack {
                    Image(systemName: "checkmark.circle.fill")
                        .foregroundColor(.green)
                    
                    Text("API Key: \(maskAPIKey(viewModel.apiKey))")
                        .font(.headline)
                }
                .padding()
                .background(Color.green.opacity(0.1))
                .cornerRadius(8)
            }
            
            let apiKeyBinding = Binding<String>(
                get: { self.viewModel.apiKey },
                set: { newValue in
                    self.appState.apiKey = newValue
                }
            )
            
            SecureField("Enter OpenAI API Key", text: apiKeyBinding)
                .textFieldStyle(RoundedBorderTextFieldStyle())
                .autocapitalization(.none)
                .disableAutocorrection(true)
                .padding(.vertical, 5)
            
            Button(action: {
                self.viewModel.saveAPIKey()
            }) {
                Text("Save API Key")
                    .frame(maxWidth: .infinity)
                    .padding()
                    .background(Color.blue)
                    .foregroundColor(.white)
                    .cornerRadius(8)
            }
            .disabled(viewModel.apiKey.isEmpty)
        }
    }
    
    // Subscription tab with Stripe integration
    private var subscriptionTab: some View {
        VStack(alignment: .leading, spacing: 20) {
            Text("Subscription Management")
                .font(.title2)
            
            // Current Plan Status
            VStack(alignment: .leading, spacing: 10) {
                HStack {
                    Image(systemName: viewModel.currentSubscription == .premium ? "crown.fill" : "person.circle")
                        .foregroundColor(viewModel.currentSubscription == .premium ? .yellow : .gray)
                        .font(.title2)
                    
                    VStack(alignment: .leading) {
                        Text("Current Plan: \(viewModel.currentSubscription.displayName)")
                            .font(.headline)
                        
                        if viewModel.currentSubscription == .premium {
                            Text("Active until: \(viewModel.subscriptionEndDate)")
                                .font(.caption)
                                .foregroundColor(.secondary)
                        }
                    }
                    
                    Spacer()
                    
                    if viewModel.currentSubscription == .premium {
                        VStack {
                            Text("ACTIVE")
                                .font(.caption)
                                .foregroundColor(.white)
                                .padding(.horizontal, 8)
                                .padding(.vertical, 4)
                                .background(Color.green)
                                .cornerRadius(4)
                        }
                    }
                }
                
                Text("Plan Features:")
                    .font(.subheadline)
                    .padding(.top, 5)
                
                ForEach(viewModel.subscriptionFeatures(for: viewModel.currentSubscription), id: \.self) { feature in
                    HStack(alignment: .top) {
                        Image(systemName: "checkmark.circle.fill")
                            .foregroundColor(.green)
                            .frame(width: 20)
                        
                        Text(feature)
                            .font(.body)
                    }
                }
            }
            .padding()
            .background(Color(.secondarySystemBackground))
            .cornerRadius(12)
            
            // Subscription Plans
            if viewModel.currentSubscription == .freemium {
                VStack(spacing: 15) {
                    Text("Choose Your Plan")
                        .font(.title3)
                    
                    // Premium Plan Card
                    VStack(alignment: .leading, spacing: 12) {
                        HStack {
                            VStack(alignment: .leading) {
                                Text("Premium Plan")
                                    .font(.headline)
                                
                                Text("$9.99/month")
                                    .font(.title2)
                                    .foregroundColor(.blue)
                            }
                            
                            Spacer()
                            
                            Image(systemName: "crown.fill")
                                .foregroundColor(.yellow)
                                .font(.title)
                        }
                        
                        VStack(alignment: .leading, spacing: 8) {
                            FeatureRow(text: "Unlimited learning plans per day", isIncluded: true)
                            FeatureRow(text: "10 resources per plan", isIncluded: true)
                            FeatureRow(text: "Email notifications", isIncluded: true)
                            FeatureRow(text: "Priority support", isIncluded: true)
                            FeatureRow(text: "Advanced analytics", isIncluded: true)
                        }
                        
                        Button(action: {
                            self.viewModel.initiateStripeSubscription()
                        }) {
                            HStack {
                                if viewModel.isLoadingSubscription {
                                    ProgressView()
                                        .progressViewStyle(CircularProgressViewStyle(tint: .white))
                                        .scaleEffect(0.8)
                                }
                                
                                Text(viewModel.isLoadingSubscription ? "Processing..." : "🌟 Subscribe with Stripe")
                            }
                            .frame(maxWidth: .infinity)
                            .padding()
                            .background(Color.blue)
                            .foregroundColor(.white)
                            .cornerRadius(8)
                        }
                        .disabled(viewModel.isLoadingSubscription)
                    }
                    .padding()
                    .background(Color(.tertiarySystemBackground))
                    .cornerRadius(12)
                    .overlay(
                        RoundedRectangle(cornerRadius: 12)
                            .stroke(Color.blue.opacity(0.3), lineWidth: 1)
                    )
                    
                    // Restore Purchases
                    Button(action: {
                        self.viewModel.restorePurchases()
                    }) {
                        Text("Restore Purchases")
                            .foregroundColor(.blue)
                    }
                    .padding(.top, 5)
                    
                    // Secure Payment Info
                    HStack {
                        Image(systemName: "lock.shield.fill")
                            .foregroundColor(.green)
                        
                        Text("Secure payment powered by Stripe")
                            .font(.caption)
                            .foregroundColor(.secondary)
                    }
                    .padding(.top, 10)
                }
                .padding()
                .background(Color(.secondarySystemBackground))
                .cornerRadius(12)
            } else {
                // Manage Subscription for Premium users
                VStack(spacing: 15) {
                    Text("Manage Subscription")
                        .font(.title3)
                    
                    VStack(spacing: 12) {
                        Button(action: {
                            self.viewModel.openStripeCustomerPortal()
                        }) {
                            HStack {
                                Image(systemName: "creditcard")
                                Text("Manage Payment Methods")
                            }
                            .frame(maxWidth: .infinity)
                            .padding()
                            .background(Color.blue)
                            .foregroundColor(.white)
                            .cornerRadius(8)
                        }
                        
                        Button(action: {
                            self.viewModel.cancelSubscription()
                        }) {
                            HStack {
                                Image(systemName: "xmark.circle")
                                Text("Cancel Subscription")
                            }
                            .frame(maxWidth: .infinity)
                            .padding()
                            .background(Color.red.opacity(0.1))
                            .foregroundColor(.red)
                            .cornerRadius(8)
                        }
                    }
                }
                .padding()
                .background(Color(.secondarySystemBackground))
                .cornerRadius(12)
            }
        }
    }
    
    // Appearance tab
    private var appearanceTab: some View {
        VStack(alignment: .leading, spacing: 20) {
            Text("Appearance Settings")
                .font(.title2)
            
            VStack(alignment: .leading, spacing: 10) {
                Text("Theme")
                    .font(.headline)
                
                ForEach(AppTheme.allCases, id: \.self) { theme in
                    Button(action: { 
                        self.viewModel.setTheme(theme)
                    }) {
                        HStack {
                            Image(systemName: theme == .dark ? "moon.fill" : "sun.max.fill")
                                .foregroundColor(theme == .dark ? .purple : .orange)
                                .frame(width: 30)
                            
                            Text(theme.displayName)
                                .foregroundColor(.primary)
                            
                            Spacer()
                            
                            if viewModel.selectedTheme == theme {
                                Image(systemName: "checkmark")
                                    .foregroundColor(.blue)
                            }
                        }
                        .padding()
                        .background(
                            RoundedRectangle(cornerRadius: 8)
                                .stroke(viewModel.selectedTheme == theme ? Color.blue : Color.gray.opacity(0.3), lineWidth: 1)
                        )
                    }
                }
            }
            
            // Legal and Version info
            VStack(alignment: .leading, spacing: 15) {
                Text("Legal")
                    .font(.headline)
                
                VStack(spacing: 12) {
                    Button(action: {
                        openPrivacyPolicy()
                    }) {
                        HStack {
                            Image(systemName: "hand.raised.fill")
                                .foregroundColor(.blue)
                            Text("Privacy Policy")
                                .foregroundColor(.primary)
                            Spacer()
                            Image(systemName: "chevron.right")
                                .foregroundColor(.secondary)
                        }
                        .padding()
                        .background(Color(.secondarySystemBackground))
                        .cornerRadius(8)
                    }
                    
                    Button(action: {
                        openTermsOfService()
                    }) {
                        HStack {
                            Image(systemName: "doc.text.fill")
                                .foregroundColor(.blue)
                            Text("Terms of Service")
                                .foregroundColor(.primary)
                            Spacer()
                            Image(systemName: "chevron.right")
                                .foregroundColor(.secondary)
                        }
                        .padding()
                        .background(Color(.secondarySystemBackground))
                        .cornerRadius(8)
                    }
                }
            }
            
            Spacer()
            
            VStack(alignment: .center, spacing: 5) {
                Text("CoachAI")
                    .font(.headline)
                
                Text("Version 1.0.0")
                    .font(.caption)
                    .foregroundColor(.secondary)
                
                Text("© 2024 CoachAI. All rights reserved.")
                    .font(.caption2)
                    .foregroundColor(.secondary)
                    .multilineTextAlignment(.center)
            }
            .frame(maxWidth: .infinity)
        }
    }
    
    // Helper function to mask API key
    private func maskAPIKey(_ key: String) -> String {
        guard key.count > 8 else { return "••••••••" }
        
        let prefix = String(key.prefix(4))
        let suffix = String(key.suffix(4))
        return "\(prefix)••••••••\(suffix)"
    }
    
    // Legal document functions
    private func openPrivacyPolicy() {
        guard let url = URL(string: "https://coachai.app/privacy") else { return }
        #if canImport(UIKit)
        if #available(iOS 10.0, *) {
            UIApplication.shared.open(url)
        }
        #endif
    }
    
    private func openTermsOfService() {
        guard let url = URL(string: "https://coachai.app/terms") else { return }
        #if canImport(UIKit)
        if #available(iOS 10.0, *) {
            UIApplication.shared.open(url)
        }
        #endif
    }
}

// Helper Views
struct FeatureRow: View {
    let text: String
    let isIncluded: Bool
    
    var body: some View {
        HStack(alignment: .top, spacing: 8) {
            Image(systemName: isIncluded ? "checkmark.circle.fill" : "xmark.circle.fill")
                .foregroundColor(isIncluded ? .green : .red)
                .frame(width: 16)
            
            Text(text)
                .font(.subheadline)
                .foregroundColor(isIncluded ? .primary : .secondary)
        }
    }
}

// Preview
struct SettingsView_Previews: PreviewProvider {
    static var previews: some View {
        SettingsView()
            .environmentObject(AppState())
    }
} 