# 题目拆分 v1（文本 → JSON）设计

## 背景与目标

当前知识库以文件为最小单位（Markdown/文本），不利于按“小题粒度”复习与检索。需要新增“题目拆分”能力：从知识库中已有的 `.md/.txt` 文本文件中识别题号与选项，生成结构化 JSON，供后续错题本、练习模式使用。

目标：

- 从知识库内的文本文件拆题，生成 `*.questions.json` 落盘
- v1 先保证：题号（id）、题干（stem）、选项（options）稳定产出
- 前端在文件列表提供“拆题”按钮，并在弹窗预览拆题结果

非目标：

- 直接对扫描 PDF/图片进行结构化拆题（v1 不做）
- 自动识别答案/解析（v1 为空字符串）
- 复杂题型（填空/简答/作文）精细结构化（v1 仅粗拆为 stem）

## 数据结构

输出文件：`knowledge_base/{category}/{stem}.questions.json`（与源文件同目录）

```json
{
  "version": 1,
  "source": {
    "category": "语文",
    "filename": "语文.md",
    "generated_at": "2026-04-29T12:00:00+08:00"
  },
  "items": [
    {
      "id": "1",
      "stem": "……题干……",
      "options": ["A.…", "B.…", "C.…", "D.…"],
      "answer": "",
      "analysis": "",
      "tags": []
    }
  ]
}
```

## 拆分规则（v1）

题号识别（行首优先）：

- `1.` / `1、` / `1)` / `（1）`
- 允许前导空白

选择题选项识别：

- `A.` `B.` `C.` `D.`（兼容 `A、`、全角 `Ａ`）
- 若识别到 A/B/C/D，则将题干与选项分离
- 若未识别到选项，则 `options=[]`，整段作为 `stem`

大题标题（可选）：

- `一、二、三、…` 仅作为 tags（v1 可留空或后续增强）

## API 设计

### `POST /api/split`

入参（JSON）：

```json
{ "category": "语文", "filename": "语文.md" }
```

行为：

- 读取源文件文本（仅允许 `.md/.txt/.csv`）
- 拆题生成 JSON 并写入 `*.questions.json`

返回：

```json
{
  "status": "success",
  "source": {"category":"语文","filename":"语文.md"},
  "output": {"filename":"语文.questions.json","path":"knowledge_base/语文/语文.questions.json"},
  "count": 22
}
```

### `GET /api/questions/{category}/{filename}`

- `filename` 指 `*.questions.json`
- 返回 JSON 文件内容

## 前端交互

- 在“知识库结构”列表每个文件 hover 操作区新增按钮：`拆题`
- 点击后：
  1) 调用 `POST /api/split`
  2) 再调用 `GET /api/questions/...` 获取结果
  3) 复用预览弹窗：展示前 N 题（题号、题干、选项），并提供 JSON 下载链接

