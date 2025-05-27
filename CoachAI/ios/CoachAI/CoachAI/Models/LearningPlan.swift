import Foundation

struct LearningPlan: Identifiable, Codable {
    var id: String
    var subject: String
    var level: String
    var currentKnowledge: String
    var learningPurpose: String
    var timeCommitment: String
    var preferredResources: [String]
    var content: String
    var resources: [Resource]
    var createdAt: Date
    var estimatedHours: Double
    
    struct Resource: Identifiable, Codable {
        var id: UUID
        var title: String
        var url: String
        var type: ResourceType
        
        init(id: UUID = UUID(), title: String, url: String, type: ResourceType) {
            self.id = id
            self.title = title
            self.url = url
            self.type = type
        }
    }
    
    enum ResourceType: String, Codable, CaseIterable {
        case article = "Article"
        case video = "Video"
        case course = "Course"
        case book = "Book"
        case interactive = "Interactive"
        case documentation = "Documentation"
        case other = "Other"
    }
    
    init(id: String = UUID().uuidString,
         subject: String,
         level: String,
         currentKnowledge: String = "",
         learningPurpose: String,
         timeCommitment: String,
         preferredResources: [String],
         content: String,
         resources: [Resource] = [],
         createdAt: Date = Date(),
         estimatedHours: Double = 0.0) {
        
        self.id = id
        self.subject = subject
        self.level = level
        self.currentKnowledge = currentKnowledge
        self.learningPurpose = learningPurpose
        self.timeCommitment = timeCommitment
        self.preferredResources = preferredResources
        self.content = content
        self.resources = resources
        self.createdAt = createdAt
        self.estimatedHours = estimatedHours
    }
} 