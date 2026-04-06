import streamlit as st
import google.generativeai as genai
import requests
import pandas as pd

# 1. إعداد الصفحة
st.set_page_config(page_title="Casa Cosmetique Dashboard", layout="wide")

# 2. جلب المفاتيح من Secrets
try:
    GEMINI_API_KEY = st.secrets["GEMINI_KEY"]
    YOUCAN_TOKEN = st.secrets["DELIVERY_TOKEN"]
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error("⚠️ تأكد من إضافة GEMINI_KEY و DELIVERY_TOKEN في Secrets.")
    st.stop()

# 3. دالة جلب البيانات مع فحص الأخطاء (Debug Mode)
def fetch_data_debug():
    # الرابط الأساسي لـ YouCan Ship
    url = "https://api.youcanship.com/v1/orders"
    
    headers = {
        "Authorization": f"Bearer {YOUCAN_TOKEN.strip()}",
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(url, headers=headers)
        
        # إذا كان الرد ناجحاً
        if response.status_code == 200:
            return response.json().get('data', []), "SUCCESS"
        
        # إذا كان هناك خطأ في المفتاح (Unauthorized)
        elif response.status_code == 401:
            return None, "المفتاح (Token) غير صالحة أو منتهي الصلاحية. يرجى إعادة نسخه من YouCan Ship."
        
        # أي خطأ آخر
        else:
            return None, f"خطأ من السيرفر: {response.status_code} - {response.text[:100]}"
            
    except Exception as e:
        return None, f"فشل الاتصال تماماً: {str(e)}"

# 4. واجهة المستخدم
st.title("📊 لوحة تحكم كازا كوزميتيك - فحص الاتصال")

if st.button("🚀 محاولة جلب البيانات الحقيقية الآن"):
    with st.spinner('جاري فحص الاتصال بـ YouCan Ship...'):
        orders, message = fetch_data_debug()
        
        if message == "SUCCESS":
            if orders:
                st.success(f"✅ تم الاتصال بنجاح! تم العثور على {len(orders)} طلب.")
                df = pd.DataFrame(orders)
                st.dataframe(df)
            else:
                st.warning("✅ تم الاتصال بنجاح، ولكن حسابك لا يحتوي على أي طلبيات حالياً.")
        else:
            st.error(f"❌ فشل الاتصال. السبب: {message}")
            
            # تعليمات الإصلاح بناءً على تجربة YouCan Ship
            st.info("""
            **خطوات الإصلاح المقترحة:**
            1. تأكد من أن التوكن في **Secrets** لا يحتوي على مسافات زائدة.
            2. في حسابك على YouCan Ship، تأكد أن التوكن لديه صلاحية **Orders: Read**.
            3. جرب صنع توكن جديد (New Token) ووضعه في Secrets.
            """)

# 5. تحليل Gemini (اختياري في حال وجود بيانات)
st.divider()
st.subheader("🤖 ذكاء Gemini الاصطناعي")
st.write("بمجرد نجاح الاتصال، سيقوم Gemini بتحليل أرباحك هنا.")
