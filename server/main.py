from fastapi import FastAPI, HTTPException, Body
from pydantic import BaseModel
import os
import sys
from typing import List, Optional
from datetime import datetime

app = FastAPI(title="InsightPipe Backend")

# Configuration
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATES_DIR = os.path.join(BASE_DIR, 'templates')
DOCS_DIR = os.path.join(BASE_DIR, 'docs')

# Ensure docs directory exists
if not os.path.exists(DOCS_DIR):
    os.makedirs(DOCS_DIR)

class PromptRequest(BaseModel):
    user_input: str
    template_name: str = "base_prompt.txt"

class SaveDocRequest(BaseModel):
    title: str
    content: str
    overwrite: bool = False

class DocMetadata(BaseModel):
    filename: str
    title: str
    created_at: str
    size: int

def get_template_content(template_name: str) -> str:
    template_path = os.path.join(TEMPLATES_DIR, template_name)
    if not os.path.exists(template_path):
        raise FileNotFoundError(f"Template '{template_name}' not found.")
    with open(template_path, 'r', encoding='utf-8') as f:
        return f.read()

def sanitize_filename(name: str) -> str:
    keepcharacters = (' ','.','_')
    return "".join(c for c in name if c.isalnum() or c in keepcharacters).rstrip()

@app.get("/health")
def health_check():
    return {"status": "ok", "version": "0.1.0"}

@app.post("/api/prompt/generate")
def generate_prompt(request: PromptRequest):
    try:
        template_content = get_template_content(request.template_name)
        final_prompt = template_content.replace("{{USER_INPUT}}", request.user_input)
        return {"prompt": final_prompt}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Template {request.template_name} not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/docs/save")
def save_document(request: SaveDocRequest):
    try:
        safe_name = sanitize_filename(request.title)
        if not safe_name:
             raise HTTPException(status_code=400, detail="Invalid title provided")
             
        filename = f"{safe_name}.md"
        filepath = os.path.join(DOCS_DIR, filename)
        
        if os.path.exists(filepath) and not request.overwrite:
            raise HTTPException(status_code=409, detail=f"File '{filename}' already exists.")
            
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(request.content)
            
        return {"message": "Document saved successfully", "path": filepath}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/docs", response_model=List[DocMetadata])
def list_documents():
    docs = []
    try:
        for filename in os.listdir(DOCS_DIR):
            if filename.endswith(".md"):
                filepath = os.path.join(DOCS_DIR, filename)
                stats = os.stat(filepath)
                created_at = datetime.fromtimestamp(stats.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
                
                # Try to extract a title from the file content if possible, simplistic approach
                # Or just use filename as title for metadata list
                title = filename.replace(".md", "")
                
                docs.append(DocMetadata(
                    filename=filename,
                    title=title,
                    created_at=created_at,
                    size=stats.st_size
                ))
        # Sort by most recent
        docs.sort(key=lambda x: x.created_at, reverse=True)
        return docs
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
