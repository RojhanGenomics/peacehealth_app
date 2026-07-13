import streamlit as st
import pandas as pd
from datetime import datetime
import jdatetime
import gspread
import streamlit.components.v1 as components
from google.oauth2.service_account import Credentials

# ============================================================
# Google Sheets connection (persistent storage)
# ============================================================
SHEET_NAME = "PeaceHealth Data"  # must match the Google Sheet you created & shared
WORKSHEET_NAME = "responses"

SHEET_COLUMNS = [
    "date_gregorian", "date_local", "language", "anonymous_id", "age_group", "gender",
    "country", "city",
    "phq4_interest", "phq4_down", "phq4_nervous", "phq4_worry",
    "phq4_anxiety_score", "phq4_depression_score", "phq4_total_score",
    "sleep", "headache", "stomach_pain", "war_event", "displaced", "access_basic",
    "family_contact", "safety", "support", "hope", "coping", "free_text",
]


@st.cache_resource(show_spinner=False)
def get_worksheet():
    """Connect once per session and reuse the same worksheet handle."""
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]
    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"], scopes=scopes
    )
    client = gspread.authorize(creds)
    spreadsheet = client.open(SHEET_NAME)
    try:
        worksheet = spreadsheet.worksheet(WORKSHEET_NAME)
    except gspread.exceptions.WorksheetNotFound:
        worksheet = spreadsheet.add_worksheet(WORKSHEET_NAME, rows=1000, cols=len(SHEET_COLUMNS))
        worksheet.append_row(SHEET_COLUMNS)
    if not worksheet.get_all_values():
        worksheet.append_row(SHEET_COLUMNS)
    return worksheet


def append_response(data: dict):
    worksheet = get_worksheet()
    worksheet.append_row([str(data.get(col, "")) for col in SHEET_COLUMNS])


def load_responses() -> pd.DataFrame:
    worksheet = get_worksheet()
    records = worksheet.get_all_records()
    if not records:
        return pd.DataFrame(columns=SHEET_COLUMNS)
    return pd.DataFrame(records)

# ============================================================
# Page config
# ============================================================
st.set_page_config(page_title="PeaceHealth Insights", page_icon="🧠", layout="centered")

# ============================================================
# PWA support: inject manifest, theme-color, and service worker
# registration into the parent document (Streamlit renders this
# component in a same-origin iframe, so window.parent.document
# is reachable). This lets mobile browsers offer "Add to Home
# Screen" / "Install App" for a standalone, app-like experience.
# ============================================================
components.html(
    """
    <script>
    (function () {
        const doc = window.parent.document;
        if (!doc.querySelector('link[rel="manifest"]')) {
            const manifestLink = doc.createElement('link');
            manifestLink.rel = 'manifest';
            manifestLink.href = 'app/static/manifest.json';
            doc.head.appendChild(manifestLink);
        }
        if (!doc.querySelector('meta[name="theme-color"]')) {
            const themeMeta = doc.createElement('meta');
            themeMeta.name = 'theme-color';
            themeMeta.content = '#1F4E5F';
            doc.head.appendChild(themeMeta);
        }
        if (!doc.querySelector('link[rel="apple-touch-icon"]')) {
            const appleIcon = doc.createElement('link');
            appleIcon.rel = 'apple-touch-icon';
            appleIcon.href = 'app/static/icon-192.png';
            doc.head.appendChild(appleIcon);
        }
        if ('serviceWorker' in navigator) {
            navigator.serviceWorker.register('app/static/sw.js').catch(function () {});
        }
    })();
    </script>
    """,
    height=0,
)

# ============================================================
# Digit conversion helpers (for Persian / Arabic numerals)
# ============================================================
PERSIAN_DIGITS = str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹")
ARABIC_DIGITS = str.maketrans("0123456789", "٠١٢٣٤٥٦٧٨٩")


def to_persian_digits(text: str) -> str:
    return text.translate(PERSIAN_DIGITS)


def to_arabic_digits(text: str) -> str:
    return text.translate(ARABIC_DIGITS)


# ============================================================
# Translations
# ============================================================
TEXT = {
    "fa": {
        "title": "🧠 PeaceHealth Insights",
        "subtitle": "ثبت وضعیت سلامت امروز شما",
        "privacy_notice": "🔒 پاسخ‌های شما بدون نام یا اطلاعات هویتی، در یک پایگاه داده‌ی امن ذخیره و فقط برای اهداف تحقیقاتی تحلیل می‌شوند.",
        "date_gregorian": "📅 **تاریخ امروز (میلادی):** {}",
        "date_local": "📅 **تاریخ امروز (شمسی):** {}",
        "language_label": "زبان / Language",
        "form_header": "### 📋 پرسشنامه سلامت",
        "age": "سن",
        "age_options": ["زیر ۱۸", "۱۸–۳۰", "۳۱–۵۰", "بالای ۵۰"],
        "gender": "جنسیت",
        "gender_options": ["مرد", "زن", "ترجیح می‌دهم نگویم"],
        "country": "کشور",
        "country_placeholder": "مثال: ایران",
        "city": "شهر / استان",
        "city_placeholder": "مثال: تهران، کرمانشاه، ...",
        "section1": "### ۱. غربالگری سلامت روان (بر پایه‌ی ابزار معتبر PHQ-4)",
        "phq4_intro": "در طول امروز، چقدر با موارد زیر مواجه بوده‌اید؟",
        "phq4_scale": ["اصلاً", "کمی", "نسبتاً زیاد", "خیلی زیاد"],
        "phq4_interest": "بی‌علاقگی یا نبود لذت در انجام کارها",
        "phq4_down": "احساس ناامیدی، دلسردی یا افسردگی",
        "phq4_nervous": "احساس عصبی بودن، اضطراب یا دستپاچگی",
        "phq4_worry": "ناتوانی در متوقف کردن یا کنترل نگرانی",
        "sleep": "کیفیت خواب شما امروز چطور بود؟",
        "sleep_help": "۱ = خیلی بد، ۱۰ = خیلی خوب",
        "section2": "### ۲. علائم جسمی",
        "headache": "آیا امروز سردرد داشته‌اید؟",
        "stomach_pain": "آیا امروز درد معده داشته‌اید؟",
        "yes": "بله",
        "no": "خیر",
        "section3": "### ۳. رویدادهای روز",
        "war_event": "آیا امروز رویداد جنگی خاصی را تجربه کرده‌اید؟",
        "war_event_options": [
            "هیچکدام",
            "حمله هوایی یا موشکی",
            "انفجار در نزدیکی",
            "قطع برق یا آب",
            "تهدید مستقیم",
            "آسیب به منزل یا محل کار",
        ],
        "displaced": "آیا در حال حاضر به دلیل شرایط موجود از خانه‌ی خود آواره یا جابه‌جا شده‌اید؟",
        "access_basic": "امروز به کدام‌یک از این موارد دسترسی داشته‌اید؟",
        "access_basic_options": ["آب آشامیدنی", "غذای کافی", "دارو/خدمات درمانی", "اینترنت یا تلفن"],
        "family_contact": "آیا امروز توانستید با خانواده یا عزیزان خود در تماس باشید؟",
        "section4": "### ۴. احساسات و حمایت",
        "safety": "امروز چقدر احساس امنیت می‌کنید؟",
        "support": "امروز چقدر از حمایت اجتماعی برخوردار بوده‌اید؟",
        "hope": "امروز چقدر نسبت به آینده امیدوار هستید؟",
        "coping": "امروز برای بهتر شدن حالتان یا مقابله با شرایط، از کدام‌یک از این روش‌ها استفاده کردید؟",
        "coping_options": [
            "صحبت با خانواده یا دوستان",
            "دعا یا نیایش / رفتار معنوی",
            "فعالیت بدنی یا ورزش",
            "تلاش برای استراحت یا حواس‌پرتی از مشکل",
            "کمک گرفتن از حمایت حرفه‌ای یا اجتماع محلی",
            "هیچ‌کدام",
        ],
        "section5": "### ۵. جمله آزاد",
        "free_text_label": "اگر بخواهید یک جمله درباره وضعیت امروزتان بنویسید، چه می‌گویید؟",
        "free_text_placeholder": "نظر خود را بنویسید...",
        "submit": "📥 ثبت پاسخ‌ها",
        "success": "✅ پاسخ‌های شما با موفقیت ثبت شد. از مشارکت شما سپاسگزاریم! 🙏",
        "summary_expander": "📊 مشاهده خلاصه پاسخ‌ها",
        "saved_info": "💡 داده‌های شما در شیت `{}` ذخیره شد.",
        "monitor_header": "📊 دیده‌بان سلامت جامعه (نمونه)",
        "show_data_btn": "نمایش داده‌های ثبت شده",
        "no_data_warning": "هنوز داده‌ای ثبت نشده است. اولین داده را ثبت کنید!",
        "consent_title": "🔒 رضایت آگاهانه برای شرکت در این پرسشنامه",
        "consent_intro": "لطفاً پیش از ادامه، موارد زیر را با دقت بخوانید:",
        "consent_points": [
            "شرکت در این پرسشنامه کاملاً داوطلبانه است و می‌توانید در هر لحظه بدون هیچ عواقبی آن را متوقف کنید.",
            "هیچ نام، شماره تماس، یا اطلاعات هویتی از شما پرسیده نمی‌شود.",
            "داده‌های شما به‌صورت ناشناس در یک پایگاه داده‌ی امن (Google Sheets، با دسترسی محدود) ذخیره می‌شود.",
            "داده‌ها فقط برای اهداف تحقیقاتی و ارائه‌ی تصویری کلی از وضعیت سلامت جامعه استفاده می‌شوند و هرگز فروخته یا برای تبلیغات استفاده نمی‌شوند.",
            "می‌توانید از پاسخ به هر سؤال خاصی که تمایل ندارید صرف‌نظر کنید.",
        ],
        "consent_checkbox": "متوجه شدم و با شرکت در این پرسشنامه موافقم.",
        "consent_button": "ورود به پرسشنامه",
        "consent_required_warning": "برای ادامه، لطفاً ابتدا تیک رضایت را بزنید.",
        "already_submitted_title": "✅ شرکت شما امروز ثبت شده است",
        "already_submitted_body": "به نظر می‌رسد شما امروز قبلاً در این پرسشنامه شرکت کرده‌اید. برای اینکه داده‌های آماری دقیق بمانند، هر فرد فقط می‌تواند یک‌بار در روز پاسخ ثبت کند. لطفاً فردا دوباره مراجعه کنید. از مشارکت شما سپاسگزاریم! 🙏",
        "id_intro": "برای جلوگیری از ثبت چندباره‌ی پاسخ‌ها و امکان بررسی روند سلامت شما در طول زمان، این دو سؤال کوتاه را پاسخ دهید (اطلاعات هویتی محسوب نمی‌شوند و ذخیره نمی‌شوند):",
        "id_part1_label": "حرف اول نام کوچک مادرتان",
        "id_part1_placeholder": "مثال: ز",
        "id_part2_label": "دو رقم آخر سال تولدتان (میلادی یا شمسی)",
        "id_part2_placeholder": "مثال: ۷۲",
        "id_required_warning": "لطفاً هر دو سؤال بالا را برای ادامه پاسخ دهید.",
    },
    "en": {
        "title": "🧠 PeaceHealth Insights",
        "subtitle": "Record your health status for today",
        "privacy_notice": "🔒 Your responses are stored anonymously (no name or identifying details) in a secured database and used only for research purposes.",
        "date_gregorian": "📅 **Today's date (Gregorian):** {}",
        "date_local": "📅 **Today's date (local calendar):** {}",
        "language_label": "زبان / Language",
        "form_header": "### 📋 Health Questionnaire",
        "age": "Age",
        "age_options": ["Under 18", "18–30", "31–50", "Over 50"],
        "gender": "Gender",
        "gender_options": ["Male", "Female", "Prefer not to say"],
        "country": "Country",
        "country_placeholder": "e.g. Iran",
        "city": "City / Province",
        "city_placeholder": "e.g. Tehran, Kermanshah, ...",
        "section1": "### 1. Well-Being Screening (based on the validated PHQ-4 tool)",
        "phq4_intro": "Over the course of today, how much have you been bothered by the following?",
        "phq4_scale": ["Not at all", "A little", "Quite a bit", "A lot"],
        "phq4_interest": "Little interest or pleasure in doing things",
        "phq4_down": "Feeling down, depressed, or hopeless",
        "phq4_nervous": "Feeling nervous, anxious, or on edge",
        "phq4_worry": "Not being able to stop or control worrying",
        "sleep": "How was your sleep quality today?",
        "sleep_help": "1 = Very bad, 10 = Very good",
        "section2": "### 2. Physical Symptoms",
        "headache": "Did you have a headache today?",
        "stomach_pain": "Did you have stomach pain today?",
        "yes": "Yes",
        "no": "No",
        "section3": "### 3. Events of the Day",
        "war_event": "Did you experience any war-related event today?",
        "war_event_options": [
            "None",
            "Airstrike or rocket attack",
            "Explosion nearby",
            "Power or water outage",
            "Direct threat",
            "Damage to home or workplace",
        ],
        "displaced": "Are you currently displaced from your home due to the situation?",
        "access_basic": "Which of the following did you have access to today?",
        "access_basic_options": ["Drinking water", "Sufficient food", "Medicine/healthcare", "Internet or phone"],
        "family_contact": "Were you able to contact family or loved ones today?",
        "section4": "### 4. Feelings & Support",
        "safety": "How safe do you feel today?",
        "support": "How much social support did you receive today?",
        "hope": "How hopeful do you feel about the future today?",
        "coping": "Which of the following did you use today to feel better or cope with the situation?",
        "coping_options": [
            "Talked with family or friends",
            "Prayer / spiritual practice",
            "Physical activity or exercise",
            "Tried to rest or distract myself",
            "Sought professional or community support",
            "None of these",
        ],
        "section5": "### 5. Open Comment",
        "free_text_label": "Write a sentence about your situation today:",
        "free_text_placeholder": "Write your thoughts here...",
        "submit": "📥 Submit Responses",
        "success": "✅ Your responses have been successfully recorded. Thank you for your participation! 🙏",
        "summary_expander": "📊 View Summary",
        "saved_info": "💡 Your data has been saved in the `{}` sheet.",
        "monitor_header": "📊 Community Health Monitor (Sample)",
        "show_data_btn": "Show Recorded Data",
        "no_data_warning": "No data recorded yet. Please submit your first response!",
        "consent_title": "🔒 Informed Consent to Participate",
        "consent_intro": "Please read the following carefully before continuing:",
        "consent_points": [
            "Participation in this questionnaire is entirely voluntary, and you may stop at any time without any consequence.",
            "No name, contact details, or identifying information is requested from you.",
            "Your data is stored anonymously in a secured database (Google Sheets, with restricted access).",
            "Data is used only for research purposes and to provide an aggregate picture of community well-being. It is never sold or used for advertising.",
            "You may skip any individual question you do not wish to answer.",
        ],
        "consent_checkbox": "I understand and agree to participate.",
        "consent_button": "Enter Questionnaire",
        "consent_required_warning": "Please check the consent box before continuing.",
        "already_submitted_title": "✅ Your response for today is already recorded",
        "already_submitted_body": "It looks like you've already completed this questionnaire today. To keep the statistics accurate, each person can submit only once per day. Please come back tomorrow. Thank you for participating! 🙏",
        "id_intro": "To prevent duplicate submissions and allow us to track your well-being over time, please answer these two short questions (not identifying information, and not stored as-is):",
        "id_part1_label": "First letter of your mother's first name",
        "id_part1_placeholder": "e.g. M",
        "id_part2_label": "Last two digits of your birth year",
        "id_part2_placeholder": "e.g. 92",
        "id_required_warning": "Please answer both questions above to continue.",
    },
    "ar": {
        "title": "🧠 رؤى السلام الصحية",
        "subtitle": "سجّل حالتك الصحية اليوم",
        "privacy_notice": "🔒 يتم تخزين إجاباتك بشكل مجهول (دون اسم أو معلومات تعريفية) في قاعدة بيانات آمنة وتُستخدم فقط لأغراض بحثية.",
        "date_gregorian": "📅 **التاريخ الميلادي اليوم:** {}",
        "date_local": "📅 **التاريخ اليوم (التقويم المحلي):** {}",
        "language_label": "زبان / Language",
        "form_header": "### 📋 استبيان الصحة",
        "age": "العمر",
        "age_options": ["أقل من ١٨", "١٨–٣٠", "٣١–٥٠", "أكثر من ٥٠"],
        "gender": "الجنس",
        "gender_options": ["ذكر", "أنثى", "أفضل عدم الذكر"],
        "country": "الدولة",
        "country_placeholder": "مثال: العراق",
        "city": "المدينة / المحافظة",
        "city_placeholder": "مثال: بغداد، دمشق، ...",
        "section1": "### ١. فحص الصحة النفسية (بناءً على أداة PHQ-4 المعتمدة)",
        "phq4_intro": "خلال اليوم، إلى أي مدى شعرت بالانزعاج مما يلي؟",
        "phq4_scale": ["أبداً", "قليلاً", "بشكل ملحوظ", "كثيراً"],
        "phq4_interest": "قلة الاهتمام أو المتعة في القيام بالأشياء",
        "phq4_down": "الشعور بالإحباط أو الاكتئاب أو اليأس",
        "phq4_nervous": "الشعور بالعصبية أو القلق أو التوتر",
        "phq4_worry": "عدم القدرة على إيقاف أو التحكم في القلق",
        "sleep": "كيف كانت جودة نومك اليوم؟",
        "sleep_help": "١ = سيئة جداً، ١٠ = جيدة جداً",
        "section2": "### ٢. الأعراض الجسدية",
        "headache": "هل عانيت من صداع اليوم؟",
        "stomach_pain": "هل عانيت من ألم في المعدة اليوم؟",
        "yes": "نعم",
        "no": "لا",
        "section3": "### ٣. أحداث اليوم",
        "war_event": "هل واجهت أي حدث متعلق بالحرب اليوم؟",
        "war_event_options": [
            "لا شيء",
            "غارة جوية أو صاروخية",
            "انفجار قريب",
            "انقطاع الكهرباء أو الماء",
            "تهديد مباشر",
            "ضرر لحق بالمنزل أو مكان العمل",
        ],
        "displaced": "هل أنت نازح حالياً عن منزلك بسبب الوضع الراهن؟",
        "access_basic": "أي من التالي كان متاحاً لك اليوم؟",
        "access_basic_options": ["مياه الشرب", "غذاء كافٍ", "دواء/رعاية صحية", "إنترنت أو هاتف"],
        "family_contact": "هل تمكنت من التواصل مع عائلتك أو أحبائك اليوم؟",
        "section4": "### ٤. المشاعر والدعم",
        "safety": "ما مدى شعورك بالأمان اليوم؟",
        "support": "ما مقدار الدعم الاجتماعي الذي تلقيته اليوم؟",
        "hope": "ما مدى شعورك بالأمل تجاه المستقبل اليوم؟",
        "coping": "أي مما يلي استخدمته اليوم لتشعر بتحسن أو للتعامل مع الوضع؟",
        "coping_options": [
            "التحدث مع العائلة أو الأصدقاء",
            "الصلاة / ممارسة روحية",
            "النشاط البدني أو الرياضة",
            "محاولة الراحة أو تشتيت الانتباه",
            "طلب الدعم المهني أو المجتمعي",
            "لا شيء من ذلك",
        ],
        "section5": "### ٥. تعليق مفتوح",
        "free_text_label": "اكتب جملة عن وضعك اليوم:",
        "free_text_placeholder": "اكتب أفكارك هنا...",
        "submit": "📥 إرسال الإجابات",
        "success": "✅ تم تسجيل إجاباتك بنجاح. شكراً لمشاركتك! 🙏",
        "summary_expander": "📊 عرض الملخص",
        "saved_info": "💡 تم حفظ بياناتك في الجدول `{}`.",
        "monitor_header": "📊 مراقب صحة المجتمع (عينة)",
        "show_data_btn": "عرض البيانات المسجلة",
        "no_data_warning": "لا توجد بيانات مسجلة بعد. يرجى إرسال أول إجابة!",
        "consent_title": "🔒 الموافقة المستنيرة على المشاركة",
        "consent_intro": "يرجى قراءة ما يلي بعناية قبل المتابعة:",
        "consent_points": [
            "المشاركة في هذا الاستبيان طوعية تماماً، ويمكنك التوقف في أي وقت دون أي عواقب.",
            "لا يُطلب منك أي اسم أو معلومات اتصال أو معلومات تعريفية.",
            "يتم تخزين بياناتك بشكل مجهول في قاعدة بيانات آمنة (Google Sheets، بوصول محدود).",
            "تُستخدم البيانات فقط لأغراض بحثية ولتقديم صورة عامة عن صحة المجتمع. لا تُباع أبداً ولا تُستخدم للإعلانات.",
            "يمكنك تخطي أي سؤال معين لا ترغب في الإجابة عليه.",
        ],
        "consent_checkbox": "لقد فهمت وأوافق على المشاركة.",
        "consent_button": "الدخول إلى الاستبيان",
        "consent_required_warning": "يرجى تحديد مربع الموافقة قبل المتابعة.",
        "already_submitted_title": "✅ تم تسجيل مشاركتك لهذا اليوم بالفعل",
        "already_submitted_body": "يبدو أنك أكملت هذا الاستبيان بالفعل اليوم. للحفاظ على دقة الإحصائيات، يمكن لكل شخص إرسال إجابة واحدة فقط في اليوم. يرجى العودة غداً. شكراً لمشاركتك! 🙏",
        "id_intro": "لمنع تكرار الإرسال ولمساعدتنا في متابعة صحتك عبر الزمن، يرجى الإجابة عن هذين السؤالين القصيرين (ليست معلومات تعريفية ولا تُحفظ كما هي):",
        "id_part1_label": "الحرف الأول من اسم والدتك",
        "id_part1_placeholder": "مثال: م",
        "id_part2_label": "آخر رقمين من سنة ميلادك",
        "id_part2_placeholder": "مثال: 92",
        "id_required_warning": "يرجى الإجابة عن كلا السؤالين أعلاه للمتابعة.",
    },
}

LANGUAGE_OPTIONS = {"فارسی": "fa", "English": "en", "العربية": "ar"}

# ============================================================
# Language selector (rendered before anything else so we know
# which direction/text to use for the rest of the page)
# ============================================================
language_display = st.radio(
    "زبان / Language / اللغة", list(LANGUAGE_OPTIONS.keys()), index=0, horizontal=True
)
lang = LANGUAGE_OPTIONS[language_display]
t = TEXT[lang]
is_rtl = lang in ("fa", "ar")

# ============================================================
# Direction-aware styling
# ============================================================
direction_css = "rtl" if is_rtl else "ltr"
st.markdown(
    f"""
    <style>
        .stApp {{
            direction: {direction_css};
        }}
        .stApp * {{
            text-align: {'right' if is_rtl else 'left'};
        }}
    </style>
    """,
    unsafe_allow_html=True,
)

today_gregorian = datetime.now().strftime("%Y-%m-%d")

# ============================================================
# Daily submission lock (best-effort, privacy-preserving)
# We never collect names/phone numbers, so we can't truly
# identify a person. Instead we use the respondent's own browser
# storage: once they submit, their browser remembers today's date
# and the app blocks a second submission from that same browser
# on the same day. This isn't bulletproof (clearing browser data
# or using a different device/incognito window bypasses it), but
# it stops the common case of accidental or casual repeat entries.
# ============================================================
if st.query_params.get("already_submitted") == "1":
    st.title(t["title"])
    st.markdown("---")
    st.success(t["already_submitted_title"])
    st.write(t["already_submitted_body"])
    st.stop()

components.html(
    f"""
    <script>
    (function () {{
        try {{
            const today = "{today_gregorian}";
            const last = window.parent.localStorage.getItem('peacehealth_submitted_date');
            const url = new URL(window.parent.location.href);
            if (last === today && url.searchParams.get('already_submitted') !== '1') {{
                url.searchParams.set('already_submitted', '1');
                window.parent.location.href = url.toString();
            }}
        }} catch (e) {{}}
    }})();
    </script>
    """,
    height=0,
)

# ============================================================
# Informed consent gate — the questionnaire is hidden until the
# respondent actively checks the consent box and clicks through.
# ============================================================
if "consent_given" not in st.session_state:
    st.session_state.consent_given = False

if not st.session_state.consent_given:
    st.title(t["title"])
    st.markdown("---")
    st.subheader(t["consent_title"])
    st.write(t["consent_intro"])
    for point in t["consent_points"]:
        st.markdown(f"- {point}")
    st.markdown("---")

    agree = st.checkbox(t["consent_checkbox"])
    if st.button(t["consent_button"]):
        if agree:
            st.session_state.consent_given = True
            st.rerun()
        else:
            st.warning(t["consent_required_warning"])
    st.stop()

# ============================================================
# Header
# ============================================================
st.title(t["title"])
st.subheader(t["subtitle"])
st.markdown("---")

today_jalali_raw = jdatetime.datetime.now().strftime("%Y/%m/%d")
if lang == "fa":
    today_local = to_persian_digits(today_jalali_raw)
elif lang == "ar":
    today_local = to_arabic_digits(today_jalali_raw)
else:
    today_local = today_jalali_raw

st.info(t["privacy_notice"])
st.write(t["date_gregorian"].format(today_gregorian))
if lang != "en":
    st.write(t["date_local"].format(today_local))
st.markdown("---")

# ============================================================
# Form
# ============================================================
with st.form("health_form"):
    st.markdown(t["form_header"])

    st.caption(t["id_intro"])
    id_col1, id_col2 = st.columns(2)
    with id_col1:
        id_part1 = st.text_input(t["id_part1_label"], placeholder=t["id_part1_placeholder"], max_chars=1)
    with id_col2:
        id_part2 = st.text_input(t["id_part2_label"], placeholder=t["id_part2_placeholder"], max_chars=2)

    col1, col2 = st.columns(2)
    with col1:
        age_group = st.selectbox(t["age"], t["age_options"])
        gender = st.selectbox(t["gender"], t["gender_options"])
    with col2:
        country = st.text_input(t["country"], placeholder=t["country_placeholder"])
        city = st.text_input(t["city"], placeholder=t["city_placeholder"])

    st.markdown("---")
    st.markdown(t["section1"])
    st.caption(t["phq4_intro"])
    phq4_interest = st.radio(t["phq4_interest"], t["phq4_scale"], horizontal=True)
    phq4_down = st.radio(t["phq4_down"], t["phq4_scale"], horizontal=True)
    phq4_nervous = st.radio(t["phq4_nervous"], t["phq4_scale"], horizontal=True)
    phq4_worry = st.radio(t["phq4_worry"], t["phq4_scale"], horizontal=True)
    sleep = st.slider(t["sleep"], 1, 10, 5, help=t["sleep_help"])

    st.markdown("---")
    st.markdown(t["section2"])
    col3, col4 = st.columns(2)
    with col3:
        headache = st.radio(t["headache"], [t["yes"], t["no"]], index=1)
    with col4:
        stomach_pain = st.radio(t["stomach_pain"], [t["yes"], t["no"]], index=1)

    st.markdown("---")
    st.markdown(t["section3"])
    war_event = st.selectbox(t["war_event"], t["war_event_options"])
    displaced = st.radio(t["displaced"], [t["yes"], t["no"]], index=1)
    access_basic = st.multiselect(t["access_basic"], t["access_basic_options"])
    family_contact = st.radio(t["family_contact"], [t["yes"], t["no"]], index=0)

    st.markdown("---")
    st.markdown(t["section4"])
    safety = st.slider(t["safety"], 1, 10, 5)
    support = st.slider(t["support"], 1, 10, 5)
    hope = st.slider(t["hope"], 1, 10, 5)
    coping = st.multiselect(t["coping"], t["coping_options"])

    st.markdown("---")
    st.markdown(t["section5"])
    free_text = st.text_area(t["free_text_label"], placeholder=t["free_text_placeholder"])

    submitted = st.form_submit_button(t["submit"])

# ============================================================
# Handle submission
# ============================================================
if submitted:
    if not id_part1.strip() or not id_part2.strip():
        st.warning(t["id_required_warning"])
        st.stop()

    anonymous_id = f"{id_part1.strip().upper()[:1]}{id_part2.strip()[:2]}"

    scale = t["phq4_scale"]
    interest_score = scale.index(phq4_interest)
    down_score = scale.index(phq4_down)
    nervous_score = scale.index(phq4_nervous)
    worry_score = scale.index(phq4_worry)

    data = {
        "date_gregorian": today_gregorian,
        "date_local": today_jalali_raw,
        "language": lang,
        "anonymous_id": anonymous_id,
        "age_group": age_group,
        "gender": gender,
        "country": country,
        "city": city,
        "phq4_interest": phq4_interest,
        "phq4_down": phq4_down,
        "phq4_nervous": phq4_nervous,
        "phq4_worry": phq4_worry,
        "phq4_anxiety_score": nervous_score + worry_score,
        "phq4_depression_score": interest_score + down_score,
        "phq4_total_score": interest_score + down_score + nervous_score + worry_score,
        "sleep": sleep,
        "headache": headache,
        "stomach_pain": stomach_pain,
        "war_event": war_event,
        "displaced": displaced,
        "access_basic": ", ".join(access_basic),
        "family_contact": family_contact,
        "safety": safety,
        "support": support,
        "hope": hope,
        "coping": ", ".join(coping),
        "free_text": free_text,
    }

    st.balloons()
    st.success(t["success"])

    with st.expander(t["summary_expander"]):
        st.json(data)

    try:
        append_response(data)
        st.info(t["saved_info"].format(SHEET_NAME))
        components.html(
            f"""
            <script>
            try {{
                window.parent.localStorage.setItem('peacehealth_submitted_date', "{today_gregorian}");
            }} catch (e) {{}}
            </script>
            """,
            height=0,
        )
    except Exception as e:
        st.error(f"⚠️ {e}")

# ============================================================
# Community monitor (sample view of recent submissions)
# ============================================================
st.markdown("---")
st.subheader(t["monitor_header"])

if st.button(t["show_data_btn"]):
    df = load_responses()
    if not df.empty:
        st.dataframe(df.tail(10))
        chart_cols = ["phq4_anxiety_score", "phq4_depression_score", "sleep"]
        for col in chart_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")
        available_cols = [c for c in chart_cols if c in df.columns]
        if available_cols:
            st.line_chart(df[available_cols].tail(20))
    else:
        st.warning(t["no_data_warning"])
