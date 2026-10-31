---
name: mc-modpack-localize
license: MIT
description:
  汉化 Minecraft 整合包配置中的玩家可见文本，主要是 Slate 任务书（config/slate/quests），
  并能构建模组 lang 资源包。只替换 title/subtitle/description 等文本字段，ID、坐标、
  奖励、数值一律不动，产物按目录结构输出并自动校验。
  触发场景：用户提到「汉化整合包」「任务书汉化」「Slate 任务书」「config 里的文字翻译」
  「资源包 lang」「zh_cn.json」「modpack localization」「quest book 翻译」，
  或要求把整合包配置里的英文改成中文、检查哪些配置项可汉化。
metadata:
  author: DSH
  version: "1.0.0"
  created: "2026-10-31"
---

# Minecraft 整合包汉化

把整合包里**玩家能看见的文字**汉化，且保证配置文件结构零破坏。

## 核心原则

1. **只改文本，不动结构** —— 只替换 `title` / `subtitle` / `description`，ID、坐标、图标、依赖、奖励、数值原样保留。
2. **翻译与生成解耦** —— 译文写在独立 JSON（`t*.json`），生成器只负责套用。换翻译方式不动代码。
3. **不做无意义的汉化** —— 很多配置里只有数值和内部 ID（如 `oneblock-phases.json` 的 `id` 字段，改了会坏），这些**不要碰**。
4. **产物必须可校验** —— 生成后逐层比对结构，确认无遗漏、无残留英文。

## 第一步：判断能汉化什么

先扫描目标目录，按此表分类：

| 文件类型 | 可汉化 | 说明 |
| --- | --- | --- |
| `slate/quests/book.json` | 是 | 书名、副标题、分组名 |
| `slate/quests/chapters/*.json` | 是 | 章节 + 任务全部文本 |
| `slate/quests/lang/*.json` | 是 | 语言覆盖层，新增 `zh_cn.json` |
| `*.toml`（模组配置） | 否 | 只有数值 / 布尔 / 维度 ID，注释不显示给玩家 |
| `*phases.json` 等数据文件 | 否 | 只有方块 ID 与权重，`id` 是程序内部标识 |
| `*-server.json` | 否 | 纯服务端开关 |

模组的**物品名、HUD、成就名**不在 config 里，它们在 jar 内 `assets/<mod>/lang/en_us.json`，需另做资源包（见 `references/resourcepack.md`）。

## 第二步：Slate 任务书汉化

```powershell
# 1. 准备译文源：<工作目录>\toolkit\config\t1.json ...
#    格式见 references/translation-format.md

# 2. 生成 + 自动校验
python scripts/gen_slate.py "<整合包>\config" "<输出目录>"
python scripts/verify_slate.py "<整合包>\config\slate\quests" "<输出目录>\config\slate\quests"
```

`gen_slate.py` 会产出两套，任选其一安装：

- `book.json` + `chapters/*.json` —— 强制中文，任何语言环境都显示中文
- `lang/zh_cn.json` —— 标准 i18n 覆盖，不改原文，适合多语言服（**推荐**）

## 第三步：校验

`verify_slate.py` 检查四项，全部通过才算完成：

1. **结构等价** —— 键名、键序、数组长度、类型与原文逐层一致
2. **翻译完整** —— 所有文本字段都含中文
3. **lang 覆盖** —— `zh_cn.json` 覆盖参考语言文件的全部键
4. **残留英文** —— 报出未翻译的英文词（专有名词白名单除外）

有 ERR 时退出码为 1，逐条补译文后重跑。

## 关键约束

- **键名必须和原文 `id` 完全一致**，否则报「缺失译文」
- **`description` 是数组，段数必须和原文相同**，否则报「段落数不一致」
- 译文源可任意增减文件（`t1.json`~`tN.json`），按文件名排序自动合并
- 输出统一 UTF-8 无 BOM、2 空格缩进、LF，与原始文件风格一致

## 进阶

- **译文源格式示例** → [assets/example-mini/t1.json](assets/example-mini/t1.json)
- 译文格式与写法约定 → [references/translation-format.md](references/translation-format.md)
- 术语表（维度/模组名/材料名怎么译）→ [references/glossary.md](references/glossary.md)
- 模组 lang 资源包流程 → [references/resourcepack.md](references/resourcepack.md)
- 排障（校验报错怎么修）→ [references/troubleshooting.md](references/troubleshooting.md)
