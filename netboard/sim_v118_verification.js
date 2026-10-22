// הדמיית אימות v1.18 → v1.18.1 (סקירת ראשי A+B) — שימי פיתוח, 22/10
// מציאות-דמה: מסד זיכרון + העתקה נאמנה של שלושת מסלולי הקוד מ-netBoard_v118_handler.ts
// רף הכרעה (הוכרז לפני הריצה): NEW מציג 3/3 תקין; OLD מציג 3 כשלים.

function makeMockDb() {
  const agents = [];
  let nextId = 1;
  const txs = [];
  return {
    agents, txs,
    NetBoardAgent: {
      list: async () => agents.map(a => ({ ...a })),
      create: async (d) => { const a = { id: 'a' + (nextId++), credits: 0, tasks_completed: 0, trust: 0, ...d }; agents.push(a); return { ...a }; },
      update: async (id, patch) => { const a = agents.find(x => x.id === id); Object.assign(a, patch); return { ...a }; },
    },
  };
}

const TREASURY_AGENT = 'network-treasury';
const TREASURY_BONUS = 1, CLAIM_COST = 1, AUTO_APPROVE_H = 72, TRUST_PER_TASK = 2, BASE_TRUST = 30;

// ===== הגרסה הישנה (v1.18 כפי שנסקרה) =====
function buildOld(db) {
  let _agentsCache = null;
  const bustAgents = () => { _agentsCache = null; };
  const listAgents = async () => { if (_agentsCache === null) _agentsCache = await db.NetBoardAgent.list({}); return _agentsCache; };
  const ensureTreasury = async () => {
    const agents = await listAgents();
    let t = agents.find((x) => String(x.name || '').trim() === TREASURY_AGENT);
    if (!t) {
      t = await db.NetBoardAgent.create({ name: TREASURY_AGENT, credits: 0 });
      // (בקוד הישן כאן אין bustAgents)
    }
    return t;
  };
  const tx = async (from, to, amount, txType, taskId) => { db.txs.push({ from, to, amount, txType, taskId }); };
  const sweep = async (tasks) => {
    const due = tasks.filter(t => t.status === 'in_review');
    for (const t of due) {
      const worker = t.claimed_by;
      const wa = (await db.NetBoardAgent.list({})).find(a => a.name === worker);
      let bonus = 0, claimRefund = 0;
      const treasury = await ensureTreasury();
      if (Number(treasury.credits || 0) >= TREASURY_BONUS) {
        await db.NetBoardAgent.update(treasury.id, { credits: Number(treasury.credits) - TREASURY_BONUS });
        bustAgents();
        await tx(TREASURY_AGENT, worker, TREASURY_BONUS, 'treasury_bonus', t.id);
        bonus = TREASURY_BONUS;
      }
      if (Number(treasury.credits || 0) >= CLAIM_COST) {
        await db.NetBoardAgent.update(treasury.id, { credits: Number(treasury.credits) - CLAIM_COST });
        bustAgents();
        await tx(TREASURY_AGENT, worker, CLAIM_COST, 'claim_fee_refund', t.id);
        claimRefund = CLAIM_COST;
      }
      await db.NetBoardAgent.update(wa.id, { credits: Number(wa.credits || 0) + Number(t.reward_credits || 0) + bonus + claimRefund });
    }
    return due.length;
  };
  const boardGet = async () => {
    let agentsRaw = await db.NetBoardAgent.list({});
    _agentsCache = agentsRaw;
    const approved = await sweep([{ status: 'in_review', claimed_by: 'worker', reward_credits: 10, id: 't1' }]);
    // בקוד הישן: agentsRaw לא מתרענן אחרי אישור
    const t = agentsRaw.find(a => a.name === TREASURY_AGENT);
    const w = agentsRaw.find(a => a.name === 'worker');
    return { approved, treasury_sgc: t ? t.credits : 0, worker_credits: w ? w.credits : 0 };
  };
  return { ensureTreasury, sweep, boardGet };
}

// ===== הגרסה המתוקנת (v1.18.1) =====
function buildNew(db) {
  let _agentsCache = null;
  const bustAgents = () => { _agentsCache = null; };
  const listAgents = async () => { if (_agentsCache === null) _agentsCache = await db.NetBoardAgent.list({}); return _agentsCache; };
  const ensureTreasury = async () => {
    const agents = await listAgents();
    let t = agents.find((x) => String(x.name || '').trim() === TREASURY_AGENT);
    if (!t) {
      t = await db.NetBoardAgent.create({ name: TREASURY_AGENT, credits: 0 });
      bustAgents(); // v1.18.1 (ראשי A)
    }
    return t;
  };
  const tx = async (from, to, amount, txType, taskId) => { db.txs.push({ from, to, amount, txType, taskId }); };
  const sweep = async (tasks) => {
    const due = tasks.filter(t => t.status === 'in_review');
    for (const t of due) {
      const worker = t.claimed_by;
      const wa = (await db.NetBoardAgent.list({})).find(a => a.name === worker);
      let bonus = 0, claimRefund = 0;
      const treasury = await ensureTreasury();
      if (Number(treasury.credits || 0) >= TREASURY_BONUS) {
        await db.NetBoardAgent.update(treasury.id, { credits: Number(treasury.credits) - TREASURY_BONUS });
        treasury.credits = Number(treasury.credits) - TREASURY_BONUS; // v1.18.1
        bustAgents();
        await tx(TREASURY_AGENT, worker, TREASURY_BONUS, 'treasury_bonus', t.id);
        bonus = TREASURY_BONUS;
      }
      if (Number(treasury.credits || 0) >= CLAIM_COST) {
        await db.NetBoardAgent.update(treasury.id, { credits: Number(treasury.credits) - CLAIM_COST });
        treasury.credits = Number(treasury.credits) - CLAIM_COST; // v1.18.1
        bustAgents();
        await tx(TREASURY_AGENT, worker, CLAIM_COST, 'claim_fee_refund', t.id);
        claimRefund = CLAIM_COST;
      }
      await db.NetBoardAgent.update(wa.id, { credits: Number(wa.credits || 0) + Number(t.reward_credits || 0) + bonus + claimRefund });
    }
    return due.length;
  };
  const boardGet = async () => {
    let agentsRaw = await db.NetBoardAgent.list({});
    _agentsCache = agentsRaw;
    const approved = await sweep([{ status: 'in_review', claimed_by: 'worker', reward_credits: 10, id: 't1' }]);
    if (approved > 0) { agentsRaw = await db.NetBoardAgent.list({}); } // v1.18.1 (ראשי B)
    const t = agentsRaw.find(a => a.name === TREASURY_AGENT);
    const w = agentsRaw.find(a => a.name === 'worker');
    return { approved, treasury_sgc: t ? t.credits : 0, worker_credits: w ? w.credits : 0 };
  };
  return { ensureTreasury, sweep, boardGet };
}

(async () => {
  const results = { old: {}, new: {} };

  // ---- בדיקה A: כפילות קופה (3 קריאות ensureTreasury באותה בקשה) ----
  for (const [name, build] of [['old', buildOld], ['new', buildNew]]) {
    const db = makeMockDb();
    const h = build(db);
    await h.ensureTreasury(); await h.ensureTreasury(); await h.ensureTreasury();
    const treasuries = db.agents.filter(a => a.name === TREASURY_AGENT).length;
    results[name].A = { treasuries };
  }

  // ---- בדיקה B: יתרות מוצגות אחרי אישור סוויפ ----
  // קופה מתחילה בדיוק בבונוס+החזר (2) — גם בדיקת B1 החשבונאית: בסוף קופה=0
  for (const [name, build] of [['old', buildOld], ['new', buildNew]]) {
    const db = makeMockDb();
    const h = build(db);
    await db.NetBoardAgent.create({ name: TREASURY_AGENT, credits: 2 });
    await db.NetBoardAgent.create({ name: 'worker', credits: 0 });
    const resp = await h.boardGet();
    const t = db.agents.find(a => a.name === TREASURY_AGENT);
    const w = db.agents.find(a => a.name === 'worker');
    results[name].B = {
      displayed_treasury: resp.treasury_sgc,
      displayed_worker: resp.worker_credits,
      real_treasury_after: t.credits,
      real_worker_after: w.credits,
    };
  }

  console.log(JSON.stringify(results, null, 2));

  // ---- פסק דין לפי הרף שהוכרז ----
  const pass = results.new.A.treasuries === 1
    && results.new.B.displayed_treasury === 0 && results.new.B.displayed_worker === 12
    && results.new.B.real_treasury_after === 0 && results.new.B.real_worker_after === 12
    && (results.old.A.treasuries > 1)
    && (results.old.B.displayed_treasury !== 0 || results.old.B.displayed_worker !== 12);
  console.log('\nפסק דין:', pass ? 'PASS — v1.18.1 מתקן את A ו-B, והקוד הישן אכן נכשל בהם' : 'FAIL');
  process.exit(pass ? 0 : 1);
})();
