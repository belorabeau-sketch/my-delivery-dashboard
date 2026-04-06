import streamlit as st
import google.generativeai as genai
import requests
import pandas as pd
from datetime import datetime

# 1. إعداد الصفحة
st.set_page_config(page_title="Casa Cosmetique Dashboard", layout="wide")

# 2. جلب المفاتيح
try:
    GEMINI_API_KEY = st.secrets["GEMINI_KEY"]
    YOUCAN_TOKEN = st.secrets["DELIVERY_TOKEN"].strip()
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
except:
    st.error("⚠️ تأكد من ضبط Secrets.")
    st.stop()

# 3. نظام تسجيل الدخول
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🔐 لوحة تحكم كازا كوزميتيك")
    user = st.text_input("اسم المستخدم")
    pwd = st.text_input("كلمة المرور", type="password")
    if st.button("دخول"):
        if user == "yassine" and pwd == "casa2026":
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("بيانات الدخول خاطئة")
    st.stop()

# --- 4. دالة جلب البيانات (الرابط المباشر) ---
def fetch_youcan_data():
    # جربنا v1/ship/orders وأعطى 404، الآن نعود للرابط الأساسي الأكثر ثباتاً
    url = "https://api.youcanship.com/v1/orders"
    
    headers = {
        "Authorization": f"Bearer {YOUCAN_TOKEN}",
        "Accept": "application/json"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=20)
        if response.status_code == 200:
            res_json = response.json()
            # التأكد من مكان البيانات (أحياناً تكون مباشرة وأحياناً داخل 'data')
            if isinstance(res_json, list):
                return res_json, "SUCCESS"
            return res_json.get('data', []), "SUCCESS"
        else:
            return None, f"Status: {response.status_code}"
    except Exception as e:
        return None, str(e)

# --- 5. العرض الرسومي ---
st.title("📊 لوحة تحكم الشحنات الحية")

if st.button("🔄 تحديث ومزامنة البيانات الحقيقية"):
    with st.spinner('جاري مزامنة بيانات Casa Cosmetique...'):
        orders, status = fetch_youcan_data()
        
        if status == "SUCCESS" and orders:
            df = pd.DataFrame(orders)
            st.success(f"✅ تم الاتصال! وجدنا {len(df)} طلب.")
            
            # عرض البيانات بشكل احترافي
            c1, c2, c3 = st.columns(3)
            c1.metric("إجمالي الطلبيات", len(df))
            
            st.divider()
            st.subheader("📋 قائمة شحناتك الحقيقية")
            st.dataframe(df, use_container_width=True)
            
            # تحليل Gemini
            st.subheader("🤖 تحليل ذكاء Gemini")
            ai_resp = model.generate_content(f"حلل هذه البيانات لمتجري في المغرب: {orders[:3]}")
            st.info(ai_resp.text)
        else:
            st.error(f"❌ فشل جلب البيانات: {status}")
            st.info("إذا استمر الخطأ 404، جرب التواصل مع دعم YouCan Ship للتأكد من رابط الـ API الخاص بحسابك.")
