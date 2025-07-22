import SwiftUI

struct DashboardView: View {
    @EnvironmentObject private var appState: AppState
    @StateObject private var viewModel: DashboardViewModel
    
    init() {
        let apiService = APIService()
        let storeService = StoreService()
        
        // Set the API key from UserDefaults
        if let savedApiKey = UserDefaults.standard.string(forKey: "apiKey") {
            apiService.setAPIKey(savedApiKey)
        }
        
        _viewModel = StateObject(wrappedValue: DashboardViewModel(storeService: storeService, apiService: apiService))
    }
    
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
                    // Progress Overview with Liquid Glass cards
                    VStack(spacing: 16) {
                        HStack {
                            LiquidGlassProgressCard(
                                title: "Today",
                                value: String(format: "%.1f", viewModel.timeSpentToday),
                                unit: "hours",
                                iconName: "clock.fill",
                                color: .blue
                            )
                            
                            LiquidGlassProgressCard(
                                title: "Total",
                                value: String(format: "%.1f", viewModel.totalTimeSpent),
                                unit: "hours",
                                iconName: "calendar.badge.clock",
                                color: .purple
                            )
                        }
                        
                        if let selectedPlan = viewModel.selectedPlanId,
                           let plan = viewModel.learningPlans.first(where: { $0.id == selectedPlan }) {
                            
                            VStack(alignment: .leading, spacing: 12) {
                                Text(plan.subject)
                                    .font(.headline)
                                    .foregroundColor(.primary)
                                
                                ProgressView(value: viewModel.completionPercentage, total: 100)
                                    .progressViewStyle(LinearProgressViewStyle(tint: .green))
                                
                                HStack {
                                    let percentage = viewModel.completionPercentage.isFinite ? Int(viewModel.completionPercentage) : 0
                                    Text("Progress: \(percentage)%")
                                        .font(.caption)
                                        .foregroundColor(.secondary)
                                    
                                    Spacer()
                                    
                                    let timeSpent = viewModel.getTimeSpent(forPlanId: plan.id)
                                    let estimatedHours = plan.estimatedHours.isFinite ? plan.estimatedHours : 0.0
                                    let timeSpentDisplay = timeSpent.isFinite ? timeSpent : 0.0
                                    Text("\(String(format: "%.1f", timeSpentDisplay)) / \(String(format: "%.1f", estimatedHours)) hours")
                                        .font(.caption)
                                        .foregroundColor(.secondary)
                                }
                            }
                            .padding(16)
                            .background {
                                RoundedRectangle(cornerRadius: 16)
                                    .fill(.ultraThinMaterial)
                                    .overlay {
                                        RoundedRectangle(cornerRadius: 16)
                                            .stroke(.white.opacity(0.2), lineWidth: 1)
                                    }
                            }
                        }
                    }
                    .padding(.horizontal, 20)
                    
                    // Learning Plans Section
                    VStack(alignment: .leading, spacing: 16) {
                        HStack {
                            Text("Your Learning Plans")
                                .font(.title2)
                                .fontWeight(.semibold)
                                .foregroundColor(.primary)
                            
                            Spacer()
                            
                            if !viewModel.learningPlans.isEmpty {
                                Button(action: {
                                    viewModel.showAllPlans = true
                                }) {
                                    HStack(spacing: 6) {
                                        Text("View All")
                                        Image(systemName: "chevron.right")
                                            .font(.caption)
                                    }
                                    .font(.subheadline)
                                    .foregroundColor(.blue)
                                }
                                .liquidGlassButton(size: .small)
                            }
                        }
                        .padding(.horizontal, 20)
                        
                        if viewModel.learningPlans.isEmpty {
                            LiquidGlassEmptyStateView(message: "No learning plans yet. Create one in the Learning Plan tab!")
                        } else {
                            ScrollView(.horizontal, showsIndicators: false) {
                                HStack(spacing: 16) {
                                    ForEach(viewModel.learningPlans) { plan in
                                        LiquidGlassPlanCard(
                                            plan: plan,
                                            isSelected: viewModel.selectedPlanId == plan.id
                                        )
                                        .onTapGesture {
                                            viewModel.selectPlan(plan)
                                        }
                                    }
                                }
                                .padding(.horizontal, 20)
                            }
                        }
                    }
                    
                    // Time Logging Section
                    VStack(alignment: .leading, spacing: 16) {
                        Text("Log Your Learning Time")
                            .font(.title2)
                            .fontWeight(.semibold)
                            .foregroundColor(.primary)
                            .padding(.horizontal, 20)
                        
                        VStack(spacing: 16) {
                            HStack {
                                Text("Hours spent:")
                                    .font(.subheadline)
                                    .foregroundColor(.primary)
                                
                                Spacer()
                                
                                Stepper(
                                    value: $viewModel.hoursToLog,
                                    in: 0...24,
                                    step: 0.5
                                ) {
                                    Text("\(viewModel.hoursToLog, specifier: "%.1f")")
                                        .font(.subheadline)
                                        .fontWeight(.medium)
                                        .frame(width: 50)
                                        .foregroundColor(.primary)
                                }
                            }
                            
                            TextField("Notes (optional)", text: $viewModel.logNotes)
                                .padding(12)
                                .background {
                                    RoundedRectangle(cornerRadius: 12)
                                        .fill(.ultraThinMaterial)
                                        .overlay {
                                            RoundedRectangle(cornerRadius: 12)
                                                .stroke(.white.opacity(0.2), lineWidth: 1)
                                        }
                                }
                            
                            Button(action: viewModel.logTime) {
                                Text("Log Time")
                                    .font(.subheadline)
                                    .fontWeight(.semibold)
                                    .frame(maxWidth: .infinity)
                                    .padding(14)
                                    .background {
                                        RoundedRectangle(cornerRadius: 12)
                                            .fill(.blue)
                                    }
                                    .foregroundColor(.white)
                            }
                            .disabled(viewModel.hoursToLog <= 0 || viewModel.selectedPlanId == nil || viewModel.isLoading)
                            .opacity(viewModel.hoursToLog <= 0 || viewModel.selectedPlanId == nil || viewModel.isLoading ? 0.6 : 1.0)
                        }
                        .padding(20)
                        .background {
                            RoundedRectangle(cornerRadius: 20)
                                .fill(.ultraThinMaterial)
                                .overlay {
                                    RoundedRectangle(cornerRadius: 20)
                                        .stroke(.white.opacity(0.2), lineWidth: 1)
                                }
                        }
                        .shadow(color: .black.opacity(0.05), radius: 8, x: 0, y: 4)
                        .padding(.horizontal, 20)
                    }
                    
                    // Recent Activity Section
                    VStack(alignment: .leading, spacing: 16) {
                        Text("Recent Activity")
                            .font(.title2)
                            .fontWeight(.semibold)
                            .foregroundColor(.primary)
                            .padding(.horizontal, 20)
                        
                        if viewModel.getTimeLogsForCurrentPlan().isEmpty {
                            LiquidGlassEmptyStateView(message: "No activity logged for the selected plan yet.")
                        } else {
                            VStack(spacing: 12) {
                                ForEach(viewModel.getTimeLogsForCurrentPlan().prefix(5)) { log in
                                    LiquidGlassTimeLogRow(log: log)
                                }
                            }
                            .padding(.horizontal, 20)
                        }
                    }
                }
                .padding(.vertical, 20)
            }
        }
        .onAppear {
            viewModel.loadData()
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
            .sheet(isPresented: $viewModel.showAllPlans) {
                NavigationView {
                    VStack {
                        Text("All Learning Plans")
                            .font(.largeTitle)
                            .frame(maxWidth: .infinity, alignment: .leading)
                            .padding(.horizontal)
                        
                        if viewModel.learningPlans.isEmpty {
                            VStack(spacing: 20) {
                                Image(systemName: "doc.text")
                                    .font(.system(size: 60))
                                    .foregroundColor(.gray)
                                
                                Text("No learning plans yet")
                                    .font(.headline)
                                
                                Text("Create your first learning plan to get started")
                                    .font(.subheadline)
                                    .foregroundColor(.secondary)
                                    .multilineTextAlignment(.center)
                            }
                            .padding(.top, 60)
                        } else {
                            ScrollView {
                                VStack(spacing: 16) {
                                    ForEach(viewModel.learningPlans) { plan in
                                                                                 DashboardPlanCard(plan: plan)
                                             .onTapGesture {
                                                 viewModel.selectedPlanForDetail = plan
                                                 viewModel.showPlanDetail = true
                                             }
                                    }
                                }
                                .padding(.horizontal)
                                .padding(.top, 8)
                            }
                        }
                        
                        Spacer()
                    }
                    .navigationBarTitleDisplayMode(.inline)
                    .toolbar {
                        ToolbarItem(placement: .navigationBarTrailing) {
                            Button("Done") {
                                viewModel.showAllPlans = false
                            }
                        }
                    }
                }
            }
            .sheet(isPresented: $viewModel.showPlanDetail) {
                if let plan = viewModel.selectedPlanForDetail {
                    DashboardPlanDetailSheet(plan: plan) {
                        viewModel.showPlanDetail = false
                    }
                }
            }
        }
    }

// MARK: - Liquid Glass Components

struct LiquidGlassProgressCard: View {
    var title: String
    var value: String
    var unit: String
    var iconName: String
    var color: Color
    
    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            HStack(spacing: 8) {
                ZStack {
                    Circle()
                        .fill(color.opacity(0.2))
                        .frame(width: 32, height: 32)
                    
                    Image(systemName: iconName)
                        .font(.system(size: 16, weight: .semibold))
                        .foregroundColor(color)
                }
                
                Text(title)
                    .font(.caption)
                    .fontWeight(.medium)
                    .foregroundColor(.secondary)
                
                Spacer()
            }
            
            HStack(alignment: .firstTextBaseline, spacing: 4) {
                Text(value)
                    .font(.title2)
                    .fontWeight(.semibold)
                    .foregroundColor(.primary)
                
                Text(unit)
                    .font(.caption)
                    .foregroundColor(.secondary)
            }
        }
        .padding(16)
        .frame(maxWidth: .infinity, alignment: .leading)
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
}

struct LiquidGlassPlanCard: View {
    var plan: LearningPlan
    var isSelected: Bool
    
    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            // Header with icon
            HStack {
                ZStack {
                    RoundedRectangle(cornerRadius: 8)
                        .fill(.blue.opacity(0.2))
                        .frame(width: 32, height: 32)
                    
                    Image(systemName: "book.fill")
                        .font(.system(size: 16, weight: .semibold))
                        .foregroundColor(.blue)
                }
                
                Spacer()
                
                if isSelected {
                    Image(systemName: "checkmark.circle.fill")
                        .font(.system(size: 20))
                        .foregroundColor(.blue)
                }
            }
            
            // Content
            VStack(alignment: .leading, spacing: 6) {
                Text(plan.subject)
                    .font(.headline)
                    .fontWeight(.semibold)
                    .lineLimit(2)
                    .foregroundColor(.primary)
                
                Text(plan.level)
                    .font(.caption)
                    .foregroundColor(.secondary)
            }
            
            Spacer()
            
            // Footer
            HStack {
                let estimatedHours = plan.estimatedHours.isFinite ? plan.estimatedHours : 0.0
                Text("\(String(format: "%.0f", estimatedHours)) hrs")
                    .font(.caption)
                    .fontWeight(.medium)
                    .foregroundColor(.secondary)
                
                Spacer()
                
                Image(systemName: "clock.fill")
                    .font(.caption)
                    .foregroundColor(.secondary)
            }
        }
        .padding(16)
        .frame(width: 160, height: 140)
        .background {
            RoundedRectangle(cornerRadius: 16)
                .fill(.ultraThinMaterial)
                .overlay {
                    RoundedRectangle(cornerRadius: 16)
                        .stroke(isSelected ? .blue.opacity(0.6) : .white.opacity(0.2), lineWidth: isSelected ? 2 : 1)
                }
        }
        .shadow(color: .black.opacity(0.05), radius: 8, x: 0, y: 4)
        .scaleEffect(isSelected ? 1.02 : 1.0)
        .animation(.spring(response: 0.3, dampingFraction: 0.8), value: isSelected)
    }
}

struct LiquidGlassEmptyStateView: View {
    let message: String
    
    var body: some View {
        VStack(spacing: 16) {
            ZStack {
                Circle()
                    .fill(.blue.opacity(0.1))
                    .frame(width: 80, height: 80)
                
                Image(systemName: "doc.text")
                    .font(.system(size: 32, weight: .medium))
                    .foregroundColor(.blue)
            }
            
            VStack(spacing: 8) {
                Text("No learning plans yet")
                    .font(.headline)
                    .fontWeight(.semibold)
                    .foregroundColor(.primary)
                
                Text(message)
                    .font(.subheadline)
                    .foregroundColor(.secondary)
                    .multilineTextAlignment(.center)
                    .lineLimit(3)
            }
        }
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
    }
}

struct LiquidGlassTimeLogRow: View {
    let log: TimeLog
    
    var body: some View {
        HStack(spacing: 16) {
            // Time indicator
            ZStack {
                RoundedRectangle(cornerRadius: 8)
                    .fill(.green.opacity(0.2))
                    .frame(width: 32, height: 32)
                
                Image(systemName: "clock.fill")
                    .font(.system(size: 14, weight: .semibold))
                    .foregroundColor(.green)
            }
            
            // Content
            VStack(alignment: .leading, spacing: 4) {
                Text(DateFormatter.relativeDateFormatter.string(from: log.timestamp))
                    .font(.subheadline)
                    .fontWeight(.medium)
                    .foregroundColor(.primary)
                
                if let notes = log.notes, !notes.isEmpty {
                    Text(notes)
                        .font(.caption)
                        .foregroundColor(.secondary)
                        .lineLimit(2)
                }
            }
            
            Spacer()
            
            // Hours display
            VStack(alignment: .trailing, spacing: 2) {
                Text("\(log.hours, specifier: "%.1f")")
                    .font(.subheadline)
                    .fontWeight(.semibold)
                    .foregroundColor(.primary)
                
                Text("hours")
                    .font(.caption)
                    .foregroundColor(.secondary)
            }
        }
        .padding(16)
        .background {
            RoundedRectangle(cornerRadius: 16)
                .fill(.ultraThinMaterial)
                .overlay {
                    RoundedRectangle(cornerRadius: 16)
                        .stroke(.white.opacity(0.2), lineWidth: 1)
                }
        }
        .shadow(color: .black.opacity(0.05), radius: 4, x: 0, y: 2)
    }
}

struct DashboardPlanCard: View {
    let plan: LearningPlan
    
    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(plan.subject)
                .font(.headline)
                .lineLimit(2)
            
            Text(plan.level)
                .font(.subheadline)
                .foregroundColor(.secondary)
            
            HStack {
                Text(formatDate(plan.createdAt))
                    .font(.caption)
                    .foregroundColor(.secondary)
                
                Spacer()
                
                let estimatedHours = plan.estimatedHours.isFinite ? plan.estimatedHours : 0.0
                Text("\(Int(estimatedHours)) hours")
                    .font(.caption)
                    .foregroundColor(.secondary)
            }
        }
        .padding()
        .background(Color(.secondarySystemBackground))
        .cornerRadius(10)
        .foregroundColor(.primary)
    }
    
    private func formatDate(_ date: Date) -> String {
        let formatter = DateFormatter()
        formatter.dateStyle = .medium
        formatter.timeStyle = .none
        return formatter.string(from: date)
    }
}

// Old TimeLogRow removed - using LiquidGlassTimeLogRow instead

// Old EmptyStateView removed - using LiquidGlassEmptyStateView instead



// MARK: - Dashboard Plan Detail Sheet
struct DashboardPlanDetailSheet: View {
    let plan: LearningPlan
    let onDismiss: () -> Void
    @State private var selectedTab = 0
    
    var body: some View {
        NavigationView {
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
                                        DashboardResourceRow(resource: resource)
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

struct DashboardResourceRow: View {
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

 