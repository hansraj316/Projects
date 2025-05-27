import Foundation

struct TimeLog: Identifiable, Codable {
    var id: UUID
    var planId: String
    var hours: Double
    var timestamp: Date
    var notes: String?
    
    init(id: UUID = UUID(), planId: String, hours: Double, timestamp: Date = Date(), notes: String? = nil) {
        self.id = id
        self.planId = planId
        self.hours = hours
        self.timestamp = timestamp
        self.notes = notes
    }
} 