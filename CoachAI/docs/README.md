# CoachAI Learning Wizard 🎓

CoachAI is an intelligent learning path generator that creates personalized learning plans using OpenAI's GPT-4 and web search capabilities. It helps learners create structured, up-to-date learning paths tailored to their goals, current level, and learning style.

## Features ✨

- 🎯 Personalized learning plan generation
- 🌐 Real-time web search integration for current resources
- 🎨 Learning style adaptation
- ⏱️ Time-based planning
- 📚 Curated resource recommendations
- 💾 Downloadable learning plans
- 💳 Subscription tiers with Stripe integration
- 📧 Email notifications for premium users
- 🔑 In-app OpenAI API key configuration

## System Architecture 🏗️

### High-Level Overview

```mermaid
graph TD
    A[User Interface] -->|Input| B[Streamlit App]
    B -->|Learning Goals| C[PlannerAgent]
    B -->|Payments| S[StripeAgent]
    B -->|Notifications| E[EmailAgent]
    C -->|API Request| D[OpenAI GPT-4]
    S -->|Payment Processing| P[Stripe API]
    D -->|Web Search| I[Internet]
    I -->|Search Results| D
    D -->|Response| C
    C -->|Learning Plan| B
    B -->|Display| A

    style A fill:#f9f,stroke:#333,stroke-width:2px
    style B fill:#bbf,stroke:#333,stroke-width:2px
    style C fill:#dfd,stroke:#333,stroke-width:2px
    style D fill:#fdd,stroke:#333,stroke-width:2px
    style E fill:#ddf,stroke:#333,stroke-width:2px
    style S fill:#ffd,stroke:#333,stroke-width:2px
    style P fill:#ffa,stroke:#333,stroke-width:2px
    style I fill:#ddd,stroke:#333,stroke-width:2px
```

### Detailed Component Architecture

```mermaid
graph TB
    subgraph Frontend
        A[Streamlit UI] -->|User Input| B[State Management]
        B -->|Session State| A
    end
    
    subgraph Backend
        C[PlannerAgent] -->|API Calls| D[OpenAI Client]
        D -->|Responses| C
        S[StripeAgent] -->|Payment Processing| P[Stripe API]
        P -->|Payment Status| S
        E[EmailAgent] -->|Send Notifications| M[Email Service]
    end
    
    subgraph External
        X[OpenAI API] -->|Web Search| I[Internet]
        I -->|Results| X
    end
    
    B -->|Learning Goals| C
    B -->|Payment Info| S
    B -->|Email Requests| E
    C -->|Learning Plan| B
    D -->|Requests| X
    X -->|Responses| D

    style Frontend fill:#f0f0f0,stroke:#333,stroke-width:2px
    style Backend fill:#e0e0e0,stroke:#333,stroke-width:2px
    style External fill:#d0d0d0,stroke:#333,stroke-width:2px
```

## User Flow 🔄

```mermaid
sequenceDiagram
    participant User
    participant UI as Streamlit UI
    participant PlanAgent as PlannerAgent
    participant StripeAgent as StripeAgent
    participant EmailAgent as EmailAgent
    participant OpenAI as GPT-4 + Web Search
    participant Stripe as Stripe API
    
    User->>UI: Enter Topic (Step 1)
    User->>UI: Select Current Level (Step 2)
    User->>UI: Set Learning Purpose (Step 3)
    User->>UI: Set Time Commitment (Step 4)
    User->>UI: Choose Preferred Resources (Step 5)
    UI->>PlanAgent: Create Learning Goal
    
    alt Freemium User
        Note over UI,PlanAgent: Limited resources (1 plan/day, 3 resources/plan)
    else Premium User
        Note over UI,PlanAgent: Full resources (10 plans/day, 10 resources/plan)
    end
    
    PlanAgent->>OpenAI: Generate Plan Request
    OpenAI-->>PlanAgent: Learning Plan
    PlanAgent->>OpenAI: Get Resources Request
    OpenAI-->>PlanAgent: Resource List
    PlanAgent->>UI: Complete Learning Plan
    UI->>User: Display Plan
    UI->>User: Offer Download
    
    opt Premium Upgrade
        User->>UI: Request Premium Upgrade
        UI->>StripeAgent: Create Checkout Session
        StripeAgent->>Stripe: Payment Request
        Stripe-->>User: Payment Form
        User->>Stripe: Complete Payment
        Stripe-->>StripeAgent: Payment Confirmation
        StripeAgent-->>UI: Update User Tier
        UI->>User: Show Success Page
        UI->>EmailAgent: Send Welcome Email
        EmailAgent-->>User: Email Confirmation
    end
    
    opt Email Plan (Premium Only)
        User->>UI: Request Email Delivery
        UI->>EmailAgent: Send Plan Email
        EmailAgent-->>User: Learning Plan Email
    end
```

## Prerequisites 📋

- Python 3.9+
- OpenAI API key
- Stripe API key (for subscription features)
- Streamlit
- Internet connection for web search functionality

## Quick Start 🚀

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/CoachAI.git
cd CoachAI
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Unix
venv\Scripts\activate     # Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt  # For development
```

4. Set up your API keys:
```bash
# Create a .env file or export directly
export OPENAI_API_KEY='your-openai-api-key-here'
export STRIPE_SECRET_KEY='your-stripe-secret-key-here'
export STRIPE_WEBHOOK_SECRET='your-stripe-webhook-secret-here'
```

### Usage

1. Start the Streamlit app:
```bash
streamlit run ui/web/app.py
```

2. Follow the 5-step wizard to create your learning plan:
   - Step 1: Choose your learning topic
   - Step 2: Specify your current knowledge level
   - Step 3: Define your learning purpose
   - Step 4: Set your time commitment
   - Step 5: Select preferred learning resources

3. Get your personalized learning plan!

4. Upgrade to Premium for additional features:
   - 10 learning plans per day (vs 1 for free users)
   - 10 resources per plan (vs 3 for free users)
   - Email delivery of learning plans
   - Priority support

5. Configure your OpenAI API key in the app:
   - Expand the "⚙️ API Settings" section in the sidebar
   - Enter your OpenAI API key
   - Click "Save API Key"

## Development Guide 👩‍💻

### Project Structure 📁

```
CoachAI/
├── agents/
│   ├── planner.py         # Core planning logic and OpenAI integration
│   ├── email_agent.py     # Email notification handling
│   └── stripe_agent.py    # Subscription and payment processing
├── ui/
│   └── web/
│       └── app.py         # Streamlit web interface
├── src/
│   └── config.py          # Configuration and settings
├── tests/
│   ├── test_planner.py
│   ├── test_stripe.py
│   └── test_ui.py
└── README.md             # Project documentation
```

### Component Details

#### 1. Streamlit UI Flow

```mermaid
stateDiagram-v2
    [*] --> Step1
    Step1 --> Step2: Topic Selected
    Step2 --> Step3: Knowledge Level Set
    Step3 --> Step4: Purpose Set
    Step4 --> Step5: Time Commitment Set
    Step5 --> Generation: Resources Chosen
    Generation --> PlanDisplay: Plan Created
    PlanDisplay --> [*]: Done
    
    state PlanDisplay {
        [*] --> ShowPlan
        ShowPlan --> Download: Download Button
        ShowPlan --> Email: Email Button (Premium)
        ShowPlan --> Upgrade: Upgrade Button (Freemium)
        Upgrade --> Payment: Checkout
        Payment --> Premium: Success
        Payment --> ShowPlan: Cancel
    }
```

#### 2. Core Classes

```mermaid
classDiagram
    class BaseModel {
        <<Pydantic>>
    }
    class LearningGoal {
        +str subject
        +str level
        +str current_knowledge
        +str learning_purpose
        +str time_commitment
        +str preferred_resources
    }
    class LearningPlan {
        +str content
        +List[str] suggested_resources
        +str estimated_duration
    }
    class PlannerAgent {
        -OpenAI client
        +create_plan(goal: LearningGoal) LearningPlan
        -_format_resources(text: str) List[str]
    }
    class SubscriptionTier {
        <<Enum>>
        FREEMIUM
        PREMIUM
    }
    class SubscriptionConfig {
        +int daily_plans
        +int resources_per_plan
        +bool email_notifications
        +float price
        +SubscriptionTier tier
    }
    class StripeAgent {
        -string api_key
        +tier_configs: Dict
        +create_checkout_session()
        +update_subscription_status()
        +get_tier_features()
    }
    class EmailAgent {
        +send_email()
        +send_learning_plan_email()
    }

    BaseModel <|-- LearningGoal
    BaseModel <|-- LearningPlan
    PlannerAgent ..> LearningGoal
    PlannerAgent ..> LearningPlan
    StripeAgent ..> SubscriptionTier
    StripeAgent ..> SubscriptionConfig
```

### API Integration 🔌

#### OpenAI

```python
# Example OpenAI Responses API call
response = client.responses.create(
    model="gpt-4o",
    tools=[{"type": "web_search_preview"}],
    input="Your prompt here"
)
```

#### Stripe

```python
# Example Stripe checkout session creation
checkout_session = stripe.checkout.Session.create(
    success_url="http://localhost:8501/success?session_id={CHECKOUT_SESSION_ID}",
    cancel_url="http://localhost:8501/cancel",
    mode="subscription",
    line_items=[{"price": "price_id", "quantity": 1}]
)
```

### Session State Management

The application uses Streamlit's session state for maintaining user data across steps:

```python
# Session state initialization
if "step" not in st.session_state:
    st.session_state.step = 1

if "subject" not in st.session_state:
    st.session_state.subject = ""

# Form handling with session state
subject_value = st.session_state.get("subject", "")
subject = st.text_input("Subject or Topic", value=subject_value)

# Storing values in session state
if st.button("Next"):
    st.session_state["subject"] = subject
    next_step()
```

### Webhook Handling

For handling Stripe webhooks, we use a dedicated endpoint in the Streamlit app:

```python
async def handle_webhook():
    """Handle incoming Stripe webhook events."""
    # Verify webhook signature
    # Process different event types like 'checkout.session.completed'
    # Update user subscription status
```

### Code Style 📝

We follow PEP 8 with these additions:
- Line length: 88 characters (Black formatter)
- Docstring style: Google format
- Type hints: Required for all functions

Example:
```python
def process_data(input_data: str) -> Dict[str, Any]:
    """Process the input data and return results.

    Args:
        input_data: The raw input string to process.

    Returns:
        Dict containing processed results.

    Raises:
        ValueError: If input_data is invalid.
    """
    pass
```

### Testing 🧪

Run tests with:
```bash
pytest tests/                    # Run all tests
pytest tests/ -v --cov=src      # With coverage
pytest tests/integration/       # Integration tests
```

### Deployment 🚀

#### Production Setup

1. Environment variables:
```bash
OPENAI_API_KEY=your-key-here
STRIPE_SECRET_KEY=your-stripe-key-here
STRIPE_WEBHOOK_SECRET=your-webhook-secret-here
STREAMLIT_SERVER_PORT=8501
```

2. Docker deployment:
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
CMD ["streamlit", "run", "ui/web/app.py"]
```

### Best Practices 🎯

1. Performance Optimization:
   - Cache frequent API requests
   - Implement rate limiting
   - Monitor memory usage
   - Handle concurrent users

2. Security:
   - Use environment variables for secrets
   - Implement key rotation
   - Sanitize inputs
   - Validate form data before submission
   - Verify webhook signatures

### Troubleshooting 🔍

1. OpenAI API Issues:
   - Verify API key and format
   - Check rate limits
   - Monitor usage
   - Use the in-app API key configuration if needed

2. Stripe API Issues:
   - Validate API keys
   - Check webhook configuration
   - Ensure correct product/price setup
   - Test with Stripe CLI

3. Streamlit Issues:
   - Clear cache: `streamlit cache clear`
   - Check port conflicts
   - Verify session state initialization
   - Check for widget key conflicts

4. Form Data Issues:
   - Ensure all input validation is in place
   - Check for empty string values in session state
   - Validate selections against available options
   - Use defensive programming for all form inputs

## Recent Improvements 🆕

- 🔧 Enhanced session state management to maintain data between steps
- 🛠️ Improved form validation and error handling
- 🔐 Added in-app OpenAI API key configuration
- 🔍 Better debugging for API connections 
- 🧪 Fixed handling of multiselect values between steps
- 🔄 Better loading indicators and error messages

## Contributing 🤝

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Write tests and documentation
4. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
5. Push to the branch (`git push origin feature/AmazingFeature`)
6. Open a Pull Request

## License 📄

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments 🙏

- OpenAI for their powerful GPT-4 API
- Stripe for payment processing
- Streamlit for the amazing web framework
- All contributors and users of CoachAI

## Support 💪

For support, please open an issue in the GitHub repository or contact the maintainers.

---

Made with ❤️ by [Your Name/Team] 