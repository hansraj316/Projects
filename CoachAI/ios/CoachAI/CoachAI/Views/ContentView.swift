import SwiftUI

struct ContentView: View {
    @EnvironmentObject private var appState: AppState
    @State private var selectedTab = 0
    @State private var showOnboarding = false
    @State private var showNavigationMenu = false
    
    var body: some View {
        NavigationView {
            ZStack {
                // Background gradient with Liquid Glass effect
                LinearGradient(
                    colors: [.blue.opacity(0.15), .purple.opacity(0.1), .clear],
                    startPoint: .top,
                    endPoint: .bottom
                )
                .ignoresSafeArea()
                
                VStack(spacing: 0) {
                    // Custom Navigation Bar with Liquid Glass design
                    liquidGlassNavigationBar
                    
                    // Main Content Area
                    Group {
                        switch selectedTab {
                        case 0:
                            DashboardView()
                        case 1:
                            LearningPlanView()
                        case 2:
                            SettingsView()
                        default:
                            DashboardView()
                        }
                    }
                    .frame(maxWidth: .infinity, maxHeight: .infinity)
                }
            }
        }
        .preferredColorScheme(appState.theme == .dark ? .dark : .light)
        .sheet(isPresented: $showNavigationMenu) {
            navigationMenuSheet
        }
        .onAppear {
            showOnboarding = !appState.hasCompletedOnboarding
            setupNotificationObserver()
        }
    }
    
    // MARK: - Liquid Glass Navigation Bar
    private var liquidGlassNavigationBar: some View {
        VStack(spacing: 0) {
            HStack {
                // App Title with Liquid Glass effect
                Button(action: {
                    showNavigationMenu.toggle()
                }) {
                    HStack(spacing: 8) {
                        Text(tabTitle)
                            .font(.title2)
                            .fontWeight(.semibold)
                            .foregroundColor(.primary)
                        
                        Image(systemName: "chevron.down")
                            .font(.caption)
                            .foregroundColor(.secondary)
                            .rotationEffect(.degrees(showNavigationMenu ? 180 : 0))
                            .animation(.spring(response: 0.3, dampingFraction: 0.8), value: showNavigationMenu)
                    }
                }
                .liquidGlassButton()
                
                Spacer()
                
                // Action Buttons with Liquid Glass containers
                HStack(spacing: 12) {
                    Button(action: {
                        // Search action
                    }) {
                        Image(systemName: "magnifyingglass")
                            .font(.title3)
                            .foregroundColor(.primary)
                    }
                    .liquidGlassButton(size: .medium)
                    
                    Button(action: {
                        // Profile/Account action
                    }) {
                        Image(systemName: "person.circle")
                            .font(.title3)
                            .foregroundColor(.primary)
                    }
                    .liquidGlassButton(size: .medium)
                }
            }
            .padding(.horizontal, 20)
            .padding(.vertical, 12)
            .background {
                // Liquid Glass navigation bar background
                RoundedRectangle(cornerRadius: 0)
                    .fill(.ultraThinMaterial)
                    .overlay {
                        LinearGradient(
                            colors: [.blue.opacity(0.2), .purple.opacity(0.15)],
                            startPoint: .leading,
                            endPoint: .trailing
                        )
                    }
            }
        }
    }
    
    // MARK: - Navigation Menu Sheet (visionOS-inspired)
    private var navigationMenuSheet: some View {
        NavigationView {
            VStack(spacing: 0) {
                // Header
                HStack {
                    Text("Navigation")
                        .font(.title2)
                        .fontWeight(.semibold)
                        .foregroundColor(.primary)
                    
                    Spacer()
                    
                    Button("Done") {
                        showNavigationMenu = false
                    }
                    .liquidGlassButton(size: .small)
                }
                .padding(.horizontal, 20)
                .padding(.vertical, 12)
                
                // Navigation Options
                LazyVStack(spacing: 16) {
                    ForEach(navigationItems, id: \.id) { item in
                        NavigationMenuItem(
                            item: item,
                            isSelected: selectedTab == item.id,
                            action: {
                                selectedTab = item.id
                                showNavigationMenu = false
                            }
                        )
                    }
                }
                .padding(.horizontal, 20)
                .padding(.top, 20)
                
                Spacer()
            }
            .background {
                LinearGradient(
                    colors: [.blue.opacity(0.1), .purple.opacity(0.05), .clear],
                    startPoint: .top,
                    endPoint: .bottom
                )
                .ignoresSafeArea()
            }
        }
    }
    
    // MARK: - Helper Properties
    private var tabTitle: String {
        switch selectedTab {
        case 0: return "Dashboard"
        case 1: return "Learning Plan"
        case 2: return "Settings"
        default: return "CoachAI"
        }
    }
    
    private var navigationItems: [NavigationItem] {
        [
            NavigationItem(id: 0, title: "Dashboard", icon: "chart.bar.fill", description: "View your progress"),
            NavigationItem(id: 1, title: "Learning Plan", icon: "book.fill", description: "Create and manage plans"),
            NavigationItem(id: 2, title: "Settings", icon: "gear", description: "App preferences")
        ]
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

// MARK: - Navigation Item Model
struct NavigationItem {
    let id: Int
    let title: String
    let icon: String
    let description: String
}

// MARK: - Navigation Menu Item View
struct NavigationMenuItem: View {
    let item: NavigationItem
    let isSelected: Bool
    let action: () -> Void
    
    var body: some View {
        Button(action: action) {
            HStack(spacing: 16) {
                // Icon container with Liquid Glass effect
                ZStack {
                    RoundedRectangle(cornerRadius: 12)
                        .fill(.ultraThinMaterial)
                        .overlay {
                            RoundedRectangle(cornerRadius: 12)
                                .stroke(.white.opacity(0.2), lineWidth: 1)
                        }
                        .frame(width: 50, height: 50)
                    
                    Image(systemName: item.icon)
                        .font(.title3)
                        .foregroundColor(isSelected ? .blue : .primary)
                }
                
                // Content
                VStack(alignment: .leading, spacing: 4) {
                    Text(item.title)
                        .font(.headline)
                        .foregroundColor(.primary)
                    
                    Text(item.description)
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
                
                Spacer()
                
                // Selection indicator
                if isSelected {
                    Image(systemName: "checkmark.circle.fill")
                        .font(.title3)
                        .foregroundColor(.blue)
                }
            }
            .padding(.horizontal, 16)
            .padding(.vertical, 12)
            .background {
                RoundedRectangle(cornerRadius: 16)
                    .fill(isSelected ? .blue.opacity(0.1) : .clear)
                    .overlay {
                        RoundedRectangle(cornerRadius: 16)
                            .stroke(.white.opacity(0.1), lineWidth: 1)
                    }
            }
        }
        .buttonStyle(PlainButtonStyle())
    }
}

struct ContentView_Previews: PreviewProvider {
    static var previews: some View {
        ContentView()
            .environmentObject(AppState())
    }
}

// MARK: - Global Liquid Glass Components
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