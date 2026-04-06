import streamlit as st
import google.generativeai as genai
import requests
import pandas as pd
from datetime import datetime, timedelta

# 1. إعدادات الصفحة والستايل (Ozon Style)
st.set_page_config(page_title="Casa Cosmetique Dashboard", layout="wide")

# 2. جلب المفاتيح من Secrets
try:
    GEMINI_API_KEY = st.secrets["GEMINI_KEY"]
    YOUCAN_TOKEN = st.secrets["DELIVERY_TOKEN"]
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error("⚠️ يرجى التأكد من إضافة GEMINI_KEY و DELIVERY_TOKEN في إعدادات Secrets.")
    st.stop()

# 3. نظام تسجيل الدخول
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🔐 دخول الإدارة - كازا كوزميتيك")
    user = st.text_input("اسم المستخدم", placeholder="yassine")
    pwd = st.text_input("كلمة المرور", type="password", placeholder="casa2026")
    if st.button("دخول"):
        if user == "yassine" and pwd == "casa2026":
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("بيانات الدخول غير صحيحة")
    st.stop()

# --- 4. دالة جلب البيانات من YouCan Ship (تعديل الرابط) ---
def fetch_youcan_data():
    # حساب التواريخ تلقائياً لآخر 30 يوم
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    
    # الرابط المحدث لـ API YouCan Ship
    url = f"https://api.youcanship.com/v1/orders?include=customer,city&limit=100"
    headers = {
        "Authorization": f"Bearer {YOUCAN_TOKEN}",
        "Accept": "application/json"
    }
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json().get('data', [])
        else:
            return f"Error Code: {response.status_code}"
    except Exception as e:
        return str(e)

# --- 5. واجهة المستخدم الاحترافية ---
st.sidebar.title("Coopérative Casa Cosmetique")
if st.sidebar.button("تسجيل الخروج"):
    st.session_state.logged_in = False
    st.rerun()

st.title("📊 لوحة تحكم الشحنات الحية (Live)")
st.write(f"تحديث تلقائي للفترة من **{(datetime.now() - timedelta(days=30)).strftime('%d/%m')}** إلى اليوم")

if st.button("🔄 تحديث وتحليل البيانات الآن"):
    with st.spinner('جاري جلب بياناتك الحقيقية من YouCan Ship...'):
        data = fetch_youcan_data()
        
        if isinstance(data, list) and len(data) > 0:
            df = pd.DataFrame(data)
            
            # حساب الإحصائيات (تعديل الحقول لتناسب YouCan)
            total = len(df)
            delivered = len(df[df['status'].str.contains('delivered|complete', case=False, na=False)])
            returned = len(df[df['status'].str.contains('return|refuse|cancel', case=False, na=False)])
            ongoing = total - (delivered + returned)
            
            # حساب المبالغ المالية
            total_revenue = df['total_price'].astype(float).sum() if 'total_price' in df.columns else 0

            # عرض الصناديق العلوية (Stats Cards)
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("الطلبات المسلمة", delivered, f"{round((delivered/total)*100, 1)}%" if total > 0 else "0%")
            c2.metric("المرتجعات", returned, f"-{round((returned/total)*100, 1)}%", delta_color="inverse")
            c3.metric("في طور التوزيع", ongoing)
            c4.metric("إجمالي المبالغ", f"{total_revenue} DH")

            st.divider()

            # عرض الجدول والتحليل
            col_table, col_ai = st.columns([2, 1])
            
            with col_table:
                st.subheader("📋 قائمة الطلبيات الأخيرة")
                # عرض أعمدة محددة للتنظيم
                cols = ['tracking_number', 'status', 'total_price', 'created_at']
                st.dataframe(df[cols] if all(c in df.columns for c in cols) else df, use_container_width=True)
                
            with col_ai:
                st.subheader("🤖 تحليل خبير Gemini AI")
                prompt = f"حلل أداء متجر Casa Cosmetique في المغرب: {total} طلب، {delivered} تسليم، {returned} مرتجع. أعط نصيحة باللغة العربية لتقليل المرتجع."
                try:
                    ai_response = model.generate_content(prompt)
                    st.info(ai_response.text)
                except:
                    st.write("الذكاء الاصطناعي مشغول حالياً، حاول مرة أخرى.")
        else:
            st.warning(f"⚠️ لم نجد بيانات نشطة في حسابك حالياً. تأكد أن التوكن صحيح. (التفاصيل: {data})")
