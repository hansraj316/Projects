import Foundation
import Combine
import Network

class LearningPlanViewModel: ObservableObject {
    // Input fields
    @Published var subject: String = ""
    @Published var level: String = "Beginner (No prior knowledge)"
    @Published var currentKnowledge: String = ""
    @Published var learningPurpose: String = ""
    @Published var timeCommitment: String = "3-5 hours"
    @Published var preferredResources: [String] = []
    
    // State
    @Published var currentStep: Int = 1
    @Published var isLoading: Bool = false
    @Published var error: String? = nil
    @Published var learningPlan: LearningPlan? = nil
    @Published var showPlanDetail: Bool = false
    
    // Services
    private let apiService: APIService
    private let storeService: StoreService
    private var cancellables = Set<AnyCancellable>()
    
    // Constants
    let knowledgeLevels = [
        "Beginner (No prior knowledge)",
        "Intermediate (Some basics understood)",
        "Advanced (Looking to deepen knowledge)"
    ]
    
    let timeCommitmentOptions = [
        "1-2 hours",
        "3-5 hours",
        "6-8 hours",
        "9-12 hours",
        "13+ hours"
    ]
    
    let resourceOptions = [
        "Articles",
        "Video tutorials",
        "Online courses",
        "Books",
        "Documentation",
        "Interactive exercises",
        "Forums & communities"
    ]
    
    init(apiService: APIService, storeService: StoreService) {
        self.apiService = apiService
        self.storeService = storeService
        
        // Set the API key from UserDefaults
        if let savedApiKey = UserDefaults.standard.string(forKey: "apiKey") {
            apiService.setAPIKey(savedApiKey)
        }
        
        // Observe changes to the API key
        NotificationCenter.default.addObserver(
            forName: NSNotification.Name("APIKeyChanged"),
            object: nil,
            queue: .main
        ) { [weak self] notification in
            if let apiKey = notification.userInfo?["apiKey"] as? String {
                self?.apiService.setAPIKey(apiKey)
            }
        }
    }
    
    func nextStep() {
        if validateCurrentStep() {
            currentStep += 1
        }
    }
    
    func previousStep() {
        if currentStep > 1 {
            currentStep -= 1
        }
    }
    
    func resetForm() {
        subject = ""
        level = "Beginner (No prior knowledge)"
        currentKnowledge = ""
        learningPurpose = ""
        timeCommitment = "3-5 hours"
        preferredResources = []
        currentStep = 1
        learningPlan = nil
        error = nil
    }
    
    func validateCurrentStep() -> Bool {
        switch currentStep {
        case 1:
            if subject.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty {
                error = "Please enter a subject"
                return false
            }
        case 3:
            if learningPurpose.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty {
                error = "Please enter your learning purpose"
                return false
            }
        case 5:
            if preferredResources.isEmpty {
                error = "Please select at least one resource type"
                return false
            }
        default:
            break
        }
        
        error = nil
        return true
    }
    
    func generatePlan() {
        if !validateCurrentStep() {
            return
        }
        
        isLoading = true
        error = nil
        
        // Check if we have a valid API key
        let apiKey = UserDefaults.standard.string(forKey: "apiKey") ?? ""
        if apiKey.isEmpty {
            isLoading = false
            error = "Please set your OpenAI API key in Settings"
            return
        }
        
        // Ensure the API service has the latest key
        apiService.setAPIKey(apiKey)
        
        // Check for network connectivity
        let monitor = NWPathMonitor()
        let queue = DispatchQueue(label: "NetworkCheck")
        
        monitor.pathUpdateHandler = { [weak self] path in
            guard let self = self else {
                monitor.cancel()
                return
            }
            
            DispatchQueue.main.async {
                if path.status != .satisfied {
                    self.isLoading = false
                    self.error = "No internet connection. Please check your network settings."
                    monitor.cancel()
                    return
                }
                
                // Network is available, proceed with API call
                self.executeAPICall()
                monitor.cancel()
            }
        }
        
        monitor.start(queue: queue)
    }
    
    private func executeAPICall() {
        apiService.createLearningPlan(
            subject: subject,
            level: level,
            currentKnowledge: currentKnowledge,
            learningPurpose: learningPurpose,
            timeCommitment: timeCommitment,
            preferredResources: preferredResources
        )
        .receive(on: DispatchQueue.main)
        .sink(
            receiveCompletion: { [weak self] completion in
                self?.isLoading = false
                
                if case .failure(let error) = completion {
                    switch error {
                    case .missingAPIKey:
                        self?.error = "Please set your OpenAI API key in Settings"
                    case .networkError(let err):
                        self?.error = "Network error: \(err.localizedDescription). Please check your connection."
                    case .serverError(let code):
                        self?.error = "Server error (\(code)). Please try again later."
                    case .openAIError(let message):
                        self?.error = "OpenAI API error: \(message)"
                    case .decodingError:
                        self?.error = "Error processing the response. Please try again."
                    default:
                        self?.error = "Error generating plan: \(error.localizedDescription)"
                    }
                }
            },
            receiveValue: { [weak self] plan in
                self?.learningPlan = plan
                self?.storeService.saveLearningPlan(plan)
            }
        )
        .store(in: &cancellables)
    }
    
    func loadPlan(id: String) {
        if let savedPlan = storeService.getLearningPlan(id: id) {
            self.learningPlan = savedPlan
            return
        }
        
        isLoading = true
        error = nil
        
        apiService.fetchLearningPlan(id: id)
            .receive(on: DispatchQueue.main)
            .sink(
                receiveCompletion: { [weak self] completion in
                    self?.isLoading = false
                    
                    if case .failure(let error) = completion {
                        switch error {
                        case .networkError:
                            self?.error = "Network error. Please check your connection."
                        default:
                            self?.error = "Error loading plan: \(error.localizedDescription)"
                        }
                    }
                },
                receiveValue: { [weak self] plan in
                    self?.learningPlan = plan
                    self?.storeService.saveLearningPlan(plan)
                }
            )
            .store(in: &cancellables)
    }
} 