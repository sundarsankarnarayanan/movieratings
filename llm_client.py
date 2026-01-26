from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

class LLMClient:
    def __init__(self):
        self.api_key = os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            print("Warning: OPENAI_API_KEY not found.")
            self.client = None
        else:
            self.client = OpenAI(api_key=self.api_key)

    def summarize_reviews(self, movie_title, reviews_text):
        """
        Generates positive and negative summaries from reviews.
        Returns a tuple: (positive_summary, negative_summary)
        """
        if not self.client:
            return ("AI Integration pending.", "AI Integration pending.")

        prompt = f"""
        Analyze the following reviews for the movie "{movie_title}".
        Provide two concise summaries:
        1. "Positives": What critics liked (max 3 sentences).
        2. "Negatives": What critics disliked (max 3 sentences).
        
        Reviews:
        {reviews_text}
        
        Format output strictly as:
        POSITIVES: [summary]
        NEGATIVES: [summary]
        """

        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7
            )
            content = response.choices[0].message.content
            
            # Simple parsing
            positives, negatives = "", ""
            if "POSITIVES:" in content and "NEGATIVES:" in content:
                parts = content.split("NEGATIVES:")
                positives = parts[0].replace("POSITIVES:", "").strip()
                negatives = parts[1].strip()
            else:
                positives = content # Fallback
                
            return positives, negatives

        except Exception as e:
            print(f"LLM Error: {e}")
            return ("Error generating summary.", "Error generating summary.")
