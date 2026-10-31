#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
校验汉化产物：结构等价 / 残留英文 / lang 键覆盖。

用法：
    python verify_slate.py <源 slate/quests 目录> [汉化产物 slate/quests 目录]

    # 例
    python verify_slate.py "<整合包>/config/slate/quests" "./out/config/slate/quests"

不传第二个参数时，默认取 ../output/config/slate/quests。
"""
import json, io, re, sys
from pathlib import Path

TEXT_KEYS = {"title", "subtitle", "description"}
CJK = re.compile(r"[\u4e00-\u9fff]")
# “中文（English）”式的专名括注是允许的
PAREN_ENG = re.compile(r"[（(][^）)]*[A-Za-z][^）)]*[）)]")
LATIN_WORD = re.compile(r"[A-Za-z]{2,}")
# 允许保留的专有名词 / 模组术语
ALLOW = {
    "OneBlock", "Ars", "Nouveau", "Iron's", "Spells", "Create", "Mekanism", "Powah",
    "Mystical", "Agriculture", "Ex", "Deorum", "Inferium", "Prudentium", "Tertium",
    "Imperium", "Supremium", "Zanite", "Cloggrum", "Powah's", "PvP", "XP", "HUD",
    "Slate", "Rift", "Compass", "Wilden", "Naga", "OS", "TPS", "MSPT",
}


def load(p):
    with io.open(p, "r", encoding="utf-8") as f:
        return json.load(f, object_pairs_hook=dict)


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        raise SystemExit(2)

    SRC = Path(sys.argv[1]).resolve()
    DST = (Path(sys.argv[2]).resolve() if len(sys.argv) > 2
           else (Path(__file__).resolve().parent.parent.parent / "output" / "config" / "slate" / "quests"))

    errs, warns = [], []

    def walk(a, b, path):
        """a=原文 b=译文，比较结构（键名与类型），并收集仍需汉化的文本"""
        if type(a) is not type(b):
            errs.append("类型不符 %s: %s vs %s" % (path, type(a), type(b)))
            return
        if isinstance(a, dict):
            if list(a.keys()) != list(b.keys()):
                errs.append("键集合/顺序不符 %s: %s vs %s" % (path, list(a.keys()), list(b.keys())))
                return
            for k in a:
                walk(a[k], b[k], path + "/" + k)
        elif isinstance(a, list):
            if len(a) != len(b):
                errs.append("数组长度不符 %s: %d vs %d" % (path, len(a), len(b)))
                return
            for i, (x, y) in enumerate(zip(a, b)):
                walk(x, y, path + "[%d]" % i)
        elif isinstance(a, str):
            key = path.rsplit("/", 1)[-1]
            if key in TEXT_KEYS and a.strip():
                if not CJK.search(b):
                    errs.append("未汉化 %s: %r" % (path, b))
                for w in LATIN_WORD.findall(PAREN_ENG.sub("", b)):
                    if w in ALLOW:
                        continue
                    warns.append("含英文词 %s: %r -> %r" % (path, w, b))

    # 1) book.json
    sb = SRC / "book.json"
    db = DST / "book.json"
    if sb.exists() and db.exists():
        walk(load(sb), load(db), "book")
    else:
        errs.append("book.json 缺失（源:%s 产物:%s）" % (sb.exists(), db.exists()))

    # 2) chapters
    srcs = {p.stem: p for p in (SRC / "chapters").glob("*.json")}
    dsts = {p.stem: p for p in (DST / "chapters").glob("*.json")}
    if set(srcs) != set(dsts):
        errs.append("章节文件不一致: 缺 %s / 多 %s"
                    % (sorted(set(srcs) - set(dsts)), sorted(set(dsts) - set(srcs))))
    for name in sorted(srcs):
        if name in dsts:
            walk(load(srcs[name]), load(dsts[name]), "chapters/" + name)

    # 3) lang 键覆盖：应覆盖源包已有语言文件的全部键
    frs = sorted((SRC / "lang").glob("*.json")) if (SRC / "lang").is_dir() else []
    zhp = DST / "lang" / "zh_cn.json"
    if not zhp.exists():
        errs.append("缺少 zh_cn.json: %s" % zhp)
        fr = {}
        zh = {}
    else:
        zh = load(zhp)
        fr = load(frs[0]) if frs else {}
        miss = [k for k in fr if k not in zh]
        extra = [k for k in zh if k not in fr]
        if miss:
            errs.append("zh_cn 缺少参考语言文件中的键 %d 个: %s" % (len(miss), miss[:10]))
        if extra:
            warns.append("zh_cn 新增键 %d 个: %s" % (len(extra), extra[:10]))

    for k, v in zh.items():
        if isinstance(v, str):
            if v.strip() and not CJK.search(v):
                errs.append("lang 未汉化 %s: %r" % (k, v))
        elif isinstance(v, list):
            for i, s in enumerate(v):
                if s.strip() and not CJK.search(s):
                    errs.append("lang 未汉化 %s[%d]: %r" % (k, i, s))

    print("原文章节 %d / 译文章节 %d" % (len(srcs), len(dsts)))
    print("lang: 参考 %d 键 / zh_cn %d 键" % (len(fr), len(zh)))
    print("错误 %d 条；英文残留提示 %d 条" % (len(errs), len(warns)))
    for e in errs:
        print("  [ERR] " + e)
    seen = set()
    for w in warns:
        if w in seen:
            continue
        seen.add(w)
        print("  [WARN] " + w)

    raise SystemExit(1 if errs else 0)


if __name__ == "__main__":
    main()
