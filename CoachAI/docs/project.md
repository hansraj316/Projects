# CoachAI Learning Assistant

**Goal:** Modular, memory‑driven AI tutor with multi‑agent orchestration and premium subscription features.  
**Stack:** Cursor AI, OpenAI API, Supabase, Streamlit, Stripe API, FastAPI.

---

## Why

Provides personalized learning plans with tiered access through Stripe subscriptions. CoachAI helps learners create structured, customized learning paths that adapt to their goals, knowledge level, and preferred learning resources.

---

## Key Components

### 1. Learning Plan Generator
Uses OpenAI's GPT models to create personalized learning plans based on user input about their topic, current knowledge level, learning purpose, time commitment, and preferred resources.

### 2. User Interface
- Streamlit-based web interface with dark mode UI
- Intuitive navigation sidebar with Dashboard, Learning Plan, and Settings sections
- Step-by-step wizard for learning plan creation

### 3. Dashboard
- Comprehensive tracking of learning progress
- Visualization of estimated vs. actual time spent
- Task completion monitoring
- Time logging capability

### 4. Time Tracking
- Record time spent on learning activities
- Compare estimated vs. actual learning hours
- Historical view of learning sessions

### 5. Subscription System
Tiered access model with Stripe integration:
- Freemium tier: Basic functionality at no cost
- Premium tier: Enhanced functionality for monthly subscription
- Refer to [subscription_system.md](./subscription_system.md) for details

### 6. Data Storage
- Persistent storage with Supabase
- User learning data 
- Learning plans and time logs
- Subscription information

### 7. OpenAI Integration
- Configurable API key in the Settings page
- Clear guidance on obtaining and setting up API keys
- Secure key storage

---

## Recent Improvements

1. **Dark Mode UI Implementation**
   - Improved visibility and reduced eye strain
   - Modern, clean interface design

2. **Navigation Enhancements**
   - Intuitive sidebar with three main sections
   - Better user flow and experience

3. **Comprehensive Dashboard**
   - Learning progress tracking
   - Visual representation of time metrics
   - Task completion monitoring

4. **Time Tracking Features**
   - Log learning hours
   - Track estimated vs. actual time spent
   - Historical view of learning sessions

5. **Technical Fixes**
   - SubscriptionConfig initialization error resolved
   - Streamlined API key configuration
   - Fixed nested columns issue in Streamlit
   - Corrected attribute access for LearningPlan objects

6. **User Data Persistence**
   - Supabase integration for data storage
   - Tracking learning progress over time
   - Secure storage of user preferences

---

## Future Developments

1. **Enhanced Analytics**
   - Learning patterns identification
   - Personalized recommendations based on progress

2. **Mobile Compatibility**
   - Responsive design for mobile devices
   - Potential dedicated mobile application

3. **Collaborative Learning**
   - Share learning plans with others
   - Group progress tracking

---

For subscription system details, see [subscription_system.md](./subscription_system.md).  
For state management information, see [workflow_state.md](./workflow_state.md). 