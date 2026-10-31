# 术语表

汉化 Minecraft 整合包时保持一致性的术语约定。新增内容请追加到对应分类。

## 维度名（用官方简体中文译名）

| 英文 | 中文 | 备注 |
| --- | --- | --- |
| Overworld | 主世界 | |
| the Nether | 下界 | 不译「地狱」 |
| the End | 末地 | 不译「终界」 |
| Twilight Forest | 暮色森林 | |
| Aether | 天境 | 不译「以太」 |
| Undergarden | 深暗之境 | |
| Deeper Darker / Otherside | 幽邃黑暗 / 彼界 | |

## 模组名（保留英文，不音译）

Create、Mekanism、Powah、Ars Nouveau、Iron's Spells、Mystical Agriculture、
Ex Deorum、Slate、JourneyMap、Xaero's Minimap、Apotheosis、Twilight Forest。

> 原则：模组名是品牌，音译会让玩家搜不到资料。首次出现可加括注。

## 材料 / 物品名

| 英文 | 中文 | 说明 |
| --- | --- | --- |
| Inferium | Inferium 精华 | 神秘农业基础材料，保留原名 |
| Prudentium | Prudentium | |
| Tertium | Tertium | |
| Imperium | Imperium | |
| Supremium | Supremium | |
| Cloggrum | 克洛格鲁姆（Cloggrum） | 深暗之境金属，首次括注 |
| Zanite | 赞尼特（Zanite） | 天境宝石，首次括注 |
| Ironwood | 铁木 | |
| Source | 魔源 | Ars Nouveau 的能量 |
| Prosperity Shard | 繁荣碎片 | |

## Slate 系统术语（本整合包）

| 英文 | 中文 | 说明 |
| --- | --- | --- |
| OneBlock | OneBlock | 保留原名，是玩法核心概念 |
| gateway | 维度之门 | |
| Return Gateway | 返回之门 | |
| Dimensional Fracture | 维度裂隙 | |
| Dormant Fracture | 休眠裂隙 | |
| Dimensional Fragment | 维度碎片 | |
| Rift Compass | 裂隙罗盘 | |
| Rift Guardian | 裂隙守卫 | |
| cycle | 周期 | 「每 15 分钟一个周期」 |
| expedition | 远征 | |
| island tier | 岛屿等级 | |
| border radius | 边界半径 | |

## 常见 UI 词

| 英文 | 中文 |
| --- | --- |
| Main objective | 主线目标 |
| Optional | 可选 |
| Chapter | 第 N 章 |
| Expansion | 扩张 N |
| Side chapter | 支线 |
| Story | 故事 |
| Expected time | 预计用时 |
| Tip | 小提示 |

## 章节标题格式

- 主线：`第一章 · 虚空`（中文数字 + 间隔号）
- 支线：`支线 · 迷失于门后`
- 扩张：`扩张 1 · 初次启程`（阿拉伯数字）
- 数值范围用 `→`：`边界半径 16 → 24`

## 时间与单位

- 「15 分钟」不写「十五分钟」（可读性）
- 区间用 `–` 或 `-`：`15–30 分钟`
- 小时：`2–3 小时`

## 校验白名单

`verify_slate.py` 的 `ALLOW` 集合列出允许保留的英文词。新增模组名或
材料名时需同步追加，否则会报英文残留：

```python
ALLOW = {
    "OneBlock", "Ars", "Nouveau", "Iron's", "Spells", "Create",
    "Mekanism", "Powah", "Mystical", "Agriculture", ...
}
```

「中文（English）」形式的括注会自动被豁免，无需加白名单。
