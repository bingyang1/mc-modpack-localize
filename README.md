# mc-modpack-localize

Minecraft 整合包汉化技能 —— 把任务书等玩家可见文本翻成中文，**不改动任何配置结构**。

面向 AI Agent 的技能（skill）格式，安装到 `~/.dsh/skills/` 或 `~/.claude/skills/` 即可被调用。

## 解决什么问题

整合包里的玩家可见文本分两类，位置完全不同：

| 内容 | 位置 | 手段 |
| --- | --- | --- |
| 任务书文本（Slate） | `config/slate/quests/` | 本技能 |
| 物品名 / HUD / 成就名 | 模组 jar 内 `assets/<mod>/lang/en_us.json` | 资源包（见 references） |

而那些满是数字和内部 ID 的配置（TOML、`*phases.json`）**根本不需要汉化**——
贸然改动 `id` 字段反而会破坏配置。本技能的第一步就是帮你判断"哪些该翻、哪些别碰"。

## 核心设计

**翻译与生成解耦**。译文写在独立 JSON，生成器只负责套用：

```
译文源 (t*.json)  ──┐
                    ├──> gen_slate.py ──> 中文产物 ──> verify_slate.py
原文 (book/chapters)┘                        │              │
                                             └──────────────┘
                                              结构逐层比对
```

好处：

- 换翻译方式（人工 / 机翻 / 大模型）只需替换 JSON，代码一行不动
- 校验器独立，能证明"没漏译、没改结构"

## 快速开始

```powershell
# 1. 准备译文源（格式见 assets/example-mini/t1.json）
#    默认读 ../config/t*.json，可用环境变量覆盖：
$env:MC_LOCALIZE_TR_DIR = ".\my-translations"

# 2. 生成
python scripts/gen_slate.py "<整合包>/config" ".\out"

# 3. 校验（退出码 0 才算过）
python scripts/verify_slate.py "<整合包>/config/slate/quests" ".\out\config\slate\quests"
```

## 产物与安装

生成两套，任选其一：

| 产物 | 效果 | 适用 |
| --- | --- | --- |
| `book.json` + `chapters/*.json` | 强制中文，任何语言都显示中文 | 单人 / 固定中文服 |
| `lang/zh_cn.json` | 标准 i18n 覆盖，不改原文 | 多语言服，**推荐** |

安装时把产物复制到 `<整合包>/config/slate/quests/` 对应位置即可。

## 校验保证

`verify_slate.py` 检查四项：

1. **结构等价** —— 键名、键序、数组长度、类型与原文逐层一致
2. **翻译完整** —— 所有文本字段含中文
3. **lang 覆盖** —— 覆盖参考语言文件全部键
4. **残留英文** —— 报出漏译词（专有名词白名单除外）

## 文档

- [SKILL.md](SKILL.md) —— 技能主指令
- [references/translation-format.md](references/translation-format.md) —— 译文源格式与硬性规则
- [references/glossary.md](references/glossary.md) —— 术语表（维度/模组/材料译名）
- [references/resourcepack.md](references/resourcepack.md) —— 模组文字资源包流程
- [references/troubleshooting.md](references/troubleshooting.md) —— 排障手册

## 关键约束

- 键名必须与原文 `id` **完全一致**，否则报「缺失译文」
- `description` 是数组，**段数必须与原文相同**
- 输出统一 UTF-8 无 BOM / 2 空格 / LF

## 已知边界

- 只处理 Slate 任务书；其他任务系统（FTB Quests 等）需自行适配译文源
- 资源包部分提供流程与排查方法，未附自动化脚本
- 翻译质量取决于译文源本身——本工具不调用任何翻译 API，完全离线

## License

MIT
