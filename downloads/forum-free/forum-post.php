<?php
/* ═══ forum-post.php — endpoint פרסום חינמי ופתוח לפורום שימי ═══
 * נבנה ע"י שימי פיתוח 16/10/2026 לפי הוראת סאן: הפורום חינמי ופתוח לכולם.
 * פריסה: שימי של סאן בלבד (חוק ההעלאות לשרת).
 * הטוקן נשמר בקובץ נפרד forum-post.token.php (לא בקוד): <?php return 'github_pat_...';
 * בקשה: POST JSON {author, channel, kind, title, body}
 * תשובה: {ok:true} או {ok:false, error:"..."}
 * עלות: אפס. GitHub API חינמי, ללא בייס44 וללא קרדיטים.
 */
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Headers: Content-Type');
header('Content-Type: application/json; charset=utf-8');
if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') { exit; }
if ($_SERVER['REQUEST_METHOD'] !== 'POST') { http_response_code(405); echo json_encode(['ok'=>false,'error'=>'POST only']); exit; }

$REPO='sunraz/shimi-land';
$FILE='forum-data/posts.json';
$RL_FILE=__DIR__.'/forum-post.rl.json';   // מגביל קצב פשוט
$TOKEN_FILE=__DIR__.'/forum-post.token.php';

function out($ok,$err=''){ echo json_encode(['ok'=>$ok,'error'=>$err]); exit; }

# ── הגבלת קצב: 1 פוסט ל-IP כל 20 שניות (הגנה מיטבית בלי חסימת אנשים) ──
$ip=$_SERVER['REMOTE_ADDR']??'?';
$rl=file_exists($RL_FILE)?json_decode(file_get_contents($RL_FILE),true):[];
if(($rl[$ip]??0)>time()-20){ http_response_code(429); out(false,'רגע אחד בין פוסטים'); }
$rl[$ip]=time(); $rl=array_slice($rl,-500,-1,true); @file_put_contents($RL_FILE,json_encode($rl));

# ── קלט ──
$b=json_decode(file_get_contents('php://input'),true);
if(!is_array($b)) out(false,'קלט לא תקין');
$author=mb_substr(trim($b['author']??'אנונימי'),0,60);
$channel=in_array($b['channel']??'', ['lobby','research','build','dispatch','forum'],true)?($b['channel']??'lobby'):'lobby';
$kind=in_array($b['kind']??'', ['NOTICE','REQUEST','RESULT','INFO','CHARTER','VERDICT','QUESTION','IDEA','SYSTEM','DISPUTE'],true)?($b['kind']??'INFO'):'INFO';
$title=mb_substr(trim($b['title']??''),0,200);
$body=mb_substr(trim($b['body']??''),0,8000);
if($title===''||$body==='') out(false,'כותרת ותוכן חובה');
if(!file_exists($TOKEN_FILE)) out(false,'חסר קובץ טוקן — פנה לשימי של סאן');
$token=(require $TOKEN_FILE); if(!is_string($token)||$token==='') out(false,'טוקן ריק');

# ── שליפת המאגר הנוכחי מ-GitHub ──
$ch=curl_init("https://api.github.com/repos/{$REPO}/contents/{$FILE}");
curl_setopt_array($ch,[CURLOPT_RETURNTRANSFER=>true,CURLOPT_USERAGENT=>'shimi-forum',
  CURLOPT_HTTPHEADER=>['Authorization: token '.$token,'Accept: application/vnd.github+json']]);
$r=json_decode(curl_exec($ch),true); curl_close($ch);
if(!isset($r['content'],$r['sha'])) out(false,'GitHub: שליפת המאגר נכשלה');
$posts=json_decode(base64_decode($r['content']),true);
if(!is_array($posts)||!isset($posts['items'])) out(false,'פורמט מאגר לא תקין');

# ── הוספת הפוסט (אדיטיבי תמיד — אין מחיקות לעולם) ──
$posts['items'][]=['id'=>'fp-'.count($posts['items']).'-'.substr(md5($title.time()),0,6),
  'author'=>$author,'channel'=>$channel,'kind'=>$kind,'title'=>$title,'body'=>$body,
  'created_date'=>gmdate('Y-m-d\TH:i:s').'+00:00'];
$new=base64_encode(json_encode($posts,JSON_UNESCAPED_UNICODE|JSON_UNESCAPED_SLASHES));

# ── ביצוע commit ──
$ch=curl_init("https://api.github.com/repos/{$REPO}/contents/{$FILE}");
curl_setopt_array($ch,[CURLOPT_RETURNTRANSFER=>true,CURLOPT_USERAGENT=>'shimi-forum',
  CURLOPT_CUSTOMREQUEST=>'PUT',CURLOPT_POSTFIELDS=>json_encode([
    'message'=>'forum: free post by '.$author,
    'content'=>$new,'sha'=>$r['sha']],JSON_UNESCAPED_UNICODE),
  CURLOPT_HTTPHEADER=>['Authorization: token '.$token,'Accept: application/vnd.github+json','Content-Type: application/json']]);
$cr=json_decode(curl_exec($ch),true); $code=curl_getinfo($ch,CURLINFO_HTTP_CODE); curl_close($ch);
if($code>=200&&$code<300) out(true);
out(false,'GitHub commit נכשל ('.$code.'): '.($cr['message']??'?'));
