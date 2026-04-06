import streamlit as st
import google.generativeai as genai
import requests
import pandas as pd

# 1. إعدادات الصفحة (يجب أن تكون أول سطر في الكود)
st.set_page_config(page_title="Casa Cosmetique Dashboard", layout="wide")

# 2. جلب المفاتيح من Secrets
try:
    GEMINI_API_KEY = st.secrets["GEMINI_KEY"]
    YOUCAN_TOKEN = st.secrets["DELIVERY_TOKEN"]
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error("⚠️ خطأ في الإعدادات: يرجى التأكد من وضع المفاتيح في Secrets بشكل صحيح.")
    st.stop()

# 3. دالة التحقق من تسجيل الدخول
def check_password():
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False

    if not st.session_state["password_correct"]:
        st.title("🔐 تسجيل الدخول - كازا كوزميتيك")
        user = st.text_input("اسم المستخدم", placeholder="yassine")
        pwd = st.text_input("كلمة المرور", type="password", placeholder="casa2026")
        if st.button("دخول"):
            if user == "yassine" and pwd == "casa2026":
                st.session_state["password_correct"] = True
                st.rerun()
            else:
                st.error("❌ بيانات الدخول خاطئة")
        return False
    return True

# 4. التطبيق الرئيسي (يفتح فقط بعد الدخول)
if check_password():
    st.sidebar.success("تم تسجيل الدخول بنجاح ✅")
    if st.sidebar.button("تسجيل الخروج"):
        st.session_state["password_correct"] = False
        st.rerun()

    st.title("📊 لوحة تحكم كازا كوزميتيك الاحترافية (YouCan Ship)")
    st.divider()

    # محاكاة لبيانات YouCan Ship الحقيقية (بانتظار الربط النهائي)
    # ملاحظة: سنقوم بعرض بيانات مشابهة لتصميم Ozon الذي أعجبك
    summary_data = {
        "Livrés": 941,
        "Retournés": 228,
        "En cours": 15,
        "Total CRBT": "208,201 DH"
    }

    # 1. الصناديق العلوية (Stats Cards)
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.info("📦 طرود تم تسليمها")
        st.header(summary_data["Livrés"])
    with c2:
        st.warning("🔄 طرود مرتجعة")
        st.header(summary_data["Retournés"])
    with c3:
        st.success("🚚 في طور التوزيع")
        st.header(summary_data["En cours"])
    with c4:
        st.error("💰 المبالغ الإجمالية")
        st.header(summary_data["Total CRBT"])

    st.divider()

    # 2. الرسوم البيانية والجداول
    col_left, col_right = st.columns([1, 2])

    with col_left:
        st.subheader("📈 نسبة التوصيل")
        chart_df = pd.DataFrame({
            "الحالة": ["Livré", "Retourné"],
            "العدد": [941, 228]
        })
        st.bar_chart(chart_df.set_index("الحالة"))

    with col_right:
        st.subheader("📋 تفاصيل الحساب (المبالغ)")
        # جدول احترافي مثل Ozon
        details = {
            "STATUT": ["Livré", "Refusé", "En cours"],
            "COLIS": [941, 23, 15],
            "TOTAL CRBT": [208201, 4689, 3140],
            "FRAIS": [33710, 200, 450],
            "NET": [174491, -200, 2690]
        }
        st.table(pd.DataFrame(details))

    # 3. تحليل Gemini AI (العقل المدبر)
    st.divider()
    st.subheader("🤖 تحليل خبير Gemini الذكي للأداء")
    if st.button("تحليل البيانات الآن باستخدام AI"):
        with st.spinner("جاري تحليل بيانات Casa Cosmetique..."):
            prompt = f"حلل أداء المبيعات لشركة كازا كوزميتيك في المغرب. لدينا {summary_data['Livrés']} طلب تم توصيله و {summary_data['Retournés']} مرتجع. الصافي المالي هو 174,491 درهم. قدم نصائح لتقليل المرتجع وزيادة الأرباح."
            try:
                response = model.generate_content(prompt)
                st.write(response.text)
            except Exception as e:
                st.error(f"حدث خطأ في الاتصال بالذكاء الاصطناعي: {e}")
