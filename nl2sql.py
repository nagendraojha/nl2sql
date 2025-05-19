import requests
import os
from dotenv import load_dotenv
from time import sleep
import re

load_dotenv()

class NL2SQLClient:
    def __init__(self):
        self.api_token = os.getenv("HUGGINGFACE_API_TOKEN")
        if not self.api_token:
            raise ValueError("Missing HUGGINGFACE_API_TOKEN in .env file")
        self.api_url = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.3"
        self.headers = {"Authorization": f"Bearer {self.api_token}"}
        self.schema = """
        Table employees: id (INT), name (TEXT), department (TEXT), salary (FLOAT), hire_date (DATE)
        Table departments: id (INT), name (TEXT), location (TEXT)
        """

    def generate_sql(self, question, retry_count=0, max_retries=5):
        prompt = f"""
You are an expert in SQL. Convert the following question into a valid SQL query using this schema:
{self.schema}
Question: {question}
SQL:
"""
        try:
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json={"inputs": prompt},
                timeout=30
            )

            if response.status_code == 503:
                if retry_count >= max_retries:
                    print("Model still loading after retries. Aborting.")
                    return None
                wait_time = 2 ** retry_count  # exponential backoff
                print(f"Model is loading. Retrying in {wait_time}s...")
                sleep(wait_time)
                return self.generate_sql(question, retry_count + 1, max_retries)

            response.raise_for_status()
            text = response.json()[0].get("generated_text", "")

            # Extract SQL query from generated text (looking for SELECT or WITH statements)
            sql_match = re.search(r"(SELECT|WITH)[\s\S]*?;", text, re.IGNORECASE)
            if sql_match:
                sql_query = sql_match.group(0).strip()
                return sql_query
            else:
                # fallback: extract lines starting with SELECT or WITH until blank or comment line
                lines = text.splitlines()
                sql_lines = []
                recording = False
                for line in lines:
                    if re.match(r"^\s*(SELECT|WITH)", line, re.IGNORECASE):
                        recording = True
                    if recording:
                        if line.strip() == "" or line.strip().startswith("--") or line.strip().startswith("```"):
                            break
                        sql_lines.append(line.strip())
                return "\n".join(sql_lines) if sql_lines else "Could not parse SQL"

        except requests.RequestException as e:
            print("Request error:", e)
            return None
        except Exception as e:
            print("Unexpected error:", e)
            return None

def loose_sql_match(pred, ref):
    def tokenize(sql):
        return [token for token in re.findall(r"\b\w+\b", sql.lower())]
    pred_tokens = set(tokenize(pred))
    ref_tokens = set(tokenize(ref))
    return ref_tokens.issubset(pred_tokens)

def calculate_loose_match_accuracy(predictions, references):
    correct = 0
    for pred, ref in zip(predictions, references):
        if pred is None:
            print(f"Prediction is None for reference: {ref}")
            continue
        if loose_sql_match(pred, ref):
            correct += 1
        else:
            print("\nMismatch:\nPredicted:", pred, "\nExpected:", ref)
    return correct / len(references) if references else 0

def main():
    client = NL2SQLClient()

    test_questions = [
        "Show all IT department employees",
        "Find employees hired after 2020",
        "Count employees in each department"
    ]

    references = [
        "SELECT id, name, salary, hire_date FROM employees WHERE department = 'IT';",
        "SELECT * FROM employees WHERE hire_date > '2020-01-01';",
        "SELECT department, COUNT(*) FROM employees GROUP BY department;"
    ]

    predictions = []

    for question in test_questions:
        print(f"\nQ: {question}")
        sql = client.generate_sql(question)
        print("Generated SQL:")
        print(sql)
        predictions.append(sql)

    accuracy = calculate_loose_match_accuracy(predictions, references)
    print(f"\nLoose Match Accuracy: {accuracy * 100:.2f}%")

if __name__ == "__main__":
    main()
