"""Kivy mobile interface for CoachAI."""

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.spinner import Spinner
from kivy.uix.textinput import TextInput
from kivy.properties import StringProperty, ObjectProperty

from agents.planner import LearningGoal, PlannerAgent

class WizardScreen(Screen):
    """Base class for wizard screens."""
    def on_enter(self):
        """Called when screen is entered."""
        self.update_progress()

    def update_progress(self):
        """Update progress bar."""
        app = App.get_running_app()
        app.root.ids.progress_bar.value = self.progress_value

class TopicScreen(WizardScreen):
    """First screen: Topic selection."""
    progress_value = 0

    def on_next(self, topic):
        """Handle next button press."""
        if topic.strip():
            app = App.get_running_app()
            app.responses['topic'] = topic
            self.manager.current = 'current_level'

class CurrentLevelScreen(WizardScreen):
    """Second screen: Current level selection."""
    progress_value = 0.25

    def on_next(self, level):
        """Handle next button press."""
        app = App.get_running_app()
        app.responses['current_level'] = level
        self.manager.current = 'target_level'

class TargetLevelScreen(WizardScreen):
    """Third screen: Target level selection."""
    progress_value = 0.5

    def on_next(self, level):
        """Handle next button press."""
        app = App.get_running_app()
        app.responses['target_level'] = level
        self.manager.current = 'time_commitment'

class TimeCommitmentScreen(WizardScreen):
    """Fourth screen: Time commitment selection."""
    progress_value = 0.75

    def on_next(self, time):
        """Handle next button press."""
        app = App.get_running_app()
        app.responses['time_commitment'] = time
        self.manager.current = 'learning_style'

class LearningStyleScreen(WizardScreen):
    """Fifth screen: Learning style selection."""
    progress_value = 1.0

    def on_next(self, style):
        """Handle next button press."""
        app = App.get_running_app()
        app.responses['learning_style'] = style
        self.generate_plan()

    def generate_plan(self):
        """Generate and display learning plan."""
        app = App.get_running_app()
        try:
            goal = LearningGoal(
                topic=app.responses['topic'],
                current_level=app.responses['current_level'],
                target_level=app.responses['target_level'],
                time_commitment=app.responses['time_commitment'],
                learning_style=app.responses['learning_style']
            )
            
            planner = PlannerAgent()
            plan = planner.generate_plan(goal)
            
            # Store plan in app and show results
            app.current_plan = plan
            self.manager.current = 'results'
            
        except Exception as e:
            # Show error dialog
            pass

class ResultsScreen(Screen):
    """Screen to display the generated learning plan."""
    def on_enter(self):
        """Update display with current plan."""
        app = App.get_running_app()
        plan = app.current_plan
        
        # Update UI with plan details
        self.ids.plan_title.text = plan.title
        self.ids.plan_description.text = plan.description
        # ... update other plan components

class CoachAIApp(App):
    """Main application class."""
    responses = {}
    current_plan = None

    def build(self):
        """Build and return the root widget."""
        # Create the screen manager
        sm = ScreenManager()
        sm.add_widget(TopicScreen(name='topic'))
        sm.add_widget(CurrentLevelScreen(name='current_level'))
        sm.add_widget(TargetLevelScreen(name='target_level'))
        sm.add_widget(TimeCommitmentScreen(name='time_commitment'))
        sm.add_widget(LearningStyleScreen(name='learning_style'))
        sm.add_widget(ResultsScreen(name='results'))
        return sm

if __name__ == '__main__':
    CoachAIApp().run() 