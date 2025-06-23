#!/usr/bin/env python3
"""
Blog Session Management for Vibe Coding Documentation
"""
import os
import sys
import json
from datetime import datetime
from pathlib import Path

class BlogSessionManager:
    def __init__(self, project_root="."):
        self.project_root = Path(project_root)
        self.blog_dir = self.project_root / "docs/blog_content"
        self.raw_notes_dir = self.blog_dir / "research/raw_notes"
        self.templates_dir = self.blog_dir / "templates"
        self.assets_dir = self.blog_dir / "assets"
        
        # Ensure directories exist
        self.raw_notes_dir.mkdir(parents=True, exist_ok=True)
        self.templates_dir.mkdir(parents=True, exist_ok=True)
        self.assets_dir.mkdir(parents=True, exist_ok=True)
        
    def start_session(self, session_type="vibe_coding"):
        """Start a new blog tracking session"""
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
        session_file = self.raw_notes_dir / f"{timestamp}_{session_type}.md"
        
        # Load template
        template_file = self.templates_dir / "daily_vibe_log.md"
        if template_file.exists():
            with open(template_file) as f:
                template = f.read()
        else:
            template = "# Blog Session Template Not Found"
            
        # Fill in basic info
        day_number = self._get_session_day_number()
        content = template.replace("{DAY}", str(day_number))
        content = content.replace("{DATE}", datetime.now().strftime("%Y-%m-%d"))
        
        # Write session file
        with open(session_file, 'w') as f:
            f.write(content)
            
        print(f"🎯 Started vibe coding session: {session_file}")
        print(f"📝 Day {day_number} of your CoachAI journey")
        return session_file
        
    def add_note(self, note_text, category="general"):
        """Add a quick note to today's session"""
        today = datetime.now().strftime("%Y-%m-%d")
        session_files = list(self.raw_notes_dir.glob(f"{today}*.md"))
        
        if not session_files:
            print("No session started today. Starting new session...")
            session_file = self.start_session()
        else:
            session_file = max(session_files, key=os.path.getctime)
        
        # Append note
        note_entry = f"""
## Quick Note - {datetime.now().strftime("%H:%M")}
**Category**: {category}
**Note**: {note_text}
"""
        
        with open(session_file, 'a') as f:
            f.write(note_entry)
            
        print(f"📝 Added note to {session_file}")
        
    def add_insight(self, insight_text):
        """Add a development insight"""
        self.add_note(insight_text, "insight")
        
    def add_quote(self, quote_text):
        """Add a quotable moment"""
        today = datetime.now().strftime("%Y-%m-%d")
        session_files = list(self.raw_notes_dir.glob(f"{today}*.md"))
        
        if session_files:
            session_file = max(session_files, key=os.path.getctime)
            quote_entry = f'\n> "{quote_text}" - {datetime.now().strftime("%H:%M")}\n'
            
            with open(session_file, 'a') as f:
                f.write(quote_entry)
                
            print(f"💬 Added quote to {session_file}")
        else:
            print("No active session found. Start a session first.")
            
    def add_demo(self, demo_description):
        """Mark a demo opportunity"""
        self.add_note(f"DEMO OPPORTUNITY: {demo_description}", "demo")
        
    def compile_weekly_summary(self):
        """Compile weekly summary for blog content"""
        # Get all session files from this week
        today = datetime.now()
        week_start = today - datetime.timedelta(days=today.weekday())
        
        session_files = []
        for i in range(7):
            day = week_start + datetime.timedelta(days=i)
            day_str = day.strftime("%Y-%m-%d")
            session_files.extend(list(self.raw_notes_dir.glob(f"{day_str}*.md")))
        
        if not session_files:
            print("No sessions found for this week")
            return
            
        # Create weekly summary
        week_str = week_start.strftime("%Y-W%W")
        summary_file = self.blog_dir / "research" / f"weekly_summary_{week_str}.md"
        
        with open(summary_file, 'w') as f:
            f.write(f"# Weekly Summary - Week {week_str}\n\n")
            f.write("## Sessions This Week\n")
            
            for session_file in sorted(session_files):
                f.write(f"- [{session_file.name}]({session_file.relative_to(self.blog_dir)})\n")
                
        print(f"📊 Created weekly summary: {summary_file}")
        
    def _get_session_day_number(self):
        """Calculate which day of the project this is"""
        all_sessions = list(self.raw_notes_dir.glob("*.md"))
        return len(all_sessions) + 1

def main():
    if len(sys.argv) < 2:
        print("Usage: python blog_session.py <command> [args]")
        print("Commands: start, note, insight, quote, demo, compile")
        sys.exit(1)
        
    manager = BlogSessionManager()
    command = sys.argv[1]
    
    if command == "start":
        manager.start_session()
    elif command == "note":
        if len(sys.argv) < 3:
            note = input("Enter your note: ")
        else:
            note = " ".join(sys.argv[2:])
        manager.add_note(note)
    elif command == "insight":
        if len(sys.argv) < 3:
            insight = input("Enter your insight: ")
        else:
            insight = " ".join(sys.argv[2:])
        manager.add_insight(insight)
    elif command == "quote":
        if len(sys.argv) < 3:
            quote = input("Enter your quote: ")
        else:
            quote = " ".join(sys.argv[2:])
        manager.add_quote(quote)
    elif command == "demo":
        if len(sys.argv) < 3:
            demo = input("Describe the demo opportunity: ")
        else:
            demo = " ".join(sys.argv[2:])
        manager.add_demo(demo)
    elif command == "compile":
        manager.compile_weekly_summary()
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)

if __name__ == "__main__":
    main() 