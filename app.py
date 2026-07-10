import streamlit as st
import pandas as pd
from datetime import datetime
import json
import os
import jdatetime

# تنظیمات صفحه
st.set_page_config(page_title="PeaceHealth Insights", page_icon="🧠", layout="centered")

# تنظیم جهت متن برای فارسی
st.markdown("""
<style>
    .stApp {
        direction: rtl;
    }
    .stApp * {
        text-align: right;
    }
    .st-bw, .st-cq, .st-df, .st-dg {
        direction: rtl;
    }
</style>
""", unsafe_allow_html=True)

# عنوان اپلیکیشن
st.title("🧠 PeaceHealth Insights")
st.subheader("ثبت وضعیت سلامت امروز شما")
st.markdown("---")

# تاریخ امروز (شمسی و میلادی)
today_gregorian = datetime.now().strftime("%Y-%m-%d")
today_jalali = jdatetime.datetime.now().strftime("%Y-%m-%d")

st.info(f"🔒 تمام داده‌ها به صورت ناشناس ذخیره می‌شوند و فقط برای اهداف تحقیقاتی استفاده می‌شوند.")
st.write(f"📅 **تاریخ امروز (میلادی):** {today_gregorian}")
st.write(f"📅 **تاریخ امروز (شمسی):** {today_jalali}")
st.markdown("---")

# زبان
language = st.radio("زبان / Language", ["فارسی", "English"], index=0)

st.markdown("---")

# فرم ورودی
with st.form("health_form"):
    if language == "فارسی":
        st.markdown("### 📋 پرسشنامه سلامت")
    else:
        st.markdown("### 📋 Health Questionnaire")

    col1, col2 = st.columns(2)

    with col1:
        if language == "فارسی":
            age_group = st.selectbox("سن", ["زیر ۱۸", "۱۸-۳۰", "۳۱-۵۰", "بالای ۵۰"])
            gender = st.selectbox("جنسیت", ["مرد", "زن"])
            region = st.text_input("منطقه (شهر یا استان)", placeholder="مثال: تهران، کرمانشاه، ...")
        else:
            age_group = st.selectbox("Age", ["Under 18", "18-30", "31-50", "Over 50"])
            gender = st.selectbox("Gender", ["Male", "Female"])
            region = st.text_input("Region (City or Province)", placeholder="Example: Tehran, Kermanshah, ...")

    with col2:
        if language == "فارسی":
            st.write(f"📅 تاریخ امروز (شمسی): {today_jalali}")
        else:
            st.write(f"📅 Today's Date (Gregorian): {today_gregorian}")

    st.markdown("---")

    # سوالات
    if language == "فارسی":
        st.markdown("### ۱. سطح استرس و اضطراب")
        stress = st.slider("امروز چقدر استرس داشته‌اید؟", 1, 10, 5, help="۱ = خیلی کم، ۱۰ = خیلی زیاد")
        anxiety = st.slider("امروز چقدر احساس اضطراب کرده‌اید؟", 1, 10, 5)
        depression = st.slider("امروز چقدر احساس افسردگی یا ناامیدی کرده‌اید؟", 1, 10, 5)
        sleep = st.slider("امروز چقدر خوب خوابیده‌اید؟", 1, 10, 5, help="۱ = خیلی بد، ۱۰ = خیلی خوب")

        st.markdown("---")
        st.markdown("### ۲. علائم جسمی")

        col3, col4 = st.columns(2)
        with col3:
            headache = st.radio("آیا امروز سردرد داشته‌اید؟", ["بله", "خیر"], index=1)
        with col4:
            stomach_pain = st.radio("آیا امروز درد معده داشته‌اید؟", ["بله", "خیر"], index=1)

        st.markdown("---")
        st.markdown("### ۳. رویدادهای روز")

        war_event = st.selectbox("آیا امروز رویداد جنگی خاصی را تجربه کرده‌اید؟", [
            "هیچکدام",
            "حمله هوایی یا موشکی",
            "انفجار در نزدیکی",
            "قطع برق یا آب",
            "تهدید مستقیم"
        ])

        st.markdown("---")
        st.markdown("### ۴. احساسات و حمایت")

        safety = st.slider("امروز چقدر احساس امنیت می‌کنید؟", 1, 10, 5)
        support = st.slider("امروز چقدر از حمایت اجتماعی برخوردار بوده‌اید؟", 1, 10, 5)

        st.markdown("---")
        st.markdown("### ۵. جمله آزاد")

        free_text = st.text_area("اگر بخواهید یک جمله درباره وضعیت امروزتان بنویسید، چه می‌گویید؟", placeholder="نظر خود را بنویسید...")

        submitted = st.form_submit_button("📥 ثبت پاسخ‌ها")

    else:
        st.markdown("### ۱. Stress & Anxiety Level")
        stress = st.slider("How much stress did you feel today?", 1, 10, 5, help="1 = Very low, 10 = Very high")
        anxiety = st.slider("How much anxiety did you feel today?", 1, 10, 5)
        depression = st.slider("How much depression or hopelessness did you feel today?", 1, 10, 5)
        sleep = st.slider("How well did you sleep today?", 1, 10, 5, help="1 = Very bad, 10 = Very good")

        st.markdown("---")
        st.markdown("### ۲. Physical Symptoms")

        col3, col4 = st.columns(2)
        with col3:
            headache = st.radio("Did you have a headache today?", ["Yes", "No"], index=1)
        with col4:
            stomach_pain = st.radio("Did you have stomach pain today?", ["Yes", "No"], index=1)

        st.markdown("---")
        st.markdown("### ۳. Events of the Day")

        war_event = st.selectbox("Did you experience any war-related event today?", [
            "None",
            "Airstrike or rocket attack",
            "Explosion nearby",
            "Power or water outage",
            "Direct threat"
        ])

        st.markdown("---")
        st.markdown("### ۴. Feelings & Support")

        safety = st.slider("How safe do you feel today?", 1, 10, 5)
        support = st.slider("How much social support did you receive today?", 1, 10, 5)

        st.markdown("---")
        st.markdown("### ۵. Open Comment")

        free_text = st.text_area("Write a sentence about your situation today...", placeholder="Write your thoughts here...")

        submitted = st.form_submit_button("📥 Submit Responses")

# پردازش بعد از ثبت
if submitted:
    # ذخیره داده‌ها
    data = {
        "تاریخ_میلادی": today_gregorian,
        "تاریخ_شمسی": today_jalali,
        "زبان": language,
        "سن": age_group,
        "جنسیت": gender,
        "منطقه": region,
        "استرس": stress,
        "اضطراب": anxiety,
        "افسردگی": depression,
        "خواب": sleep,
        "سردرد": headache,
        "درد_معده": stomach_pain,
        "رویداد_جنگی": war_event,
        "احساس_امنیت": safety,
        "حمایت_اجتماعی": support,
        "جمله_آزاد": free_text
    }

    st.balloons()
    if language == "فارسی":
        st.success("✅ پاسخ‌های شما با موفقیت ثبت شد. از مشارکت شما سپاسگزاریم! 🙏")
    else:
        st.success("✅ Your responses have been successfully recorded. Thank you for your participation! 🙏")

    with st.expander("📊 مشاهده خلاصه پاسخ‌ها / View Summary"):
        st.json(data)

    # ذخیره در CSV
    csv_file = "peacehealth_data.csv"
    try:
        df_existing = pd.read_csv(csv_file)
        df_new = pd.DataFrame([data])
        df_combined = pd.concat([df_existing, df_new], ignore_index=True)
        df_combined.to_csv(csv_file, index=False)
    except FileNotFoundError:
        pd.DataFrame([data]).to_csv(csv_file, index=False)

    if language == "فارسی":
        st.info(f"💡 داده‌های شما در فایل `{csv_file}` ذخیره شد.")
    else:
        st.info(f"💡 Your data has been saved in `{csv_file}`.")

# نمایش داده‌های قبلی
st.markdown("---")
if language == "فارسی":
    st.subheader("📊 دیده‌بان سلامت جامعه (نمونه)")
else:
    st.subheader("📊 Community Health Monitor (Sample)")

if st.button("نمایش داده‌های ثبت شده / Show Recorded Data"):
    csv_file = "peacehealth_data.csv"
    if os.path.exists(csv_file):
        df = pd.read_csv(csv_file)
        st.dataframe(df.tail(10))
        st.line_chart(df[["استرس", "اضطراب", "افسردگی"]].tail(20))
    else:
        if language == "فارسی":
            st.warning("هنوز داده‌ای ثبت نشده است. اولین داده را ثبت کنید!")
        else:
            st.warning("No data recorded yet. Please submit your first response!")