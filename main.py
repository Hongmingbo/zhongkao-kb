import os
import shutil
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path

app = FastAPI(title="中考知识库 (Zhongkao Knowledge Base)")

# Ensure directories exist
BASE_DIR = Path(__file__).parent
KNOWLEDGE_BASE_DIR = BASE_DIR / "knowledge_base"
STATIC_DIR = BASE_DIR / "static"

KNOWLEDGE_BASE_DIR.mkdir(parents=True, exist_ok=True)
STATIC_DIR.mkdir(parents=True, exist_ok=True)

# Mount static files
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

SUBJECT_KEYWORDS = {
    "语文": ["语文", "阅读", "作文", "古诗", "文言文", "chinese"],
    "数学": ["数学", "几何", "代数", "函数", "方程", "math"],
    "英语": ["英语", "单词", "语法", "听力", "english"],
    "物理": ["物理", "力学", "电学", "光学", "physics"],
    "化学": ["化学", "元素", "反应", "实验", "chemistry"],
    "历史": ["历史", "朝代", "近代史", "古代史", "history"],
    "政治": ["政治", "道德与法治", "道法", "politics"],
    "生物": ["生物", "细胞", "遗传", "biology"],
    "地理": ["地理", "地图", "气候", "地形", "geography"],
}

def classify_file(filename: str, content_preview: str = "") -> str:
    """Simple classification based on filename and content keywords."""
    text_to_check = (filename + " " + content_preview).lower()
    for subject, keywords in SUBJECT_KEYWORDS.items():
        if any(kw in text_to_check for kw in keywords):
            return subject
    return "综合与其他"

@app.get("/", response_class=HTMLResponse)
async def get_index():
    index_file = STATIC_DIR / "index.html"
    if index_file.exists():
        return index_file.read_text(encoding="utf-8")
    return "<h1>前端页面未找到</h1>"

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        # Read a small chunk of the file for content-based classification if it's a text file
        content_preview = ""
        if file.filename.endswith(('.txt', '.md', '.csv')):
            chunk = await file.read(1024)
            content_preview = chunk.decode(errors='ignore')
            await file.seek(0)
            
        category = classify_file(file.filename, content_preview)
        
        # Create category directory
        category_dir = KNOWLEDGE_BASE_DIR / category
        category_dir.mkdir(exist_ok=True)
        
        file_path = category_dir / file.filename
        
        # Save file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        return JSONResponse({
            "status": "success",
            "filename": file.filename,
            "category": category,
            "path": f"knowledge_base/{category}/{file.filename}",
            "message": f"文件已成功分类并保存到 {category} 目录"
        })
    except Exception as e:
        return JSONResponse({"status": "error", "message": str(e)}, status_code=500)

@app.get("/api/stats")
async def get_stats():
    """Returns the current state of the knowledge base for display."""
    stats = {}
    for item in KNOWLEDGE_BASE_DIR.iterdir():
        if item.is_dir():
            files = [f.name for f in item.iterdir() if f.is_file()]
            if files:
                stats[item.name] = files
    return stats
