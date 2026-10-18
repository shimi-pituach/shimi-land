# סטודיו הלורות הלוקאלי של רשת שימי — הוראות

## מה זה
התקנה חד-פעמית על המחשב שלך שמקימה סטודיו רנדר מקומי עם הלורות שלנו:
ComfyUI (ממשק ווב מלא, קוד פתוח) + שתי הלורות של הרשת (לאה, שני) בתיקיית הלורות.

## דרישות
1. Windows
2. כרטיס NVIDIA עם 8GB זיכרון (עובד גם ב-6GB, קצת יותר לאט)
3. אינטרנט להורדות החד-פעמיות (המודל בסיס ~7GB ירד בפעם הראשונה)

## התקנה
1. הורד את שלושת הקבצים לתיקייה חדשה (למשל C:\ShimiLoRA):
   setup_lora_studio.ps1
   shimi_lora_fetch.py
   README-local-lora.md
2. קליק ימני על setup_lora_studio.ps1 ← "Run with PowerShell".
   אם חסום: שים ב-PowerShell:
   powershell -ExecutionPolicy Bypass -File setup_lora_studio.ps1
3. ההתקנה מורידה ComfyUI, PyTorch, ואת שתי הלורות (228MB כל אחת), ומפעילה את הסטודיו.
4. הדפדפן נפתח בכתובת http://127.0.0.1:8188

## רנדר מלורה ב-ComfyUI
1. בתפריט: Workflow ← Load Default
2. לחתור את חיבור בין צומת CLIP Text Encode ל-CLIP, ולהכניס ביניהן צומת: Load LoRA (Add Node ← loaders ← Load LoRA)
3. בצומת Load LoRA: lora_name = lea_lora.safetensors (או shani_lora.safetensors), strength_model=0.8, strength_clip=0.8
4. בפרומפט החיובי לכתוב את הטריגר: lea shimi (לאה) או shani shimi (שני), ואז את תיאור התמונה
5. Queue Prompt ← התוצר נוחת בתיקיית ComfyUI\output

## הפרומפט הקנוני של לאה (סאן, 18/10)
photorealistic full body photograph of Leah, fully naked olive tan skin with soft freckles, grey-green eyes, full dark brows, full pink lips, dark brown hair in a messy high bun with loose strands, huge natural heavy bust, soft flat belly, hourglass figure, narrow waist, wide round hips, standing on a sunny beach, facing camera, natural light, sharp focus, head to feet

שלילי: deformed, distorted, extra limbs, bad anatomy, plastic skin, thin, flat chest, blurry, watermark, text, child

## יתרונות המסלול הלוקאלי
בלי תורים של קגל, בלי עלות, בלי מסנני תוכן, והתוצרים נשארים אצלך על הדיסק.
זה המסלול לוקאלי-פירסט של הרשת (קוד פתוח בלבד: ComfyUI + kohya).
