import SwiftUI

struct LearningPlanListView: View {
    @EnvironmentObject private var appState: AppState
    @StateObject private var viewModel: LearningPlanListViewModel
    @State private var showingCreatePlan = false
    
    init() {
        let storeService = StoreService()
        _viewModel = StateObject(wrappedValue: LearningPlanListViewModel(storeService: storeService))
    }
    
    var body: some View {
        NavigationView {
            VStack {
                // Header
                Text("Your Learning Plans")
                    .font(.largeTitle)
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .padding(.horizontal)
                
                if viewModel.learningPlans.isEmpty {
                    // Empty state
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
                        
                        Button(action: {
                            showingCreatePlan = true
                        }) {
                            Text("Create Learning Plan")
                                .frame(maxWidth: .infinity)
                                .padding()
                                .background(Color.blue)
                                .foregroundColor(.white)
                                .cornerRadius(10)
                        }
                        .padding(.horizontal, 40)
                        .padding(.top, 10)
                    }
                    .padding(.top, 60)
                } else {
                    // Plan list
                    ScrollView {
                        VStack(spacing: 16) {
                            ForEach(viewModel.learningPlans) { plan in
                                PlanCard(plan: plan)
                                    .onTapGesture {
                                        viewModel.selectedPlan = plan
                                        viewModel.showPlanDetail = true
                                    }
                            }
                        }
                        .padding(.horizontal)
                        .padding(.top, 8)
                    }
                    
                    // Add new plan button
                    Button(action: {
                        showingCreatePlan = true
                    }) {
                        Text("Create New Plan")
                            .frame(maxWidth: .infinity)
                            .padding()
                            .background(Color.blue)
                            .foregroundColor(.white)
                            .cornerRadius(10)
                    }
                    .padding(.horizontal)
                    .padding(.vertical, 8)
                }
            }
            .padding(.vertical)
            .navigationBarHidden(true)
            .sheet(isPresented: $showingCreatePlan) {
                LearningPlanView()
                    .environmentObject(appState)
            }
            .sheet(isPresented: $viewModel.showPlanDetail) {
                if let plan = viewModel.selectedPlan {
                    PlanDetailSheet(plan: plan) {
                        viewModel.showPlanDetail = false
                    }
                }
            }
            .onAppear {
                viewModel.loadPlans()
            }
        }
    }
}

struct PlanCard: View {
    let plan: LearningPlan
    
    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(plan.subject)
                .font(.headline)
                .lineLimit(1)
            
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

// MARK: - Plan Detail Sheet (Reused from LearningPlanView)
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
                                    SimpleResourceRow(resource: resource)
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

struct SimpleResourceRow: View {
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
    static let shortDateFormatter: DateFormatter = {
        let formatter = DateFormatter()
        formatter.dateStyle = .medium
        formatter.timeStyle = .none
        return formatter
    }()
}

// Preview
struct LearningPlanListView_Previews: PreviewProvider {
    static var previews: some View {
        LearningPlanListView()
            .environmentObject(AppState())
    }
} 