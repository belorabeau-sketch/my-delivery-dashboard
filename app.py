import streamlit as st
import google.generativeai as genai
import requests
import pandas as pd
from datetime import datetime, timedelta

# 1. إعدادات الصفحة
st.set_page_config(page_title="Casa Cosmetique Live Dashboard", layout="wide")

# 2. جلب المفاتيح من Secrets
try:
    GEMINI_API_KEY = st.secrets["GEMINI_KEY"]
    YOUCAN_TOKEN = st.secrets["DELIVERY_TOKEN"]
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
except:
    st.error("⚠️ يرجى التأكد من ضبط Secrets (GEMINI_KEY و DELIVERY_TOKEN)")
    st.stop()

# 3. دالة جلب البيانات مع تواريخ تلقائية (Live)
def fetch_live_data():
    # تحديد التاريخ تلقائياً (من شهر مضى إلى اليوم)
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    
    # رابط YouCan Ship مع الفلترة التلقائية للتواريخ
    url = f"https://api.youcanship.com/v1/orders?start_date={start_date}&end_date={end_date}"
    headers = {
        "Authorization": f"Bearer {YOUCAN_TOKEN}",
        "Accept": "application/json"
    }
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json().get('data', [])
        else:
            return None
    except:
        return None

# 4. واجهة المستخدم الاحترافية (تصميم Ozon)
st.title("📊 لوحة تحكم كازا كوزميتيك الحية")
st.write(f"تحديث تلقائي للفترة من {(datetime.now() - timedelta(days=30)).strftime('%d/%m')} إلى اليوم")

if st.button("🔄 تحديث البيانات الآن"):
    data = fetch_live_data()
    
    if data:
        df = pd.DataFrame(data)
        
        # حساب الإحصائيات الحقيقية
        total_orders = len(df)
        delivered = len(df[df['status'].str.contains('delivered|complete', case=False, na=False)])
        returned = len(df[df['status'].str.contains('return|refuse', case=False, na=False)])
        ongoing = total_orders - (delivered + returned)
        
        # عرض البطاقات العلوية (Stats Cards)
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("الطلبيات المستلمة", delivered, f"{round((delivered/total_orders)*100, 1)}%" if total_orders > 0 else "0%")
        c2.metric("الطلبيات المرتجعة", returned, f"-{round((returned/total_orders)*100, 1)}%", delta_color="inverse")
        c3.metric("في طور التوزيع", ongoing)
        c4.metric("إجمالي المبالغ", f"{df['total_price'].sum()} DH")

        st.divider()

        # عرض الجدول المفصل والتحليل
        col_left, col_right = st.columns([2, 1])
        
        with col_left:
            st.subheader("📋 تفاصيل الشحنات الأخيرة")
            st.dataframe(df[['tracking_number', 'city', 'status', 'total_price']], use_container_width=True)
            
        with col_right:
            st.subheader("🤖 تحليل Gemini AI")
            prompt = f"حلل أداء متجري Casa Cosmetique: إجمالي {total_orders} طلب، {delivered} تم تسليمها، {returned} مرتجعة. قدم نصيحة سريعة."
            try:
                response = model.generate_content(prompt)
                st.info(response.text)
            except:
                st.write("الذكاء الاصطناعي مشغول حالياً، حاول لاحقاً.")
    else:
        st.error("لم نتمكن من سحب البيانات تلقائياً. تأكد من أن التوكن فعال وأن هناك طلبيات في آخر 30 يوم.")
