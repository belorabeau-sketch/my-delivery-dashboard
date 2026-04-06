import streamlit as st
import google.generativeai as genai
import requests
import pandas as pd

# --- الإعدادات وجلب المفاتيح ---
try:
    GEMINI_API_KEY = st.secrets["GEMINI_KEY"]
    YOUCAN_TOKEN = st.secrets["DELIVERY_TOKEN"]
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
except:
    st.error("تأكد من ضبط الـ Secrets أولاً")
    st.stop()

st.set_page_config(page_title="Casa Cosmetique Dashboard", layout="wide")

# --- دالة جلب البيانات من YouCan Ship ---
def fetch_youcan_data():
    # رابط YouCan Ship لجلب الطلبات (Orders)
    url = "https://api.youcanship.com/v1/orders" 
    headers = {"Authorization": f"Bearer {YOUCAN_TOKEN}"}
    
    try:
        # ملاحظة: هنا نفترض البيانات قادمة من API YouCan
        # سأضع هيكلة مشابهة لـ Ozon لكي يظهر التصميم
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json().get('data', [])
        else:
            # بيانات تجريبية بنفس هيكلة الصورة الاحترافية التي أرسلتها
            return {
                "summary": {"livre": 941, "retourne": 228, "encours": 15, "total_crbt": 208201},
                "details": [
                    {"Statut": "Livré", "Colis": 941, "Total CRBT": 208201, "Frais": 33710, "Net": 174491},
                    {"Statut": "Refusé", "Colis": 23, "Total CRBT": 4689, "Frais": 200, "Net": -200},
                ]
            }
    except:
        return None

# --- تصميم الواجهة (UI) ---
st.title("📊 لوحة تحكم كازا كوزميتيك الاحترافية")

data = fetch_youcan_data()

if data:
    # 1. الصناديق العلوية (Stats Cards) مثل Ozon
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Colis Livrés", data['summary']['livre'], "79.5%")
    with col2:
        st.metric("Colis Retournés", data['summary']['retourne'], "-20.5%", delta_color="inverse")
    with col3:
        st.metric("Colis En Cours", data['summary']['encours'])
    with col4:
        st.metric("Total CRBT", f"{data['summary']['total_crbt']} DH")

    st.divider()

    # 2. الرسم البياني والجدول
    c1, c2 = st.columns([1, 2])
    
    with c1:
        st.subheader("📈 نسبة التوصيل")
        chart_data = pd.DataFrame({
            'Status': ['Livré', 'Retourné'],
            'Count': [data['summary']['livre'], data['summary']['retourne']]
        })
        st.bar_chart(chart_data.set_index('Status'))

    with c2:
        st.subheader("📋 تفاصيل المبالغ (Colis Facturés)")
        df = pd.DataFrame(data['details'])
        st.dataframe(df, use_container_width=True)

    # 3. تحليل Gemini الذكي (العقل المدبر)
    st.divider()
    st.subheader("🤖 تحليل Gemini AI للنتائج")
    if st.button("تحليل الأداء الآن"):
        with st.spinner("جاري تحليل البيانات..."):
            prompt = f"حلل أداء المبيعات لشركة كازا كوزميتيك. لدينا {data['summary']['livre']} تسليم و {data['summary']['retourne']} مرتجع. الصافي هو 174,491 درهم. أعطني نصائح لتقليل نسبة المرتجع (20%) في السوق المغربي."
            response = model.generate_content(prompt)
            st.info(response.text)
