# 标签筛选 v1（筛选面板）设计

## 背景与目标

当前系统已有上传、分类、预览、删除、全文搜索能力；但缺少“按标签/元数据筛选”能力，导致资料较多时定位困难。需要新增“标签筛选”能力，支持按以下字段组合筛选，并仍按学科分组展示结果：

- 元数据：`year` / `region` / `type`（来源于 `.meta.json`）
- 基础字段：`category`（学科目录）/ `ext`（文件后缀）

目标：

- 前端新增独立“筛选面板”卡片（在“知识库结构”卡片内）
- 支持组合筛选与一键清除
- 筛选结果按学科分组展示，并保留“预览/删除”交互

非目标（v1 不做）：

- 自由标签（自定义 tag 编辑/保存）
- 与全文搜索深度融合（先筛后搜）
- 复杂排序（命中次数、相关性等）

## API 设计

### 1) `GET /api/filters/options`

用途：提供前端下拉框候选项。

返回：

```json
{
  "categories": ["语文", "数学"],
  "years": ["2022", "2023"],
  "regions": ["北京", "上海"],
  "types": ["中考真题", "模拟卷"],
  "exts": ["md", "txt"]
}
```

规则：

- `categories`：来自 `knowledge_base/*` 的目录名
- `exts`：来自目录内实际文件后缀（排除 `.meta.json`）
- `years/regions/types`：扫描 `*.meta.json` 汇总，字段缺失则跳过

### 2) `GET /api/filter`

Query 参数（均可选，可组合）：

- `category`：学科目录名
- `year`：年份
- `region`：地区
- `type`：类型
- `ext`：后缀（允许 `md` 或 `.md`，后端统一规范化）

返回：与 `/api/stats` 同结构，按学科分组的文件列表：

```json
{
  "语文": [{"name": "语文.md", "has_meta": true}],
  "数学": [{"name": "函数.md", "has_meta": false}]
}
```

匹配规则：

- `category`：只筛该目录
- `ext`：按文件后缀匹配（不含点的标准化形式）
- `year/region/type`：
  - 若文件存在 `.meta.json`，读取并匹配对应字段
  - 若文件无 `.meta.json`，则仅能通过 `category/ext` 命中；若用户指定了 `year/region/type` 则该文件视为不匹配

性能与边界：

- 只读取 `.meta.json` 与文件名，不读取全文内容
- 过滤时排除 `.meta.json` 自身

## 前端交互（Cloudflare Pages）

在“知识库结构”卡片内新增“筛选面板”：

- 下拉：学科 / 年份 / 地区 / 类型 / 后缀
- 按钮：应用筛选 / 清除筛选

流程：

1. 页面加载或刷新目录时，请求 `/api/filters/options` 填充下拉候选
2. 点击“应用筛选”调用 `/api/filter`，用返回结果渲染 `kb-stats`
3. 点击“清除筛选”恢复原 `loadStats()` 逻辑

