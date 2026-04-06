import streamlit as st
import google.generativeai as genai
import requests
import pandas as pd

# 1. إعدادات الصفحة (تصميم Ozon)
st.set_page_config(page_title="Casa Cosmetique Dashboard", layout="wide")

# 2. جلب المفاتيح من Secrets
try:
    GEMINI_API_KEY = st.secrets["GEMINI_KEY"]
    YOUCAN_TOKEN = st.secrets["DELIVERY_TOKEN"].strip()
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
except:
    st.error("⚠️ يرجى التأكد من ضبط Secrets (GEMINI_KEY و DELIVERY_TOKEN)")
    st.stop()

# 3. دالة جلب البيانات (الرابط الصحيح 100% لـ YouCan Ship)
def fetch_data_final():
    # الرابط المخصص للشحن بناءً على الوثائق
    url = "https://api.youcanship.com/v1/ship/orders"
    
    headers = {
        "Authorization": f"Bearer {YOUCAN_TOKEN}",
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=20)
        if response.status_code == 200:
            data = response.json().get('data', [])
            return data, "SUCCESS"
        else:
            # تجربة الرابط البديل إذا فشل الأول
            url_alt = "https://api.youcanship.com/v1/orders"
            response_alt = requests.get(url_alt, headers=headers, timeout=20)
            if response_alt.status_code == 200:
                return response_alt.json().get('data', []), "SUCCESS"
            return None, f"Status: {response.status_code}"
    except Exception as e:
        return None, str(e)

# 4. واجهة المستخدم الاحترافية
st.title("📊 لوحة تحكم كازا كوزميتيك (Ozon Style)")
st.markdown("---")

if st.button("🚀 تحديث المزامنة الحية الآن"):
    with st.spinner('جاري سحب بيانات الشحنات من YouCan Ship...'):
        orders, status = fetch_data_final()
        
        if status == "SUCCESS" and orders:
            df = pd.DataFrame(orders)
            
            # حساب الإحصائيات الحقيقية
            total = len(df)
            delivered = len(df[df['status'].str.contains('delivered|complete', case=False, na=False)])
            returned = len(df[df['status'].str.contains('return|refuse|cancel', case=False, na=False)])
            
            # عرض البطاقات (مثل Ozon)
            c1, c2, c3, c4 = st.columns(4)
            with c1:
                st.metric("الطلبات المسلمة", delivered, f"{round((delivered/total)*100, 1)}%" if total > 0 else "0%")
            with c2:
                st.metric("المرتجعات", returned, f"-{round((returned/total)*100, 1)}%", delta_color="inverse")
            with c3:
                st.metric("إجمالي الشحنات", total)
            with c4:
                revenue = df['total_price'].astype(float).sum() if 'total_price' in df.columns else 0
                st.metric("المبالغ الإجمالية", f"{revenue} DH")

            st.divider()

            # الجدول والتحليل
            col_t, col_ai = st.columns([2, 1])
            with col_t:
                st.subheader("📋 تفاصيل الطلبيات")
                st.dataframe(df[['tracking_number', 'city', 'status', 'total_price']] if 'tracking_number' in df.columns else df)
            
            with col_ai:
                st.subheader("🤖 تحليل Gemini AI")
                prompt = f"حلل أداء شركة Casa Cosmetique: {total} طلب، {delivered} تسليم. قدم نصيحة باللغة العربية."
                st.info(model.generate_content(prompt).text)
        else:
            st.error(f"❌ فشل جلب البيانات: {status}")
            st.info("ملاحظة: إذا ظهر رد فارغ، فقد يحتاج حسابك في YouCan Ship إلى وجود طلبية واحدة على الأقل مسجلة في نظام 'Ship'.")
