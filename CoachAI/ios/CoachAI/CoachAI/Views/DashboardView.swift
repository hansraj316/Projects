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
        NavigationView {
            ScrollView {
                VStack(spacing: 20) {
                    // Header
                    Text("Learning Dashboard")
                        .font(.largeTitle)
                        .frame(maxWidth: .infinity, alignment: .leading)
                        .padding(.horizontal)
                    
                    // Progress Overview
                    VStack(spacing: 15) {
                        HStack {
                            ProgressCard(
                                title: "Today",
                                value: String(format: "%.1f", viewModel.timeSpentToday),
                                unit: "hours",
                                iconName: "clock.fill",
                                color: .blue
                            )
                            
                            ProgressCard(
                                title: "Total",
                                value: String(format: "%.1f", viewModel.totalTimeSpent),
                                unit: "hours",
                                iconName: "calendar.badge.clock",
                                color: .purple
                            )
                        }
                        
                        if let selectedPlan = viewModel.selectedPlanId,
                           let plan = viewModel.learningPlans.first(where: { $0.id == selectedPlan }) {
                            
                            VStack(alignment: .leading, spacing: 10) {
                                Text(plan.subject)
                                    .font(.headline)
                                
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
                            .padding()
                            .background(Color(.secondarySystemBackground))
                            .cornerRadius(10)
                        }
                    }
                    .padding(.horizontal)
                    
                    // Learning Plans
                    VStack(alignment: .leading, spacing: 10) {
                        HStack {
                            Text("Your Learning Plans")
                                .font(.title2)
                            
                            Spacer()
                            
                            if !viewModel.learningPlans.isEmpty {
                                Button(action: {
                                    viewModel.showAllPlans = true
                                }) {
                                    HStack(spacing: 4) {
                                        Text("View All")
                                        Image(systemName: "chevron.right")
                                    }
                                    .font(.subheadline)
                                    .foregroundColor(.blue)
                                }
                            }
                        }
                        .padding(.horizontal)
                        
                        if viewModel.learningPlans.isEmpty {
                            EmptyStateView(message: "No learning plans yet. Create one in the Learning Plan tab!")
                        } else {
                            ScrollView(.horizontal, showsIndicators: false) {
                                HStack(spacing: 15) {
                                    ForEach(viewModel.learningPlans) { plan in
                                        PlanCard(
                                            plan: plan,
                                            isSelected: viewModel.selectedPlanId == plan.id
                                        )
                                        .onTapGesture {
                                            viewModel.selectPlan(plan)
                                        }
                                    }
                                }
                                .padding(.horizontal)
                            }
                        }
                    }
                    
                    // Time Logging
                    VStack(alignment: .leading, spacing: 10) {
                        Text("Log Your Learning Time")
                            .font(.title2)
                            .padding(.horizontal)
                        
                        VStack {
                            HStack {
                                Text("Hours spent:")
                                
                                Spacer()
                                
                                Stepper(
                                    value: $viewModel.hoursToLog,
                                    in: 0...24,
                                    step: 0.5
                                ) {
                                    Text("\(viewModel.hoursToLog, specifier: "%.1f")")
                                        .frame(width: 50)
                                }
                            }
                            
                            TextField("Notes (optional)", text: $viewModel.logNotes)
                                .textFieldStyle(RoundedBorderTextFieldStyle())
                                .padding(.vertical, 5)
                            
                            Button(action: viewModel.logTime) {
                                Text("Log Time")
                                    .frame(maxWidth: .infinity)
                                    .padding()
                                    .background(Color.blue)
                                    .foregroundColor(.white)
                                    .cornerRadius(8)
                            }
                            .disabled(viewModel.hoursToLog <= 0 || viewModel.selectedPlanId == nil || viewModel.isLoading)
                        }
                        .padding()
                        .background(Color(.secondarySystemBackground))
                        .cornerRadius(10)
                        .padding(.horizontal)
                    }
                    
                    // Recent Activity
                    VStack(alignment: .leading, spacing: 10) {
                        Text("Recent Activity")
                            .font(.title2)
                            .padding(.horizontal)
                        
                        if viewModel.getTimeLogsForCurrentPlan().isEmpty {
                            EmptyStateView(message: "No activity logged for the selected plan yet.")
                        } else {
                            ForEach(viewModel.getTimeLogsForCurrentPlan().prefix(5)) { log in
                                TimeLogRow(log: log)
                            }
                        }
                    }
                }
                .padding(.vertical)
            }
            .navigationBarHidden(true)
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
}

// Helper Views

struct ProgressCard: View {
    var title: String
    var value: String
    var unit: String
    var iconName: String
    var color: Color
    
    var body: some View {
        VStack(alignment: .leading, spacing: 5) {
            HStack {
                Image(systemName: iconName)
                    .foregroundColor(color)
                Text(title)
                    .font(.caption)
                    .foregroundColor(.secondary)
            }
            
            HStack(alignment: .firstTextBaseline) {
                Text(value)
                    .font(.title2)
                
                Text(unit)
                    .font(.caption)
                    .foregroundColor(.secondary)
            }
        }
        .padding()
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(Color(.secondarySystemBackground))
        .cornerRadius(10)
    }
}

struct PlanCard: View {
    var plan: LearningPlan
    var isSelected: Bool
    
    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(plan.subject)
                .font(.headline)
                .lineLimit(1)
            
            Text(plan.level)
                .font(.caption)
                .foregroundColor(.secondary)
            
            Spacer()
            
            HStack {
                let estimatedHours = plan.estimatedHours.isFinite ? plan.estimatedHours : 0.0
                Text("Est: \(String(format: "%.1f", estimatedHours)) hrs")
                    .font(.caption)
                    .foregroundColor(.secondary)
                
                Spacer()
                
                Image(systemName: "clock.fill")
                    .foregroundColor(.secondary)
            }
        }
        .padding()
        .frame(width: 150, height: 120)
        .background(isSelected ? Color.blue.opacity(0.2) : Color(.secondarySystemBackground))
        .cornerRadius(10)
        .overlay(
            RoundedRectangle(cornerRadius: 10)
                .stroke(isSelected ? Color.blue : Color.clear, lineWidth: 2)
        )
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

struct TimeLogRow: View {
    var log: TimeLog
    
    var body: some View {
        HStack {
            VStack(alignment: .leading) {
                Text(DateFormatter.relativeDateFormatter.string(from: log.timestamp))
                    .font(.subheadline)
                
                if let notes = log.notes {
                    Text(notes)
                        .font(.caption)
                        .foregroundColor(.secondary)
                        .lineLimit(1)
                }
            }
            
            Spacer()
            
            Text("\(log.hours, specifier: "%.1f") hours")
                .font(.subheadline)
                .foregroundColor(.secondary)
        }
        .padding()
        .background(Color(.secondarySystemBackground))
        .cornerRadius(8)
        .padding(.horizontal)
    }
}

struct EmptyStateView: View {
    var message: String
    
    var body: some View {
        VStack(spacing: 10) {
            Image(systemName: "doc.text")
                .font(.system(size: 40))
                .foregroundColor(.gray)
            
            Text(message)
                .font(.body)
                .foregroundColor(.secondary)
                .multilineTextAlignment(.center)
        }
        .frame(maxWidth: .infinity)
        .padding()
        .background(Color(.secondarySystemBackground))
        .cornerRadius(10)
        .padding(.horizontal)
    }
}

struct AlertItem: Identifiable {
    var id = UUID()
    var message: String
}

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

extension DateFormatter {
    static let relativeDateFormatter: DateFormatter = {
        let formatter = DateFormatter()
        formatter.doesRelativeDateFormatting = true
        formatter.dateStyle = .short
        formatter.timeStyle = .short
        return formatter
    }()
} 