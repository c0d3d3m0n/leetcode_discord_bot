import requests
import logging

class LeetCodeService:
    BASE_URL = "https://leetcode.com/graphql"
    
    def __init__(self):
        self.headers = {
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

    def get_daily_challenge(self):
        """Fetches the active daily coding challenge from LeetCode."""
        query = """
        query questionOfToday {
            activeDailyCodingChallengeQuestion {
                date
                link
                question {
                    questionId
                    title
                    titleSlug
                    difficulty
                    topicTags {
                        name
                    }
                }
            }
        }
        """
        
        payload = {"query": query}
        
        try:
            response = requests.post(self.BASE_URL, json=payload, headers=self.headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            challenge = data.get("data", {}).get("activeDailyCodingChallengeQuestion", {})
            if not challenge:
                logging.error("No active daily challenge found in response.")
                return None
                
            question = challenge.get("question", {})
            return {
                "date": challenge.get("date"),
                "title": question.get("title"),
                "difficulty": question.get("difficulty"),
                "link": "https://leetcode.com" + challenge.get("link", ""),
                "topics": [tag["name"] for tag in question.get("topicTags", [])],
                "slug": question.get("titleSlug"),
                "id": question.get("questionId")
            }
            
        except requests.RequestException as e:
            logging.error(f"Error fetching LeetCode daily challenge: {e}")
            return None

if __name__ == "__main__":
    # Test the service
    service = LeetCodeService()
    daily = service.get_daily_challenge()
    if daily:
        print("Fetched Daily Challenge:")
        print(daily)
    else:
        print("Failed to fetch daily challenge.")
