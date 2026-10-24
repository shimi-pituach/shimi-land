# שיטות הפקה, מנועים ואוטומציה — לאה
ארכיון האושיות · לאה · 24/10/2026

## מסלולי הפקת וידאו מוכחים

1. *LTX-Video (gradio_client על ZeroGPU)* — קליפי תנועה 4-5 שניות מפריים קאנוני.
   מרחב: Lightricks/ltx-video-distilled. api_name=/image_to_video.
   פרמטרים מוכחים לפריימים מרובעים: height_ui=768, width_ui=768, duration_ui=5, improve_texture_flag=True, ui_guidance_scale=1, negative_prompt="worst quality, inconsistent motion, blurry, jittery, distorted".
   חובה בפרומפט: "Wide full shot, static camera, her entire body from head to toe stays fully in frame throughout, no camera movement, no zoom".
   סקיל מותקן: .agents/skills/ltx-free-clip/ (בכל סביבת סוכן — ראו 04_protocol).
2. *מנוע הסטודיו (Base44 renderApi)* — grok/seedance, איכות גבוהה, צורך קרדיטים פעילים.
3. *הרכבה מקומית (ffmpeg + PIL)* — כרטיסי כותרת/חתימה, המרה לאנכי 1080x1920 לשורטס, האטה (setpts) לקריאות תנועה. שיטת RTL תקינה: PIL עם raqm (טקסט בסדר לוגי + direction="rtl"). אזהרה מתועדת: get_display/reshape לפני PIL-raqm יוצר טקסט הפוך (באג שתוקן 23/10).

## טבלת פרומפטי התנועה המוכחים (מהקורס, פריים → קליפ)

| קליפ | פריים פתיחה | פרומפט תנועה |
|---|---|---|
| l1_ex1 | gallery/lea-koda-20-10/20261021_lea_lesson1_s01_horsestance_feet.jpg | She sinks smoothly down into a deep horse stance: feet wide, knees bending outward over the toes, back straight, arms pressing forward, then holds the stance steady. |
| l1_ex3 | gallery/lea-koda-20-10/20261021_lea_lesson1_s07_kick_kneeraise.jpg | From the raised knee position she snaps the leg out into a sharp controlled front kick, holds the extension briefly, then retracts smoothly back to a stable ready stance. |
| l2_trans | gallery/lea-koda-20-10/20261021_lea_lesson2_t02_horse_to_front_midstep.jpg | She completes the step into a front stance with a straight punch, then flows into a cat stance, and finishes with one clean kick and controlled return. |
| l3_ex1 | gallery/lea-koda-20-10/20261021_lea_lesson3_f02_sidekick_chamber.jpg | From the chambered knee position she drives the leg out into a powerful side kick, holds full extension briefly, then retracts back to a stable stance. |
| l3_ex2 | gallery/lea-koda-20-10/20261021_lea_lesson3_f06_roundkick_chamber.jpg | From the chambered position she swings the leg in a fast controlled roundhouse arc, hips rotating, holds briefly, then retracts. |
| l5_ex1/ex2, l6-l10 | מופיעים בקובץ lesson_clips/motion_all.py בסביבת קודה | תבנית זהה: פעולה אחת ברורה, החזקה קצרה, חזרה לעמידה. |

כלל תנועה: פרומפט מתאר מה *קורה אחרי* הפריים. זהות ולבוש מגיעים מהפריים. סטטי, תאורה קבועה.

## המנוע היומי האוטונומי (עובד כבר עכשיו)

1. *19:00 כל יום* — וורקפלוא "Lea Daily Engine" מעיר את קודה: הרצת תור הרינדור על מכסת sun-shimi (LTX), QC מידות ותנועה (ffprobe + signalstats), העלאה לגלריה + אינדוקס + בניית Pages, הרכבת שורט יומי, דיווח לבעלים עם לינקים.
2. *תור הרינדור* — lesson_clips/ltx_jobs.json בסביבת קודה. רינדר מחדש מתווסף לראש התור עם מפתח seed משלו.
3. *הגבול המבצעי של המכסה החינמית* — בערך 4 קליפים ביום בחשבון אחד. העלאת תפוקה: כל סוכן מרנדר בחשבונו שלו מסביבתו (חבילות ג'ובים ב04), או HF PRO.

## מכשירי QC חובה לכל קליפ חדש

1. ffprobe: קידוד h264, מידות 768x768 (או 1080x1920 לשורט), משך 4-8 שניות.
2. בדיקת תנועה: signalstats YDIF — מצגות וקליפים קפואים נפסלים (מדד: static_pct<35 או חציון>0.4 לקליפ נטו).
3. בדיקת חדירות חפצים: מיפוי פיקסלים כהים בפינות — עלייה של מעל 12% במהלך הקליפ = פגם (כמו סופטבוקס שחור).
4. אנטומיה: העין האנושית של הבעלים = השער הסופי. קליפ חדש לשיעור מאושר לפני הטמעה.
