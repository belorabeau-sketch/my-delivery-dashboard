import streamlit as st
import google.generativeai as genai
import requests
import pandas as pd
from datetime import datetime, timedelta

# 1. إعدادات الصفحة والستايل
st.set_page_config(page_title="Casa Cosmetique Live Dashboard", layout="wide")

# 2. جلب المفاتيح من Secrets
try:
    GEMINI_API_KEY = st.secrets["GEMINI_KEY"]
    YOUCAN_TOKEN = st.secrets["DELIVERY_TOKEN"]
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error("⚠️ يرجى التأكد من إضافة GEMINI_KEY و DELIVERY_TOKEN في إعدادات Secrets على Streamlit.")
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
            st.error("بيانات الدخول غير صحيحة")
    st.stop()

# --- 4. دالة جلب البيانات من YouCan Ship برمجياً ---
def fetch_youcan_data():
    # حساب تواريخ الشهر الحالي تلقائياً لجعل اللوحة Live
    today = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    
    # الرابط الصحيح لطلب الطلبيات مع التواريخ
    url = f"https://api.youcanship.com/v1/orders?start_date={start_date}&end_date={today}"
    headers = {
        "Authorization": f"Bearer {YOUCAN_TOKEN}",
        "Accept": "application/json"
    }
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json().get('data', [])
        else:
            return f"Error: {response.status_code}"
    except Exception as e:
        return str(e)

# --- 5. واجهة العرض الاحترافية (تصميم Ozon) ---
st.sidebar.title("Coopérative Casa Cosmetique")
if st.sidebar.button("تسجيل الخروج"):
    st.session_state.logged_in = False
    st.rerun()

st.title("📊 لوحة تحكم الشحنات الحية (YouCan Ship)")
st.write(f"تحديث تلقائي للفترة: من **{ (datetime.now() - timedelta(days=30)).strftime('%d-%m-%Y') }** إلى اليوم")

if st.button("🔄 تحديث البيانات الحقيقية الآن"):
    with st.spinner('جاري الاتصال بـ YouCan Ship...'):
        data = fetch_youcan_data()
        
        if isinstance(data, list) and len(data) > 0:
            df = pd.DataFrame(data)
            
            # حساب الإحصائيات الحقيقية
            total_orders = len(df)
            delivered = len(df[df['status'].str.contains('delivered|complete', case=False, na=False)])
            returned = len(df[df['status'].str.contains('return|refuse|cancel', case=False, na=False)])
            in_transit = total_orders - (delivered + returned)
            
            # حساب المبالغ (نستخدم حقل total_price من الـ API)
            total_money = df['total_price'].astype(float).sum() if 'total_price' in df.columns else 0

            # عرض البطاقات العلوية (Stats Cards)
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("الطلبات المسلمة", delivered, f"{round((delivered/total_orders)*100, 1)}%" if total_orders > 0 else "0%")
            c2.metric("المرتجعات", returned, f"-{round((returned/total_orders)*100, 1)}%", delta_color="inverse")
            c3.metric("قيد التوزيع", in_transit)
            c4.metric("إجمالي المبالغ", f"{total_money} DH")

            st.divider()

            # عرض الجدول والتحليل
            col_table, col_ai = st.columns([2, 1])
            
            with col_table:
                st.subheader("📋 تفاصيل الطلبيات الحقيقية")
                cols = ['tracking_number', 'city', 'status', 'total_price']
                st.dataframe(df[cols] if all(c in df.columns for c in cols) else df, use_container_width=True)
                
            with col_ai:
                st.subheader("🤖 تحليل ذكاء Gemini AI")
                prompt = f"حلل أداء المبيعات لشركة كازا كوزميتيك: {total_orders} طلب إجمالي، {delivered} تسليم، {returned} مرتجع. قدم نصيحة واحدة باللغة العربية."
                try:
                    response = model.generate_content(prompt)
                    st.info(response.text)
                except:
                    st.write("الذكاء الاصطناعي قيد التحديث، حاول لاحقاً.")
        else:
            st.warning(f"لم نتمكن من جلب بيانات. تأكد أن التوكن صحيح وأن لديك طلبيات في آخر 30 يوم. (التفاصيل: {data})")
