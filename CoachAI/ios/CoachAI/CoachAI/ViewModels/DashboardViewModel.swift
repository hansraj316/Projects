import Foundation
import Combine

class DashboardViewModel: ObservableObject {
    // Data
    @Published var learningPlans: [LearningPlan] = []
    @Published var timeLogs: [TimeLog] = []
    @Published var totalTimeSpent: Double = 0.0
    @Published var timeSpentToday: Double = 0.0
    @Published var completionPercentage: Double = 0.0
    @Published var hoursToLog: Double = 0.0
    @Published var logNotes: String = ""
    
    // State
    @Published var isLoading: Bool = false
    @Published var error: String? = nil
    @Published var selectedPlanId: String? = nil
    @Published var showAllPlans: Bool = false
    @Published var showPlanDetail: Bool = false
    @Published var selectedPlanForDetail: LearningPlan? = nil
    
    // Services
    private let storeService: StoreService
    private let apiService: APIService
    private var cancellables = Set<AnyCancellable>()
    
    init(storeService: StoreService, apiService: APIService) {
        self.storeService = storeService
        self.apiService = apiService
        
        loadData()
    }
    
    func loadData() {
        isLoading = true
        
        DispatchQueue.global(qos: .userInitiated).async { [weak self] in
            guard let self = self else { return }
            
            let plans = self.storeService.getAllLearningPlans()
            let logs = self.storeService.getAllTimeLogs()
            let total = self.storeService.calculateTotalTimeSpent()
            let today = self.storeService.calculateTimeSpentToday()
            
            DispatchQueue.main.async {
                self.learningPlans = plans
                self.timeLogs = logs
                self.totalTimeSpent = total
                self.timeSpentToday = today
                
                self.calculateCompletionPercentage()
                self.isLoading = false
            }
        }
    }
    
    func calculateCompletionPercentage() {
        guard let selectedPlan = selectedPlanId,
              let plan = learningPlans.first(where: { $0.id == selectedPlan }) else {
            completionPercentage = 0.0
            return
        }
        
        let planTime = storeService.calculateTimeSpent(forPlanId: plan.id)
        
        // Validate both planTime and estimatedHours to prevent NaN values
        guard planTime.isFinite && planTime >= 0,
              plan.estimatedHours.isFinite && plan.estimatedHours > 0 else {
            completionPercentage = 0.0
            return
        }
        
        let percentage = (planTime / plan.estimatedHours) * 100
        
        // Ensure the result is finite and within valid range
        if percentage.isFinite {
            completionPercentage = min(100, max(0, percentage))
        } else {
            completionPercentage = 0.0
        }
    }
    
    func logTime() {
        guard hoursToLog > 0, let planId = selectedPlanId else {
            error = "Please enter a valid time and select a plan"
            return
        }
        
        isLoading = true
        error = nil
        
        let timeLog = TimeLog(planId: planId, hours: hoursToLog, notes: logNotes.isEmpty ? nil : logNotes)
        
        // Save to local storage
        storeService.saveTimeLog(timeLog)
        
        // Reset form and reload data
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.5) { [weak self] in
            self?.isLoading = false
            self?.hoursToLog = 0.0
            self?.logNotes = ""
            self?.loadData()
        }
    }
    
    func selectPlan(_ plan: LearningPlan) {
        selectedPlanId = plan.id
        calculateCompletionPercentage()
    }
    
    func getTimeLogsForCurrentPlan() -> [TimeLog] {
        guard let selectedPlan = selectedPlanId else {
            return []
        }
        
        return timeLogs.filter { $0.planId == selectedPlan }
            .sorted { $0.timestamp > $1.timestamp }
    }
    
    func getTimeSpent(forPlanId planId: String) -> Double {
        return storeService.calculateTimeSpent(forPlanId: planId)
    }
} 