#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Slate 任务书汉化生成器

用法：
    python gen_slate.py <源 config 目录> [输出目录]

    # 例
    python gen_slate.py "<整合包>/config" "./out"

约定：
  * 源目录下应有 slate/quests/book.json 与 slate/quests/chapters/*.json
  * 译文源默认为 ../config/t*.json，可用环境变量 MC_LOCALIZE_TR_DIR 覆盖
    （按文件名排序自动合并，可任意增减）
  * 只替换 title / subtitle / description 三类文本字段，
    ID、坐标、图标、依赖、奖励、数值一律原样保留
  * 输出：
        <out>/config/slate/quests/book.json
        <out>/config/slate/quests/chapters/*.json
        <out>/config/slate/quests/lang/zh_cn.json
"""
import json, sys, io, os
from collections import OrderedDict
from pathlib import Path

HERE = Path(__file__).resolve().parent          # toolkit/core
TK = HERE.parent                                # toolkit
TR_DIR = Path(os.environ.get('MC_LOCALIZE_TR_DIR', str(TK / 'config')))  # 译文源 t*.json

# 与任务标题不一致的“进度条目”可单独覆盖（键：<章节>/<任务>.<序号>）
TASK_TITLE_OVERRIDE = {
    "island_tier_%d/island_tier_%d.0" % (i, i): "扩张岛屿" for i in range(1, 9)
}


def load(p):
    with io.open(p, "r", encoding="utf-8") as f:
        return json.load(f, object_pairs_hook=OrderedDict)


def dump(obj, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with io.open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
        f.write("\n")


def load_translations():
    """合并 toolkit/config/t*.json"""
    tr = {"book": {}, "groups": {}, "chapters": {}}
    files = sorted(TR_DIR.glob("t*.json"))
    if not files:
        raise SystemExit("!! 找不到译文源: %s/t*.json" % TR_DIR)
    for p in files:
        d = load(p)
        for k in ("book", "groups", "chapters"):
            if k in d and isinstance(d[k], dict):
                tr[k].update(d[k])
    return tr


class Translator:
    def __init__(self, tr):
        self.tr = tr
        self.problems = []
        self.used = 0

    def text(self, path, src):
        node = self.tr
        for k in path:
            if not isinstance(node, dict) or k not in node:
                self.problems.append("缺失译文: " + " / ".join(map(str, path)))
                return src
            node = node[k]
        self.used += 1
        return node

    def desc(self, path, src):
        got = self.text(path, src)
        if isinstance(got, list) and isinstance(src, list) and len(got) != len(src):
            self.problems.append("段落数不一致(%d!=%d): %s"
                                 % (len(got), len(src), " / ".join(map(str, path))))
        return got


def build_book(src_book, T):
    out = OrderedDict()
    for k, v in src_book.items():
        if k == "title":
            out[k] = T.text(["book", "title"], v)
        elif k == "subtitle":
            out[k] = T.text(["book", "subtitle"], v)
        elif k == "groups":
            gs = []
            for g in v:
                g2 = OrderedDict(g)
                g2["title"] = T.text(["groups", g["id"]], g["title"])
                gs.append(g2)
            out[k] = gs
        else:
            out[k] = v
    return out


def build_chapter(src, cname, T):
    out = OrderedDict()
    for k, v in src.items():
        if k == "title":
            out[k] = T.text(["chapters", cname, "title"], v)
        elif k == "subtitle":
            out[k] = T.text(["chapters", cname, "subtitle"], v)
        elif k == "description":
            out[k] = T.desc(["chapters", cname, "description"], v)
        elif k == "quests":
            qs = []
            for q in v:
                qid = q["id"]
                q2 = OrderedDict()
                for qk, qv in q.items():
                    if qk == "title":
                        q2[qk] = T.text(["chapters", cname, "quests", qid, "title"], qv)
                    elif qk == "subtitle":
                        q2[qk] = T.text(["chapters", cname, "quests", qid, "subtitle"], qv)
                    elif qk == "description":
                        q2[qk] = T.desc(["chapters", cname, "quests", qid, "description"], qv)
                    elif qk == "tasks":
                        tasks = []
                        for ti, t in enumerate(qv):
                            t2 = OrderedDict(t)
                            if t2.get("title"):
                                key = "%s/%s.%d" % (cname, qid, ti)
                                if key in TASK_TITLE_OVERRIDE:
                                    t2["title"] = TASK_TITLE_OVERRIDE[key]
                                else:
                                    t2["title"] = T.text(
                                        ["chapters", cname, "quests", qid, "title"],
                                        t2["title"])
                            tasks.append(t2)
                        q2[qk] = tasks
                    else:
                        q2[qk] = qv
                qs.append(q2)
            out[k] = qs
        else:
            out[k] = v
    return out


def build_lang(book, chapters):
    lang = OrderedDict()
    lang["book.title"] = book["title"]
    lang["book.subtitle"] = book["subtitle"]
    for g in book["groups"]:
        lang["group.%s.title" % g["id"]] = g["title"]

    for cname, ch in chapters.items():
        lang["chapter.%s.title" % cname] = ch["title"]
        if ch.get("subtitle"):
            lang["chapter.%s.subtitle" % cname] = ch["subtitle"]
        if ch.get("description"):
            lang["chapter.%s.description" % cname] = ch["description"]
        for q in ch["quests"]:
            base = "quest.%s/%s" % (cname, q["id"])
            for field in ("title", "subtitle", "description"):
                if q.get(field):
                    lang["%s.%s" % (base, field)] = q[field]
            for i, t in enumerate(q.get("tasks", [])):
                if t.get("title"):
                    lang["task.%s/%s.%d.title" % (cname, q["id"], i)] = t["title"]
    return lang


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        raise SystemExit(2)

    src_cfg = Path(sys.argv[1]).resolve()
    out_dir = Path(sys.argv[2]).resolve() if len(sys.argv) > 2 else (TK.parent / "output")

    qdir = src_cfg / "slate" / "quests"
    book_p = qdir / "book.json"
    ch_dir = qdir / "chapters"

    if not book_p.exists():
        raise SystemExit("!! 找不到: %s" % book_p)
    if not ch_dir.is_dir():
        raise SystemExit("!! 找不到章节目录: %s" % ch_dir)

    print("源配置 : %s" % src_cfg)
    print("译文源 : %s" % TR_DIR)
    print("输出   : %s" % out_dir)

    T = Translator(load_translations())

    book = build_book(load(book_p), T)
    chapters = OrderedDict()
    for p in sorted(ch_dir.glob("*.json"), key=lambda x: x.stem):
        chapters[p.stem] = build_chapter(load(p), p.stem, T)

    lang = build_lang(book, chapters)

    base = out_dir / "config" / "slate" / "quests"
    dump(book, base / "book.json")
    for cname, ch in chapters.items():
        dump(ch, base / "chapters" / (cname + ".json"))
    dump(lang, base / "lang" / "zh_cn.json")

    print()
    print("章节 %d | 任务 %d | 已译字段 %d | lang 键 %d"
          % (len(chapters), sum(len(c["quests"]) for c in chapters.values()),
             T.used, len(lang)))

    if T.problems:
        print("\n!! 问题 %d 条:" % len(T.problems))
        for x in T.problems:
            print("   - " + x)
        raise SystemExit(1)

    print("OK 无缺失")


if __name__ == "__main__":
    main()
