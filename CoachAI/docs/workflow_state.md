# Workflow State Management

## Session State in CoachAI

CoachAI uses Streamlit's session state to maintain the application's state across multiple steps of the learning plan creation wizard and track learning progress. This document outlines how session state is managed throughout the application.

### Key Session State Variables

| Variable | Type | Description | Default Value |
|----------|------|-------------|---------------|
| `step` | `int` | Current step in the wizard (1-5) | `1` |
| `subject` | `str` | Topic the user wants to learn | `""` |
| `level` | `str` | User's current knowledge level | `"Beginner (No prior knowledge)"` |
| `current_knowledge` | `str` | User's description of their knowledge | `""` |
| `learning_purpose` | `str` | Why the user wants to learn the subject | `""` |
| `time_commitment` | `str` | User's weekly time commitment | `"3-5 hours"` |
| `preferred_resources` | `str` or `list` | Learning resources (as string or list) | `""` |
| `preferred_resources_str` | `str` | String version of preferred resources | `""` |
| `subscription` | `SubscriptionConfig` | User's subscription configuration | `SubscriptionConfig(FREEMIUM)` |
| `plans_created` | `int` | Total plans created by the user | `0` |
| `plans_created_today` | `int` | Plans created today (resets daily) | `0` |
| `learning_plan` | `LearningPlan` | Generated learning plan | `None` |
| `current_page` | `str` | Current page in navigation | `"learning_plan"` |
| `theme_mode` | `str` | UI theme (light/dark) | `"dark"` |
| `actual_time_spent` | `float` | Total time spent on learning | `0.0` |
| `today_time_spent` | `float` | Time spent today on learning | `0.0` |
| `time_logs` | `dict` | History of logged time entries | `{}`|
| `user_data` | `dict` | User's persistent data | `{}`|

### Initialization

Session state is initialized when the application starts and for new users:

```python
# Initialize the session state
if "step" not in st.session_state:
    st.session_state.step = 1

if "subject" not in st.session_state:
    st.session_state.subject = ""
    
# Initialize other form fields
if "level" not in st.session_state:
    st.session_state.level = ""
    
if "current_knowledge" not in st.session_state:
    st.session_state.current_knowledge = ""
    
if "learning_purpose" not in st.session_state:
    st.session_state.learning_purpose = ""
    
if "time_commitment" not in st.session_state:
    st.session_state.time_commitment = ""
    
if "preferred_resources" not in st.session_state:
    st.session_state.preferred_resources = ""
    
# Initialize plan counters
if "plans_created" not in st.session_state:
    st.session_state.plans_created = 0
    
if "plans_created_today" not in st.session_state:
    st.session_state.plans_created_today = 0
    
# Initialize navigation and UI settings
if "current_page" not in st.session_state:
    st.session_state.current_page = "learning_plan"
    
if "theme_mode" not in st.session_state:
    st.session_state.theme_mode = "dark"
    
# Initialize time tracking
if "actual_time_spent" not in st.session_state:
    st.session_state.actual_time_spent = 0.0
    
if "today_time_spent" not in st.session_state:
    st.session_state.today_time_spent = 0.0
    
if "time_logs" not in st.session_state:
    st.session_state.time_logs = {}
    
# Initialize user data storage
if "user_data" not in st.session_state:
    st.session_state.user_data = {}
```

### Navigation Functions

Session state is updated when navigating between pages and steps:

```python
def navigate_to(page):
    """Navigate to a specific page."""
    st.session_state.current_page = page

def next_step():
    """Proceed to next step in the learning plan wizard."""
    st.session_state.step += 1

def prev_step():
    """Go back to previous step in the learning plan wizard."""
    st.session_state.step -= 1
```

### Form Data Management

Each step of the wizard uses the session state to pre-fill form fields and store user input:

```python
# Pre-fill form with existing value if available
subject_value = st.session_state.get("subject", "")
subject = st.text_input("Subject or Topic", value=subject_value)

# Store value in session state when user navigates
if st.button("Next"):
    st.session_state["subject"] = subject
    next_step()
```

### Time Tracking Management

The application tracks learning time for each plan:

```python
def log_time_spent(hours_spent, plan_id=None):
    """Log time spent on learning activities."""
    if not plan_id and "learning_plan" in st.session_state:
        plan_id = st.session_state.learning_plan.id
        
    # Update total time spent
    st.session_state.actual_time_spent += hours_spent
    st.session_state.today_time_spent += hours_spent
    
    # Record timestamp for the entry
    timestamp = datetime.now().isoformat()
    
    # Add to time logs
    if plan_id not in st.session_state.time_logs:
        st.session_state.time_logs[plan_id] = []
        
    st.session_state.time_logs[plan_id].append({
        "timestamp": timestamp,
        "hours": hours_spent
    })
    
    # Persist to storage if available
    if "storage_client" in st.session_state:
        store_user_data()
```

### Dashboard State

The dashboard page uses session state to display learning metrics:

```python
def initialize_dashboard():
    """Initialize dashboard state variables."""
    if "completion_percentage" not in st.session_state:
        st.session_state.completion_percentage = 0
        
    if "estimated_total_hours" not in st.session_state:
        st.session_state.estimated_total_hours = 0
    
    # Calculate completion percentage based on time spent
    if "learning_plan" in st.session_state and st.session_state.learning_plan:
        plan = st.session_state.learning_plan
        estimated_hours = extract_hours_from_time_commitment(plan.time_commitment)
        st.session_state.estimated_total_hours = estimated_hours
        
        if estimated_hours > 0:
            percentage = min(100, (st.session_state.actual_time_spent / estimated_hours) * 100)
            st.session_state.completion_percentage = round(percentage, 1)
```

### Form Validation

Input validation ensures all values are in expected formats:

```python
# Ensure level_value is one of the valid options
valid_options = ["Beginner (No prior knowledge)", "Intermediate (Some basics understood)", "Advanced (Looking to deepen knowledge)"]
if level_value not in valid_options:
    level_value = valid_options[0]  # Default to Beginner
```

### Handling Special Input Types

For complex inputs like multiselect:

```python
# Get the default selection for multiselect
default_resources = []
if "preferred_resources" in st.session_state:
    if isinstance(st.session_state.preferred_resources, str) and st.session_state.preferred_resources.strip():
        # Convert string back to list if needed
        default_resources = [r.strip() for r in st.session_state.preferred_resources.split(",")]
    elif isinstance(st.session_state.preferred_resources, list):
        default_resources = st.session_state.preferred_resources

# Ensure all default values exist in options
default_resources = [r for r in default_resources if r in resource_options]

# Store multiselect values properly
if preferred_resources:
    # Store processed values with different keys to avoid conflicts
    st.session_state["preferred_resources_str"] = ", ".join(preferred_resources)
    st.session_state["preferred_resources_list"] = preferred_resources
```

### User Data Persistence

User data is stored persistently:

```python
def store_user_data():
    """Store user data to persistent storage."""
    if "user_id" not in st.session_state:
        # Generate a unique user ID if needed
        st.session_state.user_id = str(uuid.uuid4())
    
    user_data = {
        "user_id": st.session_state.user_id,
        "learning_plan": st.session_state.learning_plan.to_dict() if "learning_plan" in st.session_state and st.session_state.learning_plan else None,
        "time_logs": st.session_state.time_logs,
        "actual_time_spent": st.session_state.actual_time_spent,
        "theme_mode": st.session_state.theme_mode,
        "subscription": st.session_state.subscription.tier.value
    }
    
    # Store to session state
    st.session_state.user_data = user_data
    
    # Store to external persistence
    if "storage_client" in st.session_state:
        st.session_state.storage_client.upsert_user_data(user_data)
```

### Subscription State

The user's subscription status is maintained:

```python
# Initialize subscription status if needed
if "subscription_tier" not in st.session_state:
    st.session_state.subscription_tier = SubscriptionTier.FREEMIUM
    
# Check if user has a premium subscription stored
if "user_email" in st.session_state:
    user_email = st.session_state.user_email
    if check_premium_status(user_email):
        st.session_state.subscription_tier = SubscriptionTier.PREMIUM
```

### Plan Generation

When generating a plan, the session state is used to create the `LearningGoal` object:

```python
# Create learning goal from session state
learning_goal = LearningGoal(
    subject=st.session_state.subject,
    level=st.session_state.level,
    current_knowledge=st.session_state.current_knowledge,
    learning_purpose=st.session_state.learning_purpose,
    time_commitment=st.session_state.time_commitment,
    preferred_resources=preferred_resources  # Properly formatted string
)

# Store the result in session state
st.session_state.learning_plan = learning_plan
st.session_state.plans_created += 1
st.session_state.plans_created_today += 1

# Initialize time tracking for this plan
if learning_plan.id not in st.session_state.time_logs:
    st.session_state.time_logs[learning_plan.id] = []
```

## Best Practices

1. **Always check for existence** before accessing session state variables
2. **Use .get() with defaults** to safely retrieve values
3. **Validate inputs** before storing in session state
4. **Use separate keys** for different representations of the same data
5. **Reset state appropriately** for wizard initialization
6. **Keep track of initialization** in one central place
7. **Persist important state** to external storage
8. **Handle navigation state** separately from form data
9. **Log time data consistently** using the provided functions

## Troubleshooting

- **Missing data between steps**: Check that values are being stored after input
- **Form validation errors**: Ensure validation is applied to all inputs
- **Widget errors**: Use unique keys for widgets or avoid key conflicts
- **Default value errors**: Validate that default values exist in option lists 
- **Navigation issues**: Verify current_page is being set properly
- **Time tracking problems**: Check time logs structure in session state 