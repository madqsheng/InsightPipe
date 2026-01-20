import sys
import os
import pyperclip

# Configuration
TEMPLATE_PATH = os.path.join(os.path.dirname(__file__), '../templates/base_prompt.txt')

def load_template(path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"Error: Template file not found at {path}")
        sys.exit(1)

def main():
    if len(sys.argv) < 2:
        print("Usage: python ask.py \"Your question here\"")
        sys.exit(1)

    user_input = " ".join(sys.argv[1:])
    template_content = load_template(TEMPLATE_PATH)
    
    # Replace placeholder
    final_prompt = template_content.replace("{{USER_INPUT}}", user_input)
    
    # Copy to clipboard
    try:
        pyperclip.copy(final_prompt)
        print("\n✅ Prompt generated and COPIED to clipboard!")
        print("--------------------------------------------------")
        print(f"Question: {user_input}")
        print("--------------------------------------------------")
        print("Now paste it into your AI assistant.")
    except Exception as e:
        print(f"\n⚠️  Could not copy to clipboard (Error: {e})")
        print("Here is the prompt to copy manually:\n")
        print(final_prompt)

if __name__ == "__main__":
    main()
