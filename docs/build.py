#!/usr/bin/env python3
"""从 _src/ 下的正文片段生成 docs/ 里的完整 HTML 页面。

用法：
    python docs/build.py            # 全部重建
    python docs/build.py ch03       # 只重建某一章

正文片段（_src/*.html）只写 <main> 里的内容。页面外壳由本脚本统一生成，
所以改导航只需要改这里一处：

  · 左侧栏：品牌、代码语言开关、按「部分」分组的章节列表（来自 CHAPTERS）
  · 本章目录：正文里的 <div id="chapter-toc"></div> 会被替换成
    由 <h2 id="..."> 抽取的目录
  · 图号：每个 <figcaption> 前自动加「图 N-k」，增删图不用手动改号
  · 上一章 / 下一章
  · 首页：<div id="toc-grid"></div> 替换成全部章节卡片
"""

import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).parent
SRC = ROOT / "_src"
SITE = "Learning LangChain 中文精读"

# (文件名, 章号, 侧栏短标题, 页面完整标题, 一句话简介, 所属部分——只写在该部分的第一章上)
CHAPTERS = [
    ("ch01", 1, "LLM 基础与构建块", "LLM 基础与 LangChain 构建块",
     "聊天模型、提示模板、结构化输出，以及拼装零件的两种方式", "第一部分 · 知识"),
    ("ch02", 2, "RAG 上篇：建索引", "RAG 上篇：为你的数据建索引",
     "嵌入到底是什么；加载、切分、入库，以及索引优化三招", None),
    ("ch03", 3, "RAG 下篇：对话", "RAG 下篇：与你的数据对话",
     "查询改写、多查询、RAG-Fusion、HyDE、路由与文本转 SQL", None),
    ("ch04", 4, "加记忆", "用 LangGraph 给机器人加记忆",
     "状态、节点、边；检查点与线程；聊天记录的三种整理术", "第二部分 · 记忆"),
    ("ch05", 5, "认知架构", "LangGraph 认知架构",
     "自主性阶梯：单次调用、链、路由器——先想清楚再动手", "第三部分 · 行动"),
    ("ch06", 6, "Agent 架构", "Agent 架构",
     "计划—执行循环、ToolNode、强制先调工具、工具检索", None),
    ("ch07", 7, "反思与多智能体", "Agent 进阶：反思与多智能体",
     "生成—批评循环、子图的两种接法、Supervisor 架构", None),
    ("ch08", 8, "实用模式", "榨干 LLM 的实用模式",
     "结构化输出、流式输出、人在环路与并发输入", "第四部分 · 可信"),
    ("ch09", 9, "部署", "部署：送上生产",
     "LangGraph Platform 的数据模型、本地调试、上线与安全清单", None),
    ("ch10", 10, "测试与评估", "测试：评估、监控与持续改进",
     "自纠正 RAG、数据集、三类评估器、Agent 的三层评估", None),
    ("ch11", 11, "用 LLM 做产品", "用 LLM 做产品",
     "聊天助手、协同编辑、环境计算：三种 LLM 原生交互范式", "第五部分 · 产品"),
]

HEAD = """<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<script>try{{const t=localStorage.getItem('llc-doc-theme');if(t)document.documentElement.dataset.theme=t}}catch{{}}</script>
<link rel="stylesheet" href="assets/course.css">
</head>
<body data-chapter="{n}">
"""

# 图里的箭头。marker 内容不会从引用它的元素继承颜色，所以直接用 CSS 变量上色。
MARKERS = """<svg width="0" height="0" style="position:absolute" aria-hidden="true"><defs>
<marker id="ar" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--fg-faint)"/></marker>
<marker id="ar-a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--accent)"/></marker>
</defs></svg>
"""

FOOT = """</main>
</div>
<script src="assets/course.js"></script>
</body>
</html>
"""


def sidebar(cur):
    out = [
        '<aside id="sidebar">',
        '<a class="brand" href="index.html"><span class="mark" aria-hidden="true">&#129436;</span>'
        '<span>LangChain 中文精读<small>《Learning LangChain》图解教程</small></span></a>',
        '<div class="langswitch" role="group" aria-label="示例代码语言"><span>代码</span>'
        '<button type="button" data-lang-btn="py" aria-pressed="true">Python</button>'
        '<button type="button" data-lang-btn="js" aria-pressed="false">JavaScript</button></div>',
    ]
    for slug, n, short, _full, _desc, part in CHAPTERS:
        if part:
            out.append(f'<div class="part">{part}</div>')
        if n == cur:
            out.append(f'<a class="ch active" aria-current="page" href="{slug}.html">'
                       f'<span class="n">{n}</span><span>{short}</span></a>')
        else:
            out.append(f'<a class="ch" href="{slug}.html"><span class="n">{n}</span><span>{short}</span></a>')
    out.append('</aside>')
    return "\n".join(out) + "\n"


def chapter_toc(body):
    items = [(m.group(1), re.sub(r"<[^>]+>", "", m.group(2)).strip())
             for m in re.finditer(r'<h2 id="([^"]+)">(.*?)</h2>', body, re.S)]
    if len(items) < 3:
        return ""
    lis = "\n".join(f'    <li><a href="#{i}">{t}</a></li>' for i, t in items)
    return (f'<nav class="toc" aria-label="本章目录">\n  <div class="h">本章目录</div>\n'
            f'  <ol>\n{lis}\n  </ol>\n</nav>')


def number_figures(body, n):
    k = 0

    def repl(m):
        nonlocal k
        k += 1
        return f'<figcaption><span class="fig-n">图 {n}-{k}</span>'
    return re.sub(r"<figcaption>", repl, body)


def pager(n):
    by_n = {c[1]: c for c in CHAPTERS}
    prev_c, next_c = by_n.get(n - 1), by_n.get(n + 1)
    if prev_c:
        prev = (f'<a class="prev" href="{prev_c[0]}.html"><span>&larr; 上一章</span>'
                f'第 {prev_c[1]} 章 · {prev_c[2]}</a>')
    else:
        prev = '<a class="prev" href="index.html"><span>&larr; 返回</span>课程首页</a>'
    if next_c:
        nxt = (f'<a class="next" href="{next_c[0]}.html"><span>下一章 &rarr;</span>'
               f'第 {next_c[1]} 章 · {next_c[2]}</a>')
    else:
        nxt = '<a class="next" href="index.html"><span>读完了 &rarr;</span>回到课程首页</a>'
    return f'<nav class="pager" aria-label="章节翻页">\n{prev}\n{nxt}\n</nav>\n'


def toc_grid():
    cards = "\n".join(
        f'<a class="toc-card" href="{slug}.html"><div class="n">第 {n} 章</div>'
        f'<div class="t">{full}</div><div class="d">{desc}</div></a>'
        for slug, n, _short, full, desc, _part in CHAPTERS)
    return f'<div class="toc-grid">\n{cards}\n</div>'


def page(title, desc, n, body):
    return (HEAD.format(title=title, desc=desc, n=n) + MARKERS + '<div id="app">\n'
            + sidebar(n) + "<main>\n" + body + FOOT)


def build_chapter(slug, n, _short, full, desc, _part):
    body = (SRC / f"{slug}.html").read_text(encoding="utf-8")
    body = body.replace('<div id="chapter-toc"></div>', chapter_toc(body))
    body = number_figures(body, n)
    html = page(f"第 {n} 章 · {full} — {SITE}", desc, n, body + "\n" + pager(n))
    (ROOT / f"{slug}.html").write_text(html, encoding="utf-8")
    return len(html)


def build_index():
    body = (SRC / "index.html").read_text(encoding="utf-8")
    body = body.replace('<div id="toc-grid"></div>', toc_grid())
    body = number_figures(body, 0)
    html = page(SITE,
                "《Learning LangChain》全 11 章中文图解教程，配套 LangChain 1.x / LangGraph 1.x 可运行代码。",
                0, body)
    (ROOT / "index.html").write_text(html, encoding="utf-8")
    return len(html)


if __name__ == "__main__":
    targets = sys.argv[1:] or ["index"] + [c[0] for c in CHAPTERS]
    for t in targets:
        if t == "index":
            print("index.html", build_index())
            continue
        chapter = next((c for c in CHAPTERS if c[0] == t), None)
        if chapter is None:
            sys.exit(f"未知章节：{t}（可选：index, {', '.join(c[0] for c in CHAPTERS)}）")
        print(f"{t}.html", build_chapter(*chapter))
