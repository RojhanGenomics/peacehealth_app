import streamlit as st
from textblob import TextBlob
import nltk
nltk.download('punkt')

st.set_page_config(page_title="PeaceTalks Analyzer", page_icon="🕊️")

st.title("🕊️ PeaceTalks Analyzer")
st.subheader("تحلیل گفت‌وگوهای صلح با هوش مصنوعی")

text = st.text_area("متن بیانیه، مصاحبه یا گزارش مذاکرات را وارد کنید:", height=200)

if text:
    blob = TextBlob(text)
    sentiment = blob.sentiment.polarity

    if sentiment > 0.1:
        label = "😊 مثبت"
        color = "green"
    elif sentiment < -0.1:
        label = "😠 منفی"
        color = "red"
    else:
        label = "😐 خنثی"
        color = "gray"

    st.markdown(f"### احساسات کلی: **{label}**")
    st.markdown(f"امتیاز احساسات: `{sentiment:.2f}` (از -۱ تا +۱)")

    st.markdown("---")
    st.subheader("🔍 تحلیل موضوعات")

    words = text.split()
    freq = {}
    for w in words:
        if len(w) > 3:
            freq[w] = freq.get(w, 0) + 1

    top_words = sorted(freq.items(), key=lambda x: x[1], reverse=True)[:10]
    st.write("کلمات کلیدی پرتکرار:")
    for word, count in top_words:
        st.write(f"- {word}: {count} بار")