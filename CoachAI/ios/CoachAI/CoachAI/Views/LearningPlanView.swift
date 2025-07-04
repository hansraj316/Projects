import SwiftUI
import Combine
import Network

struct LearningPlanView: View {
    @EnvironmentObject private var appState: AppState
    @StateObject private var viewModel = LearningPlanViewModel(apiService: APIService(), storeService: StoreService())
    @State private var isConnected = true
    
    // Store the network monitor in a class-based wrapper instead of directly in the struct
    private let networkMonitorWrapper = NetworkMonitorWrapper()
    
    var body: some View {
        ZStack {
            // Background with subtle gradient
            LinearGradient(
                colors: [.clear, .blue.opacity(0.05), .purple.opacity(0.03)],
                startPoint: .top,
                endPoint: .bottom
            )
            .ignoresSafeArea()
            
            ScrollView {
                LazyVStack(spacing: 24) {
                    // Network status alert with Liquid Glass
                    if !isConnected {
                        HStack(spacing: 12) {
                            Image(systemName: "wifi.slash")
                                .font(.title3)
                            Text("No internet connection. Please check your network settings.")
                                .font(.subheadline)
                        }
                        .foregroundColor(.white)
                        .padding(16)
                        .background {
                            RoundedRectangle(cornerRadius: 16)
                                .fill(.red)
                                .overlay {
                                    RoundedRectangle(cornerRadius: 16)
                                        .stroke(.white.opacity(0.3), lineWidth: 1)
                                }
                        }
                        .shadow(color: .black.opacity(0.1), radius: 8, x: 0, y: 4)
                        .padding(.horizontal, 20)
                    }
                    
                    if viewModel.learningPlan == nil {
                        // Wizard steps with Liquid Glass
                        LiquidGlassStepIndicator(currentStep: viewModel.currentStep)
                            .padding(.horizontal, 20)
                        
                        // Current step content with Liquid Glass
                        stepContent
                            .padding(24)
                            .background {
                                RoundedRectangle(cornerRadius: 20)
                                    .fill(.ultraThinMaterial)
                                    .overlay {
                                        RoundedRectangle(cornerRadius: 20)
                                            .stroke(.white.opacity(0.2), lineWidth: 1)
                                    }
                            }
                            .shadow(color: .black.opacity(0.05), radius: 12, x: 0, y: 6)
                            .padding(.horizontal, 20)
                        
                        // Navigation buttons with Liquid Glass
                        VStack(spacing: 16) {
                            if viewModel.currentStep < 5 {
                                Button(action: viewModel.nextStep) {
                                    HStack(spacing: 8) {
                                        Text("Continue")
                                            .fontWeight(.semibold)
                                        Image(systemName: "chevron.right")
                                            .font(.caption)
                                    }
                                    .frame(maxWidth: .infinity)
                                    .padding(16)
                                    .background {
                                        RoundedRectangle(cornerRadius: 16)
                                            .fill(.blue)
                                    }
                                    .foregroundColor(.white)
                                    .shadow(color: .blue.opacity(0.3), radius: 8, x: 0, y: 4)
                                }
                            } else {
                                Button(action: viewModel.generatePlan) {
                                    HStack(spacing: 8) {
                                        Image(systemName: "sparkles")
                                        Text("Generate My Learning Plan")
                                            .fontWeight(.semibold)
                                    }
                                    .frame(maxWidth: .infinity)
                                    .padding(16)
                                    .background {
                                        RoundedRectangle(cornerRadius: 16)
                                            .fill(.blue)
                                    }
                                    .foregroundColor(.white)
                                    .shadow(color: .blue.opacity(0.3), radius: 8, x: 0, y: 4)
                                }
                            }
                            
                            if viewModel.currentStep > 1 {
                                Button(action: viewModel.previousStep) {
                                    HStack(spacing: 8) {
                                        Image(systemName: "chevron.left")
                                            .font(.caption)
                                        Text("Back")
                                            .fontWeight(.medium)
                                    }
                                    .frame(maxWidth: .infinity)
                                    .padding(14)
                                    .background {
                                        RoundedRectangle(cornerRadius: 16)
                                            .fill(.ultraThinMaterial)
                                            .overlay {
                                                RoundedRectangle(cornerRadius: 16)
                                                    .stroke(.white.opacity(0.2), lineWidth: 1)
                                            }
                                    }
                                    .foregroundColor(.primary)
                                    .shadow(color: .black.opacity(0.05), radius: 4, x: 0, y: 2)
                                }
                            }
                        }
                        .padding(.horizontal, 20)
                    } else {
                        // Display generated plan with improved mobile layout
                        generatedPlanView
                    }
                }
                .padding(.vertical, 20)
            }
        }
        .alert(item: Binding<AlertItem?>(
            get: { viewModel.error != nil ? AlertItem(message: viewModel.error!) : nil },
            set: { _ in viewModel.error = nil }
        )) { alertItem in
            Alert(
                title: Text("Error"),
                message: Text(alertItem.message),
                dismissButton: .default(Text("OK"))
            )
        }
            .overlay(Group {
                if viewModel.isLoading {
                    LoadingView()
                }
            })
            .onAppear {
                // Start monitoring when view appears
                networkMonitorWrapper.startMonitoring { connected in
                    isConnected = connected
                }
            }
            .onDisappear {
                // Stop monitoring when view disappears
                networkMonitorWrapper.stopMonitoring()
            }
            .sheet(isPresented: $viewModel.showPlanDetail) {
                PlanDetailSheet(plan: viewModel.learningPlan) {
                    viewModel.showPlanDetail = false
                }
            }
        }
    }
    
    // Step content based on current step
    @ViewBuilder
    private var stepContent: some View {
        switch viewModel.currentStep {
        case 1:
            VStack(alignment: .leading, spacing: 15) {
                Text("Step 1: Subject or Topic")
                    .font(.headline)
                
                Text("What would you like to learn?")
                    .font(.subheadline)
                    .foregroundColor(.secondary)
                
                TextField("Subject or Topic", text: $viewModel.subject)
                    .textFieldStyle(RoundedBorderTextFieldStyle())
                    .padding(.vertical, 5)
            }
            
        case 2:
            VStack(alignment: .leading, spacing: 15) {
                Text("Step 2: Current Level")
                    .font(.headline)
                
                Text("What's your current knowledge level?")
                    .font(.subheadline)
                    .foregroundColor(.secondary)
                
                Picker("Level", selection: $viewModel.level) {
                    ForEach(viewModel.knowledgeLevels, id: \.self) { level in
                        Text(level).tag(level)
                    }
                }
                .pickerStyle(SegmentedPickerStyle())
                
                TextField("Additional details about your current knowledge (optional)", text: $viewModel.currentKnowledge)
                    .textFieldStyle(RoundedBorderTextFieldStyle())
                    .padding(.vertical, 5)
            }
            
        case 3:
            VStack(alignment: .leading, spacing: 15) {
                Text("Step 3: Learning Purpose")
                    .font(.headline)
                
                Text("What do you want to achieve?")
                    .font(.subheadline)
                    .foregroundColor(.secondary)
                
                TextField("Your learning goals", text: $viewModel.learningPurpose)
                    .textFieldStyle(RoundedBorderTextFieldStyle())
                    .padding(.vertical, 5)
            }
            
        case 4:
            VStack(alignment: .leading, spacing: 15) {
                Text("Step 4: Time Commitment")
                    .font(.headline)
                
                Text("How much time can you dedicate per week?")
                    .font(.subheadline)
                    .foregroundColor(.secondary)
                
                Picker("Time Commitment", selection: $viewModel.timeCommitment) {
                    ForEach(viewModel.timeCommitmentOptions, id: \.self) { option in
                        Text(option).tag(option)
                    }
                }
                .pickerStyle(SegmentedPickerStyle())
            }
            
        case 5:
            VStack(alignment: .leading, spacing: 15) {
                Text("Step 5: Preferred Resources")
                    .font(.headline)
                
                Text("What types of learning materials do you prefer?")
                    .font(.subheadline)
                    .foregroundColor(.secondary)
                
                ForEach(viewModel.resourceOptions, id: \.self) { option in
                    Toggle(option, isOn: Binding(
                        get: { viewModel.preferredResources.contains(option) },
                        set: { isSelected in
                            if isSelected {
                                viewModel.preferredResources.append(option)
                            } else {
                                viewModel.preferredResources.removeAll { $0 == option }
                            }
                        }
                    ))
                }
            }
            
        default:
            EmptyView()
        }
    }
    
    // Generated plan view - Improved for mobile
    private var generatedPlanView: some View {
        VStack(spacing: 24) {
            if let plan = viewModel.learningPlan {
                // Success header
                VStack(spacing: 12) {
                    Image(systemName: "checkmark.circle.fill")
                        .font(.system(size: 50))
                        .foregroundColor(.green)
                    
                    Text("Learning Plan Created!")
                        .font(.title2)
                    
                    Text("Your personalized learning plan is ready")
                        .font(.subheadline)
                        .foregroundColor(.secondary)
                        .multilineTextAlignment(.center)
                }
                .padding()
                .background(Color.green.opacity(0.1))
                .cornerRadius(16)
                .padding(.horizontal)
                
                // Plan details
                PlanDetailView(plan: plan)
                
                // Action buttons - Improved layout
                VStack(spacing: 12) {
                    Button(action: {
                        // Switch to detailed view of the plan
                        if let plan = viewModel.learningPlan {
                            // We'll use a navigation approach
                            viewModel.showPlanDetail = true
                        }
                    }) {
                        HStack {
                            Image(systemName: "doc.text.magnifyingglass")
                            Text("View Full Plan")
                        }
                        .frame(maxWidth: .infinity)
                        .padding()
                        .background(Color.green)
                        .foregroundColor(.white)
                        .cornerRadius(12)
                    }
                    
                    Button(action: {
                        NotificationCenter.default.post(name: Notification.Name("SwitchToDashboardTab"), object: nil)
                    }) {
                        HStack {
                            Image(systemName: "chart.line.uptrend.xyaxis")
                            Text("Start Tracking Progress")
                        }
                        .frame(maxWidth: .infinity)
                        .padding()
                        .background(Color.blue)
                        .foregroundColor(.white)
                        .cornerRadius(12)
                    }
                    
                    Button(action: viewModel.resetForm) {
                        HStack {
                            Image(systemName: "plus.circle")
                            Text("Create Another Plan")
                        }
                        .frame(maxWidth: .infinity)
                        .padding()
                        .background(Color.gray.opacity(0.15))
                        .foregroundColor(.primary)
                        .cornerRadius(12)
                    }
                }
                .padding(.horizontal)
            }
        }
    }

// Helper Views

// Old StepIndicator removed - using LiquidGlassStepIndicator instead

struct PlanDetailView: View {
    var plan: LearningPlan
    @State private var selectedTab = 0
    
    var body: some View {
        VStack(alignment: .leading, spacing: 20) {
            // Header Section
            VStack(alignment: .leading, spacing: 12) {
                Text(plan.subject)
                    .font(.title2)
                    .lineLimit(2)
                
                HStack {
                    Label(plan.level, systemImage: "graduationcap.fill")
                        .font(.subheadline)
                        .foregroundColor(.blue)
                    
                    Spacer()
                    
                    let estimatedHours = plan.estimatedHours.isFinite ? plan.estimatedHours : 0.0
                    Label("\(Int(estimatedHours))h", systemImage: "clock.fill")
                        .font(.subheadline)
                        .foregroundColor(.green)
                }
                
                Text("Created \(DateFormatter.shortDateFormatter.string(from: plan.createdAt))")
                    .font(.caption)
                    .foregroundColor(.secondary)
            }
            .padding()
            .background(Color(.secondarySystemBackground))
            .cornerRadius(12)
            
            // Tab Picker
            Picker("Plan Details", selection: $selectedTab) {
                Text("Learning Plan").tag(0)
                Text("Resources (\(plan.resources.count))").tag(1)
            }
            .pickerStyle(SegmentedPickerStyle())
            
            // Content Section
            if selectedTab == 0 {
                // Full plan tab - Better formatted for mobile
                ScrollView {
                    VStack(alignment: .leading, spacing: 20) {
                        if let attributed = try? AttributedString(markdown: plan.content) {
                            Text(attributed)
                                .font(.system(.body, design: .default))
                                .lineSpacing(6)
                                .multilineTextAlignment(.leading)
                                .textSelection(.enabled)
                                .fixedSize(horizontal: false, vertical: true)
                        } else {
                            Text(plan.content)
                                .font(.system(.body, design: .default))
                                .lineSpacing(6)
                                .multilineTextAlignment(.leading)
                                .textSelection(.enabled)
                                .fixedSize(horizontal: false, vertical: true)
                        }
                    }
                    .padding(20)
                    .background(Color(.tertiarySystemBackground))
                    .cornerRadius(16)
                }
                .frame(maxHeight: 500) // Increased height for better readability
            } else {
                // Resources tab - Improved layout
                if plan.resources.isEmpty {
                    VStack(spacing: 16) {
                        Image(systemName: "link.circle")
                            .font(.system(size: 40))
                            .foregroundColor(.gray)
                        
                        Text("No resources available")
                            .font(.headline)
                            .foregroundColor(.secondary)
                        
                        Text("Resources will appear here when available")
                            .font(.subheadline)
                            .foregroundColor(.secondary)
                            .multilineTextAlignment(.center)
                    }
                    .frame(maxWidth: .infinity)
                    .padding(40)
                    .background(Color(.tertiarySystemBackground))
                    .cornerRadius(12)
                } else {
                    ScrollView {
                        LazyVStack(spacing: 12) {
                            ForEach(plan.resources) { resource in
                                ResourceRow(resource: resource)
                            }
                        }
                        .padding(.vertical, 8)
                    }
                    .frame(maxHeight: 400)
                }
            }
        }
        .padding(.horizontal)
    }
}

struct ResourceRow: View {
    var resource: LearningPlan.Resource
    
    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack {
                // Resource type icon with background
                ZStack {
                    Circle()
                        .fill(colorForResourceType(resource.type).opacity(0.2))
                        .frame(width: 40, height: 40)
                    
                    Image(systemName: iconForResourceType(resource.type))
                        .foregroundColor(colorForResourceType(resource.type))
                        .font(.system(size: 18))
                }
                
                VStack(alignment: .leading, spacing: 4) {
                    Text(resource.title)
                        .font(.subheadline)
                        .lineLimit(2)
                        .multilineTextAlignment(.leading)
                    
                    Text(resource.type.rawValue)
                        .font(.caption)
                        .foregroundColor(colorForResourceType(resource.type))
                }
                
                Spacer()
                
                // External link button
                Link(destination: URL(string: resource.url) ?? URL(string: "https://example.com")!) {
                    Image(systemName: "arrow.up.right.square.fill")
                        .foregroundColor(.blue)
                        .font(.system(size: 20))
                }
            }
            
            // URL display (truncated for mobile)
            if !resource.url.isEmpty {
                Text(resource.url)
                    .font(.caption2)
                    .foregroundColor(.secondary)
                    .lineLimit(1)
                    .truncationMode(.middle)
            }
        }
        .padding(16)
        .background(Color(.tertiarySystemBackground))
        .cornerRadius(12)
        .overlay(
            RoundedRectangle(cornerRadius: 12)
                .stroke(colorForResourceType(resource.type).opacity(0.3), lineWidth: 1)
        )
    }
    
    private func iconForResourceType(_ type: LearningPlan.ResourceType) -> String {
        switch type {
        case .article:
            return "doc.text"
        case .video:
            return "play.rectangle"
        case .course:
            return "book"
        case .book:
            return "book.closed"
        case .interactive:
            return "hand.tap"
        case .documentation:
            return "doc"
        case .other:
            return "questionmark.square"
        }
    }
    
    private func colorForResourceType(_ type: LearningPlan.ResourceType) -> Color {
        switch type {
        case .article:
            return .blue
        case .video:
            return .red
        case .course:
            return .purple
        case .book:
            return .green
        case .interactive:
            return .orange
        case .documentation:
            return .gray
        case .other:
            return .secondary
        }
    }
}

struct LoadingView: View {
    var body: some View {
        ZStack {
            Color.black.opacity(0.4)
                .edgesIgnoringSafeArea(.all)
            
            VStack(spacing: 20) {
                ProgressView()
                    .progressViewStyle(CircularProgressViewStyle(tint: .white))
                    .scaleEffect(1.5)
                
                Text("Generating your personalized learning plan...")
                    .font(.headline)
                    .foregroundColor(.white)
            }
            .padding(25)
            .background(
                RoundedRectangle(cornerRadius: 15)
                    .fill(Color(.systemBackground).opacity(0.8))
            )
        }
    }
}

extension DateFormatter {
    static let shortDateFormatter: DateFormatter = {
        let formatter = DateFormatter()
        formatter.dateStyle = .medium
        formatter.timeStyle = .none
        return formatter
    }()
}

// Network monitoring wrapper class
class NetworkMonitorWrapper {
    private var monitor: NWPathMonitor?
    private var queue = DispatchQueue(label: "NetworkMonitor")
    
    func startMonitoring(updateHandler: @escaping (Bool) -> Void) {
        // Cancel any existing monitor
        stopMonitoring()
        
        // Create new monitor
        let monitor = NWPathMonitor()
        self.monitor = monitor
        
        monitor.pathUpdateHandler = { path in
            DispatchQueue.main.async {
                updateHandler(path.status == .satisfied)
            }
        }
        monitor.start(queue: queue)
    }
    
    func stopMonitoring() {
        if let monitor = monitor {
            monitor.cancel()
            self.monitor = nil
        }
    }
    
    deinit {
        stopMonitoring()
    }
}

// MARK: - Plan Detail Sheet
struct PlanDetailSheet: View {
    let plan: LearningPlan?
    let onDismiss: () -> Void
    
    var body: some View {
        NavigationView {
            Group {
                if let plan = plan {
                    PlanDetailSheetContent(plan: plan)
                } else {
                    Text("No plan available")
                        .foregroundColor(.secondary)
                }
            }
            .navigationTitle("Learning Plan")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button("Done") {
                        onDismiss()
                    }
                }
            }
        }
    }
}

struct PlanDetailSheetContent: View {
    let plan: LearningPlan
    @State private var selectedTab = 0
    
    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 20) {
                // Header Section
                VStack(alignment: .leading, spacing: 12) {
                    Text(plan.subject)
                        .font(.title2)
                        .lineLimit(2)
                    
                    HStack {
                        Label(plan.level, systemImage: "graduationcap.fill")
                            .font(.subheadline)
                            .foregroundColor(.blue)
                        
                        Spacer()
                        
                        let estimatedHours = plan.estimatedHours.isFinite ? plan.estimatedHours : 0.0
                        Label("\(Int(estimatedHours))h", systemImage: "clock.fill")
                            .font(.subheadline)
                            .foregroundColor(.green)
                    }
                    
                    Text("Created \(DateFormatter.shortDateFormatter.string(from: plan.createdAt))")
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
                .padding()
                .background(Color(.secondarySystemBackground))
                .cornerRadius(12)
                
                // Tab Picker
                Picker("Plan Details", selection: $selectedTab) {
                    Text("Learning Plan").tag(0)
                    Text("Resources (\(plan.resources.count))").tag(1)
                }
                .pickerStyle(SegmentedPickerStyle())
                
                // Content Section
                if selectedTab == 0 {
                    // Full plan tab - Better formatted for mobile
                    ScrollView {
                        VStack(alignment: .leading, spacing: 20) {
                            if let attributed = try? AttributedString(markdown: plan.content) {
                                Text(attributed)
                                    .font(.system(.body, design: .default))
                                    .lineSpacing(6)
                                    .multilineTextAlignment(.leading)
                                    .textSelection(.enabled)
                                    .fixedSize(horizontal: false, vertical: true)
                            } else {
                                Text(plan.content)
                                    .font(.system(.body, design: .default))
                                    .lineSpacing(6)
                                    .multilineTextAlignment(.leading)
                                    .textSelection(.enabled)
                                    .fixedSize(horizontal: false, vertical: true)
                            }
                        }
                        .padding(20)
                        .background(Color(.tertiarySystemBackground))
                        .cornerRadius(16)
                    }
                    .frame(maxHeight: 500)
                } else {
                    // Resources tab
                    if plan.resources.isEmpty {
                        VStack(spacing: 16) {
                            Image(systemName: "link.circle")
                                .font(.system(size: 40))
                                .foregroundColor(.gray)
                            
                            Text("No resources available")
                                .font(.headline)
                                .foregroundColor(.secondary)
                            
                            Text("Resources will appear here when available")
                                .font(.subheadline)
                                .foregroundColor(.secondary)
                                .multilineTextAlignment(.center)
                        }
                        .frame(maxWidth: .infinity)
                        .padding(40)
                        .background(Color(.tertiarySystemBackground))
                        .cornerRadius(12)
                    } else {
                        ScrollView {
                            LazyVStack(spacing: 12) {
                                ForEach(plan.resources) { resource in
                                    ResourceRow(resource: resource)
                                }
                            }
                            .padding(.vertical, 8)
                        }
                        .frame(maxHeight: 400)
                    }
                }
            }
            .padding(.horizontal)
            .padding(.vertical)
        }
    }
}

struct AlertItem: Identifiable {
    var id = UUID()
    var message: String
}

// MARK: - Liquid Glass Step Indicator
struct LiquidGlassStepIndicator: View {
    let currentStep: Int
    let totalSteps = 5
    
    var body: some View {
        VStack(spacing: 16) {
            // Progress bar
            HStack(spacing: 8) {
                ForEach(1...totalSteps, id: \.self) { step in
                    RoundedRectangle(cornerRadius: 4)
                        .fill(step <= currentStep ? .blue : .gray.opacity(0.3))
                        .frame(height: 6)
                        .animation(.spring(response: 0.3, dampingFraction: 0.8), value: currentStep)
                }
            }
            
            // Step info
            HStack {
                VStack(alignment: .leading, spacing: 4) {
                    Text("Step \(currentStep) of \(totalSteps)")
                        .font(.caption)
                        .fontWeight(.medium)
                        .foregroundColor(.secondary)
                    
                    Text(stepTitle(currentStep))
                        .font(.subheadline)
                        .fontWeight(.semibold)
                        .foregroundColor(.primary)
                }
                
                Spacer()
                
                ZStack {
                    Circle()
                        .fill(.blue.opacity(0.2))
                        .frame(width: 40, height: 40)
                    
                    Text("\(currentStep)")
                        .font(.headline)
                        .fontWeight(.bold)
                        .foregroundColor(.blue)
                }
            }
        }
        .padding(20)
        .background {
            RoundedRectangle(cornerRadius: 16)
                .fill(.ultraThinMaterial)
                .overlay {
                    RoundedRectangle(cornerRadius: 16)
                        .stroke(.white.opacity(0.2), lineWidth: 1)
                }
        }
        .shadow(color: .black.opacity(0.05), radius: 8, x: 0, y: 4)
    }
    
    private func stepTitle(_ step: Int) -> String {
        switch step {
        case 1: return "Subject or Topic"
        case 2: return "Current Level"
        case 3: return "Learning Purpose"
        case 4: return "Time Commitment"
        case 5: return "Preferred Resources"
        default: return "Setup"
        }
    }
}

struct LearningPlanView_Previews: PreviewProvider {
    static var previews: some View {
        LearningPlanView()
            .environmentObject(AppState())
    }
}