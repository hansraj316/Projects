# Workflow State Management

## Session State in CoachAI

CoachAI uses Streamlit's session state to maintain the application's state across multiple steps of the learning plan creation wizard. This document outlines how session state is managed throughout the application.

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
```

### Navigation Functions

Session state is updated when navigating between steps:

```python
def next_step():
    """Proceed to next step."""
    st.session_state.step += 1

def prev_step():
    """Go back to previous step."""
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
```

## Best Practices

1. **Always check for existence** before accessing session state variables
2. **Use .get() with defaults** to safely retrieve values
3. **Validate inputs** before storing in session state
4. **Use separate keys** for different representations of the same data
5. **Reset state appropriately** for wizard initialization
6. **Keep track of initialization** in one central place

## Troubleshooting

- **Missing data between steps**: Check that values are being stored after input
- **Form validation errors**: Ensure validation is applied to all inputs
- **Widget errors**: Use unique keys for widgets or avoid key conflicts
- **Default value errors**: Validate that default values exist in option lists 