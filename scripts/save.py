import sys
import os
import datetime

# Configuration
DOCS_DIR = os.path.join(os.path.dirname(__file__), '../docs')

def sanitize_filename(name):
    """Sanitize input to be safe for filenames."""
    keepcharacters = (' ','.','_')
    return "".join(c for c in name if c.isalnum() or c in keepcharacters).rstrip()

def ensure_docs_dir():
    if not os.path.exists(DOCS_DIR):
        os.makedirs(DOCS_DIR)

def get_multiline_input():
    print("Paste the definition/markdown content below.")
    print("Type 'EOF' on a new line and press Enter to save.")
    print("--------------------------------------------------")
    
    lines = []
    while True:
        try:
            line = input()
        except EOFError:
            break
        
        if line.strip() == 'EOF':
            break
        lines.append(line)
    return "\n".join(lines)

def main():
    if len(sys.argv) < 2:
        print("Usage: python save.py \"Topic Name\"")
        sys.exit(1)

    topic_name = " ".join(sys.argv[1:])
    safe_name = sanitize_filename(topic_name)
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d")
    
    filename = f"{safe_name}.md"
    filepath = os.path.join(DOCS_DIR, filename)

    ensure_docs_dir()

    # Check if file exists to avoid accidental overwrite
    mode = 'w'
    if os.path.exists(filepath):
        print(f"⚠️  File '{filename}' already exists.")
        choice = input("Overwrite? (y/n): ").lower()
        if choice != 'y':
            print("Operation cancelled.")
            sys.exit(0)

    # Get content
    content = get_multiline_input()
    
    if not content.strip():
        print("⚠️  No content provided. File not saved.")
        sys.exit(1)

    # Save content
    # Optional: Prepend Frontmatter or metadata here if desired
    with open(filepath, mode, encoding='utf-8') as f:
        f.write(content)
        
    print(f"\n✅ Content saved to: {filepath}")

if __name__ == "__main__":
    main()
