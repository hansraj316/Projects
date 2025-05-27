import Foundation
import Combine

enum APIError: Error {
    case invalidURL
    case networkError(Error)
    case decodingError(error: Error)
    case serverError(statusCode: Int)
    case missingAPIKey
    case requestFailed(String)
    case openAIError(String)
    case unknown
    case invalidResponse
    
    var localizedDescription: String {
        switch self {
        case .networkError(let error):
            if let urlError = error as? URLError {
                switch urlError.code {
                case .notConnectedToInternet:
                    return "Not connected to the internet. Please check your network connection."
                case .timedOut:
                    return "Request timed out. Please try again."
                case .cannotConnectToHost:
                    return "Cannot connect to OpenAI servers. Please try again later."
                case .networkConnectionLost:
                    return "Network connection was lost. Retrying..."
                default:
                    return "Network error: \(error.localizedDescription)"
                }
            }
            return "Network error: \(error.localizedDescription)"
        case .serverError(let statusCode):
            return "Server error with status code: \(statusCode)"
        case .decodingError(let error):
            return "Failed to decode response: \(error.localizedDescription)"
        case .invalidResponse:
            return "Invalid response from server"
        case .openAIError(let message):
            return "OpenAI API error: \(message)"
        case .unknown:
            return "An unknown error occurred"
        case .invalidURL:
            return "Invalid URL provided"
        case .missingAPIKey:
            return "API key is missing"
        case .requestFailed(let reason):
            return "Request failed: \(reason)"
        }
    }
}

// OpenAI Chat Completions API response structure
struct OpenAIResponse: Codable {
    let id: String
    let object: String
    let created: Int
    let model: String
    let choices: [Choice]
    let usage: Usage?
}

struct Choice: Codable {
    let index: Int
    let message: Message
    let finish_reason: String?
}

struct Message: Codable {
    let role: String
    let content: String?
}

struct Usage: Codable {
    let prompt_tokens: Int
    let completion_tokens: Int
    let total_tokens: Int
}

class APIService {
    // MARK: - Properties
    private let openAIURL = "https://api.openai.com/v1/chat/completions"
    private var apiKey: String
    private var customSession: URLSession
    
    init(apiKey: String = "") {
        self.apiKey = apiKey
        
        // Create a proper URLSession configuration for reusable connections
        let config = URLSessionConfiguration.default
        config.timeoutIntervalForRequest = 60
        config.timeoutIntervalForResource = 120
        config.httpMaximumConnectionsPerHost = 2
        config.requestCachePolicy = .reloadIgnoringLocalCacheData
        config.urlCache = nil
        config.httpShouldUsePipelining = false
        
        self.customSession = URLSession(configuration: config)
    }
    
    func setAPIKey(_ key: String) {
        self.apiKey = key
    }
    
    // Method to reset the session if needed
    private func resetSession() {
        customSession.invalidateAndCancel()
        
        let config = URLSessionConfiguration.default
        config.timeoutIntervalForRequest = 60
        config.timeoutIntervalForResource = 120
        config.httpMaximumConnectionsPerHost = 2
        config.requestCachePolicy = .reloadIgnoringLocalCacheData
        config.urlCache = nil
        config.httpShouldUsePipelining = false
        
        self.customSession = URLSession(configuration: config)
    }
    
    func createLearningPlan(subject: String, 
                           level: String, 
                           currentKnowledge: String, 
                           learningPurpose: String, 
                           timeCommitment: String, 
                           preferredResources: [String]) -> AnyPublisher<LearningPlan, APIError> {
        
        guard !apiKey.isEmpty else {
            return Fail(error: APIError.missingAPIKey).eraseToAnyPublisher()
        }
        
        guard let url = URL(string: openAIURL) else {
            return Fail(error: APIError.invalidURL).eraseToAnyPublisher()
        }
        
        // Create the prompt for GPT
        let prompt = """
        I need a structured learning plan for: "\(subject)"

        Please use these specifics:
        - Level: \(level)
        - Current knowledge: \(currentKnowledge)
        - Goal: \(learningPurpose)
        - Time available: \(timeCommitment) per week
        - Preferred resources: \(preferredResources.joined(separator: ", "))

        Respond ONLY with a valid JSON object in this exact format:
        {
          "content": "The detailed markdown learning plan content",
          "resources": [
            {
              "title": "Resource title",
              "url": "Resource URL",
              "type": "article|video|course|book|interactive|documentation|other"
            }
          ],
          "estimatedHours": total_hours_number
        }
        """
        
        // Create OpenAI Chat Completions API request
        let openAIParameters: [String: Any] = [
            "model": "gpt-4o",
            "messages": [
                [
                    "role": "system",
                    "content": "You are an expert educational content creator and learning coach. Respond ONLY with valid JSON objects."
                ],
                [
                    "role": "user",
                    "content": """
                    I need a structured learning plan for: "\(subject)"

                    Please use these specifics:
                    - Level: \(level)
                    - Current knowledge: \(currentKnowledge)
                    - Goal: \(learningPurpose)
                    - Time available: \(timeCommitment) per week
                    - Preferred resources: \(preferredResources.joined(separator: ", "))

                    Respond ONLY with a valid JSON object in this exact format:
                    {
                      "content": "The detailed markdown learning plan content",
                      "resources": [
                        {
                          "title": "Resource title",
                          "url": "Resource URL",
                          "type": "article"
                        }
                      ],
                      "estimatedHours": 20
                    }
                    """
                ]
            ],
            "temperature": 0.7,
            "max_tokens": 4096,
            "response_format": ["type": "json_object"]
        ]
        
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.addValue("application/json", forHTTPHeaderField: "Content-Type")
        request.addValue("Bearer \(apiKey)", forHTTPHeaderField: "Authorization")
        request.addValue("no-cache", forHTTPHeaderField: "Cache-Control")
        request.addValue("close", forHTTPHeaderField: "Connection")
        request.timeoutInterval = 60
        request.cachePolicy = .reloadIgnoringLocalAndRemoteCacheData
        
        do {
            let jsonData = try JSONSerialization.data(withJSONObject: openAIParameters)
            request.httpBody = jsonData
        } catch {
            return Fail(error: APIError.networkError(error)).eraseToAnyPublisher()
        }
        
        let publisher = customSession.dataTaskPublisher(for: request)
            .tryMap { data, response -> Data in
                guard let httpResponse = response as? HTTPURLResponse else {
                    throw APIError.serverError(statusCode: 500)
                }
                
                switch httpResponse.statusCode {
                case 200...299:
                    return data
                case 401:
                    throw APIError.missingAPIKey
                case 429:
                    throw APIError.openAIError("Rate limit exceeded")
                case 500...599:
                    throw APIError.serverError(statusCode: httpResponse.statusCode)
                default:
                    throw APIError.serverError(statusCode: httpResponse.statusCode)
                }
            }
            .decode(type: OpenAIResponse.self, decoder: JSONDecoder())
            .tryMap { response -> LearningPlan in
                // Debug: Print the entire response to understand the structure
                print("🔍 Full OpenAI Response: \(response)")
                
                // Extract the content from the Chat Completions API response
                guard let firstChoice = response.choices.first,
                      let outputText = firstChoice.message.content else {
                    print("❌ No content in response choices")
                    throw APIError.invalidResponse
                }
                
                print("📝 Output text: \(outputText)")
                
                // Try to parse the JSON response
                guard let jsonData = outputText.data(using: .utf8) else {
                    print("❌ Could not convert output_text to data")
                    // Fallback: use the raw output as content
                    return LearningPlan(
                        subject: subject,
                        level: level,
                        currentKnowledge: currentKnowledge,
                        learningPurpose: learningPurpose,
                        timeCommitment: timeCommitment,
                        preferredResources: preferredResources,
                        content: outputText,
                        resources: [],
                        estimatedHours: 20.0
                    )
                }
                
                guard let jsonObject = try? JSONSerialization.jsonObject(with: jsonData) as? [String: Any] else {
                    print("❌ Could not parse JSON from output_text")
                    // Fallback: use the raw output as content
                    return LearningPlan(
                        subject: subject,
                        level: level,
                        currentKnowledge: currentKnowledge,
                        learningPurpose: learningPurpose,
                        timeCommitment: timeCommitment,
                        preferredResources: preferredResources,
                        content: outputText,
                        resources: [],
                        estimatedHours: 20.0
                    )
                }
                
                print("📊 Parsed JSON: \(jsonObject)")
                
                guard let content = jsonObject["content"] as? String,
                      let resourcesArray = jsonObject["resources"] as? [[String: Any]] else {
                    print("❌ Missing required fields in JSON")
                    // Fallback: use the raw output as content
                    return LearningPlan(
                        subject: subject,
                        level: level,
                        currentKnowledge: currentKnowledge,
                        learningPurpose: learningPurpose,
                        timeCommitment: timeCommitment,
                        preferredResources: preferredResources,
                        content: outputText,
                        resources: [],
                        estimatedHours: 20.0
                    )
                }
                
                // Safely parse estimatedHours with validation
                var estimatedHours: Double = 20.0
                if let hours = jsonObject["estimatedHours"] as? Double {
                    // Check for NaN or infinite values that could cause CoreGraphics issues
                    if hours.isFinite && hours > 0 {
                        estimatedHours = hours
                    } else {
                        print("⚠️ Invalid estimatedHours value: \(hours), using default")
                    }
                } else if let hoursInt = jsonObject["estimatedHours"] as? Int {
                    estimatedHours = Double(hoursInt)
                }
                
                // Parse resources
                let resources = resourcesArray.compactMap { resourceDict -> LearningPlan.Resource? in
                    guard let title = resourceDict["title"] as? String,
                          let url = resourceDict["url"] as? String,
                          let typeString = resourceDict["type"] as? String else {
                        return nil
                    }
                    
                    let resourceType: LearningPlan.ResourceType
                    switch typeString.lowercased() {
                    case "article": resourceType = .article
                    case "video": resourceType = .video
                    case "course": resourceType = .course
                    case "book": resourceType = .book
                    case "interactive": resourceType = .interactive
                    case "documentation": resourceType = .documentation
                    default: resourceType = .other
                    }
                    
                    return LearningPlan.Resource(title: title, url: url, type: resourceType)
                }
                
                return LearningPlan(
                    subject: subject,
                    level: level,
                    currentKnowledge: currentKnowledge,
                    learningPurpose: learningPurpose,
                    timeCommitment: timeCommitment,
                    preferredResources: preferredResources,
                    content: content,
                    resources: resources,
                    estimatedHours: estimatedHours
                )
            }
            .mapError { [weak self] error -> APIError in
                if let apiError = error as? APIError {
                    // Reset session on certain network errors that might indicate session corruption
                    if case .networkError(let underlying) = apiError,
                       let urlError = underlying as? URLError {
                        switch urlError.code {
                        case .badServerResponse, .cannotConnectToHost, .networkConnectionLost:
                            print("Resetting session due to: \(urlError.localizedDescription)")
                            self?.resetSession()
                        default:
                            break
                        }
                    }
                    return apiError
                }
                if let decodingError = error as? DecodingError {
                    print("Decoding error: \(decodingError)")
                    return APIError.decodingError(error: decodingError)
                }
                return APIError.networkError(error)
            }
            .retryOnNetworkConnectionLost(retries: 3, delay: 1.0)  // Retry up to 3 times with 1 second delay
            .eraseToAnyPublisher()

        return publisher
    }
    
    func fetchLearningPlan(id: String) -> AnyPublisher<LearningPlan, APIError> {
        guard !apiKey.isEmpty else {
            return Fail(error: APIError.missingAPIKey).eraseToAnyPublisher()
        }
        
        // For demo purposes, we'll create a mock learning plan
        return Future<LearningPlan, APIError> { promise in
            // Simulate network delay
            DispatchQueue.main.asyncAfter(deadline: .now() + 1.0) {
                let sampleResources = [
                    LearningPlan.Resource(
                        title: "Comprehensive Guide",
                        url: "https://example.com/guide",
                        type: .article
                    ),
                    LearningPlan.Resource(
                        title: "Video Tutorial Series",
                        url: "https://example.com/videos",
                        type: .video
                    )
                ]
                
                let content = """
                # Demo Learning Plan
                
                This is a demo learning plan retrieved by ID. In a real app, this would
                contain the full details of the requested learning plan.
                
                ## Sample Schedule
                - Week 1: Introduction
                - Week 2: Core Concepts
                - Week 3: Advanced Topics
                - Week 4: Practical Application
                """
                
                // Create a sample learning plan with the requested ID
                let plan = LearningPlan(
                    id: id,
                    subject: "Sample Subject",
                    level: "Intermediate",
                    currentKnowledge: "Some basic understanding",
                    learningPurpose: "To master the fundamentals",
                    timeCommitment: "3-5 hours",
                    preferredResources: ["Articles", "Videos"],
                    content: content,
                    resources: sampleResources,
                    estimatedHours: 25.0
                )
                
                promise(.success(plan))
            }
        }.eraseToAnyPublisher()
    }
    
    func logLearningTime(planId: String, hours: Double, notes: String?) -> AnyPublisher<TimeLog, APIError> {
        guard !apiKey.isEmpty else {
            return Fail(error: APIError.missingAPIKey).eraseToAnyPublisher()
        }
        
        // For demo purposes, we'll create a mock time log
        return Future<TimeLog, APIError> { promise in
            // Simulate network delay
            DispatchQueue.main.asyncAfter(deadline: .now() + 0.5) {
                // Create a sample time log entry with the provided details
                let timeLog = TimeLog(
                    planId: planId,
                    hours: hours,
                    notes: notes
                )
                
                promise(.success(timeLog))
            }
        }.eraseToAnyPublisher()
    }
}

// MARK: - Combine Publisher Extension for Retry Logic
import Combine

extension Publisher {
    func retryOnNetworkConnectionLost(retries: Int, delay: TimeInterval) -> AnyPublisher<Output, Failure> {
        self.catch { error -> AnyPublisher<Output, Failure> in
            guard retries > 0 else {
                return Fail(error: error).eraseToAnyPublisher()
            }
            
            // Check for network-related errors
            if let apiError = error as? APIError,
               case .networkError(let underlying) = apiError,
               let urlError = underlying as? URLError {
                switch urlError.code {
                case .cancelled:
                    return Fail(error: error).eraseToAnyPublisher()
                case .badURL:
                    return Fail(error: error).eraseToAnyPublisher()
                case .timedOut:
                    print("Request timed out. Retrying in \(delay) seconds...")
                    return self
                        .delay(for: .seconds(delay), scheduler: DispatchQueue.global())
                        .retryOnNetworkConnectionLost(retries: retries - 1, delay: delay * 2)
                        .eraseToAnyPublisher()
                case .unsupportedURL:
                    return Fail(error: error).eraseToAnyPublisher()
                case .cannotFindHost:
                    print("Cannot find host. Retrying in \(delay) seconds...")
                    return self
                        .delay(for: .seconds(delay), scheduler: DispatchQueue.global())
                        .retryOnNetworkConnectionLost(retries: retries - 1, delay: delay * 2)
                        .eraseToAnyPublisher()
                case .cannotConnectToHost:
                    print("Cannot connect to host. Retrying in \(delay) seconds...")
                    return self
                        .delay(for: .seconds(delay), scheduler: DispatchQueue.global())
                        .retryOnNetworkConnectionLost(retries: retries - 1, delay: delay * 2)
                        .eraseToAnyPublisher()
                case .networkConnectionLost:
                    print("Network connection lost. Retrying in \(delay) seconds...")
                    return self
                        .delay(for: .seconds(delay), scheduler: DispatchQueue.global())
                        .retryOnNetworkConnectionLost(retries: retries - 1, delay: delay * 2)
                        .eraseToAnyPublisher()
                case .dnsLookupFailed:
                    print("DNS lookup failed. Retrying in \(delay) seconds...")
                    return self
                        .delay(for: .seconds(delay), scheduler: DispatchQueue.global())
                        .retryOnNetworkConnectionLost(retries: retries - 1, delay: delay * 2)
                        .eraseToAnyPublisher()
                case .httpTooManyRedirects:
                    return Fail(error: error).eraseToAnyPublisher()
                case .resourceUnavailable:
                    return Fail(error: error).eraseToAnyPublisher()
                case .notConnectedToInternet:
                    print("No internet connection. Retrying in \(delay) seconds...")
                    return self
                        .delay(for: .seconds(delay), scheduler: DispatchQueue.global())
                        .retryOnNetworkConnectionLost(retries: retries - 1, delay: delay * 2)
                        .eraseToAnyPublisher()
                case .redirectToNonExistentLocation:
                    return Fail(error: error).eraseToAnyPublisher()
                case .badServerResponse:
                    return Fail(error: error).eraseToAnyPublisher()
                case .userCancelledAuthentication:
                    return Fail(error: error).eraseToAnyPublisher()
                case .userAuthenticationRequired:
                    return Fail(error: error).eraseToAnyPublisher()
                case .zeroByteResource:
                    return Fail(error: error).eraseToAnyPublisher()
                case .cannotDecodeRawData:
                    return Fail(error: error).eraseToAnyPublisher()
                case .cannotDecodeContentData:
                    return Fail(error: error).eraseToAnyPublisher()
                case .cannotParseResponse:
                    return Fail(error: error).eraseToAnyPublisher()
                case .appTransportSecurityRequiresSecureConnection:
                    return Fail(error: error).eraseToAnyPublisher()
                case .fileDoesNotExist:
                    return Fail(error: error).eraseToAnyPublisher()
                case .fileIsDirectory:
                    return Fail(error: error).eraseToAnyPublisher()
                case .noPermissionsToReadFile:
                    return Fail(error: error).eraseToAnyPublisher()
                case .dataLengthExceedsMaximum:
                    return Fail(error: error).eraseToAnyPublisher()
                case .secureConnectionFailed:
                    print("Secure connection failed. Retrying in \(delay) seconds...")
                    return self
                        .delay(for: .seconds(delay), scheduler: DispatchQueue.global())
                        .retryOnNetworkConnectionLost(retries: retries - 1, delay: delay * 2)
                        .eraseToAnyPublisher()
                case .serverCertificateHasBadDate:
                    return Fail(error: error).eraseToAnyPublisher()
                case .serverCertificateUntrusted:
                    return Fail(error: error).eraseToAnyPublisher()
                case .serverCertificateHasUnknownRoot:
                    return Fail(error: error).eraseToAnyPublisher()
                case .serverCertificateNotYetValid:
                    return Fail(error: error).eraseToAnyPublisher()
                case .clientCertificateRejected:
                    return Fail(error: error).eraseToAnyPublisher()
                case .clientCertificateRequired:
                    return Fail(error: error).eraseToAnyPublisher()
                case .cannotLoadFromNetwork:
                    print("Cannot load from network. Retrying in \(delay) seconds...")
                    return self
                        .delay(for: .seconds(delay), scheduler: DispatchQueue.global())
                        .retryOnNetworkConnectionLost(retries: retries - 1, delay: delay * 2)
                        .eraseToAnyPublisher()
                case .backgroundSessionRequiresSharedContainer:
                    return Fail(error: error).eraseToAnyPublisher()
                case .backgroundSessionInUseByAnotherProcess:
                    return Fail(error: error).eraseToAnyPublisher()
                case .backgroundSessionWasDisconnected:
                    return Fail(error: error).eraseToAnyPublisher()
                default:
                    return Fail(error: error).eraseToAnyPublisher()
                }
            }
            
            return Fail(error: error).eraseToAnyPublisher()
        }
        .eraseToAnyPublisher()
    }
} 
