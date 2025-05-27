import SwiftUI

enum PlanViewMode {
    case standard
    case list
    case timetable
}

struct LearningPlanDetailView: View {
    let plan: LearningPlan
    @State private var viewMode: PlanViewMode = .standard
    @State private var selectedTab: Int = 0
    
    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 16) {
                // Header
                VStack(alignment: .leading, spacing: 8) {
                    Text(plan.subject)
                        .font(.largeTitle)
                    
                    HStack {
                        Text(plan.level)
                            .font(.headline)
                            .foregroundColor(.secondary)
                        
                        Spacer()
                        
                        Text(formatDate(plan.createdAt))
                            .font(.caption)
                            .foregroundColor(.secondary)
                    }
                }
                .padding(.horizontal)
                
                // View mode selector
                HStack {
                    Button(action: { viewMode = .standard }) {
                        VStack {
                            Image(systemName: "doc.text")
                                .font(.system(size: 20))
                            Text("Standard")
                                .font(.caption)
                        }
                        .padding(.vertical, 8)
                        .padding(.horizontal, 12)
                        .background(viewMode == .standard ? Color.blue.opacity(0.1) : Color.clear)
                        .cornerRadius(8)
                        .foregroundColor(viewMode == .standard ? .blue : .gray)
                    }
                    
                    Button(action: { viewMode = .list }) {
                        VStack {
                            Image(systemName: "list.bullet")
                                .font(.system(size: 20))
                            Text("List")
                                .font(.caption)
                        }
                        .padding(.vertical, 8)
                        .padding(.horizontal, 12)
                        .background(viewMode == .list ? Color.blue.opacity(0.1) : Color.clear)
                        .cornerRadius(8)
                        .foregroundColor(viewMode == .list ? .blue : .gray)
                    }
                    
                    Button(action: { viewMode = .timetable }) {
                        VStack {
                            Image(systemName: "calendar")
                                .font(.system(size: 20))
                            Text("Timetable")
                                .font(.caption)
                        }
                        .padding(.vertical, 8)
                        .padding(.horizontal, 12)
                        .background(viewMode == .timetable ? Color.blue.opacity(0.1) : Color.clear)
                        .cornerRadius(8)
                        .foregroundColor(viewMode == .timetable ? .blue : .gray)
                    }
                }
                .frame(maxWidth: .infinity)
                .padding(.vertical, 4)
                .background(Color(.tertiarySystemBackground))
                
                // Tab selection
                Picker("View", selection: $selectedTab) {
                    Text("Plan").tag(0)
                    Text("Resources").tag(1)
                }
                .pickerStyle(SegmentedPickerStyle())
                .padding(.horizontal)
                
                // Content based on selected tab
                if selectedTab == 0 {
                    // Learning plan content
                    switch viewMode {
                    case .standard:
                        StandardPlanView(content: plan.content)
                            .padding(.horizontal)
                    case .list:
                        ListPlanView(content: plan.content)
                            .padding(.horizontal)
                    case .timetable:
                        TimetablePlanView(content: plan.content)
                            .padding(.horizontal)
                    }
                } else {
                    // Resources tab
                    ResourcesView(resources: plan.resources)
                        .padding(.horizontal)
                }
                
                // Bottom buttons
                HStack {
                    Button(action: {
                        // Track progress action
                        NotificationCenter.default.post(name: Notification.Name("SwitchToDashboardTab"), object: nil)
                    }) {
                        Text("Track Progress")
                            .frame(maxWidth: .infinity)
                            .padding()
                            .background(Color.blue)
                            .foregroundColor(.white)
                            .cornerRadius(8)
                    }
                }
                .padding(.horizontal)
                .padding(.top, 8)
            }
            .padding(.vertical)
        }
        .navigationTitle("Learning Plan")
        .navigationBarTitleDisplayMode(.inline)
    }
    
    private func formatDate(_ date: Date) -> String {
        let formatter = DateFormatter()
        formatter.dateStyle = .medium
        formatter.timeStyle = .none
        return formatter.string(from: date)
    }
}

// MARK: - Content Views

struct StandardPlanView: View {
    let content: String
    
    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 16) {
                Text(parseMarkdown(content))
                    .font(.system(.body, design: .default))
                    .lineSpacing(6)
                    .multilineTextAlignment(.leading)
                    .textSelection(.enabled)
                    .fixedSize(horizontal: false, vertical: true)
            }
            .padding(20)
        }
        .background(Color(.secondarySystemBackground))
        .cornerRadius(12)
    }
    
    private func parseMarkdown(_ text: String) -> AttributedString {
        do {
            return try AttributedString(markdown: text)
        } catch {
            return AttributedString(text)
        }
    }
}

struct ListPlanView: View {
    let content: String
    let sections: [PlanSection]
    
    init(content: String) {
        self.content = content
        self.sections = extractSections(from: content)
    }
    
    var body: some View {
        VStack(alignment: .leading, spacing: 16) {
            ForEach(sections, id: \.title) { section in
                VStack(alignment: .leading, spacing: 8) {
                    Text(section.title)
                        .font(.headline)
                        .padding(.vertical, 4)
                    
                    ForEach(section.items, id: \.self) { item in
                        HStack(alignment: .top, spacing: 12) {
                            Image(systemName: "circle.fill")
                                .font(.system(size: 8))
                                .padding(.top, 8)
                                .foregroundColor(.blue)
                            
                            Text(item)
                                .font(.system(.body, design: .default))
                                .lineSpacing(4)
                                .multilineTextAlignment(.leading)
                                .fixedSize(horizontal: false, vertical: true)
                        }
                        .padding(.vertical, 4)
                    }
                }
                .padding()
                .background(Color(.secondarySystemBackground))
                .cornerRadius(8)
            }
        }
    }
    
    private static func extractSections(from content: String) -> [PlanSection] {
        var sections: [PlanSection] = []
        var currentTitle = "Overview"
        var currentItems: [String] = []
        
        // Split content by lines
        let lines = content.components(separatedBy: .newlines)
        
        for line in lines {
            let trimmedLine = line.trimmingCharacters(in: .whitespacesAndNewlines)
            
            // Check if it's a header
            if trimmedLine.hasPrefix("# ") || trimmedLine.hasPrefix("## ") {
                // Save previous section
                if !currentItems.isEmpty {
                    sections.append(PlanSection(title: currentTitle, items: currentItems))
                    currentItems = []
                }
                
                // Get new section title
                currentTitle = trimmedLine.replacingOccurrences(of: "# ", with: "")
                    .replacingOccurrences(of: "## ", with: "")
            }
            // Check if it's a list item
            else if trimmedLine.hasPrefix("- ") || trimmedLine.hasPrefix("* ") {
                let item = trimmedLine.replacingOccurrences(of: "- ", with: "")
                    .replacingOccurrences(of: "* ", with: "")
                currentItems.append(item)
            }
            // Add text that isn't a header or a list item to the current section
            else if !trimmedLine.isEmpty {
                currentItems.append(trimmedLine)
            }
        }
        
        // Add the last section
        if !currentItems.isEmpty {
            sections.append(PlanSection(title: currentTitle, items: currentItems))
        }
        
        return sections
    }
}

struct PlanSection {
    let title: String
    let items: [String]
}

struct TimetablePlanView: View {
    let content: String
    let weeks: [WeekSchedule]
    
    init(content: String) {
        self.content = content
        self.weeks = extractWeeks(from: content)
    }
    
    var body: some View {
        VStack(alignment: .leading, spacing: 20) {
            ForEach(weeks, id: \.weekTitle) { week in
                VStack(alignment: .leading, spacing: 8) {
                    Text(week.weekTitle)
                        .font(.headline)
                        .padding(.bottom, 4)
                    
                    ForEach(week.activities, id: \.self) { activity in
                        HStack(alignment: .top, spacing: 12) {
                            Image(systemName: "calendar.badge.clock")
                                .foregroundColor(.blue)
                                .frame(width: 24)
                            
                            Text(activity)
                                .font(.system(.body, design: .default))
                                .lineSpacing(4)
                                .multilineTextAlignment(.leading)
                                .fixedSize(horizontal: false, vertical: true)
                        }
                        .padding(.vertical, 6)
                    }
                }
                .padding()
                .background(Color(.secondarySystemBackground))
                .cornerRadius(8)
            }
        }
    }
    
    private static func extractWeeks(from content: String) -> [WeekSchedule] {
        var weeks: [WeekSchedule] = []
        let lines = content.components(separatedBy: .newlines)
        
        var currentWeek: String? = nil
        var currentActivities: [String] = []
        
        // Look for patterns like "Week X" or "Week X-Y"
        let weekPattern = "week\\s+[0-9]+(-[0-9]+)?:?\\s"
        let weekPatternRange = "week\\s+[0-9]+-[0-9]+:?\\s"
        
        for line in lines {
            let lowercaseLine = line.lowercased()
            
            // Check if line contains week reference
            if lowercaseLine.range(of: weekPattern, options: .regularExpression) != nil {
                // Save previous week if it exists
                if let week = currentWeek, !currentActivities.isEmpty {
                    weeks.append(WeekSchedule(weekTitle: week, activities: currentActivities))
                    currentActivities = []
                }
                
                // Extract the week title
                currentWeek = line.trimmingCharacters(in: .whitespacesAndNewlines)
            }
            // Add content to the current week
            else if let _ = currentWeek, !line.isEmpty {
                // If it's a list item, clean it up
                if line.hasPrefix("-") || line.hasPrefix("*") {
                    let activity = line.replacingOccurrences(of: "^[\\-\\*]\\s+", with: "", options: .regularExpression)
                    if !activity.isEmpty {
                        currentActivities.append(activity)
                    }
                } else if !line.hasPrefix("#") { // Skip headers
                    currentActivities.append(line.trimmingCharacters(in: .whitespacesAndNewlines))
                }
            }
        }
        
        // Add the last week
        if let week = currentWeek, !currentActivities.isEmpty {
            weeks.append(WeekSchedule(weekTitle: week, activities: currentActivities))
        }
        
        // If no weeks were found, try to create a simple schedule
        if weeks.isEmpty {
            weeks = createDefaultSchedule(from: content)
        }
        
        return weeks
    }
    
    private static func createDefaultSchedule(from content: String) -> [WeekSchedule] {
        // Create 4 default weeks if no week structure found
        let activities = content.components(separatedBy: .newlines)
            .filter { !$0.isEmpty && !$0.hasPrefix("#") }
            .map { $0.trimmingCharacters(in: .whitespacesAndNewlines) }
        
        let activityCount = activities.count
        var weeks: [WeekSchedule] = []
        
        // Split activities into 4 weeks
        if activityCount > 0 {
            let itemsPerWeek = max(1, activityCount / 4)
            
            for i in 0..<4 {
                let startIndex = i * itemsPerWeek
                let endIndex = min(startIndex + itemsPerWeek, activityCount)
                
                if startIndex < activityCount {
                    let weekActivities = Array(activities[startIndex..<endIndex])
                    weeks.append(WeekSchedule(
                        weekTitle: "Week \(i + 1)",
                        activities: weekActivities
                    ))
                }
            }
        }
        
        return weeks
    }
}

struct WeekSchedule {
    let weekTitle: String
    let activities: [String]
}

struct ResourcesView: View {
    let resources: [LearningPlan.Resource]
    
    var body: some View {
        VStack(alignment: .leading, spacing: 16) {
            if resources.isEmpty {
                Text("No resources available for this plan")
                    .foregroundColor(.secondary)
                    .padding()
                    .frame(maxWidth: .infinity)
                    .background(Color(.secondarySystemBackground))
                    .cornerRadius(8)
            } else {
                ForEach(resources) { resource in
                    Link(destination: URL(string: resource.url) ?? URL(string: "https://example.com")!) {
                        HStack {
                            Image(systemName: iconForResourceType(resource.type))
                                .foregroundColor(colorForResourceType(resource.type))
                                .frame(width: 30)
                            
                            VStack(alignment: .leading, spacing: 4) {
                                Text(resource.title)
                                    .foregroundColor(.primary)
                                    .font(.headline)
                                    .lineLimit(1)
                                
                                Text(resource.url)
                                    .foregroundColor(.secondary)
                                    .font(.caption)
                                    .lineLimit(1)
                            }
                            
                            Spacer()
                            
                            Image(systemName: "arrow.up.right.square")
                                .foregroundColor(.blue)
                        }
                        .padding()
                        .background(Color(.secondarySystemBackground))
                        .cornerRadius(8)
                    }
                }
            }
        }
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

// MARK: - Previews
struct LearningPlanDetailView_Previews: PreviewProvider {
    static var previews: some View {
        let samplePlan = LearningPlan(
            id: "123",
            subject: "Swift Programming",
            level: "Intermediate",
            currentKnowledge: "Basic knowledge of programming concepts",
            learningPurpose: "Develop iOS apps",
            timeCommitment: "5-7 hours",
            preferredResources: ["Videos", "Documentation"],
            content: "# Swift Programming Plan\n\n## Week 1: Swift Basics\n- Learn Swift syntax\n- Understand optionals\n- Practice with basic data structures\n\n## Week 2: iOS Fundamentals\n- UIKit basics\n- View controllers\n- Auto Layout\n\n## Week 3: SwiftUI\n- SwiftUI concepts\n- Building UI with SwiftUI\n- State and binding\n\n## Week 4: Networking and Data\n- REST APIs\n- JSON parsing\n- Core Data basics",
            resources: [
                LearningPlan.Resource(title: "Swift Documentation", url: "https://swift.org/documentation/", type: .documentation),
                LearningPlan.Resource(title: "iOS Development Course", url: "https://example.com/course", type: .course)
            ],
            estimatedHours: 50.0
        )
        
        return NavigationView {
            LearningPlanDetailView(plan: samplePlan)
        }
    }
} 