import streamlit as st
import google.generativeai as genai
import requests
import pandas as pd

# 1. إعدادات الصفحة
st.set_page_config(page_title="Casa Cosmetique Final Fix", layout="wide")

# 2. جلب المفاتيح من Secrets
try:
    GEMINI_API_KEY = st.secrets["GEMINI_KEY"]
    YOUCAN_TOKEN = st.secrets["DELIVERY_TOKEN"].strip() # حذف أي مسافات زائدة
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
except:
    st.error("⚠️ تأكد من وضع المفاتيح في Secrets.")
    st.stop()

# 3. دالة جلب البيانات الاحترافية
def fetch_data_final():
    # هذا هو الرابط الأكثر دقة لجلب الطلبات في YouCan Ship
    url = "https://api.youcanship.com/v1/orders"
    
    headers = {
        "Authorization": f"Bearer {YOUCAN_TOKEN}",
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        
        # إذا نجح الاتصال
        if response.status_code == 200:
            return response.json().get('data', []), "SUCCESS", None
        else:
            # إرجاع نص الخطأ الخام لفهمه
            return None, f"خطأ {response.status_code}", response.text
            
    except Exception as e:
        return None, "فشل اتصال", str(e)

# 4. الواجهة الرسومية (تصميم Ozon الاحترافي)
st.title("📊 لوحة تحكم كازا كوزميتيك - الإصدار النهائي")

if st.button("🚀 جلب البيانات الحقيقية الآن"):
    with st.spinner('جاري الاتصال بـ YouCan Ship...'):
        orders, status, raw_debug = fetch_data_final()
        
        if status == "SUCCESS":
            if orders:
                df = pd.DataFrame(orders)
                # عرض الإحصائيات بأسلوب Ozon
                total = len(df)
                st.success(f"✅ تم جلب {total} طلب بنجاح!")
                
                c1, c2, c3 = st.columns(3)
                c1.metric("إجمالي الطلبات", total)
                c2.metric("المبلغ الإجمالي", f"{df['total_price'].sum()} DH" if 'total_price' in df.columns else "0")
                
                st.divider()
                st.subheader("📋 تفاصيل الشحنات")
                st.dataframe(df)
            else:
                st.warning("✅ تم الاتصال، ولكن لا توجد طلبيات في حسابك حالياً.")
        else:
            st.error(f"❌ فشل الاتصال: {status}")
            with st.expander("🔍 تفاصيل تقنية للمبرمج (Debug)"):
                st.write("الرد القادم من السيرفر:")
                st.code(raw_debug)

# 5. تحليل Gemini
st.divider()
st.subheader("🤖 تحليل الذكاء الاصطناعي")
st.write("بمجرد ظهور البيانات أعلاه، سيقوم Gemini بتحليلها لك هنا.")
