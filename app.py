import streamlit as st
import google.generativeai as genai
import requests

# --- إعدادات الأمان ---
# يفضل وضع هذه المفاتيح في Streamlit Secrets لاحقاً، لكن سنضعها هنا للبدء
GEMINI_API_KEY = "AIzaSyB4qDcZZm79vb2TBRrjW4SQgzU34i-1eBk"
DELIVERY_TOKEN = "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9..." # التوكن الخاص بك

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# --- نظام تسجيل الدخول ---
def check_password():
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False

    if not st.session_state["password_correct"]:
        st.title("🔐 تسجيل الدخول - لوحة تحكم ياسين")
        user = st.text_input("اسم المستخدم")
        pwd = st.text_input("كلمة المرور", type="password")
        if st.button("دخول"):
            if user == "yassine" and pwd == "casa2026": # يمكنك تغيير كلمة المرور هنا
                st.session_state["password_correct"] = True
                st.rerun()
            else:
                st.error("بيانات الدخول خاطئة")
        return False
    return True

# --- التطبيق الرئيسي ---
if check_password():
    st.set_page_config(page_title="تتبع شحنات كازا كوزميتيك", layout="wide")
    st.sidebar.title("القائمة الرئيسية")
    if st.sidebar.button("تسجيل الخروج"):
        st.session_state["password_correct"] = False
        st.rerun()

    st.title("🚚 نظام تتبع الشحنات الذكي (Gemini AI)")

    # دالة جلب البيانات (تحتاج لرابط الـ API الخاص بشركتك لتصبح حقيقية)
    def fetch_data():
        # مثال لبيانات تجريبية حتى تزودني برابط الشركة
        return [
            {"الطلب": "101", "المدينة": "الدار البيضاء", "الحالة": "قيد التوصيل", "المبلغ": "250 DH"},
            {"الطلب": "102", "المدينة": "مراكش", "الحالة": "تم التوصيل", "المبلغ": "180 DH"},
            {"الطلب": "103", "المدينة": "طنجة", "الحالة": "مرتجع", "المبلغ": "300 DH"}
        ]

    if st.button("تحديث وتحليل البيانات الآن"):
        data = fetch_data()
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.subheader("📋 حالة الطلبيات")
            st.table(data)
            
        with col2:
            st.subheader("🤖 تحليل الذكاء الاصطناعي")
            with st.spinner('يتم الآن تحليل البيانات بواسطة Gemini...'):
                prompt = f"حلل هذه البيانات كخبير لوجستيك في المغرب وقدم نصائح عملية: {data}"
                response = model.generate_content(prompt)
                st.info(response.text)