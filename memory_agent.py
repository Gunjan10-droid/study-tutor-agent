# memory_agent.py
# This file defines the MemoryAgent class that manages progress.json to track student learning history.

import json
import os

class MemoryAgent:
    """
    The MemoryAgent handles loading, updating, and saving
    the student's study history and quiz scores in progress.json.
    """
    def __init__(self, filename="progress.json"):
        self.filename = filename
        self.progress = self.load_progress()

    def load_progress(self):
        """Loads study progress from progress.json. Creates default structure if file doesn't exist."""
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                print(f"Warning: {self.filename} was corrupted or invalid. Starting fresh.")
        
        # Default starting structure
        return {"studied_topics": {}, "overall_score": 0}

    def save_progress(self):
        """Saves the current progress dictionary to progress.json."""
        with open(self.filename, 'w', encoding='utf-8') as f:
            json.dump(self.progress, f, indent=4)

    def record_session(self, topic: str, score: int, max_score: int = 3):
        """
        Records a study session for a topic with the quiz score.
        Updates the overall score.
        """
        # Ensure the topic exists in our history
        if topic not in self.progress["studied_topics"]:
            self.progress["studied_topics"][topic] = []
            
        # Append the new session details
        self.progress["studied_topics"][topic].append({
            "score": score,
            "max_score": max_score
        })
        
        # Add to overall score
        self.progress["overall_score"] += score
        self.save_progress()

    def print_summary(self):
        """Prints a friendly summary of the student's progress."""
        print("\n==========================================")
        print("         🎓 STUDENT PROGRESS SUMMARY       ")
        print("==========================================")
        topics = self.progress.get("studied_topics", {})
        if not topics:
            print("No topics studied yet. Start learning today!")
        else:
            for topic, sessions in topics.items():
                best_score = max(s["score"] for s in sessions)
                attempts = len(sessions)
                print(f"📚 {topic}: studied {attempts} time(s) | Best score: {best_score}/3")
            print(f"\n🌟 Cumulative Quiz Score: {self.progress.get('overall_score', 0)}")
        print("==========================================\n")
