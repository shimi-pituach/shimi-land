// portal-core.js — v1.0 — ליבה משותפת לפורטל ההגשות: מעקב מדויק + חסימות best-effort
// רשת שימי — שימי פיתוח, 21/10/2026
(function () {
  const API = 'https://base44.app/api/apps/6a901f55a4d9a9b76a095a77/functions';
  const PAGE = (document.body && document.body.dataset.page) || location.pathname.split('/').pop() || 'unknown';

  // ---------- זיהוי מבקר וסשן ----------
  function uuid() { return (crypto.randomUUID ? crypto.randomUUID() : 'x' + Date.now() + Math.random().toString(36).slice(2)).replace(/-/g, ''); }
  let vid = null;
  try { vid = localStorage.getItem('vh_vid'); if (!vid) { vid = 'v-' + uuid(); localStorage.setItem('vh_vid', vid); } } catch (e) { vid = 'v-nostorage-' + uuid(); }
  const SID = 's-' + uuid();
  const signedAt = Date.now();
  let visibleMs = 0;         // השהות בפועל (רק כשהלשונית גלויה)
  let lastTick = Date.now();
  let hidden = document.hidden;
  setInterval(() => {
    const now = Date.now();
    if (!hidden) visibleMs += now - lastTick;
    lastTick = now;
  }, 1000);
  document.addEventListener('visibilitychange', () => { hidden = document.hidden; lastTick = Date.now(); });

  // ---------- שליחת אירועים ----------
  const queue = [];
  let flushing = false;
  function track(kind, target, extra) {
    queue.push({ kind: String(kind).slice(0, 60), page: PAGE, target: String(target || '').slice(0, 160),
      visitor_id: vid, session_id: SID, dwell_ms: Math.round(visibleMs), ...(extra || {}) });
    if (queue.length >= 15) flush();
  }
  async function flush(sync) {
    if (flushing || !queue.length) return;
    flushing = true;
    const batch = queue.splice(0, 60);
    const body = JSON.stringify({ events: batch });
    try {
      if (sync && navigator.sendBeacon) {
        navigator.sendBeacon(API + '/portalEvent', new Blob([body], { type: 'application/json' }));
      } else {
        await fetch(API + '/portalEvent', { method: 'POST', headers: { 'Content-Type': 'application/json' },
          body, keepalive: true });
      }
    } catch (e) { /* תיעוד בצד השרת בלבד */ }
    flushing = false;
  }
  setInterval(() => flush(false), 12000);        // משלוח מחזורי
  window.addEventListener('pagehide', () => { track('page_leave', location.pathname, { dwell_ms: Math.round(visibleMs) }); flush(true); });

  // ---------- מעקב קליקים ופעולות ----------
  document.addEventListener('click', (ev) => {
    const el = ev.target.closest('a,button,input,select,textarea,canvas,[data-track]') || ev.target;
    const label = (el.getAttribute('data-track') || el.id || el.getAttribute('aria-label') || el.tagName || '?').slice(0, 120);
    track('click', label);
  }, true);
  document.addEventListener('change', (ev) => {
    const el = ev.target;
    track('change', (el.id || el.name || el.tagName || '?').slice(0, 120));
  }, true);
  let scrollMarks = {};
  window.addEventListener('scroll', () => {
    const p = Math.round((window.scrollY + window.innerHeight) / document.documentElement.scrollHeight * 100);
    for (const m of [25, 50, 75, 95]) {
      if (p >= m && !scrollMarks[m]) { scrollMarks[m] = 1; track('scroll', m + '%'); }
    }
  }, { passive: true });

  // ---------- חסימות best-effort ----------
  document.addEventListener('contextmenu', (e) => { e.preventDefault(); track('blocked', 'contextmenu'); });
  document.addEventListener('copy', (e) => { e.preventDefault(); e.clipboardData && e.clipboardData.setData('text/plain', '⛔ העתקה חסומה — פורטל רשת שימי'); track('blocked', 'copy'); });
  document.addEventListener('cut', (e) => { e.preventDefault(); track('blocked', 'cut'); });
  document.addEventListener('selectstart', (e) => { if (!e.target.closest('input,textarea')) e.preventDefault(); });
  document.addEventListener('dragstart', (e) => e.preventDefault());
  // הצפנת מקור בזמן שהעמוד מוסתר — מקשה על צילום מסך/מעבר לשונית (best effort)
  const veil = document.createElement('div');
  veil.style.cssText = 'position:fixed;inset:0;z-index:2147483647;background:#0b0e14;color:#fff;display:none;align-items:center;justify-content:center;font:600 20px system-ui;direction:rtl';
  veil.textContent = '🔒 התוכן מוגן — חזרה לפורטל רשת שימי';
  document.body && document.body.appendChild(veil);
  document.addEventListener('visibilitychange', () => {
    veil.style.display = document.hidden ? 'flex' : 'none';
    if (document.hidden) track('blocked', 'tab_hidden_screenshot_guard');
  });
  window.addEventListener('blur', () => { veil.style.display = 'flex'; });
  window.addEventListener('focus', () => { veil.style.display = document.hidden ? 'flex' : 'none'; });
  document.addEventListener('keyup', (e) => {
    const k = (e.key || '').toLowerCase();
    if (e.key === 'PrintScreen') { track('blocked', 'printscreen'); navigator.clipboard && navigator.clipboard.writeText('⛔').catch(() => {}); veil.style.display = 'flex'; setTimeout(() => veil.style.display = 'none', 1500); }
  });
  document.addEventListener('keydown', (e) => {
    const k = (e.key || '').toLowerCase();
    const combo = (e.ctrlKey || e.metaKey);
    if (combo && ['p', 's', 'u'].includes(k)) { e.preventDefault(); track('blocked', 'ctrl+' + k); }
    if (combo && e.shiftKey && ['i', 'j', 'c'].includes(k)) { e.preventDefault(); track('blocked', 'devtools_' + k); }
    if (k === 'f12') { e.preventDefault(); track('blocked', 'f12'); }
  });

  // חשיפה לעמודים
  window.PORTAL = { API, track, flush, vid, SID, PAGE };
  track('page_enter', location.pathname);
})();
