# Vibe Testing: When AI Tests the Apps AI Built

## The recursive beauty of using Claude and Playwright to test what we created together

*Part 2 of the Vibe Coding series*

---

![CoachAI App Interface](https://via.placeholder.com/800x400/1a1a1a/ffffff?text=CoachAI+Learning+Plan+Interface)

Remember that vibe coding documentation system I built with Claude in [Part 1](link-to-part-1)? Well, we just took it to the next level. Today, I used AI to test the AI-assisted app we built, and documented the whole thing using the system we created.

**Meta level**: Maximum.

## The Setup: Testing Our Own Creation

After publishing Part 1 about building the vibe coding documentation system, I realized I had the perfect test case sitting right in front of me — my **CoachAI learning plan app**. This Streamlit web application was built using the exact vibe coding methodology I wrote about.

So I asked Claude: *"Can you run the web app and have Playwright MCP run an end-to-end test?"*

What happened next was pure vibe testing magic.

---

## The Vibe Testing Flow

### 🚀 Step 1: Spinning Up the App

```bash
streamlit run ui/web/app.py --server.port 8501 --server.headless true
```

Claude didn't just run the command — it understood the context. We needed headless mode for automated testing, and it configured everything perfectly.

### 🤖 Step 2: AI-Powered Browser Automation

Using Playwright through MCP (Model Context Protocol), Claude:

1. **Navigated** to `http://localhost:8501`
2. **Captured screenshots** at each step
3. **Filled form fields** with meta content: *"Vibe Coding with AI Assistants"*
4. **Tested validation** by triggering error states
5. **Explored navigation** between different app sections

### 📝 Step 3: Real-Time Documentation

Every action was automatically captured in our vibe coding system:
- Screenshots saved with descriptive names
- Test steps logged with timestamps
- Validation results documented
- Meta observations recorded

---

## The Beautiful Irony

Here's what struck me during this session:

> **I was using AI to test an AI-built app while AI documented the testing process.**

- **Claude** navigated the browser
- **Claude** filled forms with relevant test data
- **Claude** captured screenshots automatically
- **Claude** documented everything in our vibe coding system
- **The app being tested** was built with Claude's help
- **The documentation system** was designed by Claude

It's like a perfect feedback loop of AI collaboration.

---

## What We Discovered

### 🎯 Form Validation Works

The app correctly showed *"Please enter a topic to continue"* when validation failed. The error messaging was clear and user-friendly.

### 🖼️ UI Captures Everything

Screenshots showed:
- Clean, modern interface with brain emoji branding 🧠
- Proper navigation highlighting (Learning Plan tab active)
- Form states and validation messages
- Responsive layout working correctly

### 🔄 Navigation Flow

- Dashboard → Learning Plan → Settings flow worked seamlessly
- User statistics displayed correctly (Premium plan, 0/1 plans created)
- Visual feedback for active sections

### 🧠 Meta Learning Moment

The most interesting discovery? **The app handled our meta test case perfectly.** When we entered *"Vibe Coding with AI Assistants"* as a learning topic, the app was ready to create a learning plan about... itself.

---

## The Vibe Testing Methodology

From this session, I've identified what makes "vibe testing" different:

### 1. Context-Aware Testing
Instead of rigid test scripts, the AI understands the app's purpose and tests accordingly. Claude chose relevant test data that matched the app's domain.

### 2. Real-Time Documentation
Every test action is immediately captured with context:

```
📝 Vibe Testing Session: End-to-end testing CoachAI with Playwright
- Tested learning plan creation flow
- Form validation working correctly  
- Navigation between sections smooth
- Meta moment: testing vibe coding app with AI tools
```

### 3. Visual Verification
Screenshots aren't just evidence — they're part of the story. Each capture shows the app's state and user experience.

### 4. Adaptive Problem Solving
When the CSS selector `button:contains('Next')` failed, Claude immediately adapted:

```javascript
const nextBtn = Array.from(document.querySelectorAll('button'))
  .find(btn => btn.textContent.includes('Next'));
if (nextBtn) nextBtn.click();
```

---

## The Technical Magic

### Playwright + MCP Integration

The Model Context Protocol made browser automation feel natural:

- `mcp_puppeteer_puppeteer_navigate` — Go to URL
- `mcp_puppeteer_puppeteer_fill` — Fill form fields  
- `mcp_puppeteer_puppeteer_click` — Click elements
- `mcp_puppeteer_puppeteer_screenshot` — Capture visuals
- `mcp_puppeteer_puppeteer_evaluate` — Run custom JavaScript

### Smart Error Handling

When selectors failed, Claude didn't give up:

```javascript
// When CSS selectors fail, use JavaScript to find elements
const nextButton = Array.from(document.querySelectorAll('button'))
  .find(btn => btn.textContent.includes('Next'));
```

### Automatic Documentation

Our vibe coding system captured everything:
- Test execution logs
- Screenshot galleries
- Error states and resolutions
- Meta observations about the process

---

## The Bigger Picture: AI Testing AI

This session revealed something profound about the future of software development:

> **We're not just building apps faster with AI — we're testing them differently too.**

### Traditional Testing:
1. Write test scripts
2. Run automated tests
3. Parse results
4. Fix issues
5. Repeat

### Vibe Testing:
1. Describe what you want tested
2. AI explores the app contextually
3. Real-time documentation and screenshots
4. Adaptive problem-solving when issues arise
5. Meta insights about the development process

---

## What's Next?

This vibe testing session opened up new possibilities:

### Continuous Vibe Testing
Imagine running vibe tests on every deployment:
- AI explores new features contextually
- Screenshots document visual changes
- Natural language reports explain what changed
- Regression testing with adaptive intelligence

### User Journey AI
Instead of predefined user flows, AI could:
- Simulate real user behavior patterns
- Test edge cases humans might miss
- Provide UX insights from an AI perspective
- Generate user stories from actual usage

### The Documentation Loop
Every test becomes content:
- Screenshots for tutorials
- Error states for troubleshooting guides
- User flows for onboarding documentation
- Meta insights for development blogs

---

## Try Vibe Testing Yourself

Ready to test your apps the vibe way? Here's the setup:

### Prerequisites:
- Streamlit app (or any web app)
- Playwright MCP integration
- Claude or similar AI assistant
- Vibe coding documentation system (from Part 1)

### Quick Start:
1. **Start your app**: `streamlit run app.py`
2. **Ask AI to test**: *"Navigate to my app and test the main user flow"*
3. **Document everything**: Screenshots, interactions, insights
4. **Analyze results**: What worked? What didn't? What surprised you?

### Pro Tips:
- Use meta test data (like testing your vibe coding app with vibe coding content)
- Capture screenshots at every major step
- Let AI adapt when selectors fail
- Document the unexpected moments

---

## The Meta Moment

As I write this, I realize we've created something beautiful:

> **A self-documenting, self-testing, AI-assisted development workflow.**

- **Part 1**: AI helps build documentation system
- **Part 2**: AI tests the app using the documentation system
- **Part 3**: ??? *(What comes next in this recursive loop?)*

---

## Credits and Tools

**AI Testing Assistant**: [Claude by Anthropic](https://claude.ai) — for contextual testing and adaptive problem-solving

**Testing Tools**:
- Playwright with MCP integration
- Puppeteer browser automation
- Streamlit for the web app
- Our vibe coding documentation system

**The Beautiful Recursion**: Using AI to test AI-built apps while AI documents the AI testing process. The future is delightfully meta.

---

*If you're building with AI and want to test with AI, follow me for more insights on vibe coding, vibe testing, and the evolving relationship between human creativity and artificial intelligence.*

**👏 Clap if you've experienced the joy of recursive AI collaboration!**

**💬 Share your own vibe testing stories in the comments**

**🔄 What should Part 3 of this series cover? AI deployment? AI monitoring? AI teaching AI?**

---

*Originally written during a live vibe testing session with Claude. The app tested itself, the AI documented itself, and the human just watched in amazement.*

## Coming Up in Part 3...

What happens when we take this recursive AI collaboration even further? Stay tuned to find out how deep the vibe coding rabbit hole goes.

*Spoiler: It involves AI teaching other AIs what we learned from Parts 1 and 2.*

---

### About the Author

*Building the future of AI-assisted development, one vibe coding session at a time. Currently working on CoachAI, a personalized learning platform built entirely through vibe coding methodology.*

**Connect**: [Twitter](link) | [LinkedIn](link) | [GitHub](link) 