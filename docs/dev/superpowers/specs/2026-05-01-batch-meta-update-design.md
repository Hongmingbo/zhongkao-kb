# 批量改标签（year/region/type）设计（v1）

## 背景

当前知识库支持按 `.meta.json` 存储元数据，并提供筛选面板与按条件筛选能力。高频整理场景下，需要对多份资料一次性补齐或修正标签（年份/地区/类型），避免逐个文件修改。

## 目标

- 在前端支持多选文件后批量设置标签
- 支持 `year` / `region` / `type` 三个字段
- 空值不修改（只覆盖用户填写的字段）
- `.meta.json` 不存在则创建
- 返回逐项结果，允许部分成功

## 非目标

- 自定义标签体系（多标签、任意字段）
- 自动从文件内容推断标签
- 回收站条目批量改标签

## 数据模型

文件元数据仍采用 `${filename}.meta.json`：

```json
{
  "year": "2024",
  "region": "北京",
  "type": "真题"
}
```

空字符串不写入；服务端仅合并更新 patch 中出现且非空的字段。

## API 设计

### POST /api/meta/batch_update

Request:

```json
{
  "items": [
    { "category": "语文", "filename": "a.md" },
    { "category": "数学", "filename": "b.md" }
  ],
  "patch": { "year": "2024", "region": "北京", "type": "真题" }
}
```

Rules:

- `items` 必填，最多 500
- `patch` 至少包含一个非空字段；空值字段会被忽略（不修改）
- 不允许操作以下划线开头的目录（如 `_profile`、`_trash`）
- 仅更新当前用户知识库目录下的文件

Response:

```json
{
  "status": "success",
  "results": [
    { "ok": true, "category": "语文", "filename": "a.md", "has_meta": true },
    { "ok": false, "category": "数学", "filename": "b.md", "error": "文件不存在" }
  ]
}
```

## 前端交互

### 入口

- 复用现有知识库多选能力（selectedKb）
- 批量操作条增加按钮：`批量改标签`

### 弹窗

- 输入框/下拉框：
  - year（输入或下拉）
  - region（输入或下拉）
  - type（输入或下拉）
- 提示：留空则不修改
- 提交后展示汇总：成功 X / 失败 Y（失败显示前若干条原因）

### 选项来源

- 默认使用现有 `/api/filters/options` 的 `years/regions/types` 作为建议选项
- 允许用户手动输入新值

## 安全与校验

- 路径片段校验：禁止 `..`、`/`、`\`
- 禁止写入系统目录（以 `_` 开头）
- 不输出用户的敏感信息到日志

## 测试策略

- 批量更新：
  - meta 不存在时创建
  - 只更新 patch 中非空字段（空字段不覆盖原值）
  - 部分成功返回
- 与筛选联动：更新后 filter/options 可反映新增值（非强制，取决于实现是否动态扫描）

