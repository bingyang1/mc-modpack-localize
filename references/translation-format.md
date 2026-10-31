# 译文源格式

译文放在 `toolkit/config/t*.json`，结构必须与原文对齐。可任意拆成多个文件
（`t1.json` ~ `tN.json`），生成时按文件名排序自动合并。

## 完整结构

```jsonc
{
  "book": {
    "title": "维度混沌",
    "subtitle": "在虚空中求生，勇闯轮转的维度之门，扩张你的岛屿。"
  },
  "groups": {
    "skyblock_core": "故事：虚空与维度之门",
    "expeditions": "故事：远征",
    "mastery": "故事：精通",
    "island_expansion": "岛屿扩张"
  },
  "chapters": {
    "<章节文件名，不含 .json>": {
      "title": "...",
      "subtitle": "...",
      "description": ["段落1", "段落2"],
      "quests": {
        "<任务 id>": {
          "title": "...",
          "subtitle": "...",
          "description": ["..."]
        }
      }
    }
  }
}
```

## 与原文的对应关系

原文 `chapters/island_tier_1.json`：

```jsonc
{
  "title": "Expansion 1 - First Steps",
  "quests": [
    { "id": "t1_first_logs", "title": "First Logs", "subtitle": "Main objective" }
  ]
}
```

译文写成：

```jsonc
{
  "chapters": {
    "island_tier_1": {
      "title": "扩张 1 · 初次启程",
      "quests": {
        "t1_first_logs": {
          "title": "最初的木头",
          "subtitle": "主线目标"
        }
      }
    }
  }
}
```

要点：

- 章节键 = 文件名（`island_tier_1.json` → `"island_tier_1"`）
- 任务键 = 该任务的 `id` 字段，**不是**数组下标
- **原文没有 `subtitle` 的任务，译文也不要写**，否则无用键会残留

## 硬性规则

| 规则 | 违反后果 |
| --- | --- |
| 键名与原文 `id` 完全一致（含大小写、下划线） | 报「缺失译文」并退出 |
| `description` 数组段数与原文相同 | 报「段落数不一致」 |
| 文本字段非空 | 空串会被判定未翻译 |
| 纯 ASCII 文本必须含中文 | 校验报未汉化 |

## 特例：进度条目

任务条目（`tasks`）的 `title` 通常等同于任务标题，生成器会自动复用。
但少数任务两者不同，需要在 `gen_slate.py` 的 `TASK_TITLE_OVERRIDE`
里单独指定：

```python
TASK_TITLE_OVERRIDE = {
    "island_tier_1/island_tier_1.0": "扩张岛屿",
    # 键格式：<章节>/<任务id>.<task序号>
}
```

如何发现这类差异：

```python
# 逐个任务比较 tasks[i].title 与 quest.title
for q in chapter["quests"]:
    for i, t in enumerate(q.get("tasks", [])):
        if t.get("title") != q.get("title"):
            print(f"{chapter}/{q['id']}.{i}: {q['title']} vs {t['title']}")
```

## 编写风格建议

- 面向玩家，用**祈使句 + 第二人称**：「敲碎 OneBlock，获取最初的原木」
- 机制解释用短句，避免从句套从句
- 数字、坐标、物品数量保持原样，不要换算
- 提示类文本用「小提示：」开头，与正文区分
- 段落长度控制在一屏内（约 60–80 字），过长拆段
