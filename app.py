import streamlit as st
import google.generativeai as genai
import requests
import pandas as pd
from datetime import datetime, timedelta

# 1. إعدادات الصفحة
st.set_page_config(page_title="Casa Cosmetique Dashboard", layout="wide")

# 2. جلب المفاتيح من Secrets
try:
    GEMINI_API_KEY = st.secrets["GEMINI_KEY"]
    YOUCAN_TOKEN = st.secrets["DELIVERY_TOKEN"]
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error("⚠️ يرجى التأكد من ضبط Secrets بشكل صحيح.")
    st.stop()

# 3. نظام تسجيل الدخول
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🔐 دخول الإدارة - كازا كوزميتيك")
    user = st.text_input("اسم المستخدم")
    pwd = st.text_input("كلمة المرور", type="password")
    if st.button("دخول"):
        if user == "yassine" and pwd == "casa2026":
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("بيانات خاطئة")
    st.stop()

# --- 4. دالة جلب البيانات المحدثة لـ YouCan Ship ---
def fetch_youcan_data():
    # الرابط المباشر لجلب الطلبات مع تحديد العدد
    url = "https://api.youcanship.com/v1/orders?limit=50"
    headers = {
        "Authorization": f"Bearer {YOUCAN_TOKEN}",
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(url, headers=headers)
        # التحقق من أن الرد ليس فارغاً وأنه JSON صحيح
        if response.status_code == 200:
            json_data = response.json()
            return json_data.get('data', []), "SUCCESS"
        elif response.status_code == 401:
            return None, "TOKEN_EXPIRED"
        else:
            return None, f"ERROR_{response.status_code}"
    except Exception as e:
        return None, str(e)

# --- 5. واجهة العرض الاحترافية (Ozon Style) ---
st.title("📊 لوحة تحكم الشحنات الحية")
st.sidebar.title("Casa Cosmetique")
if st.sidebar.button("تسجيل الخروج"):
    st.session_state.logged_in = False
    st.rerun()

if st.button("🔄 تحديث البيانات الآن"):
    with st.spinner('جاري الاتصال بـ YouCan Ship...'):
        orders, status = fetch_youcan_data()
        
        if status == "SUCCESS" and orders:
            df = pd.DataFrame(orders)
            
            # حساب الإحصائيات (مثل واجهة Ozon)
            total = len(df)
            delivered = len(df[df['status'].str.contains('delivered|complete', case=False, na=False)])
            returned = len(df[df['status'].str.contains('return|refuse|cancel', case=False, na=False)])
            ongoing = total - (delivered + returned)
            
            # عرض البطاقات العلوية
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("المسلمة (Livré)", delivered, f"{round((delivered/total)*100, 1)}%" if total > 0 else "0%")
            c2.metric("المرتجعة (Retour)", returned, f"-{round((returned/total)*100, 1)}%", delta_color="inverse")
            c3.metric("قيد التوصيل", ongoing)
            c4.metric("إجمالي المبالغ", f"{df['total_price'].astype(float).sum() if 'total_price' in df.columns else 0} DH")

            st.divider()

            # الجدول والتحليل
            col_t, col_a = st.columns([2, 1])
            with col_t:
                st.subheader("📋 قائمة الشحنات الحقيقية")
                cols = ['tracking_number', 'city', 'status', 'total_price']
                st.dataframe(df[cols] if all(c in df.columns for c in cols) else df)
            
            with col_a:
                st.subheader("🤖 تحليل Gemini AI")
                prompt = f"حلل أداء متجر كازا كوزميتيك: {total} طلب، {delivered} تسليم. أعط نصيحة واحدة."
                st.info(model.generate_content(prompt).text)
                
        elif status == "TOKEN_EXPIRED":
            st.error("❌ التوكن (Token) غير صالح أو انتهت صلاحيته. يرجى تجديده من إعدادات YouCan Ship.")
        else:
            st.warning(f"⚠️ فشل جلب البيانات. (السبب: {status}). تأكد من وجود طلبيات في حسابك.")
