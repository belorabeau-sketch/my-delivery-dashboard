import streamlit as st
import google.generativeai as genai
import requests
import pandas as pd
from datetime import datetime, timedelta

# 1. إعدادات الصفحة والجماليات
st.set_page_config(page_title="Casa Cosmetique | YouCan Ship Dashboard", layout="wide")

# 2. جلب المفاتيح من Secrets
try:
    GEMINI_API_KEY = st.secrets["GEMINI_KEY"]
    YOUCAN_TOKEN = st.secrets["DELIVERY_TOKEN"].strip()
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error("⚠️ يرجى التأكد من ضبط المفاتيح في Secrets.")
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

# --- 4. دالة جلب البيانات الاحترافية من YouCan Ship ---
def fetch_youcan_data():
    # محاولة جلب الطلبات بآخر تحديثات الرابط
    url = "https://api.youcanship.com/v1/orders?limit=100"
    headers = {
        "Authorization": f"Bearer {YOUCAN_TOKEN}",
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code == 200:
            return response.json().get('data', []), "SUCCESS"
        else:
            return None, f"Status: {response.status_code}"
    except Exception as e:
        return None, str(e)

# --- 5. واجهة العرض (Ozon Express Style) ---
st.sidebar.title("Coopérative Casa Cosmetique")
if st.sidebar.button("تسجيل الخروج"):
    st.session_state.logged_in = False
    st.rerun()

st.title("📊 لوحة التحكم الحية (Real-time)")
st.markdown("---")

if st.button("🔄 تحديث ومزامنة البيانات الآن"):
    with st.spinner('جاري جلب أرقامك الحقيقية من YouCan Ship...'):
        orders, status = fetch_youcan_data()
        
        if status == "SUCCESS" and orders:
            df = pd.DataFrame(orders)
            
            # حساب الإحصائيات الحقيقية
            total_orders = len(df)
            # تحديد الحالات بناءً على رد السيرفر
            delivered = len(df[df['status'].str.contains('deliver|complete', case=False, na=False)])
            returned = len(df[df['status'].str.contains('return|refuse|cancel', case=False, na=False)])
            ongoing = total_orders - (delivered + returned)
            
            # حساب المبالغ المالية
            total_val = df['total_price'].astype(float).sum() if 'total_price' in df.columns else 0

            # عرض الصناديق (Metrics) مثل تصميم Ozon
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("الطلبات المسلمة", delivered, f"{round((delivered/total_orders)*100, 1)}%" if total_orders > 0 else "0%")
            c2.metric("المرتجعات", returned, f"-{round((returned/total_orders)*100, 1)}%", delta_color="inverse")
            c3.metric("في الطريق", ongoing)
            c4.metric("إجمالي المداخيل", f"{total_val} DH")

            st.divider()

            # تقسيم الصفحة للجدول والذكاء الاصطناعي
            col_t, col_ai = st.columns([2, 1])
            
            with col_t:
                st.subheader("📋 قائمة الشحنات الحقيقية")
                st.dataframe(df[['tracking_number', 'city', 'status', 'total_price']] if 'tracking_number' in df.columns else df, use_container_width=True)
            
            with col_ai:
                st.subheader("🤖 تحليل Gemini AI")
                prompt = f"حلل أداء المبيعات لشركة كازا كوزميتيك: إجمالي الطلبات {total_orders}، التسليم {delivered}، المرتجع {returned}. قدم نصيحة تجارية باللغة العربية."
                try:
                    response = model.generate_content(prompt)
                    st.success(response.text)
                except:
                    st.write("الذكاء الاصطناعي يحلل البيانات الآن...")
        else:
            st.error(f"❌ لم نتمكن من جلب البيانات. السبب: {status}")
            st.info("تأكد من وجود طلبيات نشطة في حسابك على YouCan Ship.")
