/* Learning LangChain 中文教程 — 共享交互
   1. 主题切换（跟随系统 / 亮 / 暗，记住选择）
   2. Python / JavaScript 代码切换（全站统一）
   3. 右侧目录滚动高亮
   4. 代码复制
*/
(function () {
  'use strict';

  var store = {
    get: function (k) { try { return localStorage.getItem(k); } catch (e) { return null; } },
    set: function (k, v) { try { localStorage.setItem(k, v); } catch (e) { /* 隐私模式下忽略 */ } }
  };

  /* ---------- 主题 ---------- */
  var THEME_KEY = 'llc-theme';
  function applyTheme(t) {
    if (t === 'light' || t === 'dark') document.documentElement.setAttribute('data-theme', t);
    else document.documentElement.removeAttribute('data-theme');
    var btn = document.getElementById('theme-toggle');
    if (btn) btn.textContent = t === 'dark' ? '暗色' : t === 'light' ? '亮色' : '跟随系统';
  }
  applyTheme(store.get(THEME_KEY) || 'system');

  /* ---------- 语言 ---------- */
  var LANG_KEY = 'llc-lang';
  function applyLang(lang) {
    document.querySelectorAll('.codegroup').forEach(function (group) {
      var panes = group.querySelectorAll('[data-lang]');
      var tabs = group.querySelectorAll('.langtab');
      var available = Array.prototype.map.call(panes, function (p) { return p.dataset.lang; });
      var pick = available.indexOf(lang) >= 0 ? lang : available[0];
      panes.forEach(function (p) { p.classList.toggle('is-shown', p.dataset.lang === pick); });
      tabs.forEach(function (t) { t.setAttribute('aria-selected', String(t.dataset.lang === pick)); });
    });
    document.querySelectorAll('[data-lang-btn]').forEach(function (b) {
      b.setAttribute('aria-pressed', String(b.dataset.langBtn === lang));
    });
  }

  document.addEventListener('DOMContentLoaded', function () {
    var lang = store.get(LANG_KEY) || 'py';
    applyLang(lang);

    document.addEventListener('click', function (e) {
      var tab = e.target.closest('.langtab');
      if (tab) { store.set(LANG_KEY, tab.dataset.lang); applyLang(tab.dataset.lang); return; }

      var langBtn = e.target.closest('[data-lang-btn]');
      if (langBtn) { store.set(LANG_KEY, langBtn.dataset.langBtn); applyLang(langBtn.dataset.langBtn); return; }

      var themeBtn = e.target.closest('#theme-toggle');
      if (themeBtn) {
        var order = ['system', 'light', 'dark'];
        var cur = store.get(THEME_KEY) || 'system';
        var next = order[(order.indexOf(cur) + 1) % order.length];
        store.set(THEME_KEY, next); applyTheme(next);
        return;
      }

      var copyBtn = e.target.closest('[data-copy]');
      if (copyBtn) {
        var group = copyBtn.closest('.codegroup, .shellblock');
        var pane = group.querySelector('[data-lang].is-shown pre, pre');
        if (pane && navigator.clipboard) {
          navigator.clipboard.writeText(pane.innerText).then(function () {
            var old = copyBtn.textContent;
            copyBtn.textContent = '已复制';
            setTimeout(function () { copyBtn.textContent = old; }, 1400);
          });
        }
      }
    });

    /* ---------- 目录滚动高亮 ---------- */
    var links = Array.prototype.slice.call(document.querySelectorAll('.toc a[href^="#"]'));
    if (!links.length || !('IntersectionObserver' in window)) return;
    var map = {};
    var targets = [];
    links.forEach(function (a) {
      var el = document.getElementById(a.getAttribute('href').slice(1));
      if (el) { map[el.id] = a; targets.push(el); }
    });
    var visible = new Set();
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) visible.add(en.target.id); else visible.delete(en.target.id);
      });
      var first = targets.find(function (t) { return visible.has(t.id); });
      links.forEach(function (a) { a.classList.remove('is-active'); });
      if (first && map[first.id]) map[first.id].classList.add('is-active');
    }, { rootMargin: '-72px 0px -70% 0px' });
    targets.forEach(function (t) { io.observe(t); });
  });
})();
