from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import sys
from typing import List, Optional
from datetime import datetime

app = FastAPI(title="InsightPipe Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

class GeminiImportRequest(BaseModel):
    url: str

class GeminiImportResponse(BaseModel):
    success: bool
    title: str
    markdown: str
    prompt: str
    filename: str
    turn_count: int

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

@app.get("/api/docs/{filename}")
def get_document(filename: str):
    # Basic security check to prevent directory traversal
    if ".." in filename or "/" in filename or "\\" in filename:
         raise HTTPException(status_code=400, detail="Invalid filename")
    
    filepath = os.path.join(DOCS_DIR, filename)
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="File not found")
        
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        return {"filename": filename, "content": content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/docs/{filename}")
def delete_document(filename: str):
    # Basic security check
    if ".." in filename or "/" in filename or "\\" in filename:
         raise HTTPException(status_code=400, detail="Invalid filename")
    
    filepath = os.path.join(DOCS_DIR, filename)
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="File not found")
        
    try:
        os.remove(filepath)
        return {"message": f"File {filename} deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def get_analysis_prompt() -> str:
    """返回标准的对话分析Prompt模板"""
    return """你是一个专业的对话分析师。我上传了一段Gemini对话记录。

**任务**：提取这段对话中的核心洞察（Insights）。

**输出格式**：
## 对话概览
- 主题：[一句话概括]
- 核心问题：[用户想解决什么]

## 关键洞察（3-5条）
1. [洞察标题]
   - 证据：[AI给出的数据/案例]
   - 启发：[可迁移的思维模式]

2. [洞察标题]
   - 证据：[具体支撑]
   - 启发：[实际应用]

## 可执行建议
[如果有具体行动计划，在此总结]

**注意**：
- 忽略客套话和重复内容
- 优先提取有数据支撑的结论
- 关注"为什么"而不仅是"是什么"
- 如果涉及敏感话题，客观总结事实部分即可
"""

@app.post("/api/import/gemini", response_model=GeminiImportResponse)
async def import_gemini_conversation(request: GeminiImportRequest):
    """
    导入Gemini分享链接的对话
    返回解析后的Markdown内容和推荐的分析Prompt
    """
    try:
        # 导入GeminiService
        sys.path.insert(0, os.path.join(BASE_DIR, 'server', 'services'))
        from gemini_service import GeminiService
        
        # 提取share ID
        share_id = GeminiService.extract_id(request.url)
        if not share_id:
            raise HTTPException(status_code=400, detail="无效的Gemini分享链接")
        
        # 获取对话数据
        result = GeminiService.fetch_conversation(request.url)
        
        # 处理标题（确保是字符串）
        title = result.get('title', 'Gemini对话记录')
        if isinstance(title, list):
            title = str(title[1]) if len(title) > 1 else str(title[0])
        
        # 计算轮数
        turn_count = result['content'].count('## 🙋‍♂️ User')
        
        # 生成完整的Markdown内容
        md_content = f"""# {title}

*共 {turn_count} 轮对话*
---

{result['content']}
"""
        
        # 生成安全的文件名
        safe_title = sanitize_filename(title)[:30]
        filename = f"{share_id}_{safe_title}.md"
        
        return GeminiImportResponse(
            success=True,
            title=title,
            markdown=md_content,
            prompt=get_analysis_prompt(),
            filename=filename,
            turn_count=turn_count
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"导入失败: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8100)
