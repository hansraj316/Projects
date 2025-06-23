# Windsurf Workflow Tracking Rules
## CoachAI Development Tracking

### Windsurf Configuration

```toml
[workflow]
auto_track = true
session_directory = "docs/blog_content/research/raw_notes"
real_time_sync = true
collaboration_mode = true

[tracking]
git_integration = true
ai_conversations = true
file_modifications = true
terminal_sessions = true
debugging_sessions = true
performance_monitoring = true

[templates]
session = "docs/blog_content/templates/windsurf_session_template.md"
prompt = "docs/blog_content/templates/windsurf_prompt_template.md"
collaboration = "docs/blog_content/templates/collaboration_template.md"

[filters]
include_extensions = [".py", ".swift", ".md", ".json", ".yaml", ".toml"]
exclude_patterns = ["__pycache__", ".venv", "*.log", "*.pyc", "*.xcuserstate"]
focus_paths = ["src/", "ui/web/", "ios/CoachAI/", "agents/", "docs/"]
```

### Windsurf-Specific Features

#### Real-Time Collaboration Tracking:
```yaml
collaboration:
  track_multi_cursor: true
  track_voice_notes: true
  track_screen_sharing: true
  track_code_reviews: true
  
  participant_actions:
    - cursor_movements
    - selection_changes
    - typing_patterns
    - ai_prompt_usage
```

#### Enhanced AI Integration:
```yaml
ai_tracking:
  conversation_flows: true
  context_awareness: true
  suggestion_acceptance_rate: true
  multi_turn_conversations: true
  
  windsurf_specific:
    - cascade_prompting: true
    - context_building: true
    - file_awareness: true
    - project_understanding: true
```

### Keyboard Shortcuts (Windsurf)

| Action | Shortcut | Description |
|--------|----------|-------------|
| Start Session | `Ctrl+Shift+W` | Begin Windsurf tracking session |
| Quick Note | `Ctrl+Shift+N` | Add quick development note |
| AI Context | `Ctrl+Shift+A` | Capture AI conversation context |
| Flow State | `Ctrl+Shift+F` | Mark flow state entry/exit |
| Collaboration | `Ctrl+Shift+M` | Start multi-user tracking |

### Windsurf Session Template:

```markdown
# Windsurf Development Session - {DATE}_{TIME}

## Session Metadata
- **Session ID**: {SESSION_ID}
- **Windsurf Version**: {WINDSURF_VERSION}
- **Project**: CoachAI
- **Branch**: {GIT_BRANCH}
- **Collaborators**: {COLLABORATOR_LIST}

## Development Environment
- **Python Version**: {PYTHON_VERSION}
- **Streamlit Version**: {STREAMLIT_VERSION}
- **Xcode Version**: {XCODE_VERSION}
- **Node Version**: {NODE_VERSION}

## AI Assistant Usage
- **Model Used**: {AI_MODEL}
- **Total Interactions**: {INTERACTION_COUNT}
- **Successful Suggestions**: {SUCCESS_RATE}%
- **Context Switches**: {CONTEXT_SWITCHES}

## Real-Time Activity Log
{WINDSURF_ACTIVITY_STREAM}

## Code Intelligence Insights
{AI_INSIGHTS}

## Collaboration Events
{COLLABORATION_LOG}

## Performance Metrics
{PERFORMANCE_DATA}
```

### Advanced Tracking Features

#### Flow State Detection:
```yaml
flow_state:
  detection_criteria:
    - typing_speed_consistency: true
    - low_context_switching: true
    - minimal_documentation_lookup: true
    - high_ai_acceptance_rate: true
  
  tracking:
    - duration_in_flow: true
    - productivity_metrics: true
    - code_quality_during_flow: true
    - interruption_recovery_time: true
```

#### Context-Aware Logging:
```yaml
context_awareness:
  file_context:
    - current_function: true
    - related_files: true
    - import_dependencies: true
    - recent_changes: true
  
  project_context:
    - feature_branch: true
    - related_issues: true
    - test_coverage_impact: true
    - documentation_needs: true
```

### CoachAI-Specific Windsurf Tracking

#### Streamlit Development Flow:
```markdown
## Streamlit Session Tracking

### UI Component Development
- **Component**: {COMPONENT_NAME}
- **Page**: {STREAMLIT_PAGE}
- **User Flow**: {USER_INTERACTION_FLOW}

### Real-Time Preview Tracking
- **Auto-Reload Events**: {RELOAD_COUNT}
- **Error Recovery**: {ERROR_RECOVERY_INSTANCES}
- **Performance Impact**: {PERFORMANCE_METRICS}

### State Management Changes
- **Session State Modified**: {STATE_VARIABLES}
- **Cache Updates**: {CACHE_OPERATIONS}
- **Database Interactions**: {DB_OPERATIONS}
```

#### iOS Development Flow:
```markdown
## iOS Session Tracking

### SwiftUI Development
- **Views Modified**: {SWIFTUI_VIEWS}
- **Navigation Changes**: {NAVIGATION_UPDATES}
- **State Management**: {STATE_CHANGES}

### Xcode Integration
- **Build Results**: {BUILD_STATUS}
- **Simulator Sessions**: {SIMULATOR_RUNS}
- **Device Testing**: {DEVICE_TESTS}

### App Store Readiness
- **Asset Updates**: {ASSET_CHANGES}
- **Metadata Changes**: {METADATA_UPDATES}
- **Build Archive**: {ARCHIVE_STATUS}
```

### Multi-Platform Tracking:

```yaml
platform_coordination:
  web_ios_sync:
    - shared_model_changes: true
    - api_contract_updates: true
    - design_system_alignment: true
    - feature_parity_tracking: true
    
  cross_platform_testing:
    - user_experience_consistency: true
    - performance_comparison: true
    - feature_availability: true
    - data_synchronization: true
```

### Windsurf Collaboration Template:

```markdown
## Collaboration Session - {DATE}_{TIME}

### Participants
- **Lead Developer**: {LEAD_NAME}
- **Contributors**: {CONTRIBUTOR_LIST}
- **AI Assistant**: {AI_MODEL_INFO}

### Collaboration Patterns
{COLLABORATION_ANALYTICS}

### Code Review Events
{CODE_REVIEW_LOG}

### Knowledge Sharing
{KNOWLEDGE_TRANSFER_LOG}

### Decision Making Process
{DECISION_TRACKING}
```

### Automated Insights Generation:

```yaml
insights:
  productivity_analysis:
    - peak_performance_hours: true
    - most_effective_prompts: true
    - common_debugging_patterns: true
    - feature_development_velocity: true
  
  code_quality_trends:
    - complexity_evolution: true
    - test_coverage_trends: true
    - dependency_management: true
    - technical_debt_tracking: true
```

### Integration Commands:

```bash
# Windsurf-specific tracking commands
windsurf track init                    # Initialize tracking for project
windsurf track session start          # Start new session
windsurf track session tag <tag>      # Tag current session
windsurf track collaboration invite   # Start collaborative session
windsurf track export weekly         # Export weekly summary
windsurf track analysis productivity  # Generate productivity insights
```

### Custom Windsurf Hooks:

```javascript
// .windsurf/hooks/tracking.js
module.exports = {
  onFileChange: (file, changes) => {
    trackCodeChange(file, changes);
  },
  
  onAIInteraction: (prompt, response) => {
    logAIConversation(prompt, response);
  },
  
  onBuildComplete: (buildInfo) => {
    captureBuildMetrics(buildInfo);
  },
  
  onTestRun: (testResults) => {
    trackTestOutcomes(testResults);
  }
};
```

---

*Windsurf's advanced collaboration and real-time features provide deeper insights into your CoachAI development process, especially when working in team environments or leveraging advanced AI assistance.* 