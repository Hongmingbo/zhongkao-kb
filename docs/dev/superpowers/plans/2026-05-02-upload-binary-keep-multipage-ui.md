# 上传二进制保留格式 + PDF/DOCX 派生文本 + 多页面 UI 重构 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 上传图片/PDF/DOCX 等非纯文本文件时保留原始格式；PDF/DOCX 额外生成可搜索/可拆题的派生 Markdown；前端拆成“多页面（Tabs）”并整体视觉更专业。

**Architecture:** 后端上传流水线在保存原文件的同时，针对 PDF/DOCX 生成 `*.pdf.md / *.docx.md` 派生文本文件；图片只保存原图不做 OCR。前端继续使用单文件 `frontend/index.html`，用 hash 路由实现多页面切换，避免部署和后端路径改动。

**Tech Stack:** FastAPI, 本地文件系统（`KNOWLEDGE_BASE_DIR/u_<id>/...`）, PyPDF2, python-docx, Tailwind CDN, 原生 JS, pytest。

---

## 文件与模块改动清单

**后端**
- Modify: [main.py](file:///workspace/zhongkao-kb/main.py)（上传处理 `process_single_file`、新增 raw 下载/预览接口、扩展预览类型）
- (Optional) Modify: [docs/api.md](file:///workspace/zhongkao-kb/docs/api.md)（补充 raw/下载接口说明）

**前端**
- Modify: [frontend/index.html](file:///workspace/zhongkao-kb/frontend/index.html)（Tabs 路由、上传页/知识库页/搜索页/回收站设置页拆分、二进制预览支持、整体 UI 视觉升级）

**测试**
- Modify: [tests/test_auth.py](file:///workspace/zhongkao-kb/tests/test_auth.py) 或新增 `tests/test_upload.py`（上传格式保留、派生文件生成、预览/下载行为）

---

## 规则（来自需求确认）

1) 任何上传文件都保留原扩展名落盘（zip 解压后亦同）。
2) 图片（`.jpg/.jpeg/.png`）只保存原图，不 OCR，不生成派生文本文件。
3) PDF/DOCX：保留原文件 + 生成派生 Markdown：
   - `xxx.pdf` → `xxx.pdf.md`
   - `xxx.docx` → `xxx.docx.md`
4) PDF 抽取不到文本时：不启用 OCR，派生 Markdown 写占位提示（不影响保留原 pdf）。
5) 前端多页面：上传+队列 / 知识库浏览 / 搜索 / 回收站+设置（顶部 Tabs）。

---

### Task 1: 为上传保存策略写失败测试（RED）

**Files:**
- Modify: [tests/test_auth.py](file:///workspace/zhongkao-kb/tests/test_auth.py) 或 Create: `/workspace/zhongkao-kb/tests/test_upload.py`

- [ ] **Step 1: 写失败测试：图片保持原图且不生成 `.md`**

```python
def test_upload_image_keeps_original_no_md(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("APP_DB_PATH", str(tmp_path / "app.db"))
    monkeypatch.setenv("INVITE_CODE", "abc123")
    client = TestClient(main.app)
    client.post("/api/auth/register", json={"invite_code": "abc123", "username": "u1", "password": "pw"})
    token = client.post("/api/auth/login", json={"username": "u1", "password": "pw"}).json()["token"]

    kb_root = tmp_path / "kb"
    kb_root.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(main, "KNOWLEDGE_BASE_DIR", kb_root)

    r = client.post(
        "/upload",
        headers={"Authorization": "Bearer " + token},
        files={"file": ("a.png", b"\x89PNG\r\n\x1a\nfake", "image/png")},
    )
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "success"
    saved_as = data["results"][0]["saved_as"]
    assert saved_as.endswith(".png")
    cat = data["results"][0]["category"]
    base = kb_root / "u_1" / cat
    assert (base / "a.png").exists()
    assert not (base / "a.png.md").exists()
```

- [ ] **Step 2: 写失败测试：PDF 保留原文件且生成 `*.pdf.md`**

```python
def test_upload_pdf_keeps_original_and_creates_derived_md(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("APP_DB_PATH", str(tmp_path / "app.db"))
    monkeypatch.setenv("INVITE_CODE", "abc123")
    client = TestClient(main.app)
    client.post("/api/auth/register", json={"invite_code": "abc123", "username": "u1", "password": "pw"})
    token = client.post("/api/auth/login", json={"username": "u1", "password": "pw"}).json()["token"]

    kb_root = tmp_path / "kb"
    kb_root.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(main, "KNOWLEDGE_BASE_DIR", kb_root)

    fake_pdf = b"%PDF-1.4\n%fake\n1 0 obj\n<<>>\nendobj\ntrailer\n<<>>\n%%EOF\n"
    r = client.post(
        "/upload",
        headers={"Authorization": "Bearer " + token},
        files={"file": ("a.pdf", fake_pdf, "application/pdf")},
    )
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "success"
    cat = data["results"][0]["category"]
    base = kb_root / "u_1" / cat
    assert (base / "a.pdf").exists()
    assert (base / "a.pdf.md").exists()
```

- [ ] **Step 3: 运行测试确认失败（Verify RED）**

Run:
```bash
pytest -q tests/test_upload.py -q
```
Expected: FAIL（当前实现会把 pdf/png 转为 `.md`，不会保留原格式）

- [ ] **Step 4: 提交（仅测试）**

```bash
git add tests/test_upload.py
git commit -m "test: upload keeps binary formats and creates derived md"
```

---

### Task 2: 后端上传流水线：保留原文件 + 生成派生 Markdown（GREEN）

**Files:**
- Modify: [main.py](file:///workspace/zhongkao-kb/main.py#L607-L666)

- [ ] **Step 1: 调整 `process_single_file` 的保存逻辑**

目标行为（伪代码级别，实施时按现有风格落地）：

```python
ext = Path(original_filename).suffix.lower()
dst_original = category_dir / original_filename

binary_image = ext in [".jpg", ".jpeg", ".png"]
binary_pdf_doc = ext in [".pdf", ".doc", ".docx"]
text_like = ext in [".txt", ".md", ".csv"]

if text_like:
    # 保持原名写入（可做 chunk）
    dst_original.write_text(chunk_text(text_content), encoding="utf-8")
elif binary_image:
    # 只保存原图，不 OCR，不派生
    shutil.copy2(file_path, dst_original)
elif binary_pdf_doc:
    # 1) 先保存原文件
    shutil.copy2(file_path, dst_original)
    # 2) 生成派生 Markdown：xxx.pdf.md / xxx.docx.md
    derived_name = original_filename + ".md"
    derived_path = category_dir / derived_name
    derived_text = chunk_text(text_content) if text_content.strip() else placeholder_for(ext)
    derived_path.write_text(derived_text, encoding="utf-8")
else:
    # 其它二进制：保持原格式
    shutil.copy2(file_path, dst_original)
```

- [ ] **Step 2: 元数据写入策略**

建议同时给原文件与派生 `.md` 都写一份 `.meta.json`，保证筛选/标签/展示一致：

```python
meta_for_original = extract_metadata(original_filename, text_content, file_md5)
if meta_for_original:
    (category_dir / f"{dst_original.name}.meta.json").write_text(...)
    if binary_pdf_doc:
        (category_dir / f"{derived_path.name}.meta.json").write_text(...同内容..., encoding="utf-8")
```

- [ ] **Step 3: 运行 Task 1 的测试，确认转绿**

Run:
```bash
pytest -q tests/test_upload.py -q
```
Expected: PASS

- [ ] **Step 4: 补充 zip 解压分支：保持 extracted_file 的原扩展名**

确保 `process_single_file(extracted_file, extracted_file.name, kb_dir)` 仍遵循上述逻辑即可。

- [ ] **Step 5: 提交**

```bash
git add main.py
git commit -m "feat: keep binary uploads and generate derived md for pdf/docx"
```

---

### Task 3: 二进制文件预览/下载：新增 raw 接口（图片/pdf 可直接打开）

**Files:**
- Modify: [main.py](file:///workspace/zhongkao-kb/main.py#L1189-L1208)
- Modify: [docs/api.md](file:///workspace/zhongkao-kb/docs/api.md)

- [ ] **Step 1: 写失败测试：raw 接口返回正确 content-type**

```python
def test_file_raw_serves_png(tmp_path: Path, monkeypatch):
    # 建用户、写入 kb_root/u_1/语文/a.png
    # GET /api/file/raw/语文/a.png => content-type image/png
    ...
```

- [ ] **Step 2: 实现 `GET /api/file/raw/{category}/{filename}`**

要求：
- 仅允许当前用户目录
- 返回 `Response(content=..., media_type=...)`
- `Cache-Control: no-store`
- 支持 `image/png`, `image/jpeg`, `application/pdf`, `application/octet-stream`

- [ ] **Step 3: 扩展现有 `GET /api/file/{category}/{filename}` 预览信息**

当遇到二进制文件时返回可预览/下载信息：

```json
{ "filename":"a.png", "type":"binary", "hint":"二进制文件", "raw_url":"/api/file/raw/<cat>/<name>", "ext":".png" }
```

- [ ] **Step 4: 运行测试与提交**

```bash
pytest -q
git add main.py docs/api.md tests/test_upload.py
git commit -m "feat: add raw file endpoint for binary preview"
```

---

### Task 4: 前端预览体验升级（图片/pdf 直接预览；派生 md 作为“文本预览”入口）

**Files:**
- Modify: [frontend/index.html](file:///workspace/zhongkao-kb/frontend/index.html)

- [ ] **Step 1: 调整预览弹窗渲染**

规则：
- `type === "text"`：保持现状 `<pre>`
- `type === "binary"` 且 `ext` 是图片：`<img src="API_BASE + raw_url">`
- `type === "binary"` 且 `ext` 是 `.pdf`：`<iframe src="API_BASE + raw_url">` + “下载”按钮
- 其它二进制：显示“下载链接”

- [ ] **Step 2: 如果点击的是 `*.pdf` / `*.docx`，在预览弹窗里增加一个快捷按钮：打开派生文本**

例如：点击 `a.pdf` 时，弹窗显示：
- 原文件预览（pdf iframe）
- “查看提取文本”按钮：请求 `GET /api/file/<cat>/a.pdf.md`

- [ ] **Step 3: 手工自测**
- 上传 png/pdf/docx 各 1 个
- 知识库列表点击预览：png 显示图片，pdf 显示 iframe，docx 提示下载 + “查看提取文本”

- [ ] **Step 4: 提交**

```bash
git add frontend/index.html
git commit -m "feat: preview binary files via raw endpoint"
```

---

### Task 5: 多页面 UI（顶部 Tabs + hash 路由 + 页面拆分）

**Files:**
- Modify: [frontend/index.html](file:///workspace/zhongkao-kb/frontend/index.html)

- [ ] **Step 1: 增加顶部 Tabs**
- Tabs：上传、知识库、搜索、回收站&设置
- 点击切换 `location.hash`（例如 `#/upload`）

- [ ] **Step 2: 把现有 UI 拆成 4 个容器 `<section data-page="upload">...</section>`**
- Upload：上传区 + 上传队列
- Library：知识库结构（stats）+ 批量操作
- Search：全文搜索面板 + 结果列表
- Trash&Settings：回收站 + 个人设置（头像/昵称/密码）

- [ ] **Step 3: 写一个最小 router**

```js
function setPage(name) {
  document.querySelectorAll('[data-page]').forEach(el => el.classList.toggle('hidden', el.dataset.page !== name))
  document.querySelectorAll('[data-tab]').forEach(el => el.classList.toggle('active', el.dataset.tab === name))
}

window.addEventListener('hashchange', () => setPage(parseHash()))
setPage(parseHash())
```

- [ ] **Step 4: 提交**

```bash
git add frontend/index.html
git commit -m "feat: split UI into tabbed pages"
```

---

### Task 6: 视觉与专业度提升（不改技术栈）

**Files:**
- Modify: [frontend/index.html](file:///workspace/zhongkao-kb/frontend/index.html)

- [ ] **Step 1: 统一页面布局**
- 顶部：品牌区（标题+每日名言）+ 用户栏
- 主体：单列内容（减少左右卡片堆叠），关键区域留白更大

- [ ] **Step 2: 统一按钮/输入样式层级**
- 主按钮：蓝色
- 次按钮：灰色
- 危险按钮：红色

- [ ] **Step 3: 加入更明确的信息层级**
- 页面标题（H2）
- 区块标题（H3）
- 空状态插画/提示文本（只用现有 SVG，不引入外链图片）

- [ ] **Step 4: 提交**

```bash
git add frontend/index.html
git commit -m "style: improve layout and visual hierarchy"
```

---

### Task 7: 文档与回归验证

**Files:**
- Modify: [docs/api.md](file:///workspace/zhongkao-kb/docs/api.md)
- Modify: [README.md](file:///workspace/zhongkao-kb/README.md)（可选：说明派生文件规则）

- [ ] **Step 1: 更新 API 文档**
- 增加 `GET /api/file/raw/{category}/{filename}` 说明
- 说明 PDF/DOCX 会产生 `*.pdf.md/*.docx.md`

- [ ] **Step 2: 全量测试**

```bash
pytest -q
```

- [ ] **Step 3: 推送**

```bash
git push origin main
```

---

## 自检（Spec/Plan Consistency）

- 上传：图片不 OCR、不派生；PDF/DOCX 原+文且派生命名为 `*.pdf.md/*.docx.md`
- 预览：二进制能直接预览（图片、pdf）或至少可下载
- UI：拆成 4 个 Tabs 页面，不再全部堆在首页
- OCR：PDF 抽不到文字不 OCR（派生文件写占位文本）

