# 排障

## 生成阶段报错

### `!! 找不到译文源: .../t*.json`

`toolkit/config/` 下没有任何 `t*.json`。确认译文源目录存在；若从别处复制来，
注意不要多套一层目录。

### `!! 找不到: .../slate/quests/book.json`

传入的路径不是 `config` 目录，而是它的上级。正确参数：

```
<整合包>\config          ← 传这个
<整合包>                 ← 不是这个
```

### `缺失译文: chapters/xxx/quests/yyy/title`

原文里存在该章节/任务，但译文里没写。可能原因：

1. 整合包更新后新增了章节或任务 —— 补对应的键
2. 任务 `id` 打错（大小写、下划线、连字符）—— 从原文复制而非手敲

定位方法：

```python
import json, glob
src = json.load(open(r"...\chapters\xxx.json", encoding="utf-8"))
for q in src["quests"]:
    print(q["id"])
```

### `段落数不一致(3!=2): chapters/.../description`

`description` 是数组，译文段数必须和原文一致。要么补一段，要么合并。
不要为了「看着顺眼」擅自增删段落——生成器会拒绝。

## 校验阶段报错

### `[ERR] 未汉化 chapters/.../title: 'Something'`

该字段仍是英文。补译文即可。

### `[ERR] 键集合/顺序不符 book: [...] vs [...]`

译文的键顺序或键名与原文不同。生成器会按原文顺序重建，所以这条通常意味着
**原文被改过**（整合包更新），需要重新确认结构。

### `[ERR] zh_cn 缺少参考语言文件中的键 N 个`

参考语言文件（如 `fr_fr.json`）里有、但你漏了。这些多为 `subtitle`，
按提示补上；若确认原文本来就没有该字段，可忽略此告警。

### `[WARN] zh_cn 新增键 N 个`

通常是补上了参考语言文件遗漏的 subtitle/description，属**正常且有价值**。
只要不是拼写错误的键就不用管。

### `[WARN] 含英文词 ...: '...'`

`verify_slate.py` 的 `ALLOW` 白名单之外出现了英文单词。两种情况：

- 是专有名词（模组名、材料名）→ 加进 `ALLOW`
- 是漏译 → 补译文

「中文（English）」式括注会被自动豁免。

## 游戏内问题

| 现象 | 原因 | 处理 |
| --- | --- | --- |
| 任务书仍英文 | 只放了 `zh_cn.json` 但客户端语言非中文 | 切中文语言，或改用整体覆盖 |
| 任务书排版错乱 | 译文含裸换行符 | 用 `\n` 而非真实换行 |
| 章节显示但任务空白 | 改坏了 `id` 或 `icon` | 从原文重新生成，勿手改产物 |
| 游戏报 JSON 解析错误 | 文件带 BOM 或尾逗号 | 生成器输出无 BOM；手改时注意 |

## 环境问题

### 脚本中文乱码

`cmd.exe` 读 UTF-8 的 `.cmd`/`.bat` 会乱码。**用 PowerShell 调用**
（`run.ps1` 或直接 `python xxx.py`），不要用 `.cmd` 包装。

### `python` 找不到

```powershell
# 用绝对路径调用解释器
<python安装目录>\python.exe scripts\gen_slate.py ...
```

Windows 上也可用 `py` 启动器：`py scripts\gen_slate.py ...`

### 打开产物文件弹「可能有害」

文件或**所在目录**带了来源标记 / Low 完整性标签。目录级问题更常见：

```powershell
icacls "<目录>" | Select-String 'Mandatory'     # 看是否 Low Mandatory Level
icacls "<目录>" /setintegritylevel M /T /C /Q   # 递归修复为 Medium
```

注意：`dir /r` 和 `fsutil file queryEA` 查不到不代表没问题，必须看 icacls。

## 自检清单

生成后逐项确认：

- [ ] `verify_slate.py` 退出码为 0
- [ ] 产出的章节数与原文一致
- [ ] `zh_cn.json` 键数 ≥ 参考语言文件
- [ ] 抽读 2–3 个任务，确认语句通顺、术语统一
- [ ] 确认产物未改动任何 `id` / `icon` / 数值字段
