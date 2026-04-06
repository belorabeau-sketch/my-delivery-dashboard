import streamlit as st
import google.generativeai as genai
import requests
import pandas as pd

# 1. إعداد الصفحة
st.set_page_config(page_title="Casa Cosmetique Real Dashboard", layout="wide")

# 2. جلب المفاتيح من Secrets
try:
    GEMINI_API_KEY = st.secrets["GEMINI_KEY"]
    YOUCAN_TOKEN = st.secrets["DELIVERY_TOKEN"]
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error("⚠️ خطأ في الإعدادات: يرجى التأكد من وضع GEMINI_KEY و DELIVERY_TOKEN في Secrets.")
    st.stop()

# 3. نظام تسجيل الدخول
def check_password():
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False
    if not st.session_state["password_correct"]:
        st.title("🔐 دخول الإدارة - كازا كوزميتيك")
        user = st.text_input("اسم المستخدم", placeholder="yassine")
        pwd = st.text_input("كلمة المرور", type="password", placeholder="casa2026")
        if st.button("دخول"):
            if user == "yassine" and pwd == "casa2026":
                st.session_state["password_correct"] = True
                st.rerun()
            else:
                st.error("❌ بيانات الدخول خاطئة")
        return False
    return True

# --- 4. دالة جلب البيانات الحقيقية من YouCan Ship ---
def fetch_actual_data():
    # الرابط الرسمي لـ API YouCan Ship لجلب الطلبات
    url = "https://api.youcanship.com/v1/orders" 
    headers = {
        "Authorization": f"Bearer {YOUCAN_TOKEN}",
        "Accept": "application/json"
    }
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json().get('data', [])
        else:
            st.error(f"⚠️ فشل الاتصال بـ YouCan Ship. كود الخطأ: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"❌ حدث خطأ تقني: {e}")
        return None

# 5. التطبيق الرئيسي
if check_password():
    st.title("📊 لوحة تحكم YouCan Ship الحقيقية")
    st.write("مرحباً ياسين، هذه البيانات يتم جلبها الآن مباشرة من حسابك.")

    if st.button("🔄 تحديث البيانات والتحليل الآن"):
        with st.spinner('جاري الاتصال بـ YouCan Ship...'):
            real_orders = fetch_actual_data()
            
            if real_orders:
                # تحويل البيانات لجدول (DataFrame) لسهولة الحساب
                df = pd.DataFrame(real_orders)
                
                # حساب الإحصائيات الحقيقية من بياناتك
                total_orders = len(df)
                # ملاحظة: سنحاول استخراج الحالات بناءً على نظام YouCan (مثلاً: 'delivered', 'returned')
                # إذا كانت الأسماء مختلفة في API الخاص بهم، سنقوم بتعديلها
                delivered = len(df[df['status'].str.contains('deliver', case=False, na=False)])
                returned = len(df[df['status'].str.contains('return', case=False, na=False)])
                
                # عرض الصناديق العلوية بأرقامك الحقيقية
                c1, c2, c3 = st.columns(3)
                c1.metric("إجمالي الطلبات", total_orders)
                c2.metric("تم التوصيل", delivered)
                c3.metric("المرتجعات", returned)

                st.divider()

                # عرض الجدول المفصل لطلبياتك
                st.subheader("📋 تفاصيل الطلبات الحقيقية")
                # عرض أعمدة محددة (تأكد أن هذه الأسماء موجودة في API YouCan)
                display_cols = ['tracking_number', 'city', 'status', 'total_price']
                st.dataframe(df[display_cols] if all(c in df.columns for c in display_cols) else df)

                # تحليل Gemini للبيانات الحقيقية
                st.divider()
                st.subheader("🤖 تحليل ذكاء Gemini لنتائجك الحقيقية")
                prompt = f"حلل أداء متجري بناءً على هذه الطلبيات الحقيقية: {real_orders[:5]}. أعطني نصيحة واحدة لتحسين التوصيل في المغرب."
                ai_resp = model.generate_content(prompt)
                st.success(ai_resp.text)
            else:
                st.warning("لم نتمكن من سحب البيانات. تأكد من أن التوكن (Token) صالح وأن هناك طلبيات في حسابك.")
