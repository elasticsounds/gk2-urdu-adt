/* ADT reader — واقفیتِ عامہ جماعت دوم */
(function () {
  'use strict';
  const CL = window.ADT_LANG === 'en' ? 'en' : 'ur', OL = CL === 'en' ? 'ur' : 'en', LTR = CL === 'en';
  const DATA = LTR ? 'data/en/' : 'data/';
  const IDX = window.ADT_INDEX || { total: 96, pages: [], chapters: {}, ui: {} };
  const UIA = IDX.ui || {};
  const $ = (s, r) => (r || document).querySelector(s);
  const $$ = (s, r) => Array.from((r || document).querySelectorAll(s));

  /* ---------- i18n ---------- */
  const STR = {
    ur: {
      skip: 'مرکزی مواد پر جائیں', book: 'واقفیتِ عامہ', klass: 'جماعت دوم', menu: 'فہرست', listen: 'سنیں', pause: 'روکیں', hint: 'مددگار اشارہ',
      print: 'پرنٹ کریں', settings: 'ترتیبات', vAdapt: 'سبق', vEasy: 'آسان', vOrig: 'اصل صفحہ', prev: 'پچھلا', next: 'اگلا', page: 'صفحہ', of: 'از',
      chapter: 'باب', front: 'ابتدائی صفحات', back: 'آخری صفحہ', fact: 'کیا آپ جانتے ہیں؟', teacher: 'برائے اساتذہ', activity: 'سرگرمی',
      easy: 'آسان', moderate: 'درمیانی', hard: 'مشکل', level: 'سطح', origAct: 'کتاب میں اصل سرگرمی', seeOrig: 'اصل صفحہ دیکھیں', tryAgain: 'دوبارہ کریں',
      check: 'جواب چیک کریں', showAns: 'جواب دیکھیں', model: 'نمونہ جواب', hideModel: 'جواب چھپائیں', done: 'میں نے کر لیا', up: 'اوپر', down: 'نیچے',
      mWrite: 'لکھیں', mDraw: 'تصویر بنائیں', mTalk: 'بات کریں', mDo: 'کر کے دیکھیں', writeHere: 'اپنا جواب یہاں لکھیں', tTrue: 'درست', tFalse: 'غلط',
      easyRead: 'آسان مطالعہ', easyAct: 'آسان سرگرمی', tapWord: 'لفظ سننے کے لیے تصویر دبائیں', openPdf: 'اس صفحے کی PDF کھولیں', origNote: 'یہ کتاب کا اصل صفحہ ہے۔',
      backAdapt: 'سبق پر واپس', close: 'بند کریں', start: 'پڑھنا شروع کریں', listenThis: 'یہ سنیں', noEasy: 'اس صفحے کا آسان مطالعہ نہیں ہے۔',
      sText: 'لکھائی کا سائز', sFont: 'خط', fNast: 'نستعلیق', fNaskh: 'نسخ (سادہ)', sTheme: 'رنگ', tLight: 'روشن', tDark: 'گہرا', tContrast: 'زیادہ تضاد',
      sSpace: 'سطروں کا فاصلہ', spN: 'عام', spW: 'کھلا', sSpeed: 'آواز کی رفتار', slow: 'آہستہ', normal: 'عام', fast: 'تیز', sLevel: 'سرگرمی کی سطح',
      sHl: 'پڑھتے وقت لفظ نمایاں کریں', sFb: 'جواب کے بعد رائے پڑھ کر سنائیں', sEn: 'انگریزی ترجمہ دکھائیں', sMotion: 'حرکت کم کریں', sUi: 'مینو کی زبان',
      sKeys: 'کی بورڈ', about: 'اس کتاب کے بارے میں', name: 'نام', date: 'تاریخ', forAll: 'سب کے لیے', forVision: 'دیکھنے میں مدد', forHearing: 'سننے میں مدد',
      forMotor: 'حرکت میں مدد', forCognitive: 'سمجھنے میں مدد', forTeacher: 'استاد کے لیے', noAudio: 'اس حصے کی آواز دستیاب نہیں', loading: 'صفحہ کھل رہا ہے…',
      notReady: 'یہ صفحہ ابھی تیار نہیں۔ اصل صفحہ دیکھیں۔', picked: 'منتخب', matched: 'جوڑ بن گیا', pickPair: 'پہلے ایک خانہ چنیں، پھر اس کا جوڑ چنیں۔', stars: 'ستارے',
      origPageAlt: 'کتاب کا اصل صفحہ', adaptedFrom: 'کتاب کے صفحہ سے ماخوذ', putIn: 'کس میں رکھیں؟', extraAct: 'یہ اضافی مشق ہے۔ یہ کتاب میں چھپی ہوئی نہیں، مگر اسی صفحے کے سبق پر مبنی ہے۔',
      sUr: 'اردو متن دکھائیں', sBook: 'کتاب کی زبان', sImg: 'تصویروں کی تفصیل دکھائیں اور پڑھ کر سنائیں', picture: 'تصویر', enlarge: 'تصویر بڑی کریں اور اس کی تفصیل سنیں', picDesc: 'تصویر کی تفصیل', stopListen: 'سننا بند کریں', listenTip: 'سننے کا موڈ آن ہے۔ کسی بھی جملے کو دبائیں تو وہاں سے پڑھا جائے گا۔'
    },
    en: {
      skip: 'Skip to main content', book: 'General Knowledge', klass: 'Class 2', menu: 'Contents', listen: 'Listen', pause: 'Pause', hint: 'Helpful hint',
      print: 'Print page', settings: 'Settings', vAdapt: 'Lesson', vEasy: 'Easy Read', vOrig: 'Original page', prev: 'Previous', next: 'Next', page: 'Page', of: 'of',
      chapter: 'Chapter', front: 'Front pages', back: 'Back cover', fact: 'Do you know?', teacher: 'For teachers', activity: 'Activity',
      easy: 'Easy', moderate: 'Medium', hard: 'Hard', level: 'Level', origAct: 'Original activity in the book', seeOrig: 'See original page', tryAgain: 'Try again',
      check: 'Check answer', showAns: 'Show answer', model: 'Sample answer', hideModel: 'Hide answer', done: 'I did it', up: 'Move up', down: 'Move down',
      mWrite: 'Write', mDraw: 'Draw', mTalk: 'Talk', mDo: 'Do it', writeHere: 'Write your answer here', tTrue: 'True', tFalse: 'False',
      easyRead: 'Easy Read', easyAct: 'Easy activity', tapWord: 'Tap a picture to hear the word', openPdf: 'Open this page as PDF', origNote: 'This is the original page from the book.',
      backAdapt: 'Back to lesson', close: 'Close', start: 'Start reading', listenThis: 'Listen to this', noEasy: 'No Easy Read version for this page.',
      sText: 'Text size', sFont: 'Script style', fNast: 'Nastaliq', fNaskh: 'Naskh (simpler)', sTheme: 'Colours', tLight: 'Light', tDark: 'Dark', tContrast: 'High contrast',
      sSpace: 'Line spacing', spN: 'Normal', spW: 'Wide', sSpeed: 'Voice speed', slow: 'Slow', normal: 'Normal', fast: 'Fast', sLevel: 'Activity level',
      sHl: 'Highlight words while reading', sFb: 'Read feedback aloud after answering', sEn: 'Show English translation', sMotion: 'Reduce motion', sUi: 'Menu language',
      sKeys: 'Keyboard', about: 'About this book', name: 'Name', date: 'Date', forAll: 'For everyone', forVision: 'Seeing', forHearing: 'Hearing',
      forMotor: 'Moving', forCognitive: 'Understanding', forTeacher: 'For the teacher', noAudio: 'Audio is not available for this part', loading: 'Opening page…',
      notReady: 'This page is not ready yet. See the original page.', picked: 'selected', matched: 'Matched', pickPair: 'Pick one box, then pick its partner.', stars: 'stars',
      origPageAlt: 'Original book page', adaptedFrom: 'Adapted from book page', putIn: 'Where does it go?', extraAct: 'Extra practice: not printed in the book, but based on this page of the lesson.',
      sUr: 'Show Urdu text', sBook: 'Book language', sImg: 'Show picture descriptions and read them aloud', picture: 'Picture', enlarge: 'Enlarge picture and hear its description', picDesc: 'Picture description', stopListen: 'Stop listening', listenTip: 'Listening is on. Tap any sentence to read from there.'
    }
  };
  const CS = STR[CL], OS = STR[OL];
  const ICON = {
    menu: '<path d="M4 6h16M4 12h16M4 18h16"/>', play: '<path d="M7 4v16l13-8z" fill="currentColor"/>', pause: '<path d="M8 5v14M16 5v14" stroke-width="3"/>',
    vol: '<path d="M4 9v6h4l5 4V5L8 9z" fill="currentColor" stroke="none"/><path d="M16.5 8.5a5 5 0 010 7M19 6a8.5 8.5 0 010 12"/>',
    bulb: '<path d="M9 18h6M10 21h4M12 3a6 6 0 00-4 10.5c.7.7 1 1.5 1 2.5h6c0-1 .3-1.800 1-2.500A6 6 0 0012 3z"/>',
    print: '<path d="M7 8V3h10v5M7 17H4v-7a2 2 0 012-2h12a2 2 0 012 2v7h-3M7 14h10v7H7z"/>', gear: '<circle cx="12" cy="12" r="3"/><path d="M19 12a7 7 0 00-.1-1.300l2-1.500-2-3.400-2.300 1a7 7 0 00-2.200-1.300L14 3h-4l-.4 2.500a7 7 0 00-2.200 1.300l-2.300-1-2 3.400 2 1.500A7 7 0 005 12c0 .4 0 .9.1 1.300l-2 1.500 2 3.400 2.300-1a7 7 0 002.200 1.300L10 21h4l.4-2.500a7 7 0 002.200-1.300l2.300 1 2-3.400-2-1.500c.1-.4.1-.900.1-1.300z"/>',
    book: '<path d="M4 5a2 2 0 012-2h13v16H6a2 2 0 00-2 2zM4 21V5M8 7h7M8 11h7"/>', smile: '<circle cx="12" cy="12" r="9"/><path d="M8 14a4.500 4.500 0 008 0M9 9.500v.01M15 9.500v.01" stroke-width="2.4"/>',
    file: '<path d="M6 3h8l4 4v14H6zM14 3v4h4M9 12h6M9 16h6"/>', x: '<path d="M6 6l12 12M18 6L6 18"/>', next: '<path d="M9 5l7 7-7 7"/>', prev: '<path d="M15 5l-7 7 7 7"/>',
    up: '<path d="M6 15l6-6 6 6"/>', down: '<path d="M6 9l6 6 6-6"/>', ext: '<path d="M14 4h6v6M20 4l-9 9M18 14v6H4V6h6"/>', zoom: '<circle cx="11" cy="11" r="6.5"/><path d="M16 16l5 5M11 8v6M8 11h6"/>'
  };
  const ic = (n) => `<svg class="i" viewBox="0 0 24 24" aria-hidden="true">${ICON[n]}</svg>`;

  /* ---------- settings / storage ---------- */
  const KEY = 'adt-gk2' + (LTR ? '-en' : '');
  const store = {
    get(k, d) { try { const v = localStorage.getItem(KEY + ':' + k); return v == null ? d : JSON.parse(v); } catch (e) { return d; } },
    set(k, v) { try { localStorage.setItem(KEY + ':' + k, JSON.stringify(v)); } catch (e) { } }
  };
  const SET = Object.assign({ fs: 1, font: 'nastaliq', theme: 'light', spacing: 'normal', rate: 1, level: 'moderate', hl: true, fb: true, en: false, motion: false, imgs: true, ui: CL }, store.get('settings', {}));
  let DONE = store.get('done', {});
  const t = (k) => (STR[SET.ui] || CS)[k] || CS[k] || k;
  function applySettings() {
    const r = document.documentElement;
    r.style.setProperty('--fs', SET.fs);
    r.dataset.font = SET.font; r.dataset.theme = SET.theme; r.dataset.spacing = SET.spacing; r.dataset.ui = SET.ui; r.dataset.cl = CL;
    r.classList.toggle('show-en', !!SET.en); r.classList.toggle('reduce-motion', !!SET.motion); r.classList.toggle('img-desc', !!SET.imgs);
    r.lang = SET.ui === 'en' ? 'en' : 'ur'; r.dir = SET.ui === 'en' ? 'ltr' : 'rtl';
    store.set('settings', SET);
  }

  /* ---------- dom helpers ---------- */
  function h(tag, attrs, ...kids) {
    const el = document.createElement(tag);
    if (attrs) for (const k in attrs) {
      const v = attrs[k];
      if (v == null || v === false) continue;
      if (k === 'class') el.className = v; else if (k === 'html') el.innerHTML = v; else if (k.startsWith('on')) el.addEventListener(k.slice(2), v);
      else if (k === 'dataset') Object.assign(el.dataset, v); else el.setAttribute(k, v === true ? '' : v);
    }
    for (const kid of kids.flat()) if (kid != null && kid !== false) el.append(kid);
    return el;
  }
  function fillWords(el, s) {
    const re = /\S+/g; let m, last = 0;
    while ((m = re.exec(s))) {
      if (m.index > last) el.append(s.slice(last, m.index));
      const sp = document.createElement('span'); sp.className = 'w'; sp.dataset.s = m.index; sp.textContent = m[0]; el.append(sp);
      last = m.index + m[0].length;
    }
    if (last < s.length) el.append(s.slice(last));
  }
  /* Urdu text element (speakable when it has audio) */
  function U(o, tag, cls) {
    const el = h(tag || 'span', { class: 'ur ' + (cls || ''), lang: CL, dir: LTR ? 'ltr' : 'rtl' });
    if (!o) return el;
    fillWords(el, o.ur || '');
    if (o.a) el.dataset.a = o.a;
    return el;
  }
  const EN = (o) => (o && o.en ? h('span', { class: 'en', lang: OL, dir: LTR ? 'rtl' : 'ltr' }, o.en) : null);
  const lbl = (k) => h('span', { class: 'lbl' }, t(k));
  /* per-sentence speaker buttons were removed: the Listen button drives reading, and a tap on a sentence jumps to it */
  function spkBtn() { return null; }
  /* A block of Urdu text with its own speaker button + optional English */
  function blk(o, tag, cls) {
    const el = U(o, tag || 'p');
    return h('div', { class: 'blk ' + (cls || '') }, o.a ? spkBtn(el) : null, el, EN(o));
  }
  function uiU(key, tag) { const o = UIA[key] || { ur: CS[key] || key }; return U(o, tag || 'span'); }
  function say(msg) { const l = $('#live'); l.textContent = ''; setTimeout(() => { l.textContent = msg; }, 30); }
  let toastT; function toast(msg) { const el = $('#toast'); el.textContent = msg; el.hidden = false; clearTimeout(toastT); toastT = setTimeout(() => { el.hidden = true; }, 2600); }
  const shuffle = (a) => { a = a.slice(); for (let i = a.length - 1; i > 0; i--) { const j = Math.floor(Math.random() * (i + 1));[a[i], a[j]] = [a[j], a[i]]; } return a; };
  function shuffleDiff(a) { if (a.length < 2) return a.slice(); for (let k = 0; k < 8; k++) { const s = shuffle(a); if (s.some((x, i) => x !== a[i])) return s; } return a.slice().reverse(); }

  /* ---------- audio engine ---------- */
  let LISTEN = false;
  const Audio_ = (function () {
    const au = new Audio(); au.preload = 'auto';
    let queue = [], qi = -1, cur = null, spans = [], marks = null, raf = 0, hlEl = null, mode = 'idle', onEnd = null, warned = false;
    function clearHl() { if (hlEl) { hlEl.classList.remove('hl'); hlEl = null; } }
    function stopCur() { cancelAnimationFrame(raf); clearHl(); if (cur) { cur.classList.remove('speaking'); const b = cur.closest('.blk,.sent,.opt,.wd,.hint,.q-text,.fb'); if (b) b.classList.remove('speaking'); } cur = null; }
    function tick() {
      if (!cur || au.paused) return;
      if (marks && SET.hl) {
        const ms = au.currentTime * 1000; let off = -1;
        for (let i = 0; i < marks.length; i++) { if (marks[i][0] <= ms + 60) off = marks[i][1]; else break; }
        if (off >= 0) {
          let sp = null; for (let i = 0; i < spans.length; i++) { if (spans[i].s <= off) sp = spans[i].el; else break; }
          if (sp && sp !== hlEl) { clearHl(); hlEl = sp; sp.classList.add('hl'); }
        }
      }
      raf = requestAnimationFrame(tick);
    }
    function start(el) {
      stopCur(); cur = el; const id = el.dataset.a;
      const box = el.closest('.blk,.sent,.opt,.wd,.hint,.q-text,.fb') || el; box.classList.add('speaking');
      const r = box.getBoundingClientRect(), topH = $('#top').offsetHeight, botH = $('#bottom').offsetHeight;
      if (!box.closest('dialog') && (r.top < topH + 8 || r.bottom > innerHeight - botH - 8)) window.scrollTo({ top: scrollY + r.top - topH - 24, behavior: SET.motion ? 'auto' : 'smooth' });
      spans = $$('.w', el).map((x) => ({ s: +x.dataset.s, el: x }));
      marks = (PAGE && PAGE.marks && PAGE.marks[id]) || (IDX.uiMarks && IDX.uiMarks[id]) || null;
      au.src = 'assets/audio/' + id + '.mp3'; au.playbackRate = SET.rate;
      au.play().then(() => { au.playbackRate = SET.rate; raf = requestAnimationFrame(tick); }).catch(() => fail());
    }
    function fail() {
      if (!warned) { warned = true; toast(t('noAudio')); }
      setTimeout(next, 150);
    }
    function next() {
      const last = cur, wasOne = mode === 'one';
      stopCur();
      if (mode === 'queue' && qi + 1 < queue.length) { qi++; start(queue[qi]); return; }
      const cb = onEnd; mode = 'idle'; queue = []; qi = -1; onEnd = null; ui();
      if (cb) cb();
      else if (wasOne && LISTEN && last && last.isConnected && last.closest('#main')) {
        const all = readableEls(true); const i = all.findIndex((x) => last.compareDocumentPosition(x) & 4);
        if (i >= 0) api.playQueue(all.slice(i), true);
      }
    }
    au.addEventListener('ended', next);
    au.addEventListener('error', () => { if (cur) fail(); });
    function ui() {
      const b = $('#btn-listen'); if (!b) return;
      b.innerHTML = ic(LISTEN ? 'pause' : 'play') + `<span class="lbl">${t(LISTEN ? 'stopListen' : 'listen')}</span>`;
      b.setAttribute('aria-pressed', LISTEN ? 'true' : 'false'); b.setAttribute('aria-label', t(LISTEN ? 'stopListen' : 'listen'));
    }
    au.addEventListener('play', ui); au.addEventListener('pause', ui);
    const api = {
      playOne(el, cb) { if (!el || !el.dataset.a) { if (cb) cb(); return; } if (cur === el && !au.paused) { api.stop(); return; } au.pause(); mode = 'one'; queue = []; onEnd = cb || null; start(el); ui(); },
      playQueue(els, silent) { els = els.filter((e) => e.dataset.a); if (!els.length) { if (!silent) toast(t('noAudio')); return; } au.pause(); mode = 'queue'; queue = els; qi = 0; onEnd = null; start(els[0]); ui(); },
      jump(el) {
        if (cur === el) { if (au.paused) { au.play(); raf = requestAnimationFrame(tick); } else { au.pause(); cancelAnimationFrame(raf); } return; }
        const all = readableEls(true); const i = all.indexOf(el);
        if (i < 0) { api.playOne(el); return; }
        au.pause(); mode = 'queue'; queue = all; qi = i; onEnd = null; start(el); ui();
      },
      stop() { au.pause(); stopCur(); mode = 'idle'; queue = []; qi = -1; onEnd = null; ui(); },
      setRate() { au.playbackRate = SET.rate; }, ui
    };
    return api;
  })();
  function readableEls(all) {
    const root = $('#main'); const topH = $('#top').offsetHeight;
    const els = $$('[data-a]', root).filter((el) => el.offsetParent !== null && !el.closest('.fb,.wd,.orig-b,.model-b,.done-banner,.bin .got'));
    if (all) return els;
    const i = els.findIndex((el) => el.getBoundingClientRect().bottom > topH + 4);
    return i > 0 ? els.slice(i) : els;
  }
  function setListen(on) {
    LISTEN = !!on && VIEW !== 'orig'; document.documentElement.classList.toggle('listening', LISTEN);
    if (LISTEN) { Audio_.playQueue(readableEls(), true); toast(t('listenTip')); } else Audio_.stop();
    Audio_.ui();
  }
  /* tap a sentence: in listening mode jump there; inside a dialog always read it */
  document.addEventListener('click', (e) => {
    const tg = e.target; if (!tg.closest) return;
    if (tg.closest('button,a,input,textarea,select,summary,label,[role="button"]')) return;
    const el = tg.closest('[data-a]'); if (!el) return;
    if (el.closest('dialog')) { Audio_.playOne(el); return; }
    if (LISTEN && el.closest('#main')) Audio_.jump(el);
  });

  /* ---------- routing / loading ---------- */
  const CACHE = {}; let PAGE = null, CUR = 1, VIEW = 'adapt';
  function parseHash() {
    const m = location.hash.match(/^#\/(\d+)(?:\/(adapt|easy|orig))?/);
    let n = m ? +m[1] : store.get('last', 1); n = Math.min(Math.max(1, n || 1), IDX.total);
    return { n, view: (m && m[2]) || 'adapt' };
  }
  function go(n, view) { location.hash = '#/' + n + (view && view !== 'adapt' ? '/' + view : ''); }
  function loadPage(n) {
    return new Promise((res) => {
      if (CACHE[n]) return res(CACHE[n]);
      const s = document.createElement('script'); s.src = DATA + 'p' + String(n).padStart(3, '0') + '.js';
      window.ADT_PAGE = (d) => { CACHE[d.n] = d; };
      s.onload = () => { res(CACHE[n] || null); s.remove(); }; s.onerror = () => { res(null); s.remove(); };
      document.head.append(s);
    });
  }
  const meta = (n) => IDX.pages.find((p) => p.n === n) || { n, printed: '', chapter: 0, title: { ur: CS.page + ' ' + n, en: OS.page + ' ' + n } };
  const pad = (n) => String(n).padStart(3, '0');
  async function route() {
    const r = parseHash(); Audio_.stop();
    const changed = r.n !== CUR || !PAGE; CUR = r.n; VIEW = r.view; store.set('last', CUR);
    if (changed) { $('#main').innerHTML = `<div class="loading">${t('loading')}</div>`; PAGE = await loadPage(CUR); }
    if (VIEW === 'easy' && !(PAGE && PAGE.easy)) VIEW = 'adapt';
    if (!PAGE && VIEW !== 'orig') VIEW = 'orig';
    renderTop(); renderMain(); renderBottom();
    const m = meta(CUR); document.title = `${m.title.ur} — ${CS.book} (${t('page')} ${CUR})`;
    if (changed) { window.scrollTo(0, 0); $('#main').focus({ preventScroll: true }); say(`${t('page')} ${CUR}: ${m.title.ur}`); }
    if (LISTEN && VIEW !== 'orig') setTimeout(() => { if (LISTEN) Audio_.playQueue(readableEls(changed), true); }, 450);
    if (CUR < IDX.total) loadPage(CUR + 1);
  }

  /* ---------- top bar ---------- */
  function renderTop() {
    const m = meta(CUR); const top = $('#top'); top.innerHTML = '';
    $('#skip').textContent = t('skip');
    const tab = (v, key, icon, dis) => h('button', { type: 'button', role: 'tab', id: 'tab-' + v, 'aria-selected': VIEW === v ? 'true' : 'false', 'aria-controls': 'main', disabled: dis, title: dis ? t('noEasy') : null, html: ic(icon) + `<span class="lbl">${t(key)}</span>`, onclick: () => go(CUR, v) });
    const chap = m.chapter ? `${t('chapter')} ${m.chapter}` : (m.kind === 'back' ? t('back') : t('front'));
    top.append(h('div', { class: 'top-row' },
      h('button', { class: 'btn', type: 'button', id: 'btn-menu', 'aria-haspopup': 'dialog', html: ic('menu') + `<span class="lbl">${t('menu')}</span>`, onclick: openToc }),
      h('div', { class: 'book' }, h('b', { lang: CL, dir: LTR ? 'ltr' : 'rtl' }, m.title.ur), h('small', null, `${t('book')} · ${chap} · ${t('page')} ${CUR}/${IDX.total}`)),
      h('div', { class: 'tabs', role: 'tablist', 'aria-label': 'View' }, tab('adapt', 'vAdapt', 'book', !PAGE), tab('easy', 'vEasy', 'smile', !(PAGE && PAGE.easy)), tab('orig', 'vOrig', 'file')),
      h('div', { class: 'tools' },
        h('button', { class: 'btn primary tool', type: 'button', id: 'btn-listen', 'aria-pressed': 'false', onclick: () => setListen(!LISTEN) }),
        h('button', { class: 'btn sun tool', type: 'button', id: 'btn-hint', 'aria-haspopup': 'dialog', disabled: !(PAGE && PAGE.hint && PAGE.hint.length), html: ic('bulb') + `<span class="lbl">${t('hint')}</span>`, onclick: openHint }),
        (PAGE && PAGE.print) || VIEW === 'orig' ? h('button', { class: 'btn tool', type: 'button', id: 'btn-print', html: ic('print') + `<span class="lbl">${t('print')}</span>`, onclick: () => { Audio_.stop(); window.print(); } }) : null,
        h('button', { class: 'btn tool', type: 'button', id: 'btn-set', 'aria-haspopup': 'dialog', 'aria-label': t('settings'), title: t('settings'), html: ic('gear'), onclick: openSettings })
      )));
    Audio_.ui();
    if (VIEW === 'orig') $('#btn-listen').disabled = true;
  }

  /* ---------- bottom nav ---------- */
  function renderBottom() {
    const b = $('#bottom'); b.innerHTML = '';
    const rtl = document.documentElement.dir === 'rtl';
    const sel = h('select', { 'aria-label': t('page'), onchange: (e) => go(+e.target.value) });
    for (let n = 1; n <= IDX.total; n++) { const m = meta(n); sel.append(h('option', { value: n, selected: n === CUR }, `${n}. ${SET.ui !== CL && m.title.en ? m.title.en : m.title.ur}`)); }
    b.append(h('div', { class: 'bottom-row' },
      h('button', { class: 'btn nav', type: 'button', disabled: CUR <= 1, 'aria-label': t('prev'), html: ic(rtl ? 'next' : 'prev') + `<span class="lbl">${t('prev')}</span>`, onclick: () => go(CUR - 1) }),
      h('div', { class: 'mid' }, sel, h('div', { class: 'prog', role: 'progressbar', 'aria-valuemin': 1, 'aria-valuemax': IDX.total, 'aria-valuenow': CUR, 'aria-label': `${t('page')} ${CUR} ${t('of')} ${IDX.total}` }, h('i', { style: `width:${(CUR / IDX.total) * 100}%` }))),
      h('button', { class: 'btn primary nav', type: 'button', disabled: CUR >= IDX.total, 'aria-label': t('next'), html: `<span class="lbl">${t('next')}</span>` + ic(rtl ? 'prev' : 'next'), onclick: () => go(CUR + 1) })));
  }

  /* ---------- main ---------- */
  function printHead() {
    const m = meta(CUR);
    return h('div', { class: 'print-only print-head' }, h('div', { class: 'ur' }, `${CS.book} — ${CS.klass} · ${m.title.ur} (${CS.page} ${m.printed || CUR})`), h('div', { class: 'ur fill' }, `${CS.name}: ____________  ${CS.date}: ________`));
  }
  function renderMain() {
    const main = $('#main'); main.innerHTML = ''; main.setAttribute('aria-labelledby', 'tab-' + VIEW); main.dir = LTR ? 'ltr' : 'rtl';
    main.append(printHead());
    if (VIEW === 'orig') return renderOrig(main);
    if (VIEW === 'easy') return renderEasy(main);
    renderAdapted(main);
  }
  function pageHead(extra) {
    const m = meta(CUR); const stars = starCount();
    return h('div', { class: 'page-head no-print' },
      m.chapter ? h('span', { class: 'chip' }, `${t('chapter')} ${m.chapter}`) : null,
      m.printed ? h('span', { class: 'chip pink' }, `${t('adaptedFrom')} ${m.printed}`) : null, extra || null,
      stars.total ? h('span', { class: 'stars', id: 'stars', 'aria-label': `${stars.got} / ${stars.total} ${t('stars')}` }, '⭐ ', `${stars.got}/${stars.total}`) : null);
  }
  function starCount() {
    let total = 0, got = 0; if (!PAGE) return { total, got };
    for (const b of PAGE.blocks || []) if (b.t === 'activity') { total++; if (Object.keys(DONE).some((k) => k.startsWith(b.id + ':'))) got++; }
    return { total, got };
  }
  function refreshStars() { const s = $('#stars'); if (s) { const c = starCount(); s.lastChild.textContent = `${c.got}/${c.total}`; } }
  function zoomBtn(img, b) {
    const label = t('enlarge') + (b && b.alt && b.alt.ur ? ': ' + b.alt.ur : '');
    return h('button', { class: 'imgbtn', type: 'button', 'aria-haspopup': 'dialog', 'aria-label': label, title: t('enlarge'), onclick: () => openImage(img.getAttribute('src'), b) }, img, h('span', { class: 'zoom no-print', 'aria-hidden': 'true', html: ic('zoom') }));
  }
  function figure(b, cls) {
    const img = h('img', { src: b.src, alt: '', width: b.w * 2, height: b.h * 2, loading: 'lazy' });
    return h('figure', { class: cls || '' }, zoomBtn(img, b),
      b.alt && b.alt.ur ? h('div', { class: 'blk imgdesc' }, b.alt.a ? spkBtn(null) : null, U(b.alt, 'p'), EN(b.alt)) : null,
      b.cap ? h('figcaption', null, h('div', { class: 'blk', style: 'display:inline-block' }, b.cap.a ? spkBtn(null) : null, U(b.cap, 'span'), EN(b.cap))) : null);
  }
  function openImage(src, b) {
    Audio_.stop(); b = b || {};
    const d = $('#dlg-img'); wireDialog(d); d.innerHTML = ''; d.append(dlgHead(d, 'img-h', 'picture', 'zoom'));
    const body = h('div', { class: 'dlg-b imgview', dir: LTR ? 'ltr' : 'rtl' });
    body.append(h('img', { src, alt: '' }));
    let desc = null;
    if (b.cap && b.cap.ur) body.append(h('div', { class: 'blk cap' }, b.cap.a ? spkBtn(null) : null, U(b.cap, 'p'), EN(b.cap)));
    if (b.alt && b.alt.ur) { desc = U(b.alt, 'p'); body.append(h('div', { class: 'desc-h' }, t('picDesc')), h('div', { class: 'blk' }, b.alt.a ? spkBtn(null) : null, desc, EN(b.alt))); }
    d.append(body); fixSpk(body); d.showModal();
    if (desc && desc.dataset.a) Audio_.playOne(desc);
  }
  function fixSpk(root) { $$('.blk', root).forEach((bk) => { const b = bk.querySelector(':scope>.spk'); const tEl = bk.querySelector(':scope>[data-a]'); if (b && tEl) b.onclick = (e) => { e.stopPropagation(); Audio_.playOne(tEl); }; }); }

  function renderAdapted(main) {
    const p = PAGE; main.append(pageHead());
    if (p.kind === 'cover' || p.kind === 'back') {
      main.append(h('img', { class: 'cover-hero', src: `assets/pages/p${pad(CUR)}.jpg`, alt: (p.title.ur) + ' — ' + t('origPageAlt') }));
      if (p.kind === 'cover') main.append(h('div', { class: 'row no-print', style: 'justify-content:center;margin-bottom:1rem' }, h('button', { class: 'btn primary', type: 'button', html: `<span class="lbl">${t('start')}</span>`, onclick: () => go(5) }), otherBtn()));
    }
    let card = null; let hcount = 0;
    const flush = () => { if (card && card.childNodes.length) main.append(card); card = null; };
    const inCard = (el) => { if (!card) card = h('section', { class: 'card' }); card.append(el); };
    for (const b of p.blocks || []) {
      switch (b.t) {
        case 'h': { hcount++; if (card && card.childNodes.length) flush(); inCard(blk(b, hcount === 1 ? 'h1' : 'h2', 'h')); break; }
        case 'p': inCard(blk(b, 'p')); break;
        case 'list': inCard(h('ul', { class: 'outs' }, b.items.map((it) => h('li', null, blk(it, 'p'))))); break;
        case 'img': flush(); main.append(figure(b, b.w / b.h > 1.9 ? 'wide' : '')); break;
        case 'gallery': flush(); main.append(h('div', { class: 'gallery' }, b.items.map((it) => figure(it)))); break;
        case 'fact': flush(); main.append(h('aside', { class: 'box fact' }, h('div', { class: 'box-h' }, '💡 ', uiU('fact', 'span')), blk(b, 'p'))); break;
        case 'teacher': flush(); main.append(h('aside', { class: 'box teacher' }, h('div', { class: 'box-h' }, '👩‍🏫 ', uiU('teacher', 'span')), blk(b, 'p'))); break;
        case 'note': flush(); main.append(h('aside', { class: 'box note' }, blk(b, 'p'))); break;
        case 'table': flush(); main.append(table(b)); break;
        case 'activity': flush(); main.append(activity(b, { full: true })); break;
      }
    }
    flush(); fixSpk(main);
  }
  function switchLang(to) { if (to === CL) return; Audio_.stop(); location.href = location.pathname + (to === 'en' ? '?lang=en' : '') + '#/' + CUR + (VIEW !== 'adapt' ? '/' + VIEW : ''); }
  function otherBtn() { return h('button', { class: 'btn', type: 'button', lang: OL, onclick: () => switchLang(OL) }, h('span', { class: 'lbl', style: LTR ? 'font-family:var(--font-ur)' : 'font-family:var(--font-ui);line-height:1.3' }, LTR ? 'اردو میں پڑھیں' : 'Read in English')); }
  function table(b) {
    const cell = (c, tag) => h(tag, null, c && c.ur ? h('div', { class: 'blk', style: 'padding-inline-start:0' }, U(c, 'span'), EN(c)) : '');
    return h('div', { class: 'tblwrap' }, h('table', null, b.head && b.head.length ? h('thead', null, h('tr', null, b.head.map((c) => cell(c, 'th')))) : null, h('tbody', null, b.rows.map((r) => h('tr', null, r.map((c) => cell(c, 'td')))))));
  }

  /* ---------- original ---------- */
  function renderOrig(main) {
    const src = `assets/pages/p${pad(CUR)}.jpg`, pdf = `assets/pdf/p${pad(CUR)}.pdf`; const m = meta(CUR);
    main.append(h('div', { class: 'orig-view' },
      h('div', { class: 'bar' },
        PAGE ? h('button', { class: 'btn primary', type: 'button', html: ic('book') + `<span class="lbl">${t('backAdapt')}</span>`, onclick: () => go(CUR, 'adapt') }) : null,
        h('a', { class: 'btn', href: pdf, target: '_blank', rel: 'noopener', html: ic('ext') + `<span class="lbl">${t('openPdf')}</span>` })),
      h('p', { class: 'orig-note' }, t('origNote') + (m.printed ? ` (${t('page')} ${m.printed})` : '')),
      h('div', { class: 'frame' }, h('img', { src, alt: `${t('origPageAlt')} ${m.printed || CUR}: ${m.title.ur}` })),
      !PAGE ? h('p', { class: 'orig-note' }, t('notReady')) : null));
  }

  /* ---------- easy read ---------- */
  function renderEasy(main) {
    const e = PAGE.easy; const wrap = h('div', { class: 'easy' });
    wrap.append(pageHead(h('span', { class: 'chip' }, '😊 ' + t('easyRead'))));
    wrap.append(blk(e.title, 'h1', 'h'));
    if (e.image && e.image.src) wrap.append(figure(e.image));
    for (const s of e.sentences) {
      const line = U(s, 'p');
      const words = h('div', { class: 'words', 'aria-label': t('tapWord') }, s.words.map((w) => {
        const img = w.symSrc || w.imgSrc; const txt = U(w, 'span');
        return h('button', { type: 'button', class: 'wd' + (img ? '' : ' nosym'), onclick: () => Audio_.playOne(txt) }, img ? h('img', { src: img, alt: '', class: w.imgSrc && !w.symSrc ? 'pic' : '', loading: 'lazy' }) : null, txt);
      }));
      wrap.append(h('section', { class: 'sent' }, h('div', { class: 'sent-top' }, spkBtn(line), line), EN(s), words));
    }
    if (e.activity) wrap.append(activity(Object.assign({ id: `p${pad(CUR)}-easy`, label: UIA.easyAct || { ur: CS.easyAct } }, e.activity), { full: false, big: true }));
    main.append(wrap); fixSpk(wrap);
  }

  /* ---------- activities ---------- */
  function activity(a, opt) {
    const hasLv = !!a.levels; let lv = hasLv ? (store.get('lv:' + a.id) || SET.level) : null;
    const el = h('section', { class: 'act', 'aria-label': (a.label && a.label.ur) || t('activity') });
    const star = h('span', { class: 'star', 'aria-hidden': 'true' }, '⭐');
    const head = h('div', { class: 'act-h' }, h('span', null, '✏️'), U(a.label || { ur: CS.activity }, 'h2'));
    if (hasLv) {
      const mk = (k, n) => h('button', { type: 'button', 'aria-pressed': lv === k ? 'true' : 'false', onclick: () => { lv = k; store.set('lv:' + a.id, k); $$('button', lvEl).forEach((b, i) => b.setAttribute('aria-pressed', ['easy', 'moderate', 'hard'][i] === k ? 'true' : 'false')); draw(); } },
        h('span', { class: 'dots', 'aria-hidden': 'true' }, [1, 2, 3].map((i) => h('i', { class: i <= n ? 'on' : '' }))), lbl(k));
      var lvEl = h('div', { class: 'levels no-print', role: 'group', 'aria-label': t('level') }, mk('easy', 1), mk('moderate', 2), mk('hard', 3));
      head.append(lvEl);
    }
    head.append(star);
    const body = h('div', { class: 'act-b' }); const taskEl = h('div');
    body.append(h('div', { class: 'prompt' }, blk(a.prompt, 'p')), taskEl);
    const extra = opt.full && a.label && /آزمائیں/.test((a.label.ur || '') + (a.label.en || ''));
    if (extra) body.append(h('p', { class: 'orig-note no-print', style: 'margin:.8rem 0 0' }, h('span', { class: SET.ui === 'en' ? '' : 'ui-ur' }, '➕ ' + t('extraAct'))));
    if (opt.full && a.orig && !extra) {
      body.append(h('details', { class: 'orig' }, h('summary', null, lbl('origAct')), h('div', { class: 'orig-b' }, blk(a.orig, 'p'),
        h('div', { class: 'row' }, h('button', { class: 'btn sm', type: 'button', html: ic('file') + `<span class="lbl">${t('seeOrig')}</span>`, onclick: () => go(CUR, 'orig') })))));
    }
    el.append(head, body);
    const key = () => a.id + ':' + (lv || 'x');
    const ctx = {
      big: !!opt.big,
      complete(perfect) {
        DONE[key()] = 1; store.set('done', DONE); star.classList.add('on', 'pop'); refreshStars();
        if (!taskEl.querySelector('.done-banner')) {
          const msg = uiU('alldone', 'span');
          taskEl.append(h('div', { class: 'done-banner pop', role: 'status' }, h('span', { style: 'font-size:1.6rem' }, '🌟'), msg, h('button', { class: 'btn sm', type: 'button', html: `<span class="lbl">${t('tryAgain')}</span>`, onclick: draw })));
        }
      }
    };
    function draw() {
      Audio_.stop(); taskEl.innerHTML = '';
      star.classList.toggle('on', !!DONE[key()]); star.classList.remove('pop');
      const task = hasLv ? a.levels[lv] : a.task;
      (TASKS[task.kind] || TASKS.open)(task, taskEl, ctx); fixSpk(el);
    }
    draw(); return el;
  }
  function feedback(kind, headKey, fbObj, autoplay) {
    const hd = headKey ? uiU(headKey, 'b') : null; const tx = fbObj ? U(fbObj, 'span') : null;
    const box = h('div', { class: 'fb pop ' + kind, role: 'status' }, h('span', { class: 'ico', 'aria-hidden': 'true' }, kind === 'ok' ? '✅' : kind === 'no' ? '🤔' : 'ℹ️'), h('div', { style: 'flex:1' }, hd, tx, fbObj ? EN(fbObj) : null), tx && fbObj.a ? spkBtn(tx) : null);
    if (autoplay && SET.fb) { if (hd && hd.dataset.a) Audio_.playOne(hd, () => { if (tx && tx.isConnected) Audio_.playOne(tx); }); else if (tx) Audio_.playOne(tx); }
    say((hd ? hd.textContent + ' ' : '') + (fbObj ? fbObj.ur : ''));
    return box;
  }
  const praiseKey = () => 'praise' + (1 + Math.floor(Math.random() * 3));
  function optButton(o, ctx, extraCls) {
    const img = o.symSrc || o.imgSrc; const txt = U(o, 'span'); const col = ctx.big || !!o.imgSrc;
    const b = h('button', { type: 'button', class: 'opt ' + (col && img ? 'col ' : '') + (extraCls || '') },
      img ? h('img', { src: img, alt: '', class: o.symSrc ? 'sym' : 'pic', loading: 'lazy' }) : null, h('span', { class: 'optx' }, txt, EN(o)), h('span', { class: 'mark', 'aria-hidden': 'true' }));
    if (false) b.append(h('span', { class: 'spk minispk no-print', role: 'button', tabindex: '0', 'aria-label': t('listenThis'), html: ic('vol'), onclick: (e) => { e.stopPropagation(); Audio_.playOne(txt); }, onkeydown: (e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); e.stopPropagation(); Audio_.playOne(txt); } } }));
    return b;
  }
  function setMark(b, ok) { b.classList.add(ok ? 'right' : 'wrong'); b.querySelector('.mark').textContent = ok ? '✓' : '✗'; b.setAttribute('aria-label', b.textContent.trim() + (ok ? ' — ' + CS.tTrue : ' — ' + CS.tFalse)); }

  const TASKS = {
    mcq(task, root, ctx, kind) {
      let left = task.questions.length, clean = true;
      task.questions.forEach((q, qi) => {
        const qEl = h('div', { class: 'q' }); let tries = 0, done = false;
        let qText;
        if (kind === 'fill') {
          qText = U(null, 'p'); if (q.q.a) qText.dataset.a = q.q.a;
          const parts = q.q.ur.split('___'); fillWords(qText, parts[0]);
          var blank = h('span', { class: 'blank' }, ' '); qText.append(blank);
          const tail = document.createElement('span'); fillWords(tail, parts[1] || ''); $$('.w', tail).forEach((w) => { w.dataset.s = +w.dataset.s + parts[0].length + 3; }); qText.append(...tail.childNodes);
        } else qText = U(q.q, 'p');
        qEl.append(h('div', { class: 'q-text' }, task.questions.length > 1 ? h('span', { class: 'q-num', 'aria-hidden': 'true' }, qi + 1) : null, h('div', { class: 'blk blkq' }, q.q.a ? spkBtn(qText) : null, qText, EN(q.q))));
        if (q.imgSrc) qEl.append(h('div', { class: 'q-imgw' }, zoomBtn(h('img', { class: 'q-img', src: q.imgSrc, alt: '' }), null)));
        const opts = kind === 'tf' ? [{ ur: CS.tTrue, en: OS.tTrue, a: (UIA.tTrue || {}).a, _v: true, _m: '✓' }, { ur: CS.tFalse, en: OS.tFalse, a: (UIA.tFalse || {}).a, _v: false, _m: '✗' }] : q.options;
        const ans = kind === 'tf' ? (q.answer ? 0 : 1) : q.answer;
        const grid = h('div', { class: 'opts', role: 'group' }); const fbSlot = h('div');
        const btns = opts.map((o, oi) => {
          const b = optButton(o, ctx);
          if (kind === 'tf') b.prepend(h('span', { 'aria-hidden': 'true', style: 'font-size:1.4rem;font-weight:700' }, o._m));
          b.addEventListener('click', () => {
            if (done || b.disabled) return;
            if (oi === ans) {
              done = true; setMark(b, true); btns.forEach((x) => { x.disabled = true; }); if (blank) blank.textContent = o.ur;
              fbSlot.innerHTML = ''; fbSlot.append(feedback('ok', praiseKey(), q.fb, true)); if (--left === 0) ctx.complete(clean);
            } else {
              tries++; clean = false; setMark(b, false); b.disabled = true; b.classList.add('shake');
              const remaining = btns.filter((x) => !x.disabled).length;
              if (remaining <= 1) {
                done = true; btns.forEach((x, i) => { x.disabled = true; if (i === ans) setMark(x, true); }); if (blank) blank.textContent = opts[ans].ur;
                fbSlot.innerHTML = ''; fbSlot.append(feedback('info', 'reveal', q.fb, true)); if (--left === 0) ctx.complete(false);
              } else { fbSlot.innerHTML = ''; fbSlot.append(feedback('no', 'retry', null, true)); }
            }
          });
          return b;
        });
        grid.append(...btns); qEl.append(grid, fbSlot); root.append(qEl);
      });
    },
    tf(task, root, ctx) { TASKS.mcq(task, root, ctx, 'tf'); },
    fill(task, root, ctx) { TASKS.mcq(task, root, ctx, 'fill'); },
    match(task, root, ctx) {
      const n = task.pairs.length; let sel = null, left = n, mcount = 0; const fbSlot = h('div');
      const colA = h('div', { class: 'col' }), colB = h('div', { class: 'col' });
      const mk = (o, side, idx) => { const b = optButton(o, ctx); b.dataset.side = side; b.dataset.i = idx; b.addEventListener('click', () => pick(b)); return b; };
      const A = task.pairs.map((p, i) => mk(p.a, 'a', i)); const B = shuffleDiff(task.pairs.map((p, i) => mk(p.b, 'b', i)));
      function pick(b) {
        if (b.disabled) return;
        if (!sel || sel.dataset.side === b.dataset.side) { if (sel) { sel.classList.remove('sel'); sel.setAttribute('aria-pressed', 'false'); } sel = b; b.classList.add('sel'); b.setAttribute('aria-pressed', 'true'); return; }
        const ok = sel.dataset.i === b.dataset.i; fbSlot.innerHTML = '';
        if (ok) {
          [sel, b].forEach((x) => { x.classList.remove('sel'); x.classList.add('m' + (mcount % 7), 'pop'); x.disabled = true; x.prepend(h('span', { class: 'badge', 'aria-hidden': 'true' }, mcount + 1)); });
          mcount++; sel = null; say(t('matched'));
          if (--left === 0) { fbSlot.append(feedback('ok', praiseKey(), null, true)); ctx.complete(true); }
        } else { b.classList.add('shake'); setTimeout(() => b.classList.remove('shake'), 400); sel.classList.remove('sel'); sel.setAttribute('aria-pressed', 'false'); sel = null; fbSlot.append(feedback('no', 'retry', null, true)); }
      }
      colA.append(...A); colB.append(...B);
      root.append(h('p', { class: 'en', style: 'display:block' }, t('pickPair')), h('div', { class: 'match' }, colA, colB), fbSlot);
    },
    sort(task, root, ctx) {
      let left = task.items.length; const fbSlot = h('div');
      const bins = task.groups.map((g) => { const got = h('div', { class: 'got' }); return { el: h('div', { class: 'bin' }, h('div', { class: 'ur' }, g.symSrc ? h('img', { class: 'sym', src: g.symSrc, alt: '' }) : null, U(g, 'span')), EN(g), got), got }; });
      root.append(h('div', { class: 'bins' }, bins.map((b) => b.el)));
      const list = h('div');
      shuffle(task.items).forEach((it) => {
        const img = it.symSrc || it.imgSrc; const txt = U(it, 'span');
        const row = h('div', { class: 'sort-item' }, h('div', { class: 'what' }, img ? h('img', { src: img, alt: '', class: it.symSrc ? 'sym' : 'pic' }) : null, h('div', null, txt, EN(it)), it.a ? spkBtn(txt, 'no-print') : null));
        const ch = h('div', { class: 'choices', role: 'group', 'aria-label': t('putIn') });
        task.groups.forEach((g, gi) => {
          const b = h('button', { class: 'btn', type: 'button' }, h('span', { class: 'ur' }, g.ur));
          b.addEventListener('click', () => {
            fbSlot.innerHTML = '';
            if (gi === it.group) {
              row.remove(); bins[gi].got.append(h('span', { class: 'tag pop' }, h('span', { class: 'ur' }, it.ur), ' ✓')); say(`${it.ur}: ${g.ur} ✓`);
              if (--left === 0) { fbSlot.append(feedback('ok', praiseKey(), null, true)); ctx.complete(true); }
            } else { b.disabled = true; row.classList.add('shake'); setTimeout(() => row.classList.remove('shake'), 400); fbSlot.append(feedback('no', 'retry', null, true)); }
          });
          ch.append(b);
        });
        row.append(ch); list.append(row);
      });
      root.append(list, fbSlot);
    },
    order(task, root, ctx) {
      let items = shuffleDiff(task.items.map((it, i) => ({ it, i }))); let tries = 0; const ol = h('ol', { class: 'order' }); const fbSlot = h('div');
      function draw(marks) {
        ol.innerHTML = '';
        items.forEach((x, pos) => {
          const txt = U(x.it, 'span');
          ol.append(h('li', { class: marks ? (x.i === pos ? 'good' : 'bad') : '' }, h('span', { class: 'q-num', 'aria-hidden': 'true' }, pos + 1), x.it.symSrc ? h('img', { src: x.it.symSrc, alt: '', style: 'width:54px;height:54px;background:#fff;border-radius:8px' }) : null, h('div', { style: 'flex:1' }, txt, EN(x.it)), x.it.a ? spkBtn(txt, 'no-print') : null,
            h('span', { class: 'mv no-print' },
              h('button', { class: 'btn sm', type: 'button', disabled: pos === 0, 'aria-label': `${t('up')}: ${x.it.ur}`, html: ic('up'), onclick: () => move(pos, -1) }),
              h('button', { class: 'btn sm', type: 'button', disabled: pos === items.length - 1, 'aria-label': `${t('down')}: ${x.it.ur}`, html: ic('down'), onclick: () => move(pos, 1) }))));
        });
      }
      function move(pos, d) { const j = pos + d;[items[pos], items[j]] = [items[j], items[pos]]; draw(); const b = $$('.mv .btn', ol)[j * 2 + (d < 0 ? 0 : 1)]; if (b && !b.disabled) b.focus(); else { const alt = $$('.mv .btn', ol)[j * 2 + (d < 0 ? 1 : 0)]; if (alt) alt.focus(); } say(`${items[j].it.ur}: ${j + 1}`); }
      const ctl = h('div', { class: 'row ctl' }, h('button', { class: 'btn primary', type: 'button', html: `<span class="lbl">${t('check')}</span>`, onclick: () => {
        fbSlot.innerHTML = ''; const ok = items.every((x, pos) => x.i === pos); draw(true);
        if (ok) { fbSlot.append(feedback('ok', praiseKey(), null, true)); ctx.complete(tries === 0); }
        else { tries++; fbSlot.append(feedback('no', 'orderBad', null, true)); if (tries >= 2 && !ctl.querySelector('.showans')) ctl.append(h('button', { class: 'btn showans', type: 'button', html: `<span class="lbl">${t('showAns')}</span>`, onclick: () => { items = task.items.map((it, i) => ({ it, i })); draw(true); fbSlot.innerHTML = ''; ctx.complete(false); } })); }
      } }));
      draw(); root.append(ol, ctl, fbSlot);
    },
    open(task, root, ctx) {
      const modeK = { write: ['mWrite', '✍️'], draw: ['mDraw', '🎨'], talk: ['mTalk', '💬'], do: ['mDo', '🤲'] }[task.mode] || ['mDo', '🤲'];
      root.append(h('div', { class: 'open-mode' }, h('span', { 'aria-hidden': 'true' }, modeK[1]), h('span', { class: 'ur' }, CS[modeK[0]]), SET.ui !== CL ? h('span', null, '· ' + OS[modeK[0]]) : null));
      if (task.steps && task.steps.length) root.append(h('ol', { class: 'steps' }, task.steps.map((s) => h('li', null, h('div', { class: 'blk', style: 'padding-inline-start:0;padding-inline-end:2.6rem' }, U(s, 'p'), EN(s), s.a ? h('span', { style: 'position:absolute;inset-inline-end:0;top:.3rem' }, spkBtn(null)) : null)))));
      $$('ol.steps .blk', root).forEach((bk) => { const b = bk.querySelector('.spk'), tx = bk.querySelector('[data-a]'); if (b && tx) b.onclick = () => Audio_.playOne(tx); });
      const aid = root.closest('.act') ? null : null;
      if (task.mode === 'write') {
        const k = 'ans:' + CUR + ':' + (task.steps ? task.steps.length : 0) + ':' + ((task.model && task.model.a) || '') + ':' + $$('textarea.ans').length;
        const ta = h('textarea', { class: 'ans', lang: CL, dir: LTR ? 'ltr' : 'rtl', 'aria-label': t('writeHere'), placeholder: CS.writeHere + '…' }); ta.value = store.get(k, ''); ta.addEventListener('input', () => store.set(k, ta.value)); root.append(ta);
      }
      if (task.checklist && task.checklist.length) root.append(h('ul', { class: 'checks' }, task.checklist.map((c) => { const tx = U(c, 'span'); return h('li', null, h('label', null, h('input', { type: 'checkbox' }), h('span', { style: 'flex:1' }, tx, EN(c)), c.a ? spkBtn(tx, 'no-print') : null)); })));
      const row = h('div', { class: 'row ctl' });
      if (task.model) {
        const mtx = U(task.model, 'p'); const mb = h('div', { class: 'fb info model-b', hidden: true }, h('span', { class: 'ico', 'aria-hidden': 'true' }, '📝'), h('div', { style: 'flex:1' }, h('b', { class: 'ur' }, CS.model), mtx, EN(task.model)), task.model.a ? spkBtn(mtx) : null);
        const btn = h('button', { class: 'btn', type: 'button', 'aria-expanded': 'false', html: `<span class="lbl">${t('model')}</span>`, onclick: () => { mb.hidden = !mb.hidden; btn.setAttribute('aria-expanded', String(!mb.hidden)); btn.querySelector('.lbl').textContent = t(mb.hidden ? 'model' : 'hideModel'); } });
        row.append(btn); root.append(row, mb);
      } else root.append(row);
      row.prepend(h('button', { class: 'btn primary', type: 'button', html: `✓ <span class="lbl">${t('done')}</span>`, onclick: () => ctx.complete(true) }));
    }
  };

  /* ---------- dialogs ---------- */
  function dlgHead(d, id, key, icon) {
    return h('div', { class: 'dlg-h' }, h('h2', { id }, h('span', { html: ic(icon) }), lbl(key)), h('button', { class: 'btn sm', type: 'button', 'aria-label': t('close'), html: ic('x'), onclick: () => d.close() }));
  }
  function wireDialog(d) { if (d._w) return; d._w = 1; d.addEventListener('click', (e) => { if (e.target === d) d.close(); }); d.addEventListener('close', () => Audio_.stop()); }
  function openToc() {
    const d = $('#dlg-toc'); wireDialog(d); d.innerHTML = ''; d.append(dlgHead(d, 'toc-h', 'menu', 'menu'));
    const body = h('nav', { class: 'dlg-b', 'aria-labelledby': 'toc-h' });
    const groups = {}; IDX.pages.forEach((p) => { const k = p.chapter || (p.n > 50 ? 99 : 0); (groups[k] = groups[k] || []).push(p); });
    Object.keys(groups).map(Number).sort((a, b) => a - b).forEach((c) => {
      const title = c === 0 ? { ur: CS.front, en: OS.front } : c === 99 ? { ur: CS.back, en: OS.back } : (IDX.chapters[c] || { ur: CS.chapter + ' ' + c });
      const open = groups[c].some((p) => p.n === CUR);
      body.append(h('details', { class: 'toc-group', open }, h('summary', null, h('span', { class: 'num', 'aria-hidden': 'true' }, c === 0 ? '•' : c === 99 ? '★' : c), h('span', { class: 'ur', lang: CL }, title.ur, SET.ui !== CL || SET.en ? h('span', { class: 'en', style: 'display:block' }, title.en || '') : null)),
        h('ul', null, groups[c].map((p) => h('li', null, h('a', { href: '#/' + p.n, 'aria-current': p.n === CUR ? 'page' : null, onclick: () => d.close() }, h('span', { class: 'ur', lang: CL }, p.title.ur), p.act ? h('span', { title: t('activity'), 'aria-label': t('activity') }, '✏️') : null, h('small', null, `${t('page')} ${p.n}`)))))));
    });
    d.append(body); d.showModal(); const cur = d.querySelector('[aria-current]'); if (cur) { cur.scrollIntoView({ block: 'center' }); cur.focus(); }
  }
  const WHO = { all: ['forAll', '🌟'], vision: ['forVision', '👁️'], hearing: ['forHearing', '👂'], motor: ['forMotor', '✋'], cognitive: ['forCognitive', '🧠'], teacher: ['forTeacher', '👩‍🏫'] };
  function openHint() {
    if (!PAGE || !PAGE.hint) return; Audio_.stop();
    const d = $('#dlg-hint'); wireDialog(d); d.innerHTML = ''; d.append(dlgHead(d, 'hint-h', 'hint', 'bulb'));
    const body = h('div', { class: 'dlg-b', dir: LTR ? 'ltr' : 'rtl' });
    const els = [];
    PAGE.hint.forEach((x) => {
      const w = WHO[x.for] || WHO.all; const tx = U(x, 'p'); els.push(tx);
      body.append(h('div', { class: 'hint' }, h('div', { class: 'who' }, h('span', { class: 'ic', 'aria-hidden': 'true' }, w[1]), h('span', { class: SET.ui === 'en' ? '' : 'ur' }, t(w[0]))), h('div', { class: 'txt' }, tx, EN(x)), x.a ? spkBtn(tx) : null));
    });
    body.prepend(h('div', { class: 'row', style: 'margin:0 0 .7rem' }, h('button', { class: 'btn primary', type: 'button', html: ic('play') + `<span class="lbl">${t('listen')}</span>`, onclick: () => Audio_.playQueue(els) })));
    d.append(body); d.showModal();
  }
  function openSettings() {
    const d = $('#dlg-set'); wireDialog(d); d.innerHTML = ''; d.append(dlgHead(d, 'set-h', 'settings', 'gear'));
    const seg = (key, legend, opts) => h('fieldset', null, h('legend', null, lbl(legend)), h('div', { class: 'seg' }, opts.map(([v, lk, raw]) => h('button', { type: 'button', 'aria-pressed': String(SET[key] === v), onclick: () => { SET[key] = v; applySettings(); Audio_.setRate(); if (key === 'ui' || key === 'level') { renderTop(); renderMain(); renderBottom(); } openSettings(); } }, raw ? h('span', { class: 'lbl', style: 'font-family:var(--font-ui)' }, raw) : lbl(lk)))));
    const sw = (key, lk) => h('label', { class: 'switch' }, h('input', { type: 'checkbox', checked: SET[key] || null, onchange: (e) => { SET[key] = e.target.checked; applySettings(); } }), lbl(lk));
    d.append(h('div', { class: 'dlg-b set' },
      seg('fs', 'sText', [[0.85, '', 'A−'], [1, '', 'A'], [1.2, '', 'A+'], [1.45, '', 'A++']]),
      h('fieldset', null, h('legend', null, lbl('sBook')), h('div', { class: 'seg' }, [['ur', 'اردو'], ['en', 'English']].map(([v, raw]) => h('button', { type: 'button', 'aria-pressed': String(CL === v), onclick: () => switchLang(v) }, h('span', { class: 'lbl', style: 'font-family:var(--font-ui)' }, raw))))),
      LTR ? null : seg('font', 'sFont', [['nastaliq', 'fNast'], ['naskh', 'fNaskh']]),
      seg('theme', 'sTheme', [['light', 'tLight'], ['dark', 'tDark'], ['contrast', 'tContrast']]),
      seg('spacing', 'sSpace', [['normal', 'spN'], ['wide', 'spW']]),
      seg('rate', 'sSpeed', [[0.8, 'slow'], [1, 'normal'], [1.2, 'fast']]),
      seg('level', 'sLevel', [['easy', 'easy'], ['moderate', 'moderate'], ['hard', 'hard']]),
      seg('ui', 'sUi', [['ur', '', 'اردو'], ['en', '', 'English']]),
      h('fieldset', null, h('legend', null, lbl('settings')), sw('hl', 'sHl'), sw('fb', 'sFb'), sw('imgs', 'sImg'), sw('en', LTR ? 'sUr' : 'sEn'), sw('motion', 'sMotion')),
      h('fieldset', null, h('legend', null, lbl('sKeys')), h('p', { class: 'about', html: '<kbd>←</kbd> <kbd>→</kbd> pages · <kbd>P</kbd> listen / pause · <kbd>H</kbd> hint · <kbd>E</kbd> easy read · <kbd>O</kbd> original · <kbd>L</kbd> lesson · <kbd>M</kbd> contents · <kbd>Esc</kbd> stop' })),
      h('fieldset', null, h('legend', null, lbl('about')), h('p', { class: 'about', html: 'Accessible Digital Textbook adapted from <b>واقفیتِ عامہ (General Knowledge), Class 2</b>, Punjab Curriculum and Textbook Board, Lahore (Single National Curriculum 2020). Original wording is kept; activities, hints and Easy Read pages are adaptations and every page links back to its original.<br>Pictographic symbols: © Government of Aragón, author Sergio Palao, <a href="https://arasaac.org" target="_blank" rel="noopener">ARASAAC</a>, licence CC BY-NC-SA.<br>' + (LTR ? 'This English edition is a translation made for this adaptation, not the Board’s own English-medium book; the original Urdu is available under “Show Urdu text” and on every Original page.<br>Voice: Microsoft neural English (India) voice “Neerja”, pre-recorded.' : 'Voice: Microsoft neural Urdu (Pakistan) voice “Uzma”, pre-recorded.') }))));
    if (!d.open) d.showModal();
  }

  /* ---------- keyboard ---------- */
  document.addEventListener('keydown', (e) => {
    if (e.altKey || e.ctrlKey || e.metaKey) return; const tg = e.target; const tag = tg.tagName;
    if (tag === 'INPUT' || tag === 'TEXTAREA' || tag === 'SELECT' || tg.isContentEditable) return;
    if (document.querySelector('dialog[open]')) return;
    const rtl = document.documentElement.dir === 'rtl'; const k = e.key;
    if (k === 'ArrowLeft') { const n = CUR + (rtl ? 1 : -1); if (n >= 1 && n <= IDX.total) go(n); e.preventDefault(); }
    else if (k === 'ArrowRight') { const n = CUR + (rtl ? -1 : 1); if (n >= 1 && n <= IDX.total) go(n); e.preventDefault(); }
    else if (k === 'p' || k === 'P') { if (VIEW !== 'orig') setListen(!LISTEN); }
    else if (k === 'h' || k === 'H') openHint();
    else if (k === 'e' || k === 'E') { if (PAGE && PAGE.easy) go(CUR, 'easy'); }
    else if (k === 'o' || k === 'O') go(CUR, 'orig');
    else if (k === 'l' || k === 'L') go(CUR, 'adapt');
    else if (k === 'm' || k === 'M') openToc();
    else if (k === 'Escape') Audio_.stop();
  });

  applySettings();
  window.addEventListener('hashchange', route);
  route();
})();
