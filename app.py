import streamlit as st
import google.generativeai as genai
import requests
import pandas as pd
from datetime import datetime, timedelta

# 1. إعداد الصفحة وتصميم Ozon الاحترافي
st.set_page_config(page_title="Casa Cosmetique | YouCan Ship Dashboard", layout="wide")

# 2. جلب المفاتيح من Secrets
try:
    GEMINI_API_KEY = st.secrets["GEMINI_KEY"]
    YOUCAN_TOKEN = st.secrets["DELIVERY_TOKEN"].strip()
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error("⚠️ يرجى التأكد من ضبط المفاتيح في Secrets.")
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

# --- 4. دالة جلب البيانات بناءً على وثائق Postman الرسمية ---
def fetch_youcan_data():
    # الرابط المعتمد في الوثائق التي أرسلتها
    url = "https://api.youcanship.com/v1/ship/orders"
    
    headers = {
        "Authorization": f"Bearer {YOUCAN_TOKEN}",
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    
    try:
        # جلب الطلبات (بشكل افتراضي يجلب آخر الطلبات)
        response = requests.get(url, headers=headers, timeout=20)
        
        if response.status_code == 200:
            # الوثائق تشير أن البيانات تكون داخل حقل 'data'
            result = response.json()
            return result.get('data', []), "SUCCESS"
        else:
            return None, f"Status: {response.status_code} - {response.text[:100]}"
    except Exception as e:
        return None, str(e)

# --- 5. واجهة العرض (Live Dashboard) ---
st.title("📊 لوحة تحكم Casa Cosmetique (YouCan Ship)")
st.markdown(f"تاريخ اليوم: {datetime.now().strftime('%Y-%m-%d')}")

if st.sidebar.button("تسجيل الخروج"):
    st.session_state.logged_in = False
    st.rerun()

if st.button("🔄 تحديث ومزامنة البيانات الحقيقية"):
    with st.spinner('جاري الاتصال بـ YouCan Ship باستخدام البروتوكول الرسمي...'):
        orders, status = fetch_youcan_data()
        
        if status == "SUCCESS" and orders:
            df = pd.DataFrame(orders)
            
            # حساب الإحصائيات الحقيقية
            total_orders = len(df)
            delivered = len(df[df['status'].str.contains('delivered|complete|success', case=False, na=False)])
            returned = len(df[df['status'].str.contains('return|refuse|cancel', case=False, na=False)])
            ongoing = total_orders - (delivered + returned)
            
            # محاولة حساب المبالغ
            price_col = 'total_price' if 'total_price' in df.columns else 'amount'
            total_val = df[price_col].astype(float).sum() if price_col in df.columns else 0

            # عرض الصناديق (Metrics)
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("الطلبات المسلمة", delivered, f"{round((delivered/total_orders)*100, 1)}%" if total_orders > 0 else "0%")
            c2.metric("المرتجعات", returned, f"-{round((returned/total_orders)*100, 1)}%", delta_color="inverse")
            c3.metric("في طور التوصيل", ongoing)
            c4.metric("إجمالي المبالغ", f"{total_val} DH")

            st.divider()

            # عرض الجدول والتحليل
            col_t, col_ai = st.columns([2, 1])
            
            with col_t:
                st.subheader("📋 قائمة الشحنات الحقيقية")
                # عرض الأعمدة المتوفرة في الـ API
                st.dataframe(df, use_container_width=True)
            
            with col_ai:
                st.subheader("🤖 تحليل Gemini AI")
                prompt = f"حلل أداء شركة كازا كوزميتيك: {total_orders} طلب، {delivered} تسليم، {returned} مرتجع. قدم نصيحة باللغة العربية."
                try:
                    ai_resp = model.generate_content(prompt)
                    st.info(ai_resp.text)
                except:
                    st.write("الذكاء الاصطناعي يحلل البيانات...")
        else:
            st.error(f"❌ فشل جلب البيانات. السبب: {status}")
            st.info("تأكد أن التوكن الجديد 'wallenssine' موجود في Secrets.")
