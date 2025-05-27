import Foundation
import Combine

class StoreService {
    private let defaults = UserDefaults.standard
    private let learningPlanKey = "learningPlans"
    private let timeLogsKey = "timeLogs"
    
    // MARK: - Learning Plans
    
    func saveLearningPlan(_ plan: LearningPlan) {
        var plans = getAllLearningPlans()
        
        // Update existing or add new
        if let index = plans.firstIndex(where: { $0.id == plan.id }) {
            plans[index] = plan
        } else {
            plans.append(plan)
        }
        
        do {
            let data = try JSONEncoder().encode(plans)
            defaults.set(data, forKey: learningPlanKey)
        } catch {
            print("Error saving learning plan: \(error)")
        }
    }
    
    func getAllLearningPlans() -> [LearningPlan] {
        guard let data = defaults.data(forKey: learningPlanKey) else { return [] }
        
        do {
            return try JSONDecoder().decode([LearningPlan].self, from: data)
        } catch {
            print("Error loading learning plans: \(error)")
            return []
        }
    }
    
    func getLearningPlan(id: String) -> LearningPlan? {
        return getAllLearningPlans().first(where: { $0.id == id })
    }
    
    func deleteLearningPlan(id: String) {
        var plans = getAllLearningPlans()
        plans.removeAll(where: { $0.id == id })
        
        do {
            let data = try JSONEncoder().encode(plans)
            defaults.set(data, forKey: learningPlanKey)
        } catch {
            print("Error deleting learning plan: \(error)")
        }
    }
    
    // MARK: - Time Logs
    
    func saveTimeLog(_ log: TimeLog) {
        var logs = getAllTimeLogs()
        
        // Add new log
        logs.append(log)
        
        do {
            let data = try JSONEncoder().encode(logs)
            defaults.set(data, forKey: timeLogsKey)
        } catch {
            print("Error saving time log: \(error)")
        }
    }
    
    func getAllTimeLogs() -> [TimeLog] {
        guard let data = defaults.data(forKey: timeLogsKey) else { return [] }
        
        do {
            return try JSONDecoder().decode([TimeLog].self, from: data)
        } catch {
            print("Error loading time logs: \(error)")
            return []
        }
    }
    
    func getTimeLogs(forPlanId planId: String) -> [TimeLog] {
        return getAllTimeLogs().filter { $0.planId == planId }
    }
    
    func calculateTotalTimeSpent() -> Double {
        return getAllTimeLogs().reduce(0) { $0 + $1.hours }
    }
    
    func calculateTimeSpentToday() -> Double {
        let today = Calendar.current.startOfDay(for: Date())
        
        return getAllTimeLogs()
            .filter { Calendar.current.isDate($0.timestamp, inSameDayAs: today) }
            .reduce(0) { $0 + $1.hours }
    }
    
    func calculateTimeSpent(forPlanId planId: String) -> Double {
        return getTimeLogs(forPlanId: planId).reduce(0) { $0 + $1.hours }
    }
} 