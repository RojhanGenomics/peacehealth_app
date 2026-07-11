import streamlit as st
import pandas as pd
from datetime import datetime
import jdatetime
import gspread
from google.oauth2.service_account import Credentials

# ============================================================
# Google Sheets connection (persistent storage)
# ============================================================
SHEET_NAME = "PeaceHealth Data"  # must match the Google Sheet you created & shared
WORKSHEET_NAME = "responses"

SHEET_COLUMNS = [
    "date_gregorian", "date_local", "language", "age_group", "gender",
    "country", "city", "stress", "anxiety", "depression", "sleep",
    "headache", "stomach_pain", "war_event", "displaced", "access_basic",
    "family_contact", "safety", "support", "hope", "free_text",
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
        "privacy_notice": "🔒 تمام داده‌ها به صورت ناشناس ذخیره می‌شوند و فقط برای اهداف تحقیقاتی استفاده می‌شوند.",
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
        "section1": "### ۱. سطح استرس و اضطراب",
        "stress": "امروز چقدر استرس داشته‌اید؟",
        "stress_help": "۱ = خیلی کم، ۱۰ = خیلی زیاد",
        "anxiety": "امروز چقدر احساس اضطراب کرده‌اید؟",
        "depression": "امروز چقدر احساس افسردگی یا ناامیدی کرده‌اید؟",
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
    },
    "en": {
        "title": "🧠 PeaceHealth Insights",
        "subtitle": "Record your health status for today",
        "privacy_notice": "🔒 All data is stored anonymously and used only for research purposes.",
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
        "section1": "### 1. Stress & Anxiety Level",
        "stress": "How much stress did you feel today?",
        "stress_help": "1 = Very low, 10 = Very high",
        "anxiety": "How much anxiety did you feel today?",
        "depression": "How much depression or hopelessness did you feel today?",
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
    },
    "ar": {
        "title": "🧠 رؤى السلام الصحية",
        "subtitle": "سجّل حالتك الصحية اليوم",
        "privacy_notice": "🔒 يتم تخزين جميع البيانات بشكل مجهول وتُستخدم فقط لأغراض بحثية.",
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
        "section1": "### ١. مستوى التوتر والقلق",
        "stress": "كم كان مستوى التوتر لديك اليوم؟",
        "stress_help": "١ = منخفض جداً، ١٠ = مرتفع جداً",
        "anxiety": "كم شعرت بالقلق اليوم؟",
        "depression": "كم شعرت بالاكتئاب أو اليأس اليوم؟",
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

# ============================================================
# Header
# ============================================================
st.title(t["title"])
st.subheader(t["subtitle"])
st.markdown("---")

today_gregorian = datetime.now().strftime("%Y-%m-%d")
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

    col1, col2 = st.columns(2)
    with col1:
        age_group = st.selectbox(t["age"], t["age_options"])
        gender = st.selectbox(t["gender"], t["gender_options"])
    with col2:
        country = st.text_input(t["country"], placeholder=t["country_placeholder"])
        city = st.text_input(t["city"], placeholder=t["city_placeholder"])

    st.markdown("---")
    st.markdown(t["section1"])
    stress = st.slider(t["stress"], 1, 10, 5, help=t["stress_help"])
    anxiety = st.slider(t["anxiety"], 1, 10, 5)
    depression = st.slider(t["depression"], 1, 10, 5)
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

    st.markdown("---")
    st.markdown(t["section5"])
    free_text = st.text_area(t["free_text_label"], placeholder=t["free_text_placeholder"])

    submitted = st.form_submit_button(t["submit"])

# ============================================================
# Handle submission
# ============================================================
if submitted:
    data = {
        "date_gregorian": today_gregorian,
        "date_local": today_jalali_raw,
        "language": lang,
        "age_group": age_group,
        "gender": gender,
        "country": country,
        "city": city,
        "stress": stress,
        "anxiety": anxiety,
        "depression": depression,
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
        "free_text": free_text,
    }

    st.balloons()
    st.success(t["success"])

    with st.expander(t["summary_expander"]):
        st.json(data)

    try:
        append_response(data)
        st.info(t["saved_info"].format(SHEET_NAME))
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
        for col in ["stress", "anxiety", "depression"]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")
        st.line_chart(df[["stress", "anxiety", "depression"]].tail(20))
    else:
        st.warning(t["no_data_warning"])
