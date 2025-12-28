import requests
import logging

class CodeRunner:
    """
    Executes code using the Piston API (https://emkc.org/api/v2/piston).
    """
    API_URL = "https://emkc.org/api/v2/piston/execute"

    def __init__(self):
        self.headers = {
            "Content-Type": "application/json",
            "User-Agent": "LeetCode-Discord-Bot"
        }

    def execute_code(self, language, code, stdin=""):
        """
        Sends code to Piston API for execution.
        """
        # Map common discord language names to Piston language names
        lang_map = {
            "py": "python",
            "python": "python",
            "js": "javascript",
            "javascript": "javascript",
            "cpp": "cpp",
            "c++": "cpp",
            "c": "c",
            "java": "java",
            "go": "go"
        }
        
        lang = lang_map.get(language.lower(), language.lower())

        payload = {
            "language": lang,
            "version": "*", # Use latest available
            "files": [
                {
                    "content": code
                }
            ],
            "stdin": stdin
        }

        try:
            response = requests.post(self.API_URL, json=payload, headers=self.headers, timeout=10)
            response.raise_for_status()
            result = response.json()
            
            run_stage = result.get("run", {})
            return {
                "stdout": run_stage.get("stdout", ""),
                "stderr": run_stage.get("stderr", ""),
                "output": run_stage.get("output", ""), # Combined output
                "code": run_stage.get("code", 0), # Exit code
                "signal": run_stage.get("signal", None)
            }

        except requests.RequestException as e:
            logging.error(f"Piston API Error: {e}")
            return {"error": "Failed to verify code execution service."}

if __name__ == "__main__":
    runner = CodeRunner()
    res = runner.execute_code("python", "print('Hello Piston')")
    print(res)
