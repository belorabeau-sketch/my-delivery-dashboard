import streamlit as st
import google.generativeai as genai
import requests

# --- 1. جلب المفاتيح بأمان من Streamlit Secrets ---
try:
    GEMINI_API_KEY = st.secrets["GEMINI_KEY"]
    DELIVERY_TOKEN = st.secrets["DELIVERY_TOKEN"]
    # إعداد Gemini
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error("⚠️ خطأ: تأكد من إضافة GEMINI_KEY و DELIVERY_TOKEN في إعدادات Secrets.")
    st.stop()

# --- 2. نظام تسجيل الدخول ---
def check_password():
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False

    if not st.session_state["password_correct"]:
        st.title("🔐 دخول الإدارة - كازا كوزميتيك")
        user = st.text_input("اسم المستخدم")
        pwd = st.text_input("كلمة المرور", type="password")
        if st.button("دخول"):
            if user == "yassine" and pwd == "casa2026":
                st.session_state["password_correct"] = True
                st.rerun()
            else:
                st.error("بيانات الدخول خاطئة")
        return False
    return True

# --- 3. التطبيق الرئيسي ---
if check_password():
    st.set_page_config(page_title="لوحة تحكم الشحنات الذكية", layout="wide")
    
    st.sidebar.title("إدارة الحساب")
    if st.sidebar.button("تسجيل الخروج"):
        st.session_state["password_correct"] = False
        st.rerun()

    st.title("🚚 نظام تتبع الشحنات الذكي (Gemini AI)")
    st.write("مرحباً بك يا ياسين. هذه اللوحة مرتبطة ببيانات شركتك مباشرة.")

    # دالة جلب البيانات الحقيقية (بانتظار اسم شركتك لتعديل الرابط)
    def fetch_real_data():
        # حالياً سنعرض بيانات تجريبية نظيفة حتى نضع رابط شركتك الحقيقي
        return [
            {"الطلب": "Order #550", "المدينة": "الدار البيضاء", "الحالة": "قيد التوصيل", "المبلغ": "250 DH"},
            {"الطلب": "Order #551", "المدينة": "طنجة", "الحالة": "تم التوصيل", "المبلغ": "180 DH"},
            {"الطلب": "Order #552", "المدينة": "أكادير", "الحالة": "مرتجع", "المبلغ": "320 DH"},
        ]

    if st.button("تحديث وتحليل الطلبيات الآن"):
        with st.spinner('جاري جلب البيانات وتحليلها...'):
            data = fetch_real_data()
            
            col1, col2 = st.columns([1, 1.2])
            
            with col1:
                st.subheader("📋 قائمة الطلبات الأخيرة")
                st.table(data)
                
            with col2:
                st.subheader("🤖 تحليل خبير Gemini الذكي")
                prompt = f"بصفتك خبير تجارة إلكترونية في المغرب، حلل هذه البيانات لشركة كازا كوزميتيك: {data}. أعطِ نصائح لزيادة نسبة التوصيل."
                try:
                    response = model.generate_content(prompt)
                    st.success(response.text)
                except Exception as e:
                    st.error(f"حدث خطأ في الاتصال بـ Gemini: {e}")

# --- نهاية الكود ---
