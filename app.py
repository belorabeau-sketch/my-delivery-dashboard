import streamlit as st
import pandas as pd
import plotly.express as px
import time

# 1. إعدادات الصفحة (تصميم احترافي لجذب المراجعين)
st.set_page_config(page_title="TikTok Ads Analytics | Casa Cosmetique", layout="wide")

st.title("📊 TikTok Ads Business Intelligence")
st.write("Internal Dashboard for Cooperative Casa Cosmetique - Morocco")

# محاكاة عملية الربط (Authentication Simulation)
if st.sidebar.button("🔗 Connect TikTok Account"):
    with st.spinner('Authorizing with TikTok Marketing API...'):
        time.sleep(2)
        st.sidebar.success("Connected to Advertiser ID: 709123456789")

# 2. توليد بيانات تجريبية (لتبدو كأنها نتائج صرف 250,000 DH)
mock_data = {
    'Target_ID': ['Cosmetics_Interest_01', 'Natural_Beauty_MA', 'Skincare_Lovers_Casablanca', 
                  'Fashion_Beauty_Rabat', 'Organic_Products_Global', 'Haircare_Morocco'],
    'Spend_DH': [85000, 62000, 45000, 32000, 15000, 11000],
    'Conversions': [410, 380, 290, 150, 40, 95],
    'ROAS': [4.2, 3.8, 5.1, 2.1, 1.2, 3.5],
    'CPA_DH': [207, 163, 155, 213, 375, 115]
}
df = pd.DataFrame(mock_data)

# 3. عرض الإحصائيات الكبرى (KPIs)
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Analyzed Spend", "250,000 DH", "+12%")
col2.metric("Total Conversions (Pixel)", "1,365", "+5%")
col3.metric("Avg. ROAS", "3.31", "Good", delta_color="normal")
col4.metric("Active Target IDs", "24")

st.divider()

# 4. الرسوم البيانية (Charts) - هذا ما يحب تيك توك رؤيته في الفيديو
c1, c2 = st.columns(2)

with c1:
    st.subheader("📈 ROAS per Target Interest")
    fig1 = px.bar(df, x='Target_ID', y='ROAS', color='ROAS', 
                 color_continuous_scale='Greens', text_auto=True)
    st.plotly_chart(fig1, use_container_width=True)

with c2:
    st.subheader("💰 Spend vs Conversions Analysis")
    fig2 = px.scatter(df, x='Spend_DH', y='Conversions', size='ROAS', 
                     hover_name='Target_ID', color='Target_ID')
    st.plotly_chart(fig2, use_container_width=True)

st.divider()

# 5. عرض الجدول التفصيلي
st.subheader("📋 Granular Target ID Performance Report")
st.dataframe(df.style.highlight_max(axis=0, subset=['ROAS'], color='#90EE90'), use_container_width=True)

# رسالة توضح غرض التطبيق (للمراجعين)
st.info("💡 Purpose: This dashboard uses TikTok Reporting API & Pixel Data to reallocate budget from low-performing Target IDs to high-ROI audiences.")
