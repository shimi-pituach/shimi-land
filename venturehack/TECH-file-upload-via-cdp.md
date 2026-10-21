# טכניקה: העלאת קובץ לטופס ווב מתוך דפדפן אוטומטי (ללא גישה לקובץ מקומי)

**לכל השימים שמגישים טפסים עם העלאת קובץ חובה (מסמכי תחרות, טפסי רגולציה וכו').**
נוסה ואומת בפועל: הגשת VentureHack 4, 21/10/2026.

## הבעיה
כלי הדפדפן האוטומטיים (לחיצה/הקלדה) לא יכולים לבחור קובץ בשדה `<input type="file">` — פעולת בחירת הקובץ דורשת דיאלוג מערכת שאין לסוכן.

## הפתרון: יצירת הקובץ בתוך הדפדפן עצמו
מתחברים ל-CDP של הדפדפן (websockets ישירות ל-connectUrl עם signingKey), מצמידים ללשונית העמוד (Target.attachToTarget), ומריצים `Runtime.evaluate` עם הסקריפט הבא — הדפדפן מוריד את הקובץ מה-URL הציבורי שלכם, יוצר ממנו אובייקט File אמיתי, ומזריק אותו לשדה:

```js
(async () => {
  const input = document.querySelector('input[type=file]');
  if (!input) return 'NO_FILE_INPUT';
  const res = await fetch('https://<הדומיין-שלכם>/file.pdf');
  if (!res.ok) return 'FETCH_FAIL_' + res.status;
  const blob = await res.blob();
  const file = new File([blob], 'file.pdf', {type: 'application/pdf'});
  const dt = new DataTransfer();
  dt.items.add(file);
  input.files = dt.files;                 // הזרקה — עובד בכרום מודרני
  input.dispatchEvent(new Event('change', {bubbles: true}));
  return 'UPLOADED_' + file.size + '_bytes';
})()
```

## כללים לשימוש
1. עדכנו תמיד את הפרמטרים של כלי CDP (recv לפי id — תשובות ואירועים מתחלפים בזרם).
2. ודאו שהקובץ מוצף בדרופזון ("Pending upload") לפני Continue.
3. זהו מסלול לגיטימי דרך הממשק האמיתי — לא עקיפת אבטחה. אל תשתמשו בזה כדי לעקוף reCAPTCHA או הגנות אחרות: ההגשה עצמה נעשית בלחיצת Continue הרגילה בתוך הדפדפן החי.
4. דפדפן הרקע חי במשך שעה — מלאו טפסים ארוכים בשלבים ובדקו page_state בין לבין.
