import streamlit as st
import pandas as pd
import plotly.express as px
import time

# 1. إعدادات الصفحة الاحترافية
st.set_page_config(page_title="Casa Cosmetique AI Ads Manager", layout="wide")

st.title("🎯 TikTok Advanced Audience Insights")
st.write("Comprehensive Analysis of 250,000 DH Ad Spend | Cooperative Casa Cosmetique")

# المحاكاة الجانبية
st.sidebar.header("Data Source")
if st.sidebar.button("🔄 Sync Live Pixel Data"):
    with st.spinner('Fetching Real-time Conversions...'):
        time.sleep(1.5)
        st.sidebar.success("Last Sync: Just Now")

# --- 2. البيانات النموذجية للتحليل العميق (المغرب) ---

# بيانات الاهتمامات (Interests)
interests_data = {
    'Interest': ['Organic Skincare', 'Hair Treatment', 'Traditional Hammam', 'Makeup Lovers', 'Fitness & Health'],
    'Conversions': [450, 320, 280, 150, 90],
    'ROAS': [5.2, 4.1, 3.9, 2.2, 1.5]
}

# بيانات المدن المغربية (Cities)
cities_data = {
    'City': ['Casablanca', 'Marrakech', 'Rabat', 'Agadir', 'Tangier', 'Fes'],
    'Sales': [600, 350, 200, 120, 80, 50],
    'CPA_DH': [145, 160, 185, 210, 195, 240]
}

# بيانات الديموغرافيا (Age & Gender)
demo_data = {
    'Category': ['Female 18-24', 'Female 25-34', 'Female 35-44', 'Male 25-34', 'Others'],
    'Performance': [35, 45, 15, 3, 2] # نسبة المبيعات %
}

# --- 3. عرض الرسوم البيانية ---

# الصف الأول: الاهتمامات والمدن
col1, col2 = st.columns(2)

with col1:
    st.subheader("📍 Top Converting Cities (Morocco)")
    df_city = pd.DataFrame(cities_data)
    fig_city = px.pie(df_city, values='Sales', names='City', hole=0.4,
                      title="Sales Distribution per City")
    st.plotly_chart(fig_city, use_container_width=True)

with col2:
    st.subheader("🔥 Winning Interests (Target IDs)")
    df_int = pd.DataFrame(interests_data)
    fig_int = px.bar(df_int, x='Interest', y='ROAS', color='Conversions',
                     text_auto=True, title="ROAS by Audience Interest")
    st.plotly_chart(fig_int, use_container_width=True)

st.divider()

# الصف الثاني: الأعمار والجنس والتحليل الاستراتيجي
col3, col4 = st.columns([1, 1])

with col3:
    st.subheader("👥 Age & Gender Distribution")
    df_demo = pd.DataFrame(demo_data)
    fig_demo = px.bar(df_demo, x='Category', y='Performance', 
                      color='Performance', title="Who is Buying?")
    st.plotly_chart(fig_demo, use_container_width=True)

with col4:
    st.subheader("🤖 AI Strategy for New Campaign")
    st.info("""
    **Based on 250k DH Spend Data:**
    1. **Primary Target:** Females (25-34) in **Casablanca & Marrakech**.
    2. **Best Interest:** Focus on 'Organic Skincare' (Highest ROAS: 5.2).
    3. **Action:** Stop spending in 'Fitness & Health' (Low ROI).
    4. **Budget:** Reallocate 40% of budget to 'Hair Treatment' during weekends.
    """)

# الجدول النهائي (البيانات الخام)
st.divider()
st.subheader("📋 Master Breakdown Report")
final_df = pd.DataFrame(interests_data) # مثال للجدول
st.table(final_df)
