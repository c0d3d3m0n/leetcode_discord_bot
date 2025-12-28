import json
import random
import os
from datetime import datetime

class StriverLoader:
    def __init__(self, data_path="data/striver_questions.json", history_path="data/posted_questions.json"):
        self.data_path = data_path
        self.history_path = history_path
        self.questions = self._load_questions()
        self.history = self._load_history()

    def _load_questions(self):
        """Loads questions from the JSON file."""
        if not os.path.exists(self.data_path):
            raise FileNotFoundError(f"Questions file not found: {self.data_path}")
        
        with open(self.data_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _load_history(self):
        """Loads the history of posted questions."""
        if not os.path.exists(self.history_path):
            return {"striver": [], "leetcode_daily_last_posted": None}
        
        with open(self.history_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _save_history(self):
        """Saves the current history to file."""
        with open(self.history_path, 'w', encoding='utf-8') as f:
            json.dump(self.history, f, indent=4)

    def get_random_question(self, topic=None, difficulty=None):
        """
        Selects a random question that hasn't been posted yet.
        Optionally filters by topic or difficulty.
        """
        posted_ids = set(self.history.get("striver", []))
        
        candidates = [
            q for q in self.questions 
            if q["id"] not in posted_ids
        ]

        # Apply filters
        if topic:
            candidates = [q for q in candidates if q["topic"].lower() == topic.lower()]
        if difficulty:
            candidates = [q for q in candidates if q["difficulty"].lower() == difficulty.lower()]

        if not candidates:
            # If all questions (or filtered subset) are exhausted, you might want to reset history or return None
            # For now, we return None to indicate no fresh questions available
            return None

        selected = random.choice(candidates)
        return selected

    def mark_as_posted(self, question_id):
        """Marks a question ID as posted in the history."""
        if "striver" not in self.history:
            self.history["striver"] = []
        
        if question_id not in self.history["striver"]:
            self.history["striver"].append(question_id)
            self._save_history()

    def get_question_stats(self):
        """Returns stats about total vs posted questions."""
        total = len(self.questions)
        posted = len(self.history.get("striver", []))
        return {
            "total": total,
            "posted": posted,
            "remaining": total - posted
        }

if __name__ == "__main__":
    # Simple test
    loader = StriverLoader()
    print("Stats:", loader.get_question_stats())
    q = loader.get_random_question()
    if q:
        print("Selected Question:", q["title"])
        # Uncomment to test persistence:
        # loader.mark_as_posted(q["id"])
    else:
        print("No questions available.")
