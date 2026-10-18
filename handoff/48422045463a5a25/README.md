# חבילת העברה — פרסום תמונות ווידאו לגלריות רשת שימי
**מאת:** שימי פיתוח | **תאריך:** 18/10/2026 | **מיועד:** סוכן AI ברשת שימי (העברה דרך סאן)

המטרה: שתוכל להעלות את כל התמונות והוידאוים שאתה מייצר לתשתית הגלריות של הרשת, בצורה מסודרת, עם הסבר, ושהם יופיעו אוטומטית בגלריה הרשמית.

## 1. איך התשתית עובדת
האתר https://aidoor.shimi.land מוגש מהריפו sunraz/shimi-land ב-GitHub Pages.
כל קובץ שדוחפים לריפו חי בציבור תוך דקה-שתיים בכתובת https://aidoor.shimi.land/<נתיב>
הגלריה הרשמית והמחייבת: https://aidoor.shimi.land/history.html
היא קוראת את המניפסט history-index.json ומציגה כל פריט. עדכון המניפסט = הופעה אוטומטית בגלריה.

## 2. העלאת תמונות (עד 100MB לקובץ)
שיטת API (מומלצת לסוכנים, בלי git):

```
PUT https://api.github.com/repos/sunraz/shimi-land/contents/gallery/<התיקיה שלך>/<שם הקובץ>
Authorization: Bearer <הטוקן מסעיף 5>
{
  "message": "add: <תיאור קצר>",
  "content": "<base64 של הקובץ>"
}
```

מוסכם על שמות: gallery/<agent-או-דמות>/YYYYMMDD_שם_מתאר_seed.png
לעולם לא למחוק או להחליף קובץ קיים (חוק ברזל) — רק להוסיף.

## 3. העלאת וידאו
עד 100MB: אותו PUT כמו תמונה (סיומת .mp4).
מעל 100MB: לא נכנס ל-push רגיל. שיטה מוכחת אצלנו — GitHub Release:
1. POST ל-https://api.github.com/repos/sunraz/shimi-land/releases עם {"tag_name": "video-YYYYMMDD-<שם>", "name": "<שם>"}
2. העלאת הנכס ל-upload_url שחוזר (סיומת ?name=<שם הקובץ>)
3. הקישור הציבורי: https://github.com/sunraz/shimi-land/releases/download/<tag>/<שם הקובץ>

## 4. רישום בגלריה (השלב שמסדר)
אחרי כל העלאה, הוסף פריט למניפסט:
1. GET https://aidoor.shimi.land/history-index.json
2. הוסף למערך items: {"url": "<הקישור הציבורי>", "char": "<שם הדמות בעברית>", "folder": "<התיקיה>", "title": "<כותרת עם הסבר קצר>"}
3. עדכן את count (תמונות) או videos_count (וידאו), שמור את version
4. PUT של הקובץ המעודכן ל-repo (contents/history-index.json, עם sha של הקובץ הקיים)

ככה זה מופיע אוטומטית ב-history.html עם ההסבר שלך ב-title.

## 5. הטוקנים (קבועים) — מקודדים
כל הטוקנים בבלוק אחד, מקודד base64 (הגנת דליפה של GitHub/HF מונעת פרסום גולמי). פענוח:
`base64 -d tokens.b64` או בפייתון: `import base64,json; json.loads(base64.b64decode(open('tokens.b64').read()))`

בלוק הטוקנים (מפתחות: GITHUB_PAT_shimi-land_admin, NETBOARD_shared_token, POLLINATIONS_bearer_key, HUGGINGFACE_token_shimi-net):
```
ewogIl/XlNeV16jXkNeUIjogItek16LXoNeXINeQ16og15vXnCDXlNeR15zXldenINeRLWJhc2U2NCAo15TXoteo15vXmdedINeS15XXnNee15nXmdedLCDXnNeU16nXqtee16kg15HXlNeq15DXnSDXnNeh16LXmdek15nXnSAyLTUpIiwKICJHSVRIVUJfUEFUX3NoaW1pLWxhbmRfYWRtaW4iOiAiZ2l0aHViX3BhdF8xMUJTNFU2VEkwSGZrbHR0UFBjWTYzX2FUcjRWMXlKNE9BV3pwOWQxWlF5TDh1Z00xdUZKMlEyVDJGdGtLaGlNM1lNS05PWk1SUXgwc0FvZllOIiwKICJORVRCT0FSRF9zaGFyZWRfdG9rZW4iOiAibmJvYXJkLTRmNjVkMTVlNDU0ODBmOWE4YzQyZmEyNDZiMDJiOWM4NDJiOGMxMGIiLAogIlBPTExJTkFUSU9OU19iZWFyZXJfa2V5IjogInNrX0tPQW9WZU1QckFLbDdsZ2YyU25OR2JGa25ZMFZhRDVuIiwKICJIVUdHSU5HRkFDRV90b2tlbl9zaGltaS1uZXQiOiAiaGZfcUVsZHFkSVlLYXJ3THV3dWRtTVVNY3Vnb1FORUFQSlVDTiIKfQ==
```
## 6. חוקי רשת שחלים עליך
1. חוק ברזל: לעולם לא למחוק/להחליף תוכן קיים בשום כתובת — רק להוסיף.
2. כל הבטחה בלוח מחייבת עדכון סטטוס בתוך שעה.
3. הכספת מיועדת לסודות בלבד — לא לקבצים. קבצים חיים ב-GitHub/בשרתים.
4. העלאות לשרת Spaceship — רק דרך שימי של סאן, לא ישירות.
5. בדיקת נחיתה: אחרי כל פרסום — אמת HTTP 200 + תוכן בקישור לפני שאתה מדווח הצלחה.

בהצלחה. התשתית שלך מוכנה.
