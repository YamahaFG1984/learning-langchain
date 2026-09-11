/* ================================================================
   Learning LangChain 中文精读 · 共享脚本
   侧边栏、目录、上一章/下一章都由 build.py 静态生成；这里只负责交互：
   主题切换、移动端菜单、Python/JavaScript 代码切换、复制按钮。

   以普通 <script> 加载而不是 type="module"：浏览器不允许从 file:// 加载
   模块脚本，而这套页面要能直接双击打开。用块级作用域避免污染全局。
   ================================================================ */
{
  const store = {
    get: (key) => { try { return localStorage.getItem(key); } catch { return null; } },
    set: (key, value) => { try { localStorage.setItem(key, value); } catch { /* 隐私模式下忽略 */ } },
  };
  const root = document.documentElement;
  const side = document.getElementById('sidebar');

  const makeButton = (id, label) => {
    const button = document.createElement('button');
    button.id = id;
    button.type = 'button';
    button.setAttribute('aria-label', label);
    document.body.append(button);
    return button;
  };

  /* ---------- 侧边栏：当前章节滚到可见处 ---------- */
  const active = side?.querySelector('a.ch.active');
  if (active) side.scrollTop = active.offsetTop - side.clientHeight / 2;

  /* ---------- 移动端菜单 ---------- */
  const menuButton = makeButton('menu-btn', '目录');
  menuButton.textContent = '☰';
  menuButton.addEventListener('click', () => document.body.classList.toggle('nav-open'));
  document.addEventListener('click', (event) => {
    if (!document.body.classList.contains('nav-open') || event.target === menuButton) return;
    // 点侧栏外面、或点了侧栏里的链接，都收起菜单
    if (!side.contains(event.target) || event.target.closest('a')) {
      document.body.classList.remove('nav-open');
    }
  });

  /* ---------- 主题切换 ---------- */
  const THEME_KEY = 'llc-doc-theme';
  const isDark = () => {
    const theme = root.dataset.theme;
    return theme ? theme === 'dark' : matchMedia('(prefers-color-scheme: dark)').matches;
  };
  const themeButton = makeButton('theme-btn', '切换深浅色');
  const paintThemeButton = () => { themeButton.textContent = isDark() ? '☀' : '☽'; };
  themeButton.addEventListener('click', () => {
    const next = isDark() ? 'light' : 'dark';
    root.dataset.theme = next;
    store.set(THEME_KEY, next);
    paintThemeButton();
  });
  paintThemeButton();

  /* ---------- Python / JavaScript 代码切换（全站统一） ---------- */
  const LANG_KEY = 'llc-lang';
  const applyLang = (lang) => {
    for (const box of document.querySelectorAll('.code[data-group]')) {
      const panes = [...box.querySelectorAll('pre[data-lang]')];
      // 这个代码块没有所选语言时，退回它的第一种
      const pick = panes.some((pane) => pane.dataset.lang === lang) ? lang : panes[0].dataset.lang;
      for (const pane of panes) pane.classList.toggle('is-shown', pane.dataset.lang === pick);
      for (const tab of box.querySelectorAll('.langtab')) {
        tab.setAttribute('aria-selected', String(tab.dataset.lang === pick));
      }
    }
    for (const button of document.querySelectorAll('[data-lang-btn]')) {
      button.setAttribute('aria-pressed', String(button.dataset.langBtn === lang));
    }
  };
  applyLang(store.get(LANG_KEY) ?? 'py');

  document.addEventListener('click', (event) => {
    const picker = event.target.closest('.langtab, [data-lang-btn]');
    if (picker) {
      const lang = picker.dataset.lang ?? picker.dataset.langBtn;
      // 切换会改变代码块高度；把被点的元素钉在原来的屏幕位置，页面不跳
      const before = picker.getBoundingClientRect().top;
      store.set(LANG_KEY, lang);
      applyLang(lang);
      if (!side.contains(picker)) scrollBy(0, picker.getBoundingClientRect().top - before);
      return;
    }

    const copyButton = event.target.closest('.copy');
    if (copyButton) {
      const box = copyButton.closest('.code');
      const pre = box.querySelector('pre.is-shown') ?? box.querySelector('pre');
      navigator.clipboard?.writeText(pre.innerText);
      copyButton.textContent = '已复制';
      setTimeout(() => { copyButton.textContent = '复制'; }, 1400);
    }
  });
}
