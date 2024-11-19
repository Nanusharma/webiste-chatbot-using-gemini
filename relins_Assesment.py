import os
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
from urllib.parse import urlparse

def validate_url(url):
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False

def extract_website_content(url, max_chars=5000):
    try:
        # Fetch website content
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        # Parse HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Remove scripts, styles, and navigation elements
        for script in soup(["script", "style", "nav", "header", "footer"]):
            script.decompose()
        
        # Extract main content
        content = soup.get_text(separator=' ', strip=True)
        
        # Truncate content
        return content[:max_chars]

    except requests.RequestException as e:
        print(f"Error fetching website: {e}")
        return None

def generate_initial_context(model, content):
    """Generate initial context and summary"""
    try:
        summary_prompt = f"Provide a concise 3-sentence summary of the following website content: {content}"
        summary_response = model.generate_content(summary_prompt)
        return summary_response.text
    except Exception as e:
        print(f"Error generating summary: {e}")
        return "Unable to generate summary."

def configure_gemini_model(api_key):
    # Configure Gemini API
    genai.configure(api_key=api_key)
    
    #generation configuration
    generation_config = {
        "temperature": 0.7,
        "top_p": 0.85,
        "top_k": 40,
        "max_output_tokens": 2000,
    }
    
    # Initialize Gemini model
    return genai.GenerativeModel(
        model_name="gemini-1.5-flash-001",
        generation_config=generation_config
    )

def start_interactive_chat(model, url):
    """
    Start interactive chat with website context
    """
    # Validate URL
    if not validate_url(url):
        print("Invalid URL. Please provide a valid website URL.")
        return

    # Extract website content
    content = extract_website_content(url)
    if not content:
        print("Could not extract website content.")
        return

    # Generate initial context
    summary = generate_initial_context(model, content)
    print("Website Content Summary:", summary)

    # Start chat session
    chat_session = model.start_chat(history=[])
    
    print("\n--- Chatbot Ready ---")
    print("Ask questions about the website. Type 'exit' to quit.")

    while True:
        user_input = input("\nYou: ").strip()

        if user_input.lower() in ['exit', 'quit', 'bye']:
            print("Ending chat session.")
            break

        if not user_input:
            continue

        try:
            # Enhance user input with website context
            enhanced_prompt = f"""
            Website Content: {content}
            
            User Question: {user_input}
            
            Please provide a relevant and informative response based on the website content.
            """

            # Generate response
            response = chat_session.send_message(enhanced_prompt)
            print("\nChatbot:", response.text)

        except Exception as e:
            print(f"Error generating response: {e}")

def main():
    # API Key retrieval
    def get_api_key():
        # Check environment variable
        api_key = "AIzaSyBziqQ9Zu4r4MYuG2DdYLomMxVBPwFmzIs"
        
        # Prompt if not found
        if not api_key:
            api_key = input("Enter your Gemini API Key: ").strip()
        
        return api_key

    # Get API Key
    API_KEY = get_api_key()
    
    # Validate API Key
    if not API_KEY:
        print("API Key is required.")
        return

    try:
        # Configure Gemini model
        model = configure_gemini_model(API_KEY)

        # Get website URL from user
        url = input("Enter the website URL to analyze: ")
        
        # Start interactive chat
        start_interactive_chat(model, url)

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()