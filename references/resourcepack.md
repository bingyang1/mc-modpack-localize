# 模组 lang 资源包

模组的物品名、HUD、界面文字、成就名**不在 config 里**，它们打包在
每个模组 jar 的 `assets/<modid>/lang/en_us.json`。要汉化只能做**资源包**。

## 资源包结构

```
mypack.zip
├── pack.mcmeta
├── pack.png
└── assets/
    └── <modid>/
        └── lang/
            ├── en_us.json      ← 原文（可选，见下方警告）
            └── zh_cn.json      ← 中文
```

`pack.mcmeta`：

```json
{
  "pack": {
    "pack_format": 22,
    "description": "我的整合包 简体中文"
  }
}
```

`pack_format` 对照（NeoForge / Fabric 1.20+）：

| Minecraft 版本 | pack_format |
| --- | --- |
| 1.20.1 | 15 |
| 1.20.4 | 22 |
| 1.21 / 1.21.1 | 34 |
| 1.21.4 | 46 |

不确定时写 `"supported_formats": {"min_inclusive": 1, "max_inclusive": 100}`。

## 关键陷阱：不要覆盖 en_us.json

**资源包只按当前语言查找 lang 文件。** 如果把 `en_us.json` 也写成中文：

- 英文客户端读 `en_us.json` → 看到中文 → **语言切换失效**
- 原始英文丢失，包内无备份

正确做法：**只提供 `zh_cn.json`**，`en_us.json` 保持原样（或者干脆不放）。

检查现成资源包是否犯了这个错：

```python
import zipfile, re, json
CJK = re.compile(r"[\u4e00-\u9fff]")
z = zipfile.ZipFile("resourcepack.zip")
mods = {}
for n in z.namelist():
    m = re.match(r"assets/([^/]+)/lang/(en_us|zh_cn)\.json$", n)
    if m:
        mods.setdefault(m.group(1), {})[m.group(2)] = n

for mod, d in mods.items():
    if "en_us" in d and "zh_cn" in d:
        a = z.read(d["en_us"]); b = z.read(d["zh_cn"])
        if a == b:
            print(f"{mod}: en_us 与 zh_cn 完全相同 —— 英文原文被覆盖了")
```

另一个判据：如果两者**字节数一模一样**，几乎肯定是直接拷贝。

## 从 jar 提取原文

```python
import zipfile, json, glob, os
rows = []
for jar in glob.glob(r"<整合包>\mods\*.jar"):
    try:
        with zipfile.ZipFile(jar) as z:
            for n in z.namelist():
                if n.endswith("/lang/en_us.json"):
                    rows.append((jar, n, z.read(n)))
    except zipfile.BadZipFile:
        pass
```

## 合并多模组的 zh_cn.json

每个模组独立一个 `assets/<modid>/lang/zh_cn.json`，**不要合并成一个大文件**，
键名会互相冲突。

## 安装

```
<整合包>\resourcepacks\<包名>.zip
```

游戏内：选项 → 资源包 → 启用。资源包在语言之上，会覆盖模组同名键。

## 常见问题

| 现象 | 原因 |
| --- | --- |
| 部分文字仍是英文 | 该模组用硬编码字符串，非 lang 键 |
| 数字/变量显示成 `%s` | 译文里漏了占位符，必须原样保留 `%s` `%d` `%1$s` |
| 换语言后失效 | `en_us.json` 被写成中文了 |
| 资源包不生效 | `pack_format` 与版本不匹配，或目录层级多套了一层 |

## 占位符规则

原文 `"quest.progress": "%s / %s"` → 译文必须保留占位符：

```json
{ "quest.progress": "%s / %s" }
```

顺序可调但数量必须一致，否则会抛格式化异常导致整个界面崩溃。
