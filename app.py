import streamlit as st
import google.generativeai as genai
import requests

# 1. إعدادات الصفحة
st.set_page_config(page_title="Diagnostic Mode | Casa Cosmetique", layout="wide")

# 2. جلب المفاتيح
try:
    YOUCAN_TOKEN = st.secrets["DELIVERY_TOKEN"].strip()
except:
    st.error("⚠️ التوكن غير موجود في Secrets!")
    st.stop()

st.title("🔍 وضع تشخيص الاتصال - Casa Cosmetique")
st.write("سنقوم الآن بتجربة كل الطرق الممكنة للاتصال بـ YouCan Ship.")

if st.button("🚀 بدء فحص الاتصال الآن"):
    # قائمة الروابط المحتملة بناءً على أنظمة YouCan المختلفة
    endpoints = [
        "https://api.youcanship.com/v1/orders",
        "https://api.youcanship.com/v1/ship/orders",
        "https://api.youcanship.com/v1/user/orders"
    ]
    
    headers = {
        "Authorization": f"Bearer {YOUCAN_TOKEN}",
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    for url in endpoints:
        st.write(f"---")
        st.write(f"📡 محاولة الاتصال بالرابط: `{url}`")
        try:
            response = requests.get(url, headers=headers, timeout=15)
            st.write(f"🔹 كود الاستجابة (Status Code): `{response.status_code}`")
            
            if response.status_code == 200:
                st.success(f"✅ نجح الاتصال بهذا الرابط!")
                st.json(response.json()) # عرض البيانات الحقيقية
                break
            else:
                st.warning(f"❌ رد السيرفر: {response.text[:200]}")
        except Exception as e:
            st.error(f"💥 خطأ تقني: {str(e)}")

    st.divider()
    st.info("💡 إذا كانت كل الردود أعلاه فارغة أو تعطيك 401، فهذا يعني أن 'التوكن' يحتاج لإعادة نسخ من إعدادات YouCan Ship مع التأكد من اختيار (Orders: Read).")
