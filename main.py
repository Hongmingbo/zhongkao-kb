import os
import shutil
import hashlib
import zipfile
import tempfile
import re
import json
import datetime as dt
from typing import Optional
from pathlib import Path
from fastapi import FastAPI, File, UploadFile, HTTPException, Query
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from zoneinfo import ZoneInfo

# Additional imports for new features
try:
    import PyPDF2
except ImportError:
    PyPDF2 = None

try:
    import docx
except ImportError:
    docx = None

try:
    import pytesseract
    from PIL import Image, ImageChops, ImageFilter, ImageOps
except ImportError:
    pytesseract = None
    Image = None
    ImageChops = None
    ImageFilter = None
    ImageOps = None

try:
    from pdf2image import convert_from_path
except ImportError:
    convert_from_path = None

TESSERACT_CONFIG = "--oem 1 --psm 6"
MAX_PDF_OCR_PAGES = 8

app = FastAPI(title="中考知识库 (Zhongkao Knowledge Base)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "https://zhongkao-kb.pages.dev",
    ],
    allow_origin_regex=r"^https://.*\.pages\.dev$",
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).parent
KNOWLEDGE_BASE_DIR = BASE_DIR / "knowledge_base"
STATIC_DIR = BASE_DIR / "static"

KNOWLEDGE_BASE_DIR.mkdir(parents=True, exist_ok=True)
STATIC_DIR.mkdir(parents=True, exist_ok=True)

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

# ----------------- Helper Functions ----------------- #

def _iter_target_files(base_dir: Path, category: Optional[str]):
    if category:
        dirs = [base_dir / category]
    else:
        dirs = [p for p in base_dir.iterdir() if p.is_dir()]
    for d in dirs:
        if not d.exists() or not d.is_dir():
            continue
        for f in d.iterdir():
            if not f.is_file():
                continue
            if f.name.endswith(".meta.json"):
                continue
            yield d.name, f

def _find_all(haystack: str, needle: str, max_hits: int):
    hits = []
    start = 0
    while start < len(haystack) and len(hits) < max_hits:
        idx = haystack.find(needle, start)
        if idx < 0:
            break
        hits.append(idx)
        start = idx + max(1, len(needle))
    return hits

def _make_snippet(text: str, pos: int, needle_len: int, context: int) -> str:
    left = max(0, pos - context)
    right = min(len(text), pos + needle_len + context)
    prefix = "…" if left > 0 else ""
    suffix = "…" if right < len(text) else ""
    return prefix + text[left:right].replace("\n", " ") + suffix

def search_knowledge_base(
    base_dir: Path,
    q: str,
    category: Optional[str],
    limit: int,
    context: int,
):
    q_norm = q.strip()
    q_lower = q_norm.lower()
    results = []
    for cat, f in _iter_target_files(base_dir, category):
        matches = []
        filename_lower = f.name.lower()
        if q_lower in filename_lower:
            matches.append({"where": "filename", "snippet": f.name, "pos": filename_lower.find(q_lower)})

        ext = f.suffix.lower()
        if ext in [".md", ".txt", ".csv"]:
            try:
                content = f.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                content = ""
            content_lower = content.lower()
            if q_lower in content_lower:
                for pos in _find_all(content_lower, q_lower, max_hits=3):
                    matches.append(
                        {
                            "where": "content",
                            "snippet": _make_snippet(content, pos, len(q_norm), context),
                            "pos": pos,
                        }
                    )

        if matches:
            results.append(
                {
                    "category": cat,
                    "filename": f.name,
                    "path": f"knowledge_base/{cat}/{f.name}",
                    "count": len(matches),
                    "matches": matches,
                }
            )

    results.sort(key=lambda r: (-r["count"], r["filename"]))
    return {
        "query": q_norm,
        "category": category,
        "limit": limit,
        "context": context,
        "results": results[:limit],
    }

def get_file_md5(file_path: Path) -> str:
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def is_duplicate(file_md5: str) -> bool:
    """Feature 5: 智能去重。检查是否已经存在相同MD5的文件。"""
    for meta_file in KNOWLEDGE_BASE_DIR.rglob("*.meta.json"):
        try:
            with open(meta_file, 'r', encoding='utf-8') as f:
                meta = json.load(f)
                if meta.get('original_md5') == file_md5:
                    return True
        except:
            pass
    return False

def classify_file(filename: str, text_content: str = "") -> str:
    """根据文件名和内容进行分类"""
    text_to_check = (filename + " " + text_content).lower()
    for subject, keywords in SUBJECT_KEYWORDS.items():
        if any(kw in text_to_check for kw in keywords):
            return subject
    return "综合与其他"

def extract_metadata(filename: str, text_content: str, original_md5: str) -> dict:
    """Feature 4: 智能元数据提取。提取年份、地区等。"""
    meta = {'original_md5': original_md5}
    text_to_check = filename + " " + text_content
    
    # 提取年份
    year_match = re.search(r'(20\d{2})年?', text_to_check)
    if year_match:
        meta['year'] = year_match.group(1)
        
    # 提取地区 (简单示例)
    regions = ['北京', '上海', '广州', '深圳', '黄冈', '成都', '武汉', '杭州', '天津', '重庆', '江苏', '浙江', '山东', '广东', '河南']
    for region in regions:
        if region in text_to_check:
            meta['region'] = region
            break
            
    # 提取试卷类型
    if '模拟' in text_to_check:
        meta['type'] = '模拟卷'
    elif '真题' in text_to_check or '中考' in text_to_check:
        meta['type'] = '中考真题'
    elif '期末' in text_to_check:
        meta['type'] = '期末卷'
        
    return meta

def preprocess_ocr_image(img: "Image.Image") -> "Image.Image":
    if not (Image and ImageOps and ImageFilter and ImageChops):
        return img
    base = img.convert("RGB")
    r, g, b = base.split()
    m1 = ImageChops.subtract(r, g).point(lambda p: 255 if p > 40 else 0)
    m2 = ImageChops.subtract(r, b).point(lambda p: 255 if p > 40 else 0)
    m3 = r.point(lambda p: 255 if p > 140 else 0)
    mask = ImageChops.multiply(ImageChops.multiply(m1, m2), m3)
    cleaned = Image.composite(Image.new("RGB", base.size, (255, 255, 255)), base, mask)
    gray = cleaned.convert("L")
    gray = ImageOps.autocontrast(gray)
    gray = gray.filter(ImageFilter.MedianFilter(size=3))
    if hasattr(Image, "Resampling"):
        resample = Image.Resampling.LANCZOS
    else:
        resample = Image.LANCZOS
    gray = gray.resize((gray.size[0] * 2, gray.size[1] * 2), resample=resample)
    return gray

def extract_text_from_file(file_path: Path) -> str:
    """Feature 1 & 2: 提取文本内容，用于转换Markdown或切块。"""
    ext = file_path.suffix.lower()
    text = ""
    
    if ext == '.pdf' and PyPDF2:
        try:
            with open(file_path, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                parts = []
                for page in reader.pages:
                    t = page.extract_text()
                    if t:
                        parts.append(t)
                text = "\n".join(parts)
        except Exception:
            pass
        if not text.strip() and convert_from_path and pytesseract and Image:
            try:
                images = convert_from_path(str(file_path), dpi=320, fmt="png", first_page=1, last_page=MAX_PDF_OCR_PAGES)
                ocr_parts = []
                for idx, img in enumerate(images, start=1):
                    t = pytesseract.image_to_string(preprocess_ocr_image(img), lang="chi_sim+eng", config=TESSERACT_CONFIG)
                    if t and t.strip():
                        ocr_parts.append(f"第{idx}页\n{t.strip()}")
                text = "\n\n".join(ocr_parts)
            except Exception:
                text = ""
    elif ext in ['.docx', '.doc'] and docx:
        try:
            doc = docx.Document(file_path)
            text = "\n".join(para.text for para in doc.paragraphs)
        except Exception:
            pass
    elif ext in ['.txt', '.md', '.csv']:
        try:
            text = file_path.read_text(encoding='utf-8', errors='ignore')
        except Exception:
            pass
    elif ext in ['.jpg', '.jpeg', '.png']:
        if pytesseract and Image:
            try:
                text = pytesseract.image_to_string(preprocess_ocr_image(Image.open(file_path)), lang="chi_sim+eng", config=TESSERACT_CONFIG)
            except Exception:
                text = ""
        if not text.strip():
            text = f"【未提取到有效文本：图片 OCR 失败或未安装 OCR 依赖】\n文件：{file_path.name}"
        
    return text

def placeholder_for(ext: str) -> str:
    if ext == ".pdf":
        return "【未提取到有效文本：该 PDF 可能是扫描件/图片型 PDF，且 OCR 失败或依赖未安装】"
    if ext in [".doc", ".docx"]:
        return "【未提取到有效文本：Word 文档解析失败】"
    if ext in [".jpg", ".jpeg", ".png"]:
        return "【未提取到有效文本：图片 OCR 失败】"
    return "【未提取到有效文本】"

def chunk_text(text: str) -> str:
    """Feature 3: 试卷自动拆题与切块。添加Markdown分隔符。"""
    if not text:
        return text
    # 简单的正则，将大题（如“一、选择题”）前加上明确的分割线
    chunked = re.sub(r'\n([一二三四五六七八九十]、)', r'\n\n---\n\n\1', text)
    return chunked

def process_single_file(file_path: Path, original_filename: str) -> dict:
    """处理单个文件：去重、提取文本、分类、转Markdown、切块、提取元数据并移动到对应目录"""
    
    # 1. 查重
    file_md5 = get_file_md5(file_path)
    if is_duplicate(file_md5):
        return {"status": "skipped", "filename": original_filename, "message": "文件已存在 (MD5重复)"}
    
    # 2. 提取文本
    text_content = extract_text_from_file(file_path)
    
    # 3. 分类
    category = classify_file(original_filename, text_content[:1000])
    category_dir = KNOWLEDGE_BASE_DIR / category
    category_dir.mkdir(exist_ok=True)
    
    # 4. 格式转换与切块
    ext = Path(original_filename).suffix.lower()
    final_filename = original_filename
    final_path = category_dir / final_filename
    
    if ext in ['.pdf', '.docx', '.doc', '.jpg', '.jpeg', '.png']:
        # 转换为 Markdown
        final_filename = Path(original_filename).stem + ".md"
        final_path = category_dir / final_filename
        
        # 避免同名覆盖
        counter = 1
        while final_path.exists():
            final_filename = f"{Path(original_filename).stem}_{counter}.md"
            final_path = category_dir / final_filename
            counter += 1
            
        chunked_text = chunk_text(text_content)
        if not chunked_text.strip():
            chunked_text = placeholder_for(ext)
        final_path.write_text(chunked_text, encoding='utf-8')
    else:
        # 普通文本文件直接复制，但也可以进行切块处理
        if ext in ['.txt', '.md']:
            chunked_text = chunk_text(text_content)
            final_path.write_text(chunked_text, encoding='utf-8')
        else:
            shutil.copy2(file_path, final_path)
            
    # 5. 提取并保存元数据
    meta = extract_metadata(original_filename, text_content, file_md5)
    if meta:
        meta_path = category_dir / f"{final_path.name}.meta.json"
        with open(meta_path, 'w', encoding='utf-8') as f:
            json.dump(meta, f, ensure_ascii=False, indent=2)
            
    return {
        "status": "success",
        "filename": original_filename,
        "saved_as": final_filename,
        "category": category,
        "meta": meta,
        "path": f"knowledge_base/{category}/{final_filename}"
    }

# ----------------- API Endpoints ----------------- #

@app.get("/")
async def get_index():
    return RedirectResponse(url="https://zhongkao-kb.pages.dev/", status_code=302)

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    results = []
    try:
        # Create a temporary directory to save the uploaded file
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_dir_path = Path(temp_dir)
            temp_file_path = temp_dir_path / file.filename
            
            with open(temp_file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
                
            # Feature 6: ZIP 批量上传与自动解压
            if file.filename.lower().endswith('.zip'):
                try:
                    with zipfile.ZipFile(temp_file_path, 'r') as zip_ref:
                        extract_dir = temp_dir_path / "extracted"
                        extract_dir.mkdir()
                        zip_ref.extractall(extract_dir)
                        
                        for extracted_file in extract_dir.rglob("*"):
                            if extracted_file.is_file() and not extracted_file.name.startswith('.'):
                                res = process_single_file(extracted_file, extracted_file.name)
                                results.append(res)
                except zipfile.BadZipFile:
                    return JSONResponse({"status": "error", "message": "无效的ZIP文件"}, status_code=400)
            else:
                # 处理单文件
                res = process_single_file(temp_file_path, file.filename)
                results.append(res)
                
        return JSONResponse({"status": "success", "results": results})
    except Exception as e:
        return JSONResponse({"status": "error", "message": str(e)}, status_code=500)

@app.get("/api/stats")
async def get_stats():
    """Returns the current state of the knowledge base for display."""
    stats = {}
    for item in KNOWLEDGE_BASE_DIR.iterdir():
        if item.is_dir():
            files = []
            for f in item.iterdir():
                if f.is_file() and not f.name.endswith(".meta.json"):
                    # Check if meta exists
                    meta_path = f.with_name(f.name + ".meta.json")
                    has_meta = meta_path.exists()
                    files.append({"name": f.name, "has_meta": has_meta})
            if files:
                stats[item.name] = files
    return stats

@app.get("/api/search")
async def api_search(
    q: str = Query(..., min_length=1, max_length=60),
    category: Optional[str] = Query(None),
    limit: int = Query(20, ge=1, le=50),
    context: int = Query(60, ge=10, le=200),
):
    return search_knowledge_base(
        base_dir=KNOWLEDGE_BASE_DIR,
        q=q,
        category=category,
        limit=limit,
        context=context,
    )

@app.get("/api/daily_quote")
async def get_daily_quote():
    tz = ZoneInfo("Asia/Shanghai")
    today = dt.datetime.now(tz=tz).date()
    date_str = today.isoformat()

    quotes = [
        {
            "text": "学而不思则罔，思而不学则殆。",
            "source": "《论语·为政》",
            "summary": "强调学习与思考要结合，才能真正掌握知识。",
        },
        {
            "text": "不积跬步，无以至千里；不积小流，无以成江海。",
            "source": "《荀子·劝学》",
            "summary": "强调点滴积累与长期坚持，才能实现大的目标。",
        },
        {
            "text": "纸上得来终觉浅，绝知此事要躬行。",
            "source": "陆游《冬夜读书示子聿》",
            "summary": "强调实践的重要性，知识要通过行动才能真正理解。",
        },
        {
            "text": "千磨万击还坚劲，任尔东西南北风。",
            "source": "郑燮《竹石》",
            "summary": "强调意志坚定与抗压能力，在逆境中保持韧性。",
        },
        {
            "text": "山重水复疑无路，柳暗花明又一村。",
            "source": "陆游《游山西村》",
            "summary": "强调遇到困难不要放弃，坚持下去往往会迎来转机。",
        },
        {
            "text": "业精于勤，荒于嬉；行成于思，毁于随。",
            "source": "韩愈《进学解》",
            "summary": "强调勤奋与反思能成就学业，懒散随意会导致退步。",
        },
        {
            "text": "天行健，君子以自强不息。",
            "source": "《周易·乾》",
            "summary": "强调自强与进取精神，把成长当作长期任务。",
        },
        {
            "text": "沉舟侧畔千帆过，病树前头万木春。",
            "source": "刘禹锡《酬乐天扬州初逢席上见赠》",
            "summary": "强调更新与希望：旧的会过去，新的会不断出现。",
        },
    ]

    idx = abs(hash(date_str)) % len(quotes)
    q = quotes[idx]
    return {"date": date_str, **q}

@app.get("/api/filters/options")
async def get_filter_options():
    categories = sorted([p.name for p in KNOWLEDGE_BASE_DIR.iterdir() if p.is_dir()])

    exts = set()
    years = set()
    regions = set()
    types = set()

    for cat in categories:
        d = KNOWLEDGE_BASE_DIR / cat
        for f in d.iterdir():
            if not f.is_file():
                continue
            if f.name.endswith(".meta.json"):
                continue

            ext = f.suffix.lower().lstrip(".")
            if ext:
                exts.add(ext)

            meta_path = f.with_name(f.name + ".meta.json")
            if meta_path.exists():
                try:
                    meta = json.loads(meta_path.read_text(encoding="utf-8", errors="ignore") or "{}")
                except Exception:
                    meta = {}
                y = meta.get("year")
                r = meta.get("region")
                t = meta.get("type")
                if isinstance(y, str) and y:
                    years.add(y)
                if isinstance(r, str) and r:
                    regions.add(r)
                if isinstance(t, str) and t:
                    types.add(t)

    return {
        "categories": categories,
        "years": sorted(years),
        "regions": sorted(regions),
        "types": sorted(types),
        "exts": sorted(exts),
    }

@app.get("/api/filter")
async def filter_files(
    category: Optional[str] = Query(None),
    year: Optional[str] = Query(None),
    region: Optional[str] = Query(None),
    type: Optional[str] = Query(None),
    ext: Optional[str] = Query(None),
):
    ext_norm = (ext or "").strip().lower().lstrip(".") or None
    need_meta = any([(year or "").strip(), (region or "").strip(), (type or "").strip()])

    stats = {}
    for cat, f in _iter_target_files(KNOWLEDGE_BASE_DIR, category):
        if ext_norm and f.suffix.lower().lstrip(".") != ext_norm:
            continue

        meta_path = f.with_name(f.name + ".meta.json")
        has_meta = meta_path.exists()

        if need_meta:
            if not has_meta:
                continue
            try:
                meta = json.loads(meta_path.read_text(encoding="utf-8", errors="ignore") or "{}")
            except Exception:
                meta = {}
            if year and meta.get("year") != year:
                continue
            if region and meta.get("region") != region:
                continue
            if type and meta.get("type") != type:
                continue

        stats.setdefault(cat, []).append({"name": f.name, "has_meta": has_meta})

    for cat in list(stats.keys()):
        stats[cat].sort(key=lambda x: x["name"])
        if not stats[cat]:
            del stats[cat]

    return stats

@app.delete("/api/clear")
async def clear_knowledge_base():
    try:
        for item in KNOWLEDGE_BASE_DIR.iterdir():
            if item.name == ".gitkeep":
                continue
            if item.is_dir():
                shutil.rmtree(item)
            else:
                item.unlink(missing_ok=True)
        return {"status": "success", "message": "知识库已清空"}
    except Exception as e:
        return JSONResponse({"status": "error", "message": str(e)}, status_code=500)

# Feature 7: 在线文件预览
@app.get("/api/file/{category}/{filename}")
async def get_file_content(category: str, filename: str):
    file_path = KNOWLEDGE_BASE_DIR / category / filename
    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(status_code=404, detail="文件不存在")
        
    ext = file_path.suffix.lower()
    if ext in ['.txt', '.md', '.csv']:
        content = file_path.read_text(encoding='utf-8', errors='ignore')
        return {"filename": filename, "content": content, "type": "text"}
    else:
        return {"filename": filename, "content": "二进制文件，不支持直接预览", "type": "binary"}

# Feature 7: 在线文件删除
@app.delete("/api/file/{category}/{filename}")
async def delete_file(category: str, filename: str):
    file_path = KNOWLEDGE_BASE_DIR / category / filename
    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(status_code=404, detail="文件不存在")
        
    try:
        os.remove(file_path)
        # 尝试删除对应的meta文件
        meta_path = file_path.with_name(file_path.name + ".meta.json")
        if meta_path.exists():
            os.remove(meta_path)
        return {"status": "success", "message": f"文件 {filename} 已删除"}
    except Exception as e:
        return JSONResponse({"status": "error", "message": str(e)}, status_code=500)
