#!/usr/bin/env python3
"""
Claude Blog Session Manager
Captures Claude interactions and development insights for blog content creation.
Similar to the existing blog workflow but focused on Claude AI interactions.
"""

import os
import json
import datetime
from pathlib import Path
from typing import Dict, List, Optional

class ClaudeBlogSession:
    def __init__(self, project_root: str = None):
        self.project_root = Path(project_root) if project_root else Path.cwd()
        self.blog_content_dir = self.project_root / "docs" / "blog_content"
        self.claude_sessions_dir = self.blog_content_dir / "research" / "claude_sessions"
        self.templates_dir = self.blog_content_dir / "templates"
        
        # Create directories if they don't exist
        self.claude_sessions_dir.mkdir(parents=True, exist_ok=True)
        
        # Current session file
        self.current_session = self._get_current_session_file()
        
    def _get_current_session_file(self) -> Path:
        """Get or create current session file based on today's date."""
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        session_file = self.claude_sessions_dir / f"{today}_claude_session.md"
        
        if not session_file.exists():
            self._create_new_session(session_file)
            
        return session_file
    
    def _create_new_session(self, session_file: Path):
        """Create a new Claude session file with template."""
        template_content = """# Claude Session - {date}

## Session Overview
- **Date**: {date}
- **Project**: CoachAI
- **Claude Model**: Sonnet 4
- **Focus Areas**: 

## Cost Tracking
- **Start Cost**: $0.00
- **Current Cost**: $0.00
- **Token Usage**: 
  - Input: 0
  - Output: 0
  - Cache Read: 0
  - Cache Write: 0

## Key Interactions

### Task 1: 
**Context**: 
**Claude Input**: 
**Claude Output**: 
**Insights**: 
**Blog Potential**: 

---

## Quotable Moments
- 

## Technical Insights
- 

## Development Breakthroughs
- 

## Content Assets Created
- [ ] Screenshots
- [ ] Code examples
- [ ] Workflow diagrams
- [ ] Cost analysis

## Blog Post Ideas
- 

## Notes for Next Session
- 

---
*Generated by Claude Blog Session Manager*
"""
        
        session_file.write_text(
            template_content.format(
                date=datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
            )
        )
    
    def add_interaction(self, task_name: str, context: str, claude_input: str, 
                       claude_output: str, insights: str, blog_potential: str):
        """Add a new Claude interaction to the current session."""
        interaction_template = f"""
### {task_name}
**Context**: {context}
**Claude Input**: {claude_input}
**Claude Output**: {claude_output}
**Insights**: {insights}
**Blog Potential**: {blog_potential}

---
"""
        
        # Read current content
        content = self.current_session.read_text()
        
        # Find the insertion point (after "## Key Interactions")
        lines = content.split('\n')
        insert_index = -1
        
        for i, line in enumerate(lines):
            if line.startswith("## Key Interactions"):
                # Find the next section or end of interactions
                for j in range(i + 1, len(lines)):
                    if lines[j].startswith("## ") and not lines[j].startswith("## Key Interactions"):
                        insert_index = j
                        break
                break
        
        if insert_index > 0:
            lines.insert(insert_index, interaction_template)
            self.current_session.write_text('\n'.join(lines))
    
    def add_cost_update(self, total_cost: str, duration_api: str, duration_wall: str, 
                       token_input: str, token_output: str, cache_read: str, cache_write: str):
        """Update cost tracking in the current session."""
        content = self.current_session.read_text()
        
        # Replace cost tracking section
        lines = content.split('\n')
        cost_section_start = -1
        cost_section_end = -1
        
        for i, line in enumerate(lines):
            if line.startswith("## Cost Tracking"):
                cost_section_start = i
                # Find the end of cost section
                for j in range(i + 1, len(lines)):
                    if lines[j].startswith("## ") and not lines[j].startswith("## Cost Tracking"):
                        cost_section_end = j
                        break
                break
        
        if cost_section_start >= 0:
            new_cost_section = f"""## Cost Tracking
- **Start Cost**: $0.00
- **Current Cost**: {total_cost}
- **API Duration**: {duration_api}
- **Wall Duration**: {duration_wall}
- **Token Usage**: 
  - Input: {token_input}
  - Output: {token_output}
  - Cache Read: {cache_read}
  - Cache Write: {cache_write}

"""
            
            if cost_section_end > 0:
                lines[cost_section_start:cost_section_end] = new_cost_section.split('\n')
            else:
                lines[cost_section_start:] = new_cost_section.split('\n') + lines[cost_section_end:]
            
            self.current_session.write_text('\n'.join(lines))
    
    def add_quote(self, quote: str, context: str = ""):
        """Add a quotable moment to the session."""
        content = self.current_session.read_text()
        quote_line = f"- \"{quote}\" {f'({context})' if context else ''}"
        
        # Find quotable moments section and add
        content = content.replace("## Quotable Moments\n- ", f"## Quotable Moments\n{quote_line}\n- ")
        self.current_session.write_text(content)
    
    def add_insight(self, insight: str):
        """Add a technical insight to the session."""
        content = self.current_session.read_text()
        insight_line = f"- {insight}"
        
        # Find technical insights section and add
        content = content.replace("## Technical Insights\n- ", f"## Technical Insights\n{insight_line}\n- ")
        self.current_session.write_text(content)
    
    def add_blog_idea(self, idea: str):
        """Add a blog post idea to the session."""
        content = self.current_session.read_text()
        idea_line = f"- {idea}"
        
        # Find blog post ideas section and add
        content = content.replace("## Blog Post Ideas\n- ", f"## Blog Post Ideas\n{idea_line}\n- ")
        self.current_session.write_text(content)
    
    def get_session_summary(self) -> Dict:
        """Get a summary of the current session."""
        if not self.current_session.exists():
            return {}
        
        content = self.current_session.read_text()
        
        # Basic parsing to extract key information
        summary = {
            "session_file": str(self.current_session),
            "date": datetime.datetime.now().strftime("%Y-%m-%d"),
            "interactions_count": content.count("### "),
            "quotes_count": content.count("- \""),
            "insights_count": content.count("## Technical Insights") and content.split("## Technical Insights")[1].count("- "),
            "blog_ideas_count": content.count("## Blog Post Ideas") and content.split("## Blog Post Ideas")[1].count("- "),
        }
        
        return summary


def main():
    """Command line interface for Claude Blog Session Manager."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Manage Claude blog sessions")
    parser.add_argument("action", choices=["start", "interaction", "cost", "quote", "insight", "blog-idea", "summary"])
    parser.add_argument("--task", help="Task name for interaction")
    parser.add_argument("--context", help="Context for the interaction")
    parser.add_argument("--input", help="Claude input")
    parser.add_argument("--output", help="Claude output")
    parser.add_argument("--insights", help="Key insights")
    parser.add_argument("--blog-potential", help="Blog potential assessment")
    parser.add_argument("--cost", help="Total cost")
    parser.add_argument("--duration-api", help="API duration")
    parser.add_argument("--duration-wall", help="Wall duration")
    parser.add_argument("--tokens-input", help="Input tokens")
    parser.add_argument("--tokens-output", help="Output tokens")
    parser.add_argument("--cache-read", help="Cache read tokens")
    parser.add_argument("--cache-write", help="Cache write tokens")
    parser.add_argument("--quote", help="Quotable moment")
    parser.add_argument("--quote-context", help="Context for quote", default="")
    parser.add_argument("--insight", help="Technical insight")
    parser.add_argument("--idea", help="Blog post idea")
    
    args = parser.parse_args()
    
    session = ClaudeBlogSession()
    
    if args.action == "start":
        print(f"Started new Claude session: {session.current_session}")
    
    elif args.action == "interaction":
        if not all([args.task, args.context, args.input, args.output, args.insights, args.blog_potential]):
            print("Error: interaction requires --task, --context, --input, --output, --insights, --blog-potential")
            return
        
        session.add_interaction(args.task, args.context, args.input, args.output, args.insights, args.blog_potential)
        print("Added interaction to session")
    
    elif args.action == "cost":
        if not all([args.cost, args.duration_api, args.duration_wall, args.tokens_input, args.tokens_output, args.cache_read, args.cache_write]):
            print("Error: cost requires --cost, --duration-api, --duration-wall, --tokens-input, --tokens-output, --cache-read, --cache-write")
            return
        
        session.add_cost_update(args.cost, args.duration_api, args.duration_wall, args.tokens_input, args.tokens_output, args.cache_read, args.cache_write)
        print("Updated cost tracking")
    
    elif args.action == "quote":
        if not args.quote:
            print("Error: quote requires --quote")
            return
        
        session.add_quote(args.quote, args.quote_context)
        print("Added quote to session")
    
    elif args.action == "insight":
        if not args.insight:
            print("Error: insight requires --insight")
            return
        
        session.add_insight(args.insight)
        print("Added insight to session")
    
    elif args.action == "blog-idea":
        if not args.idea:
            print("Error: blog-idea requires --idea")
            return
        
        session.add_blog_idea(args.idea)
        print("Added blog idea to session")
    
    elif args.action == "summary":
        summary = session.get_session_summary()
        print("Session Summary:")
        for key, value in summary.items():
            print(f"  {key}: {value}")


if __name__ == "__main__":
    main()