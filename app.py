import streamlit as st
import google.generativeai as genai
import requests
import pandas as pd

# 1. إعدادات الصفحة
st.set_page_config(page_title="Casa Cosmetique Dashboard", layout="wide")

# 2. جلب المفاتيح
try:
    GEMINI_API_KEY = st.secrets["GEMINI_KEY"]
    YOUCAN_TOKEN = st.secrets["DELIVERY_TOKEN"].strip()
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
except:
    st.error("⚠️ يرجى ضبط Secrets بشكل صحيح.")
    st.stop()

# 3. دالة جلب البيانات المتقدمة (حل مشكلة char 0)
def fetch_data_advanced():
    # الرابط الرسمي المباشر
    url = "https://api.youcanship.com/v1/orders"
    
    # إضافة User-Agent لمحاكاة متصفح حقيقي (هذا هو السر!)
    headers = {
        "Authorization": f"Bearer {YOUCAN_TOKEN}",
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        
        if response.status_code == 200:
            # التأكد من وجود محتوى قبل التحويل لـ JSON
            if response.text:
                return response.json().get('data', []), "SUCCESS", None
            else:
                return None, "EMPTY_RESPONSE", "السيرفر رد بصفحة فارغة تماماً"
        else:
            return None, f"ERROR_{response.status_code}", response.text
            
    except Exception as e:
        return None, "CONNECTION_FAILED", str(e)

# 4. الواجهة الرسومية (Ozon Style)
st.title("📊 لوحة تحكم كازا كوزميتيك - الربط المباشر")

if st.button("🚀 تحديث البيانات الحقيقية"):
    with st.spinner('جاري الاتصال بـ YouCan Ship...'):
        orders, status, debug_info = fetch_data_advanced()
        
        if status == "SUCCESS":
            df = pd.DataFrame(orders)
            if not df.empty:
                # عرض الإحصائيات (مثل Ozon)
                c1, c2, c3 = st.columns(3)
                c1.metric("إجمالي الطلبات", len(df))
                c2.metric("أحدث طلب", df['tracking_number'].iloc[0] if 'tracking_number' in df.columns else "N/A")
                
                st.divider()
                st.subheader("📋 قائمة الشحنات الحقيقية")
                st.dataframe(df)
                
                # تحليل Gemini
                st.subheader("🤖 تحليل الذكاء الاصطناعي")
                prompt = f"حلل أداء المبيعات بناءً على هذه البيانات: {orders[:3]}"
                st.info(model.generate_content(prompt).text)
            else:
                st.warning("✅ تم الاتصال ولكن القائمة فارغة.")
        else:
            st.error(f"❌ فشل الاتصال: {status}")
            with st.expander("🔍 تفاصيل الخطأ التقني"):
                st.write(f"الرد من السيرفر: {debug_info}")
