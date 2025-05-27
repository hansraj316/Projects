import Foundation
import Combine

class LearningPlanListViewModel: ObservableObject {
    @Published var learningPlans: [LearningPlan] = []
    @Published var isLoading: Bool = false
    @Published var error: String? = nil
    @Published var showPlanDetail: Bool = false
    @Published var selectedPlan: LearningPlan? = nil
    
    private let storeService: StoreService
    private var cancellables = Set<AnyCancellable>()
    
    init(storeService: StoreService) {
        self.storeService = storeService
    }
    
    func loadPlans() {
        isLoading = true
        
        DispatchQueue.global(qos: .userInitiated).async { [weak self] in
            guard let self = self else { return }
            
            let plans = self.storeService.getAllLearningPlans()
            
            DispatchQueue.main.async {
                // Sort plans by creation date (newest first)
                self.learningPlans = plans.sorted { $0.createdAt > $1.createdAt }
                self.isLoading = false
            }
        }
    }
    
    func deletePlan(at indexSet: IndexSet) {
        for index in indexSet {
            let planId = learningPlans[index].id
            storeService.deleteLearningPlan(id: planId)
        }
        
        // Reload plans after deletion
        loadPlans()
    }
} 