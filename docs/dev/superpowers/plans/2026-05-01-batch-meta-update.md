# 批量改标签（year/region/type）Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在知识库文件多选场景下，支持批量更新元数据 `.meta.json` 的 year/region/type（空值不修改），提升资料整理效率。

**Architecture:** 后端新增 `POST /api/meta/batch_update`，对 `items` 逐个读取/创建 `${filename}.meta.json` 并合并更新 `patch` 中的非空字段；前端批量操作条增加“批量改标签”弹窗，提交后展示成功/失败汇总并刷新视图。

**Tech Stack:** FastAPI, 原生文件系统（knowledge_base/u_<id>）, 前端原生 JS（frontend/index.html）, pytest。

---

## File Structure

- Modify: `/workspace/zhongkao-kb/main.py`
- Modify: `/workspace/zhongkao-kb/frontend/index.html`
- Modify: `/workspace/zhongkao-kb/docs/api.md`
- Test: `/workspace/zhongkao-kb/tests/test_auth.py`

---

### Task 1: 后端批量改标签 API

**Files:**
- Modify: `/workspace/zhongkao-kb/main.py`
- Test: `/workspace/zhongkao-kb/tests/test_auth.py`

- [ ] **Step 1: 写失败测试（meta 不存在会创建 + 空值不覆盖）**

在 `tests/test_auth.py` 追加测试：

```python
def test_meta_batch_update_creates_and_merges(tmp_path: Path, monkeypatch):
    db_path = tmp_path / "app.db"
    monkeypatch.setenv("APP_DB_PATH", str(db_path))
    monkeypatch.setenv("INVITE_CODE", "abc123")
    client = TestClient(main.app)

    client.post("/api/auth/register", json={"invite_code": "abc123", "username": "u1", "password": "pw"})
    token = client.post("/api/auth/login", json={"username": "u1", "password": "pw"}).json()["token"]

    kb_root = tmp_path / "kb"
    kb_root.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(main, "KNOWLEDGE_BASE_DIR", kb_root)

    cat_dir = kb_root / "u_1" / "语文"
    cat_dir.mkdir(parents=True, exist_ok=True)
    (cat_dir / "a.md").write_text("x", encoding="utf-8")

    r = client.post(
        "/api/meta/batch_update",
        json={
            "items": [{"category": "语文", "filename": "a.md"}],
            "patch": {"year": "2024", "region": "", "type": "真题"},
        },
        headers={"Authorization": "Bearer " + token},
    )
    assert r.status_code == 200
    res = (r.json().get("results") or [])[0]
    assert res["ok"] is True

    meta_path = cat_dir / "a.md.meta.json"
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    assert meta["year"] == "2024"
    assert meta["type"] == "真题"
    assert "region" not in meta

    r2 = client.post(
        "/api/meta/batch_update",
        json={
            "items": [{"category": "语文", "filename": "a.md"}],
            "patch": {"region": "北京"},
        },
        headers={"Authorization": "Bearer " + token},
    )
    assert r2.status_code == 200
    meta2 = json.loads(meta_path.read_text(encoding="utf-8"))
    assert meta2["year"] == "2024"
    assert meta2["type"] == "真题"
    assert meta2["region"] == "北京"
```

- [ ] **Step 2: 运行测试确认失败**

Run: `pytest -q tests/test_auth.py::test_meta_batch_update_creates_and_merges -q`  
Expected: FAIL（`/api/meta/batch_update` 未实现或 404）。

- [ ] **Step 3: 实现 /api/meta/batch_update**

在 `main.py` 增加路由：

```python
@app.post("/api/meta/batch_update")
async def batch_update_meta(payload: dict = Body(...), current_user: auth.User = Depends(auth.get_current_user)):
    items = payload.get("items")
    patch = payload.get("patch") or {}
    if not isinstance(items, list) or not items:
        raise HTTPException(status_code=400, detail="缺少 items")
    if not isinstance(patch, dict) or not patch:
        raise HTTPException(status_code=400, detail="缺少 patch")

    allowed = {"year", "region", "type"}
    clean_patch = {}
    for k in allowed:
        v = patch.get(k)
        if v is None:
            continue
        if not isinstance(v, str):
            v = str(v)
        v = v.strip()
        if v:
            clean_patch[k] = v
    if not clean_patch:
        raise HTTPException(status_code=400, detail="patch 不能为空")

    kb_dir = user_kb_dir(current_user.id)
    results = []
    for it in items[:500]:
        category = (it.get("category") or "").strip()
        filename = (it.get("filename") or "").strip()
        try:
            validate_path_segment(category, "category")
            validate_path_segment(filename, "filename")
            if category.startswith("_"):
                raise HTTPException(status_code=400, detail="不支持修改系统目录")

            file_path = kb_dir / category / filename
            if not file_path.exists() or not file_path.is_file():
                raise HTTPException(status_code=404, detail="文件不存在")

            meta_path = file_path.with_name(file_path.name + ".meta.json")
            if meta_path.exists():
                try:
                    meta = json.loads(meta_path.read_text(encoding="utf-8", errors="ignore") or "{}")
                except Exception:
                    meta = {}
                if not isinstance(meta, dict):
                    meta = {}
            else:
                meta = {}

            meta.update(clean_patch)
            meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
            results.append({"ok": True, "category": category, "filename": filename, "has_meta": True})
        except HTTPException as he:
            results.append({"ok": False, "category": category, "filename": filename, "error": he.detail})
        except Exception as e:
            results.append({"ok": False, "category": category, "filename": filename, "error": str(e)})
    return {"status": "success", "results": results}
```

- [ ] **Step 4: 运行测试确认通过**

Run: `pytest -q tests/test_auth.py::test_meta_batch_update_creates_and_merges -q`  
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add main.py tests/test_auth.py
git commit -m "feat: batch update meta tags"
```

---

### Task 2: 前端批量改标签弹窗 + 调用接口

**Files:**
- Modify: `/workspace/zhongkao-kb/frontend/index.html`

- [ ] **Step 1: 在批量操作条加入“批量改标签”入口按钮**

在 bulk bar 增加按钮（保持现有 Tailwind 风格）：

```html
<button id="bulkMetaBtn" class="px-3 py-2 rounded-lg bg-emerald-600 text-white text-sm hover:bg-emerald-700">批量改标签</button>
```

- [ ] **Step 2: 增加 meta 弹窗 DOM**

新增 modal：

```html
<div id="meta-modal" class="fixed inset-0 z-50 hidden bg-gray-900 bg-opacity-50 flex items-center justify-center p-4">
  <div class="bg-white rounded-xl shadow-lg w-full max-w-md">
    <div class="p-4 border-b border-gray-100 flex items-center justify-between">
      <div class="text-lg font-semibold text-gray-800">批量改标签</div>
      <button id="closeMeta" class="text-gray-400 hover:text-gray-600 focus:outline-none">…</button>
    </div>
    <div class="p-4 space-y-3">
      <div class="text-xs text-gray-500">留空则不修改该字段</div>
      <input id="metaYearInput" class="w-full px-3 py-2 border rounded-lg text-sm" placeholder="年份（例如 2024）">
      <input id="metaRegionInput" class="w-full px-3 py-2 border rounded-lg text-sm" placeholder="地区（例如 北京）">
      <input id="metaTypeInput" class="w-full px-3 py-2 border rounded-lg text-sm" placeholder="类型（例如 真题/模拟/专题）">
      <div class="flex justify-end gap-2">
        <button id="metaApplyBtn" class="px-4 py-2 rounded-lg bg-emerald-600 text-white text-sm hover:bg-emerald-700">应用到已选文件</button>
      </div>
      <div id="meta-msg" class="text-sm"></div>
    </div>
  </div>
</div>
```

- [ ] **Step 3: JS 逻辑：打开/关闭弹窗 + 提交批量请求**

实现：

```js
function showMetaModal() { metaModal.classList.remove('hidden') }
function hideMetaModal() { metaModal.classList.add('hidden'); metaMsg.textContent = '' }

bulkMetaBtn.addEventListener('click', () => {
  if (!selectedKb.size) return
  showMetaModal()
})

metaApplyBtn.addEventListener('click', async () => {
  if (!selectedKb.size) return
  const patch = {}
  const year = (metaYearInput.value || '').trim()
  const region = (metaRegionInput.value || '').trim()
  const type = (metaTypeInput.value || '').trim()
  if (year) patch.year = year
  if (region) patch.region = region
  if (type) patch.type = type
  if (!Object.keys(patch).length) { metaMsg.textContent = '请至少填写一个字段'; metaMsg.className = 'text-sm text-red-700'; return }

  const items = Array.from(selectedKb).map(k => {
    const parts = k.split('::')
    return { category: parts[0] || '', filename: parts.slice(1).join('::') || '' }
  })

  const r = await apiFetch('/api/meta/batch_update', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ items, patch }),
  })
  const data = await r.json().catch(() => ({}))
  if (!r.ok || data.status !== 'success') { metaMsg.textContent = (data && data.detail) || '批量更新失败'; metaMsg.className = 'text-sm text-red-700'; return }

  const results = Array.isArray(data.results) ? data.results : []
  const okCount = results.filter(x => x && x.ok).length
  const failCount = results.length - okCount
  metaMsg.textContent = `更新完成：成功 ${okCount}，失败 ${failCount}`
  metaMsg.className = failCount ? 'text-sm text-amber-700' : 'text-sm text-green-700'
  if (filterActive) await applyFilters()
  else await loadStats()
})
```

- [ ] **Step 4: 手动自测**

本地启动后：

1. 勾选多个文件
2. 批量改标签：填写 year=2024，region 留空
3. 刷新筛选项/筛选结果：year 选项可出现 2024（如 options 由后端动态扫描）

- [ ] **Step 5: Commit**

```bash
git add frontend/index.html
git commit -m "feat: batch edit meta tags in UI"
```

---

### Task 3: API 文档更新

**Files:**
- Modify: `/workspace/zhongkao-kb/docs/api.md`

- [ ] **Step 1: 增加接口条目**

```md
- `POST /api/meta/batch_update`：批量更新元数据标签（year/region/type，空值不修改）
```

- [ ] **Step 2: Commit**

```bash
git add docs/api.md
git commit -m "docs: add meta batch update api"
```

---

## Self-Review

- Spec coverage:
  - API：Task 1 覆盖
  - 前端入口 + 弹窗 + 汇总提示：Task 2 覆盖
  - 空值不修改、meta 不存在创建：Task 1/测试覆盖
  - 文档：Task 3 覆盖
- Placeholder scan: 无 TBD/TODO
- Type consistency: `items[{category,filename}]` 与现有多选 key 解析一致；`patch` 为 dict 且仅含非空字段

---

## Execution Handoff

Plan complete and saved to `/workspace/zhongkao-kb/docs/dev/superpowers/plans/2026-05-01-batch-meta-update.md`.

Two execution options:

1. Subagent-Driven (recommended) — 用 superpowers:subagent-driven-development 按任务分发并逐步 review
2. Inline Execution — 用 superpowers:executing-plans 在本会话中逐步执行

Which approach?

