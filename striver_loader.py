import json
import random
import os
from datetime import datetime
import logging # Added logging import

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class StriverLoader:
    QUESTION_FILE = "data/450DSA.json"
    POSTED_FILE = "data/posted_questions.json"

    def __init__(self):
        self.questions = self.load_questions()
        self.posted_questions = self.load_posted_state()

    def load_questions(self):
        """Loads questions from the local JSON file with the 450DSA schema."""
        if not os.path.exists(self.QUESTION_FILE):
            logging.error(f"File not found: {self.QUESTION_FILE}")
            return []
        
        try:
            # Fix: Use 'utf-8-sig' to handle files with BOM (Byte Order Mark)
            with open(self.QUESTION_FILE, 'r', encoding='utf-8-sig') as f:
                data = json.load(f)
                
            # Dictionary key is "Sheet1"
            raw_questions = data.get("Sheet1", [])
            
            cleaned_questions = []
            for i, q in enumerate(raw_questions):
                # Dynamic Key Discovery
                # Use the first key that looks like "Topic", "Problem", "URL"
                title_key = next((k for k in q.keys() if "Problem" in k), "Problem")
                topic_key = next((k for k in q.keys() if "Topic" in k), "Topic")
                link_key = next((k for k in q.keys() if "URL" in k or "Link" in k), "URL")

                title = q.get(title_key, "Unknown Problem").strip()
                topic = q.get(topic_key, "General").strip()
                link = q.get(link_key, "").strip()
                
                # Filter out empty or placeholder URLs if needed
                if not link or link == "<->":
                    continue

                cleaned_questions.append({
                    "id": str(i + 1), 
                    "title": title,
                    "difficulty": "Medium", # Default difficulty
                    "topic": topic,
                    "link": link,
                    "platform": "DSA Sheet"
                })
            
            unique_topics = set(q['topic'] for q in cleaned_questions)
            logging.info(f"Loaded {len(cleaned_questions)} questions. Unique Topics Found: {sorted(list(unique_topics))}")
            return cleaned_questions
            
        except json.JSONDecodeError as e:
            logging.error(f"Error parsing JSON: {e}")
            return []

    def load_posted_state(self):
        """Loads the history of posted questions."""
        if not os.path.exists(self.POSTED_FILE):
            return {"striver": [], "leetcode_daily_last_posted": None}
        
        with open(self.POSTED_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _save_posted_state(self):
        """Saves the current history to file."""
        with open(self.POSTED_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.posted_questions, f, indent=4)

    def get_random_question(self, topic_filter=None, difficulty=None):
        """
        Selects a random question that hasn't been posted yet.
        Optionally filters by topic or difficulty.
        """
        # Fix: Use self.posted_questions instead of self.history
        posted_ids = set(self.posted_questions.get("striver", []))
        
        # DEBUG: Print stats
        logging.info(f"DEBUG: Total Questions: {len(self.questions)}, Posted IDs: {len(posted_ids)}")
        
        candidates = []
        for q in self.questions:
            # Apply difficulty filter
            if difficulty:
                if q["difficulty"].lower() != difficulty.lower():
                    continue

            # Apply topic filter
            if topic_filter:
                # Robust match: normalize by removing spaces and lowercasing
                filter_norm = topic_filter.lower().replace(" ", "")
                topic_norm = str(q["topic"]).lower().replace(" ", "")
                
                # Check 1: simple substring in the normalized string
                if filter_norm in topic_norm:
                    # DEBUG regex match verification
                    # logging.info(f"Match found! Filter: {filter_lower} in Topic: {topic_str_lower}")
                    pass # Match found
                else:
                    # logging.info(f"No match: Filter: {filter_lower} not in Topic: {topic_str_lower}")
                    continue # No match

            if str(q["id"]) not in posted_ids:
                candidates.append(q)
        
        if not candidates:
            # If all posted, reset or just return None
            logging.info("All questions (in this filter) have been posted!")
            return None
            
        selected = random.choice(candidates)
        return selected

    def mark_as_posted(self, question_id):
        """Marks a question ID as posted and saves to file."""
        if "striver" not in self.posted_questions:
            self.posted_questions["striver"] = []
            
        # Ensure we store strings to match JSON format consistency
        q_id_str = str(question_id)
        if q_id_str not in self.posted_questions["striver"]:
            self.posted_questions["striver"].append(q_id_str)
            self._save_posted_state() # Fix: Call the correctly named save method
    
    def get_question_stats(self):
        """Returns stats about questions pool."""
        total = len(self.questions)
        posted = len(self.posted_questions.get("striver", []))
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
