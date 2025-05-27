import SwiftUI

struct OnboardingView: View {
    @EnvironmentObject private var appState: AppState
    @State private var currentPage = 0
    @State private var showAPIKeySetup = false
    
    private let pages = [
        OnboardingPage(
            title: "Welcome to CoachAI",
            subtitle: "Your AI-powered learning companion",
            description: "Create personalized learning plans tailored to your goals, timeline, and learning style.",
            imageName: "brain.head.profile",
            color: .blue
        ),
        OnboardingPage(
            title: "Smart Learning Plans",
            subtitle: "AI-generated roadmaps for success",
            description: "Get customized study plans with curated resources, timelines, and progress tracking.",
            imageName: "map.fill",
            color: .green
        ),
        OnboardingPage(
            title: "Track Your Progress",
            subtitle: "Stay motivated and on track",
            description: "Monitor your learning journey with detailed analytics and achievement milestones.",
            imageName: "chart.line.uptrend.xyaxis",
            color: .orange
        ),
        OnboardingPage(
            title: "Ready to Start?",
            subtitle: "Set up your OpenAI API key",
            description: "To create AI-powered learning plans, you'll need an OpenAI API key with GPT-4 access.",
            imageName: "key.fill",
            color: .purple
        )
    ]
    
    var body: some View {
        VStack {
            // Progress indicator
            HStack {
                ForEach(0..<pages.count, id: \.self) { index in
                    Circle()
                        .fill(index <= currentPage ? pages[currentPage].color : Color.gray.opacity(0.3))
                        .frame(width: 10, height: 10)
                        .scaleEffect(index == currentPage ? 1.2 : 1.0)
                        .animation(.easeInOut(duration: 0.3), value: currentPage)
                }
            }
            .padding(.top, 50)
            .padding(.bottom, 30)
            
            // Page content
            TabView(selection: $currentPage) {
                ForEach(0..<pages.count, id: \.self) { index in
                    OnboardingPageView(page: pages[index])
                        .tag(index)
                }
            }
            .tabViewStyle(PageTabViewStyle(indexDisplayMode: .never))
            .animation(.easeInOut, value: currentPage)
            
            // Navigation buttons
            HStack {
                if currentPage > 0 {
                    Button("Back") {
                        withAnimation {
                            currentPage -= 1
                        }
                    }
                    .foregroundColor(.secondary)
                }
                
                Spacer()
                
                if currentPage < pages.count - 1 {
                    Button("Next") {
                        withAnimation {
                            currentPage += 1
                        }
                    }
                    .padding(.horizontal, 30)
                    .padding(.vertical, 12)
                    .background(pages[currentPage].color)
                    .foregroundColor(.white)
                    .cornerRadius(25)
                } else {
                    Button("Get Started") {
                        showAPIKeySetup = true
                    }
                    .padding(.horizontal, 30)
                    .padding(.vertical, 12)
                    .background(pages[currentPage].color)
                    .foregroundColor(.white)
                    .cornerRadius(25)
                }
            }
            .padding(.horizontal, 30)
            .padding(.bottom, 50)
        }
        .sheet(isPresented: $showAPIKeySetup) {
            APIKeySetupView()
        }
    }
}

struct OnboardingPageView: View {
    let page: OnboardingPage
    
    var body: some View {
        VStack(spacing: 30) {
            Spacer()
            
            // Icon
            Image(systemName: page.imageName)
                .font(.system(size: 80))
                .foregroundColor(page.color)
                .padding(.bottom, 20)
            
            // Title
            Text(page.title)
                .font(.largeTitle)
                .multilineTextAlignment(.center)
                .padding(.horizontal)
            
            // Subtitle
            Text(page.subtitle)
                .font(.title2)
                .foregroundColor(.secondary)
                .multilineTextAlignment(.center)
                .padding(.horizontal)
            
            // Description
            Text(page.description)
                .font(.body)
                .foregroundColor(.secondary)
                .multilineTextAlignment(.center)
                .padding(.horizontal, 40)
                .lineSpacing(4)
            
            Spacer()
        }
    }
}

struct APIKeySetupView: View {
    @EnvironmentObject private var appState: AppState
    @Environment(\.presentationMode) var presentationMode
    @State private var apiKey = ""
    @State private var isLoading = false
    @State private var showError = false
    @State private var errorMessage = ""
    
    var body: some View {
        NavigationView {
            VStack(spacing: 30) {
                // Header
                VStack(spacing: 15) {
                    Image(systemName: "key.fill")
                        .font(.system(size: 60))
                        .foregroundColor(.blue)
                    
                    Text("OpenAI API Key Setup")
                        .font(.title)
                    
                    Text("To use CoachAI's AI features, you need an OpenAI API key with GPT-4 access.")
                        .font(.body)
                        .foregroundColor(.secondary)
                        .multilineTextAlignment(.center)
                        .padding(.horizontal)
                }
                .padding(.top, 30)
                
                // Instructions
                VStack(alignment: .leading, spacing: 15) {
                    Text("How to get your API key:")
                        .font(.headline)
                    
                    VStack(alignment: .leading, spacing: 10) {
                        HStack(alignment: .top) {
                            Text("1.")
                                .frame(width: 20)
                            Text("Visit OpenAI's API Keys page")
                        }
                        
                        HStack(alignment: .top) {
                            Text("2.")
                                .frame(width: 20)
                            Text("Create a new secret key")
                        }
                        
                        HStack(alignment: .top) {
                            Text("3.")
                                .frame(width: 20)
                            Text("Copy and paste it below")
                        }
                    }
                    .font(.body)
                    .foregroundColor(.secondary)
                    
                    Link("Get your API key here →", destination: URL(string: "https://platform.openai.com/api-keys")!)
                        .font(.headline)
                        .foregroundColor(.blue)
                }
                .padding(.horizontal, 30)
                
                // API Key input
                VStack(alignment: .leading, spacing: 10) {
                    Text("API Key")
                        .font(.headline)
                    
                    SecureField("sk-...", text: $apiKey)
                        .textFieldStyle(RoundedBorderTextFieldStyle())
                        .autocapitalization(.none)
                        .disableAutocorrection(true)
                }
                .padding(.horizontal, 30)
                
                Spacer()
                
                // Action buttons
                VStack(spacing: 15) {
                    Button(action: saveAPIKey) {
                        HStack {
                            if isLoading {
                                ProgressView()
                                    .progressViewStyle(CircularProgressViewStyle(tint: .white))
                                    .scaleEffect(0.8)
                            }
                            Text(isLoading ? "Validating..." : "Save & Continue")
                        }
                        .frame(maxWidth: .infinity)
                        .padding()
                        .background(apiKey.isEmpty ? Color.gray : Color.blue)
                        .foregroundColor(.white)
                        .cornerRadius(12)
                    }
                    .disabled(apiKey.isEmpty || isLoading)
                    
                    Button("Skip for now") {
                        completeOnboarding()
                    }
                    .foregroundColor(.secondary)
                }
                .padding(.horizontal, 30)
                .padding(.bottom, 30)
            }
            .navigationBarTitleDisplayMode(.inline)
            .navigationBarHidden(true)
        }
        .alert("Error", isPresented: $showError) {
            Button("OK") { }
        } message: {
            Text(errorMessage)
        }
    }
    
    private func saveAPIKey() {
        isLoading = true
        
        // Basic validation
        guard apiKey.hasPrefix("sk-") && apiKey.count > 20 else {
            errorMessage = "Please enter a valid OpenAI API key"
            showError = true
            isLoading = false
            return
        }
        
        // Save API key
        appState.apiKey = apiKey
        
        // Simulate validation delay
        DispatchQueue.main.asyncAfter(deadline: .now() + 1) {
            isLoading = false
            completeOnboarding()
        }
    }
    
    private func completeOnboarding() {
        UserDefaults.standard.set(true, forKey: "hasCompletedOnboarding")
        appState.hasCompletedOnboarding = true
        presentationMode.wrappedValue.dismiss()
    }
}

struct OnboardingPage {
    let title: String
    let subtitle: String
    let description: String
    let imageName: String
    let color: Color
}

struct OnboardingView_Previews: PreviewProvider {
    static var previews: some View {
        OnboardingView()
            .environmentObject(AppState())
    }
} 