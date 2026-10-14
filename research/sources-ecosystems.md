# מפקד סוכני AI אוטונומיים — מערכות אקולוגיות ופריסות ציבוריות

**תאריך דוח:** 13/10/2026  
**נערך עבור:** רשת שימי (Shimi Network Research)  
**מחבר:** עוזר מחקר אקולוגי — רשת שימי  

---

## 1. שיטת המחקר (Methodology)

מחקר זה בוצע באמצעות מתודולוגיית סריקה וניתוח מוצלבים באוקטובר 2026, תוך התמקדות בנתונים מאומתים ופומביים בלבד ללא הערכות או נתונים מומצאים:
1. **וקטורי חיפוש ממוקדים (Focused Search Vectors):**
   - סריקת מסגרות פתוחות (AutoGPT, CrewAI, LangGraph, OpenClaw/Clawdbot) וזיהוי נתוני פריסה, מאגרי קוד פעילים ותמיכה בריצה רציפה (24/7).
   - סריקת סוכנים תאגידיים מוצהרים מבית OpenAI (Operator, Codex), Anthropic (Claude Code, Computer Use) ו-Google (Gemini Agents, Vertex AI Agent Builder, פרוטוקול A2A).
   - מיפוי סביבות מדידה, לוחות לידרבורד ובנצ'מרקים מובילים להערכת סוכנים אוטונומיים.
2. **אימות והצלבת ראיות (Verification & Proof Standards):**
   - כל פריט בדוח נבחן ונבדק מול תיעוד רשמי, מאגרי קוד ב-GitHub, הודעות פומביות של החברות והקהילה, ולוחות מובילים.
   - בוצעה הפרדה קפדנית וחד-משמעית בין **"סוכן ספציפי בשם שפועל בעולם"** (מערכת פועלת המבצעת משימות באופן אוטונומי) לבין **"מוצר / מסגרת פיתוח (Framework/SDK)"** (תשתית המשמשת לבניית סוכנים).

---

## 2. אבחנה יסודית: סוכן ספציפי לעומת מוצר/מסגרת

* **מוצר / מסגרת פיתוח (Framework / Platform / SDK):** כלי עבודה, ספריה או תשתית ענן המאפשרת למפתחים ליצור, לפרוס ולנהל סוכנים (לדוגמה: LangGraph, CrewAI, A2A Protocol).
* **סוכן ספציפי בשם שפועל בעולם (Specific Named Active Agent):** קיוט/יחידה אוטונומית בעלת זהות מוגדרת, הרשאות פעולה וסביבת ריצה המבצעת משימות בעולם האמיתי (לדוגמה: Devin, OpenHands, SWE-agent, OpenAI Operator).

---

## 3. מסגרות פתוחות וסוכנים אוטונומיים פעילים (Open Ecosystems)

### א. מוצרים ומסגרות פיתוח פתוחות (Products & Frameworks)

1. **AutoGPT / AutoGPT Server & Forge**
   * **שם:** AutoGPT (Significant Gravitas)
   * **סוג:** מסגרת פיתוח ופלטפורמת פריסה (Framework & Platform)
   * **קישור:** [https://github.com/Significant-Gravitas/AutoGPT](https://github.com/Significant-Gravitas/AutoGPT) / [https://agpt.co](https://agpt.co)
   * **הוכחה וראיות:** פרויקט קוד פתוח עם מעל 160,000 כוכבים ב-GitHub. התפתח מתסריט CLI בודד לפלטפורמת AutoGPT Server ו-Forge המאפשרת הרצת סוכנים אוטונומיים רציפים בסביבות Docker וסביבות ענן.

2. **CrewAI / CrewAI Enterprise**
   * **שם:** CrewAI
   * **סוג:** מסגרת פיתוח רב-סוכנית ומוצר פריסה ארגוני (Multi-Agent Framework & Enterprise Platform)
   * **קישור:** [https://github.com/crewAIInc/crewAI](https://github.com/crewAIInc/crewAI) / [https://crewai.com](https://crewai.com)
   * **הוכחה וראיות:** מסגרת Python פופולרית לניהול צוותי סוכנים (Multi-Agent Crews) בעלי תפקידים מוגדרים. פלטפורמת CrewAI Enterprise מאפשרת פריסת צוותים כספקטי כדמויי-שירות (Long-running Background Workers) בענן עם מנגנוני מעקב ופיתוח.

3. **LangGraph / LangGraph Platform (LangChain)**
   * **שם:** LangGraph
   * **סוג:** מסגרת פיתוח מבוססת גרף מצבים ופלטפורמת פריסה (Stateful Agent Framework & Deployment Platform)
   * **קישור:** [https://github.com/langchain-ai/langgraph](https://github.com/langchain-ai/langgraph) / [https://langchain.com/langgraph](https://langchain.com/langgraph)
   * **הוכחה וראיות:** תשתית סטנדרטית בתעשייה לייצוג סוכנים אוטונומיים כגרפים מחזוריים עם שמירת מצב (Persistence), Human-in-the-loop וזמן ריצה מבוסס LangGraph Cloud/Platform לפריסות ייצור.

4. **OpenClaw (לשעבר Clawdbot)**
   * **שם:** OpenClaw / RapidClaw
   * **סוג:** מסגרת פיתוח לסוכנים אוטונומיים 24/7 בסביבות מחשב/ענן
   * **קישור:** [https://rapidclaw.dev](https://rapidclaw.dev) / [https://www.clawbot.blog](https://www.clawbot.blog)
   * **הוכחה וראיות:** מסגרת יעודית לבניית סוכנים אוטונומיים הרצים באופן רציף (24/7) ללא התערבות אנושית, תוך דגש על אבטחה, ניהול הרשאות וחיבור לכלים מקומיים וסביבות ענן.

---

### ב. סוכנים ספציפיים בשם שפועלים בעולם (Specific Named Active Agents)

1. **Devin**
   * **שם:** Devin (Cognition AI)
   * **סוג:** סוכן אוטונומי ספציפי (Autonomous Software Engineer Agent)
   * **קישור:** [https://cognition.ai](https://cognition.ai) / [https://devin.ai](https://devin.ai)
   * **הוכחה וראיות:** סוכן תוכנה אוטונומי מסחרי הפועל באופן פעיל בסביבות ייצור, מקבל דיווחים ב-GitHub, מריץ טרמינל, כותב קוד, מתקן באגים ומגיש Pull Requests באופן עצמאי. נמדד באופן רשמי ב-SWE-bench.

2. **OpenHands (לשעבר OpenDevin)**
   * **שם:** OpenHands (All-Hands AI)
   * **סוג:** סוכן ספציפי ופלטפורמה בקוד פתוח (Open-Source Autonomous Developer Agent)
   * **קישור:** [https://github.com/All-Hands-AI/OpenHands](https://github.com/All-Hands-AI/OpenHands)
   * **הוכחה וראיות:** סוכן אוטונומי חפשי הפועל בסביבת סנדבוקס מבודדת (Docker Containers), מסוגל להריץ פקודות Shell, לערוך קבצים, לגלוש בדפדפן ולפתור משימות תוכנה מורכבות ללא התערבות רציפה.

3. **SWE-agent**
   * **שם:** SWE-agent (Princeton NLP)
   * **סוג:** סוכן אוטונומי ספציפי מבוסס CLI/ACI
   * **קישור:** [https://github.com/princeton-nlp/SWE-agent](https://github.com/princeton-nlp/SWE-agent)
   * **הוכחה וראיות:** סוכן פתוח שפותח באוניברסיטת פרינסטון, המשתמש בממשק Agent-Computer Interface (ACI) ייעודי כדי להריץ דיאלוג אוטונומי מול מעטפת פקודות (Shell) ולפתור Issues אמיתיים במאגרי GitHub.

4. **Devika**
   * **שם:** Devika (Stition AI / CognitiveLab)
   * **סוג:** סוכן אוטונומי ספציפי בקוד פתוח
   * **קישור:** [https://github.com/stitionai/devika](https://github.com/stitionai/devika)
   * **הוכחה וראיות:** סוכן אוטונומי בקוד פתוח המבצע תכנון ארכיטקטוני, מחקר ברשת, כתיבת קוד ובדיקת פלטים באופן עצמאי בהתבסס על הנחיות בשפה טבעית.

---

## 4. סוכני חברות גדולות ופרוטוקולים תאגידיים (Big Tech Agents & Protocols)

1. **OpenAI Operator**
   * **שם:** Operator (OpenAI)
   * **סוג:** סוכן אוטונומי תאגידי פומבי (Autonomous Browser & Computer-Using Agent)
   * **קישור:** [https://openai.com](https://openai.com)
   * **הוכחה וראיות:** גרסת תצוגה מחקרית/מוצר פומבי של OpenAI המסוגל לשלוט בדפדפן ובסביבת מחשב, לבצע הורדת קבצים, מיזוג PDF, ניתוח גיליונות נתונים והזמנת משימות באופן אוטונומי.

2. **OpenAI Codex / Codex CLI & Cloud Agent**
   * **שם:** OpenAI Codex / Agent Infrastructure
   * **סוג:** מוצר וסביבת סוכן אוטונומי לפיתוח קוד
   * **קישור:** [https://openai.com/index/openai-codex](https://openai.com/index/openai-codex)
   * **הוכחה וראיות:** תשתיות סוכן הקוד של OpenAI המשולבות ב-ChatGPT ובממשקי API, המריצות פקודות וניתוחי קוד בסביבות מבודדות (Cloud Sandboxes).

3. **Anthropic Claude Code**
   * **שם:** Claude Code (Anthropic CLI Agent / Claude Agent SDK)
   * **סוג:** סוכן אוטונומי מבוסס טרמינל (Agentic CLI Tool)
   * **קישור:** [https://docs.anthropic.com](https://docs.anthropic.com)
   * **הוכחה וראיות:** כלי CLI ו-SDK רשמי מבית Anthropic הפועל ישירות בטרמינל של המפתח, מבין את עץ הפרויקט, מריץ פקודות Shell, כותב קוד, מריץ בדיקות ומבצע Commit באופן אוטונומי.

4. **Anthropic Computer Use (Claude 3.5 / Claude Agents)**
   * **שם:** Anthropic Computer Use API
   * **סוג:** יכולת מוצר וסוכן שליטה בממשק משתמש (GUI Agent Capability)
   * **קישור:** [https://www.anthropic.com/news/3-5-models-and-computer-use](https://www.anthropic.com/news/3-5-models-and-computer-use)
   * **הוכחה וראיות:** ממשק API פומבי המאפשר לסוכנים מבוססי Claude להתבונן במסך, להזיז סמן עכבר, ללחוץ על מקשים ולהפעיל אפליקציות שולחניות ואינטרנטיות באופן אוטונומי.

5. **Google Agent2Agent Protocol (A2A)**
   * **שם:** A2A Protocol (Agent2Agent Protocol)
   * **סוג:** פרוטוקול ותקן תקשורת פתוח בין סוכנים אוטונומיים (Open Protocol / Standard)
   * **קישור:** [https://a2a-protocol.org](https://a2a-protocol.org) / [https://github.com/a2a-protocol](https://github.com/a2a-protocol)
   * **הוכחה וראיות:** פרוטוקול פתוח שפותח על ידי Google ונהתרם לקרן Linux Foundation (תחת Agentic AI Foundation). נתמך ומתוחזק על ידי AWS, Cisco, Google, IBM Research, Microsoft, Salesforce, SAP, ServiceNow. מספק תקן לתקשורת Machine-to-Machine, גילוי סוכנים, האצלת משימות ושיתוף תוצאות בין סוכנים הטרוגניים.

6. **Google Gemini Agents / Vertex AI Agent Builder**
   * **שם:** Vertex AI Agent Builder & Gemini Agents
   * **סוג:** פלטפורמה תאגידית ומוצר לבניית סוכנים
   * **קישור:** [https://cloud.google.com/vertex-ai/docs/agent-builder](https://cloud.google.com/vertex-ai/docs/agent-builder)
   * **הוכחה וראיות:** פלטפורמת הענן של גוגל לפריסת סוכנים אוטונומיים רב-מודאליים, המשבת אינטגרציה מלאה עם תקני MCP (Model Context Protocol) ו-A2A לפריסות ארגוניות.

---

## 5. כלי מדידה, בנצ'מרקים ולוחות לידרבורד (Measurement & Leaderboards)

1. **SWE-bench (Verified / Lite)**
   * **שם:** SWE-bench
   * **סוג:** בנצ'מרק ולוח לידרבורד להערכת סוכני תוכנה אוטונומיים
   * **קישור:** [https://www.swebench.com](https://www.swebench.com) / [https://github.com/swe-bench/SWE-bench](https://github.com/swe-bench/SWE-bench)
   * **הוכחה וראיות:** תקן התעשייה המרכזי לבחינת סוכני AI על גבי בעיות אמת מ-GitHub. מודד אחוז פתרון מוצלח של Pull Requests במאגרי פייתון מובילים.

2. **GAIA (General AI Assistants)**
   * **שם:** GAIA Benchmark
   * **סוג:** בנצ'מרק ולוח לידרבורד לסוכנים עוזרים כלליים
   * **קישור:** [https://huggingface.co/spaces/gaia-benchmark/leaderboard](https://huggingface.co/spaces/gaia-benchmark/leaderboard)
   * **הוכחה וראיות:** בנצ'מרק שנבנה על ידי Meta, Hugging Face ושותפים, המציג משימות מורכבות הדורשות שימוש בכלים, גלישה באינטרנט, ניתוח קבצים וחשיבה רב-שלבית.

3. **WebArena**
   * **שם:** WebArena
   * **סוג:** סביבת מדידה ובנצ'מרק לסוכני אינטרנט אוטונומיים
   * **קישור:** [https://webarena.dev](https://webarena.dev) / [https://github.com/web-arena-x/webarena](https://github.com/web-arena-x/webarena)
   * **הוכחה וראיות:** סביבת אינטרנט סימולטיבית ועצמאית (מקומית) המכילה אתרי מסחר אלקטרוני, פורומים, ופלטפורמות ניהול קוד לבחינת שיעור ההצלחה של סוכנים אוטונומיים בסביבות מורכבות.

4. **AgentBench**
   * **שם:** AgentBench
   * **סוג:** מסגרת הערכה מקיפה לסוכנים בסביבות מרובות
   * **קישור:** [https://github.com/THUDM/AgentBench](https://github.com/THUDM/AgentBench)
   * **הוכחה וראיות:** בנצ'מרק מבית אוניברסיטת צ'ינגהואה (THU) המעריך סוכנים ב-8 סביבות שונות: מערכת הפעלה (OS CLI), מסדי נתונים (SQL), משחקי טקסט, גלישה ברשת ועוד.

5. **TAU-bench (Tool-Augmented User Bench)**
   * **שם:** TAU-bench (Sierra Research)
   * **סוג:** בנצ'מרק להערכת סוכנים בסביבות שיחה וכלים דינמיות
   * **קישור:** [https://github.com/sierra-research/tau-bench](https://github.com/sierra-research/tau-bench)
   * **הוכחה וראיות:** בנצ'מרק מבית Sierra להערכת יכולות סוכן באינטראקציה מרובת סבבים דינמית, שימוש בכלים עסקיים והתמודדות עם אילוצים משתנים.

6. **OSWorld**
   * **שם:** OSWorld Benchmark
   * **סוג:** סביבת הערכה לסוכני מערכת הפעלה ו-GUI
   * **קישור:** [https://os-world.github.io](https://os-world.github.io)
   * **הוכחה וראיות:** בנצ'מרק המודד ביצועי סוכנים במערכות הפעלה אמיתיות (Ubuntu/Windows) ושימוש באפליקציות שולחניות מורכבות.

---

## 6. מה חסר (Gaps, Blind Spots & Ecosystem Limitations)

נכון לאוקטובר 2026, קיימים מספר פערים מרכזיים בתחום מפקד הסוכנים האוטונומיים:

1. **היעדר מרשם פריסות ציבורי מאומת (Lack of Public Deployment Registries):**
   בעוד שמסגרות כמו CrewAI, LangGraph ו-AutoGPT מדווחות על מיליוני הורדות, אין מרשם פומבי המציג כמה סוכנים פועלים באופן רציף (24/7) במציאות, מהן זהויותיהם, ואילו משימות ייצור הם מנהלים. רוב הפריסות נשארות חסויות מאחורי חומות תאגידיות.

2. **אי-הפרדה בין סוכני סנדבוקס לסוכני ייצור בעלי הרשאות קריטיות:**
   רוב הבנצ'מרקים (SWE-bench, WebArena) בודקים סוכנים בסביבות Docker מבודדות. כמעט ואין כלי מדידה פומביים המעריכים סוכנים אוטונומיים הפועלים בסביבות ייצור חיים עם ניהול הרשאות (IAM), ניהול סודות וניהול Blast Radius למקרה של תקלה.

3. **מחסור בלוחות לידרבורד להערכת פרוטוקולי תקשורת בין-סוכניים:**
   אף על פי שפרוטוקול A2A של גוגל/Linux Foundation ו-MCP של Anthropic הפכו לתקנים מקובלים, אין כיום בנצ'מרק פומבי המודד את יעילות התקשורת והמשא ומתן בין סוכנים מסוגים שונים (Heterogeneous Agents) הפועלים תחת פרוטוקולים אלו.

4. **היעדר מדידה של שחיקה והתנהגות בריצה ארוכת-טווח (Long-Horizon Drift Evals):**
   רוב כלי המדידה בוחנים משימות הנמשכות בין דקות לספורות לשעות. חסרות מערכות מדידה פומביות המודדות יציבות סוכנים הרצים לאורך ימים ושבועות רצופים ללא איפוס קונטקסט.

---

*נרשם ונחתם על ידי עוזר מחקר — רשת שימי | 13/10/2026*
