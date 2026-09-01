#!/usr/bin/env python3
"""从 _src/ 下的正文片段生成 tutorials/ 里的完整 HTML 页面。

用法：
    python tutorials/build.py            # 全部重建
    python tutorials/build.py ch03       # 只重建某一章

正文片段（_src/*.html）只包含 <header> 之后的内容；页面外壳（<head>、
左侧章节导航、顶部工具条、上下章翻页）由本脚本统一生成，所以改导航
只需要改这里一处。本章目录会从正文里的 <h2 id="..."> 自动抽取。
"""

import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).parent
SRC = ROOT / "_src"

CHAPTERS = [
    ("ch01", "01", "LLM 基础与 LangChain 构建块", "聊天模型、提示模板、结构化输出，以及把它们拼起来的两种方式。"),
    ("ch02", "02", "RAG 上篇：为你的数据建索引", "加载、切分、嵌入、入库——让模型能查到你的私有资料。"),
    ("ch03", "03", "RAG 下篇：与你的数据对话", "检索、查询改写、路由与查询构造，把朴素 RAG 变成能上生产的 RAG。"),
    ("ch04", "04", "用 LangGraph 给机器人加记忆", "StateGraph、检查点、线程，以及裁剪 / 过滤 / 合并聊天记录。"),
    ("ch05", "05", "LangGraph 认知架构", "自主性阶梯：单次调用 → 链 → 路由器。"),
    ("ch06", "06", "Agent 架构", "计划—执行循环、ReAct、强制先调工具、工具太多怎么办。"),
    ("ch07", "07", "Agent 进阶：反思与多智能体", "自我批评循环、子图，以及 Supervisor 多智能体架构。"),
    ("ch08", "08", "榨干 LLM 的实用模式", "结构化输出、流式中间结果、人在环路、并发输入。"),
    ("ch09", "09", "部署：送上生产", "LangGraph Platform、Studio、Supabase 向量库与安全清单。"),
    ("ch10", "10", "测试：评估、监控与改进", "自纠正 RAG、数据集、评估器、回归测试与线上追踪。"),
    ("ch11", "11", "用 LLM 做产品", "聊天助手、协同编辑、环境计算——三种 LLM 原生交互范式。"),
]

HEAD = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600&family=Newsreader:opsz,wght@6..72,500;6..72,600&family=Noto+Sans+SC:wght@400;500;700&family=Noto+Serif+SC:wght@600&display=swap">
<link rel="stylesheet" href="{base}assets/course.css">
</head>
<body>
<div class="shell">
"""

def rail(current, toc_html=""):
    items = []
    for slug, num, name, _ in CHAPTERS:
        cur = ' aria-current="page"' if slug == current else ""
        items.append(f'    <a href="{slug}.html"{cur}><span class="num">{num}</span><span>{name}</span></a>')
    nav = "\n".join(items)
    toc_block = ""
    if toc_html:
        toc_block = f"""
  <div>
    <h3>本章目录</h3>
    <nav class="toc">
{toc_html}
    </nav>
  </div>"""
    home = ' aria-current="page"' if current == "index" else ""
    return f"""<aside class="rail">
  <a class="brand" href="index.html"{home}>
    <span class="brand__mark">Learning LangChain</span>
    <span class="brand__name">中文精读教程</span>
    <span class="brand__sub">11 章 · 图解 + 可运行代码</span>
  </a>
  <div>
    <h3>章节</h3>
    <nav class="chapnav">
{nav}
    </nav>
  </div>{toc_block}
</aside>
"""

def topbar(crumb, lang_toggle=True):
    tools = """      <button class="chip" data-lang-btn="py" aria-pressed="true">Python</button>
      <button class="chip" data-lang-btn="js" aria-pressed="false">JavaScript</button>
""" if lang_toggle else ""
    return f"""  <div class="topbar">
    <span class="crumb">{crumb}</span>
    <div class="tools">
{tools}      <button class="chip" id="theme-toggle" type="button">跟随系统</button>
    </div>
  </div>
"""

def pager(slug):
    idx = [c[0] for c in CHAPTERS].index(slug)
    prev_c = CHAPTERS[idx - 1] if idx > 0 else None
    next_c = CHAPTERS[idx + 1] if idx < len(CHAPTERS) - 1 else None
    parts = ['<nav class="pager">']
    if prev_c:
        parts.append(f'  <a href="{prev_c[0]}.html"><span class="dir">上一章</span><span class="ttl">{prev_c[1]} · {prev_c[2]}</span></a>')
    else:
        parts.append('  <a href="index.html"><span class="dir">返回</span><span class="ttl">课程首页</span></a>')
    if next_c:
        parts.append(f'  <a class="next" href="{next_c[0]}.html"><span class="dir">下一章</span><span class="ttl">{next_c[1]} · {next_c[2]}</span></a>')
    else:
        parts.append('  <a class="next" href="index.html"><span class="dir">读完了</span><span class="ttl">回到课程首页</span></a>')
    parts.append('</nav>')
    return "\n".join(parts)

def extract_toc(body):
    """从 body 中的 <h2 id="..."> 生成目录。"""
    out = []
    for m in re.finditer(r'<h2 id="([^"]+)">(.*?)</h2>', body, re.S):
        text = re.sub(r"<[^>]+>", "", m.group(2)).strip()
        out.append(f'      <a href="#{m.group(1)}">{text}</a>')
    return "\n".join(out)

def default_pane(body):
    """让每个代码组的第一个语言面板默认可见（JS 未加载时也能看到代码）。"""
    out = []
    for block in re.split(r'(<div class="codegroup">)', body):
        out.append(block)
    body = "".join(out)
    # 每个 codegroup 内第一个 data-lang 面板加上 is-shown
    def fix(m):
        inner = m.group(0)
        inner = re.sub(r'<div data-lang="(\w+)">', lambda mm: f'<div data-lang="{mm.group(1)}" class="is-shown">', inner, count=1)
        inner = re.sub(r'<button class="langtab" data-lang="(\w+)" type="button">',
                       lambda mm: f'<button class="langtab" data-lang="{mm.group(1)}" type="button" aria-selected="true">',
                       inner, count=1)
        return inner
    return re.sub(r'<div class="codegroup">.*?(?=<div class="codegroup">|<h2|<footer|\Z)', fix, body, flags=re.S)


def build_chapter(slug, num, name, desc):
    body = default_pane((SRC / f"{slug}.html").read_text(encoding="utf-8"))
    toc = extract_toc(body)
    page = HEAD.format(title=f"{name}｜Learning LangChain 中文教程", desc=desc, base="")
    page += rail(slug, toc)
    page += '<main class="main">\n<div class="wrap">\n'
    page += topbar(f"第 {num} 章")
    page += body
    page += "\n" + pager(slug) + "\n"
    page += '</div>\n</main>\n</div>\n<script src="assets/course.js"></script>\n</body>\n</html>\n'
    (ROOT / f"{slug}.html").write_text(page, encoding="utf-8")
    return len(page)

def build_index():
    body = (SRC / "index.html").read_text(encoding="utf-8")
    page = HEAD.format(title="Learning LangChain 中文精读", desc="《Learning LangChain》全 11 章中文图解教程，配套 LangChain 1.x / LangGraph 1.x 可运行代码。", base="")
    page += rail("index")
    page += '<main class="main">\n<div class="wrap--wide">\n'
    page += topbar("课程首页", lang_toggle=False)
    page += body
    page += '</div>\n</main>\n</div>\n<script src="assets/course.js"></script>\n</body>\n</html>\n'
    (ROOT / "index.html").write_text(page, encoding="utf-8")
    return len(page)

if __name__ == "__main__":
    which = sys.argv[1:] or ["index"] + [c[0] for c in CHAPTERS]
    for w in which:
        if w == "index":
            if (SRC / "index.html").exists():
                print("index.html", build_index())
        else:
            c = next((c for c in CHAPTERS if c[0] == w), None)
            if c and (SRC / f"{w}.html").exists():
                print(f"{w}.html", build_chapter(*c))
