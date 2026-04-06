import streamlit as st
import google.generativeai as genai
import requests
import pandas as pd
from datetime import datetime

# 1. إعدادات الصفحة (Ozon Style)
st.set_page_config(page_title="Casa Cosmetique Dashboard", layout="wide")

# 2. جلب المفاتيح من Secrets
try:
    GEMINI_API_KEY = st.secrets["GEMINI_KEY"]
    YOUCAN_TOKEN = st.secrets["DELIVERY_TOKEN"].strip()
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error("⚠️ خطأ: تأكد من ضبط GEMINI_KEY و DELIVERY_TOKEN في Secrets.")
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

# --- 4. دالة جلب البيانات (تعديل الرابط والترويسة) ---
def fetch_youcan_data():
    # الرابط المعتمد في آخر تحديث لـ YouCan Ship
    url = "https://api.youcanship.com/v1/orders"
    
    headers = {
        "Authorization": f"Bearer {YOUCAN_TOKEN}",
        "Accept": "application/json",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0"  # ضروري لتجنب رفض السيرفر (char 0)
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=25)
        if response.status_code == 200:
            res_json = response.json()
            # التعامل مع شكل البيانات المختلف
            if isinstance(res_json, dict):
                return res_json.get('data', []), "SUCCESS"
            elif isinstance(res_json, list):
                return res_json, "SUCCESS"
            return [], "EMPTY_JSON"
        else:
            return None, f"Status: {response.status_code}"
    except Exception as e:
        return None, str(e)

# --- 5. واجهة العرض الاحترافية ---
st.title("📊 لوحة تحكم الشحنات الذكية (Live)")
st.write(f"مرحباً ياسين | تحديث تلقائي: {datetime.now().strftime('%Y-%m-%d %H:%M')}")

if st.sidebar.button("تسجيل الخروج"):
    st.session_state.logged_in = False
    st.rerun()

if st.button("🔄 تحديث ومزامنة البيانات الحقيقية الآن"):
    with st.spinner('جاري الاتصال بـ YouCan Ship وسحب البيانات...'):
        orders, status = fetch_youcan_data()
        
        if status == "SUCCESS" and orders:
            df = pd.DataFrame(orders)
            
            # حساب الإحصائيات بأسلوب Ozon
            total = len(df)
            # محاولة قراءة الحالات (Status) والمبالغ (Total)
            delivered = len(df[df['status'].str.contains('deliver|complete|success', case=False, na=False)])
            returned = len(df[df['status'].str.contains('return|refuse|cancel', case=False, na=False)])
            
            # عرض البطاقات (Metrics)
            c1, c2, c3 = st.columns(3)
            c1.metric("إجمالي الطلبيات", total)
            c2.metric("تم التوصيل (Livré)", delivered, f"{round((delivered/total)*100, 1)}%" if total > 0 else "0%")
            c3.metric("المرتجعات (Retour)", returned, f"-{round((returned/total)*100, 1)}%", delta_color="inverse")

            st.divider()

            # عرض الجدول والتحليل
            col_t, col_ai = st.columns([2, 1])
            with col_t:
                st.subheader("📋 قائمة الشحنات الحقيقية")
                st.dataframe(df, use_container_width=True)
            
            with col_ai:
                st.subheader("🤖 تحليل Gemini AI لبياناتك")
                try:
                    # إرسال عينة من البيانات لـ Gemini للتحليل
                    prompt = f"بصفتك خبير تجارة إلكترونية في المغرب، حلل هذه البيانات لـ Casa Cosmetique: {orders[:5]}. أعط نصيحة لزيادة المبيعات."
                    response = model.generate_content(prompt)
                    st.info(response.text)
                except:
                    st.write("الذكاء الاصطناعي يحلل البيانات حالياً...")
        else:
            st.error(f"❌ فشل جلب البيانات: {status}")
            st.info("نصيحة: تأكد أن التوكن الجديد 'wallenssine' مضاف في Secrets بدون أي مسافات زائدة.")
