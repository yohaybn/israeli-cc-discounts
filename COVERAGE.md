# כיסוי מועדונים - COVERAGE

טבלת מעקב: כל המועדונים וכרטיסי ההטבות שקיימים באפליקציית Fid (נשלף מה-API הציבורי `cardslistv2.php`, 18.9.26), מול מצב הסקרייפרים בריפו.

**סיכום: 171 מועדונים | ✅ יש סקרייפר: 67 | ⬜ טרם נכתב: 30 | ⛔ חסום טכנית: 74 | ⚖️ חסום משפטית: 0**

מקרא:
- ✅ יש סקרייפר - קיים `*_scraper.py` בריפו (הקישור בעמודת "קישור להטבות" הוא מקור הנתונים שהסקרייפר קורא).
- ⬜ טרם נכתב - אין סקרייפר; לא נבדקה חסימה.
- ⛔ חסום טכנית - נבדק ונמצא חסום (לוגין/OTP/CAPTCHA/anti-bot). ההחלטות מתועדות מ-17.9.26.
- ⚖️ חסום משפטית - אין כרגע מועדון שסומן כך; לא בוצעה בדיקה משפטית לכל מועדון.

> הערה: חלק מהשמות ב-Fid הם וריאציות של אותה תוכנית (למשל GiftCard Shopping / Gift Zone של ישראכרט). הסיווג לפי שם המועדון כפי שמופיע ב-Fid.

### כרטיסי אשראי

| מועדון / כרטיס | סטטוס | קישור להטבות | הערות |
|---|---|---|---|
| כאל | ⛔ חסום טכנית | - | חסום טכנית: anti-bot / קטלוג דליל (הוחלט לדלג, 17.9.26) |
| CashCal Pro | ⛔ חסום טכנית | - | חסום טכנית: anti-bot / קטלוג דליל (הוחלט לדלג, 17.9.26) |
| ישראכרט | ✅ יש סקרייפר | [הטבות](https://benefits.isracard.co.il/) | isracard_scraper.py - קטלוג benefits.isracard.co.il (ציבורי, ללא לוגין; חד-עמדי, window.epi) |
| Isracard Top / ישראכרט טופ | ✅ יש סקרייפר | [הטבות](https://benefits.isracard.co.il/) | isracard_scraper.py - קטלוג benefits.isracard.co.il (ציבורי, ללא לוגין; חד-עמדי, window.epi) |
| Isracard Top /ישרכארט טופ מהדרין | ✅ יש סקרייפר | [הטבות](https://benefits.isracard.co.il/) | isracard_scraper.py - קטלוג benefits.isracard.co.il (ציבורי, ללא לוגין; חד-עמדי, window.epi) |
| +CashBack(ישראכרט) | ✅ יש סקרייפר | [הטבות](https://benefits.isracard.co.il/) | isracard_scraper.py - קטלוג benefits.isracard.co.il (ציבורי, ללא לוגין; חד-עמדי, window.epi) |
| מקס | ✅ יש סקרייפר | [הטבות](https://www.max.co.il) | max_benefits_scraper.py - קטלוג ההטבות הציבורי של MAX |
| מקס אקזקיוטיב | ✅ יש סקרייפר | [הטבות](https://www.max.co.il) | max_benefits_scraper.py - קטלוג ההטבות הציבורי של MAX |
| אמריקן אקספרס | ✅ יש סקרייפר | [הטבות](https://rewards.americanexpress.co.il/) | amex_scraper.py - קטלוג rewards.americanexpress.co.il (ציבורי, ללא לוגין) |
| אמריקן אקספרס עסקים | ✅ יש סקרייפר | [הטבות](https://rewards.americanexpress.co.il/) | amex_scraper.py - קטלוג rewards.americanexpress.co.il (ציבורי, ללא לוגין) |
| דיינרס | ⛔ חסום טכנית | - | חסום טכנית: anti-bot / קטלוג דליל (הוחלט לדלג, 17.9.26) |
| Extra Home דיינרס | ⛔ חסום טכנית | - | חסום טכנית: anti-bot / קטלוג דליל (הוחלט לדלג, 17.9.26) |
| Extra Family דיינרס | ⛔ חסום טכנית | - | חסום טכנית: anti-bot / קטלוג דליל (הוחלט לדלג, 17.9.26) |
| מאסטרקארד | ⛔ חסום טכנית | - | WAF של mastercard.com (403) (23.9.26) |

### כרטיסים בנקאים

| מועדון / כרטיס | סטטוס | קישור להטבות | הערות |
|---|---|---|---|
| דיסקונט | ✅ יש סקרייפר | [הטבות](https://www.discount.co.il/) | discount_key_scraper.py - כבר מכוסה ע"י הסקרייפר הקיים (דיסקונט) |
| מרכנתיל | ⬜ טרם נכתב | - |  |
| פועלים וונדר | ⛔ חסום טכנית | [אתר](https://www.bankhapoalim.co.il/poalim-wonder/fun) | באתר רק 4 הטבות לדוגמה; הקטלוג המלא באפליקציה בלבד (23.9.26) |
| לאומי גודיז / לאומי בונוס | ⛔ חסום טכנית | - | חסום טכנית: WAF של לאומי (הוחלט לדלג, 17.9.26) |
| מזרחי טפחות | ✅ יש סקרייפר | [הטבות](https://www.mizrahi-tefahot.co.il/hacartis/all/) | mizrahi_scraper.py - קטלוג "הכרטיס" הציבורי (branch feat/scrapers-round-2) |
| ביונד הבינלאומי | ⛔ חסום טכנית | - | חסום טכנית: WAF של לאומי (הוחלט לדלג, 17.9.26) |

### כוחות הביטחון ומדינה

| מועדון / כרטיס | סטטוס | קישור להטבות | הערות |
|---|---|---|---|
| בהצדעה | ⛔ חסום טכנית | - | חסום טכנית: לוגין עם ת"ז + OTP + reCAPTCHA (הוחלט לדלג, 17.9.26) |
| קרנות השוטרים / קרנות הסוהרים | ✅ יש סקרייפר | [הטבות](https://ks.style.co.il/) | police_funds_scraper.py - פלטפורמת style (style_platform.py), דפי קטגוריה ציבוריים |
| כרטיס נקודות שוטרים | ⛔ חסום טכנית | - | multipoint.mltp.co.il - כניסה עם OTP + reCAPTCHA (נבדק 23.9.26) |
| כרטיס נקודות כבאות | ⬜ טרם נכתב | - |  |
| איפ"א | ⛔ חסום טכנית | - | ipa.megalean.co.il - מגה לאן, לוגין (נבדק 23.9.26) |
| חבר קבע | ✅ יש סקרייפר | [הטבות](https://www.hvr.co.il) | hvr_scraper.py - כרטיסים נטענים וגיפטים של חבר משרתי הקבע |
| חבר מח"צ / חבר שלי | ✅ יש סקרייפר | [הטבות](https://www.mcc.co.il) | mcc_scraper.py - מועדוני חבר |
| ארגון עובדי צה"ל | ⛔ חסום טכנית | - | olam-pnay.megalean.co.il - מגה לאן, לוגין (נבדק 23.9.26) |
| ארגון נכי צה"ל | ⛔ חסום טכנית | - | inz.org.il - אתגר Cloudflare (נבדק 23.9.26) |
| כרטיס נקודות לאיש קבע (הכרטיס האפור) | ⛔ חסום טכנית | - | idfpoints.mltp.co.il - הזדהות + reCAPTCHA (נבדק 23.9.26) |
| כרטיס הכוכבים לחייל חובה | ⛔ חסום טכנית | - | idf.mltp.co.il - הזדהות + reCAPTCHA (נבדק 23.9.26) |
| fighter מילואים | ⬜ טרם נכתב | - |  |
| תוכנית עמית | ⛔ חסום טכנית | - | אפליקציה בלבד, אין רשימה ציבורית (נבדק 23.9.26) |
| שיקומי / Shikum.me | ⛔ חסום טכנית | - | אפליקציה בלבד, אין רשימה ציבורית (נבדק 23.9.26) |
| נכון | ⛔ חסום טכנית | - | nachon.boomclub.org.il - כניסה עם OTP (23.9.26) |
| P100 | ⛔ חסום טכנית | - | דף שיווק של כרטיס Amex; ההטבות הן הטבות Amex הכלליות (amex_scraper) (23.9.26) |
| יותר | ✅ יש סקרייפר | [הטבות](https://yoter.co.il/%D7%A8%D7%A9%D7%99%D7%9E%D7%AA-%D7%91%D7%AA%D7%99-%D7%A2%D7%A1%D7%A7/) | yoter_scraper.py - רשימת בתי העסק הציבורית |
| עובדי משרד הבטחון | ⛔ חסום טכנית | - | vmod.megalean.co.il - מגה לאן, לוגין (נבדק 23.9.26) |
| איחוד הצלה | ✅ יש סקרייפר | [הטבות](https://4u.1221.org.il/) | ihud_hatzala_scraper.py - WooCommerce Store API ציבורי |
| תעשייה אווירית | ✅ יש סקרייפר | [הטבות](https://icard.style.co.il/) | icard_scraper.py - פלטפורמת style |
| חוגר צה"ל | ⬜ טרם נכתב | - |  |

### מקצועי

| מועדון / כרטיס | סטטוס | קישור להטבות | הערות |
|---|---|---|---|
| הייטקזון | ✅ יש סקרייפר | [הטבות](https://www.htzone.co.il) | htzone_scraper.py |
| מצר | ✅ יש סקרייפר | [הטבות](https://metzer.htzone.co.il/) | metzer_scraper.py - פלטפורמת HTzone (htzone_platform.py), הטבות ושוברים בלבד (בלי מוצרי חנות) |
| ביחד בשבילך | ⬜ טרם נכתב | - |  |
| סילבר קארד וועד דרום | ⛔ חסום טכנית | - | silvercard.co.il - האתר סגור, אפליקציה בלבד (נבדק 23.9.26) |
| גולד צפון | ✅ יש סקרייפר | [הטבות](https://goldnorth.htzone.co.il/) | goldnorth_scraper.py - פלטפורמת HTzone |
| יחד ההסתדרות הרפואית לישראל | ✅ יש סקרייפר | [הטבות](https://www.ima.org.il/yahadclub/Categories.aspx) | ima_yahad_scraper.py - קטלוג ציבורי, קטגוריות -> ספקים -> פרטי ספק (אתר איטי, ~800 עמודים) |
| שווה | ⛔ חסום טכנית | - | אפליקציה בלבד (נבדק 23.9.26) |
| שלך | ⛔ חסום טכנית | - | yours.co.il מאחורי אתגר bot (Reblaze, 571) (23.9.26) |
| שלך לגמלאי | ⬜ טרם נכתב | - |  |
| טוב פלוס | ✅ יש סקרייפר | [הטבות](https://tovplus.org.il/) | tovplus_scraper.py - דפי קטגוריה ציבוריים (dolcemaster_platform.py) |
| הוט מועדון צרכנות | ✅ יש סקרייפר | [הטבות](https://www.hot.co.il) | hot_scraper.py - ה-API החוזר 403 לעיתים קרובות; נשען על last-good-data |
| קורפורייט \ CORPORATE | ✅ יש סקרייפר | [הטבות](https://www.mycorporate.co.il/) | corporate_scraper.py - פלטפורמת style (שמות עסקים בלבד, בלי נוסח הטבה) |
| אקסטרה ממברס לשכת עורכי הדין ExtraMembers | ⛔ חסום טכנית | - | extramembers.co.il - מפנה ללוגין (נבדק 23.9.26) |
| היי בנפיט לשכת רואי חשבון Hi-Benefit | ✅ יש סקרייפר | [הטבות](https://www.benefit-icpas.co.il/) | hibenefit_scraper.py - פלטפורמת style (style_platform.py), דפי קטגוריה ציבוריים |
| לשכת סוכני הביטוח | ✅ יש סקרייפר | [הטבות](https://insurance.style.co.il/) | insurance_agents_scraper.py - פלטפורמת style (style_platform.py), דפי קטגוריה ציבוריים |
| ארגון עובדי בנק הפועלים | ⛔ חסום טכנית | - | poalim.megalean.co.il - מגה לאן, לוגין (נבדק 23.9.26) |
| B-Kef בזק | ⛔ חסום טכנית | - | b-kef.co.il - לוגין SMS (נבדק 23.9.26) |
| PeleFun פלאפאן | ⛔ חסום טכנית | - | pelephone.megalean.co.il - מגה לאן, לוגין (נבדק 23.9.26) |
| ארגון עובדי סלקום | ⬜ טרם נכתב | - |  |
| כללית פנאי לעובדי כללית | ⛔ חסום טכנית | - | נבדק 23.9.26: האתר (פלטפורמת מגה לאן) דורש כניסה עם מספר עובד |
| עובדי מכבי שירותי בריאות | ⛔ חסום טכנית | - | maccabi.megalean.co.il - מגה לאן, לוגין (נבדק 23.9.26) |
| אסותא פאן | ⛔ חסום טכנית | - | assuta.megalean.co.il - מגה לאן, לוגין (נבדק 23.9.26) |
| שחר- מהנדסים, אדריכלים ואקדמאים במקצועות הטכנולוגיים | ✅ יש סקרייפר | [הטבות](https://www.m-shachar.org.il/benefit/) | shachar_scraper.py - דף ההטבות הציבורי בלבד; הקטלוג המלא במגה לאן דורש לוגין |
| אגד דרייבר | ✅ יש סקרייפר | [הטבות](https://www.eggedclub.co.il/) | egged_driver_scraper.py - פלטפורמת style (style_platform.py), דפי קטגוריה ציבוריים |
| עובדי שופרסל | ⛔ חסום טכנית | - | shufersal.megalean.co.il - מגה לאן, לוגין (נבדק 23.9.26) |
| עובדי עיריית תל אביב | ⛔ חסום טכנית | - | telaviv.megalean.co.il - מגה לאן, לוגין (נבדק 23.9.26) |
| להב לשכת העצמאים בישראל | ✅ יש סקרייפר | [הטבות](https://lahav.style.co.il/) | lahav_scraper.py - פלטפורמת style (style_platform.py), דפי קטגוריה ציבוריים |
| אינטל פלוס | ⛔ חסום טכנית | - | intel.megalean.co.il - מגה לאן, לוגין (נבדק 23.9.26) |
| ארגון המהנדסים והאדריכלים העצמאיים | ⬜ טרם נכתב | - |  |
| אמדוקס | ✅ יש סקרייפר | [הטבות](https://amdocs.style.co.il/) | amdocs_scraper.py - פלטפורמת style |
| קוקה קולה | ⬜ טרם נכתב | - |  |
| כח לעובדים | ✅ יש סקרייפר | [הטבות](https://workers.style.co.il/) | workers_style_scraper.py - פלטפורמת style (style_platform.py), דפי קטגוריה ציבוריים |

### מורים

| מועדון / כרטיס | סטטוס | קישור להטבות | הערות |
|---|---|---|---|
| אשמורת - הסתדרות המורים | ⛔ חסום טכנית | - | חסום טכנית: Cloudflare (הוחלט לדלג, 17.9.26) |
| תמורה - ארגון המורים | ⛔ חסום טכנית | - | נבדק 23.9.26: הנתונים נטענים ב-JavaScript, לא נמצא מקור פתוח |

### סטודנטים

| מועדון / כרטיס | סטטוס | קישור להטבות | הערות |
|---|---|---|---|
| iStudent איי סטודנט | ⛔ חסום טכנית | - | נבדק 23.9.26: reCAPTCHA באתר, לא עוקפים |
| uniq | ✅ יש סקרייפר | [הטבות](https://www.uniq-club.co.il/) | uniq_scraper.py - GraphQL ציבורי admin.uniq-club.co.il (shopId 1, ללא לוגין) |
| אוניברסיטת תל אביב TAU | ✅ יש סקרייפר | [הטבות](https://www.tauclub.co.il/) | tau_club_scraper.py - אותה פלטפורמת uniq (shopId 2) |
| סטודנט גרופ | ✅ יש סקרייפר | [הטבות](https://studentgroup.co.il/) | studentgroup_scraper.py - WP REST ציבורי (product) |
| קמפוסכרט | ✅ יש סקרייפר | [הטבות](https://campus.style.co.il/) | campus_card_scraper.py - פלטפורמת style |

### ילדים

| מועדון / כרטיס | סטטוס | קישור להטבות | הערות |
|---|---|---|---|
| צעיר | ✅ יש סקרייפר | [הטבות](https://young.style.co.il/) | tzair_scraper.py - פלטפורמת style (style_platform.py), דפי קטגוריה ציבוריים |
| My Max | ✅ יש סקרייפר | [הטבות](https://www.max.co.il) | max_benefits_scraper.py - קטלוג ההטבות הציבורי של MAX |
| My Cal | ⛔ חסום טכנית | - | חסום טכנית: anti-bot / קטלוג דליל (הוחלט לדלג, 17.9.26) |
| מפתח 14-18 | ✅ יש סקרייפר | [הטבות](https://www.discountbank.co.il/private/credit-cards/discount-key/) | discount_key_scraper.py - מפתח דיסקונט, עמוד העסקים הציבורי של דיסקונט |

### מועדנים כללי

| מועדון / כרטיס | סטטוס | קישור להטבות | הערות |
|---|---|---|---|
| פיס פלוס (מפעל הפייס) | ⛔ חסום טכנית | - | חסום טכנית: הגנת Link11 (הוחלט לדלג, 17.9.26) |
| משקארד | ⛔ חסום טכנית | - | רק ~16 מותגים מובילים ציבוריים; הקטלוג המלא ב-API של חברים (23.9.26) |
| פליי קארד / FLY CARD / הנוסע המתמיד אל על | ⬜ טרם נכתב | - |  |
| חתול פיננסי | ✅ יש סקרייפר | [הטבות](https://moneyplan.co.il/benefits/) | moneyplan_scraper.py - WP REST ציבורי (benefits) |
| לייף סטייל | ✅ יש סקרייפר | [הטבות](https://lifestyle.style.co.il/) | lifestyle_club_scraper.py - פלטפורמת style (style_platform.py), דפי קטגוריה ציבוריים |
| Living | ✅ יש סקרייפר | [הטבות](https://www.livingclub.co.il/) | living_scraper.py - פלטפורמת style |
| כללית שלנו | ⛔ חסום טכנית | - | clalitr.co.il - לוגין עובד (נבדק 23.9.26) |
| PowerCard | ✅ יש סקרייפר | [הטבות](https://powercard.style.co.il/) | powercard_scraper.py - פלטפורמת style |
| DREAMCARD VIP / דריים קארד אשראי | ✅ יש סקרייפר | [הטבות](https://www.dreamcard.co.il/dreamcard-vip/) | dreamcard_scraper.py - API ציבורי של מותגים וסניפים, 15% קאשבק |
| ביטוח ישיר | ⛔ חסום טכנית | - | בדף המועדון רק הטבות ביטוח; הטבות בתי העסק באפליקציה בלבד (23.9.26) |
| זמן הראל | ⛔ חסום טכנית | - | WAF של הראל (466) (23.9.26) |
| עדיף | ✅ יש סקרייפר | [הטבות](https://adif.style.co.il/) | adif_scraper.py - פלטפורמת style (style_platform.py), דפי קטגוריה ציבוריים |
| ידיעות אחרונות | ✅ יש סקרייפר | [הטבות](https://www.yediot.co.il/) | yedioth_scraper.py - נוסף בסבב 2 |
| דיגיתל | ⛔ חסום טכנית | - | WAF של עיריית ת"א (472) + אזור תושבים עם לוגין (23.9.26) |
| ירושלמי | ⬜ טרם נכתב | - |  |
| ויגן אקטיב - vegan active | ⛔ חסום טכנית | - | אפליקציה בלבד, אחרי תרומה/לוגין (23.9.26) |
| אותי - עמותה ישראלית לאוטיזם | ✅ יש סקרייפר | [הטבות](https://oti.style.co.il/) | oti_scraper.py - פלטפורמת style |
| i need it | ⬜ טרם נכתב | - |  |
| רעות תקני לי | ⛔ חסום טכנית | - | בלוג קניות אישי + כרטיס max, ללא רשימת הטבות (23.9.26) |
| מועדון W | ⬜ טרם נכתב | - |  |
| riseup - רייזאפ | ⬜ טרם נכתב | - |  |
| מועדון המתנדבים | ✅ יש סקרייפר | [הטבות](https://mitnadvim4u.style.co.il/) | volunteers_club_scraper.py - פלטפורמת style (style_platform.py), דפי קטגוריה ציבוריים |
| buffpay מועדון לגיימרים | ⛔ חסום טכנית | - | הדומיין לא נמצא ולא אותר אתר הטבות ציבורי (23.9.26) |
| Clal Pay | ⛔ חסום טכנית | - | דף כרטיס בלבד, ללא רשימת הטבות (23.9.26) |
| 1824 | ⛔ חסום טכנית | - | אפליקציה בלבד (23.9.26) |

### רשתות מזון

| מועדון / כרטיס | סטטוס | קישור להטבות | הערות |
|---|---|---|---|
| 4Uשופרסל | ✅ יש סקרייפר | [הטבות](https://www.shufersal4u.co.il/) | shufersal4u_scraper.py - דפי קטגוריה ציבוריים (לוגין רק לרכישה) |
| WinCard+ מחסני השוק | ⬜ טרם נכתב | - |  |
| תן ביס | ⬜ טרם נכתב | - |  |
| רמי לוי המועדון | ✅ יש סקרייפר | [הטבות](https://rmrm.style.co.il/) | rami_levy_club_scraper.py - פלטפורמת style |
| ויקטורי | ⬜ טרם נכתב | - |  |
| bitcard קרפור קלאב | ⬜ טרם נכתב | - |  |
| שטראוס+ | ⛔ חסום טכנית | - | אתר עובדים מאחורי אתגר bot (Reblaze, 247) (23.9.26) |
| סיבוס | ⛔ חסום טכנית | - | קהילת HR, לא רשימת הטבות ציבורית (23.9.26) |

### קופות חולים

| מועדון / כרטיס | סטטוס | קישור להטבות | הערות |
|---|---|---|---|
| מכבי UpApp | ⛔ חסום טכנית | - | אין רשימת הטבות ציבורית; אפליקציה בלבד (23.9.26) |
| כללית Active+ | ⛔ חסום טכנית | - | WAF של כללית (403, Imperva) (23.9.26) |

### מועדנים פתוחים לכלל הציבור

| מועדון / כרטיס | סטטוס | קישור להטבות | הערות |
|---|---|---|---|
| Samsung Members | ✅ יש סקרייפר | [הטבות](https://www.samsung.com/il/mobile/samsung-members/benefits/) | samsung_members_scraper.py - דף ההטבות הציבורי (קרוסלה, ~13 הטבות) |
| FRIENDS | ⛔ חסום טכנית | - | ה-WP API מכיל רק פוסטים ודפים; אין רשימת הטבות (23.9.26) |
| מגה לאן כללי | ⛔ חסום טכנית | - | נבדק 23.9.26: פלטפורמת מועדונים לארגונים, דורשת כניסה |
| קופונופש | ✅ יש סקרייפר | [הטבות](https://cpnclub.co.il/) | cpnclub_scraper.py - API ציבורי be.cpnclub.co.il/api/v2/search/club |
| קניוני עזריאלי | ✅ יש סקרייפר | [הטבות](https://www.azrielimalls.co.il/coupons) | azrieli_malls_scraper.py - מבצעי הקניונים (ציבורי) |
| קניוני עופר/Myofer | ✅ יש סקרייפר | [הטבות](https://myofer.co.il/) | myofer_scraper.py - דפי המבצעים הציבוריים של כל קניון (__NEXT_DATA__) |
| קרמל | ⛔ חסום טכנית | - | loadMoreData.asp מחזיר שגיאת SQL בשרת; בדף רק 11 כרטיסים (23.9.26) |
| Cashdo | ✅ יש סקרייפר | [הטבות](https://cashdo.co.il/all-stores) | cashdo_scraper.py - קטלוג ציבורי |
| Mami - מאמי | ✅ יש סקרייפר | [הטבות](https://www.hi-mami.com/) | mami_scraper.py - קטלוג ציבורי |
| Myshops | ⬜ טרם נכתב | - |  |
| באר המשאלות | ⬜ טרם נכתב | - |  |
| Paybox פייבוקס | ⬜ טרם נכתב | - |  |
| קשקאש KashCash | ⛔ חסום טכנית | - | אפליקציה בלבד (23.9.26) |

### תו קנייה / גיפט קארד

| מועדון / כרטיס | סטטוס | קישור להטבות | הערות |
|---|---|---|---|
| Ofer Gift/עופר גיפטקארד | ⬜ טרם נכתב | - |  |
| BUYME ביימי | ✅ יש סקרייפר | [הטבות](https://buyme.co.il) | buyme_scraper.py - הנחות ספקים של BUYME |
| Gift Card מקס | ✅ יש סקרייפר | [הטבות](https://www.max.co.il/gift-card-network) | max_giftcard_scraper.py - רשת הגיפטקארד של MAX |
| Gift Card Executive מקס | ✅ יש סקרייפר | [הטבות](https://www.max.co.il/gift-card-network) | max_giftcard_scraper.py - רשת הגיפטקארד של MAX |
| Super Gift Card מקס | ✅ יש סקרייפר | [הטבות](https://www.max.co.il/gift-card-network) | max_giftcard_scraper.py - רשת הגיפטקארד של MAX |
| DREAMCARD gift card / דרים קארד גיפט | ⬜ טרם נכתב | - |  |
| LOVE gift card | ⬜ טרם נכתב | - |  |
| תו הזהב | ⬜ טרם נכתב | - |  |
| התו המלא - רמי לוי | ⬜ טרם נכתב | - |  |
| תו פלוס | ⛔ חסום טכנית | - | נבדק 23.9.26: רשימת הרשתות מופיעה רק כתמונות (בדפי הקטגוריה ובעלון PDF), אין טקסט או API |
| תו ביתן | ⬜ טרם נכתב | - |  |
| נופשונית\Swish Perfect | ✅ יש סקרייפר | [הטבות](https://swish.co.il/business/all-gifts-giftcard/product-103980) | swish_scraper.py - רשימת בתי העסק מעמוד המוצר (Next.js RSC) |
| נופשונית\Swish plus | ✅ יש סקרייפר | [הטבות](https://swish.co.il/home/fashion-and-style-giftcard/product-105380) | swish_scraper.py - רשימת בתי העסק מתוך עמוד המוצר (Next.js RSC) |
| נופשונית\Swish baby | ✅ יש סקרייפר | [הטבות](https://swish.co.il/home/birth-giftcard/product-95963) | swish_scraper.py - רשימת בתי העסק מעמוד המוצר (Next.js RSC) |
| נופשונית\Swish Premium | ✅ יש סקרייפר | [הטבות](https://swish.co.il/business/all-gifts-giftcard/product-104068) | swish_scraper.py - רשימת בתי העסק מעמוד המוצר (Next.js RSC) |
| נופשונית\Swish Unique | ✅ יש סקרייפר | [הטבות](https://swish.co.il/business/all-gifts-giftcard/product-72261) | swish_scraper.py - רשימת בתי העסק מעמוד המוצר (Next.js RSC) |
| ויקטורי 100% | ⬜ טרם נכתב | - |  |
| גלובל קארד - רעיונית | ✅ יש סקרייפר | [הטבות](https://www.raayonit.co.il/club/?ClubNum=18&ClubVoucherTypeNum=47) | raayonit_scraper.py - עמוד גלובל תו (branch feat/scrapers-round-2) |
| עזריאלי גיפטקארד | ✅ יש סקרייפר | [הטבות](https://buyme.co.il/brands/398383) | azrieli_giftcard_scraper.py - רשימת בתי העסק ב-BUYME (מותג 398383) |
| GiftCard Isracard (ישראכרט) | ⛔ חסום טכנית | - | חסום טכנית: WAF של ישראכרט (הוחלט לדלג, 17.9.26) |
| GiftCard Shopping (ישראכרט) | ⛔ חסום טכנית | - | חסום טכנית: WAF של ישראכרט (הוחלט לדלג, 17.9.26) |
| GiftCard (ישראכרט) | ⛔ חסום טכנית | - | חסום טכנית: WAF של ישראכרט (הוחלט לדלג, 17.9.26) |
| GiftCard Digitali (ישראכרט) | ⛔ חסום טכנית | - | חסום טכנית: WAF של ישראכרט (הוחלט לדלג, 17.9.26) |
| Gift Zone | ⛔ חסום טכנית | - | חסום טכנית: WAF של ישראכרט (הוחלט לדלג, 17.9.26) |
| Chef Zone | ⛔ חסום טכנית | - | חסום טכנית: WAF של ישראכרט (הוחלט לדלג, 17.9.26) |
| Spa Zone | ⛔ חסום טכנית | - | חסום טכנית: WAF של ישראכרט (הוחלט לדלג, 17.9.26) |
| All-In Zone | ⛔ חסום טכנית | - | חסום טכנית: WAF של ישראכרט (הוחלט לדלג, 17.9.26) |
| Baby Zone | ⛔ חסום טכנית | - | חסום טכנית: WAF של ישראכרט (הוחלט לדלג, 17.9.26) |
| Vacation Zone | ⛔ חסום טכנית | - | חסום טכנית: WAF של ישראכרט (הוחלט לדלג, 17.9.26) |
| Kosher Zone | ⛔ חסום טכנית | - | חסום טכנית: WAF של ישראכרט (הוחלט לדלג, 17.9.26) |
| Super Zone | ⛔ חסום טכנית | - | חסום טכנית: WAF של ישראכרט (הוחלט לדלג, 17.9.26) |
| XTRA SHOPPING גיפטקארד | ⛔ חסום טכנית | - | נבדק 23.9.26: Cloudflare Turnstile (CAPTCHA) |
| XTRA FASHION גיפטקארד | ⛔ חסום טכנית | - | נבדק 23.9.26: Cloudflare Turnstile (CAPTCHA) |
| XTRA MARKET גיפטקארד | ⛔ חסום טכנית | - | נבדק 23.9.26: Cloudflare Turnstile (CAPTCHA) |
| מחסני השוק גיפטקארד Wincard | ⬜ טרם נכתב | - |  |
| גיפתא | ✅ יש סקרייפר | [הטבות](https://gifta.co.il/) | gifta_scraper.py - WordPress API ציבורי (branch feat/scrapers-round-2) |
| גולד קארד | ✅ יש סקרייפר | [הטבות](https://goldcard-gift.com/) | goldcard_scraper.py - WordPress API ציבורי (branch feat/scrapers-round-2) |
| New Card Just4u | ⬜ טרם נכתב | - |  |
| +HappyGift | ⛔ חסום טכנית | - | נבדק 23.9.26: אפליקציית Angular, לא נמצא API פתוח |
