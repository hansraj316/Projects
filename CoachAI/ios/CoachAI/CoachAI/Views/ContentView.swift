import SwiftUI

struct ContentView: View {
    @EnvironmentObject private var appState: AppState
    @State private var selectedTab = 0
    @State private var showOnboarding = false
    
    var body: some View {
        mainTabView
            .onAppear {
                showOnboarding = !appState.hasCompletedOnboarding
            }
    }
    
    private var mainTabView: some View {
        TabView(selection: $selectedTab) {
            DashboardView()
                .tabItem {
                    Label("Dashboard", systemImage: "chart.bar.fill")
                }
                .tag(0)
            
            LearningPlanView()
                .tabItem {
                    Label("Learning Plan", systemImage: "book.fill")
                }
                .tag(1)
            
            SettingsView()
                .tabItem {
                    Label("Settings", systemImage: "gear")
                }
                .tag(2)
        }
        .accentColor(.blue)
        .preferredColorScheme(appState.theme == .dark ? .dark : .light)
        .onAppear {
            setupNotificationObserver()
        }
    }
    
    private func setupNotificationObserver() {
        NotificationCenter.default.addObserver(
            forName: Notification.Name("SwitchToDashboardTab"),
            object: nil,
            queue: .main
        ) { _ in
            selectedTab = 0
        }
    }
}

struct ContentView_Previews: PreviewProvider {
    static var previews: some View {
        ContentView()
            .environmentObject(AppState())
    }
} 