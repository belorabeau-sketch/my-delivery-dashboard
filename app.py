import streamlit as st
import pandas as pd
import plotly.express as px
import time

# 1. Page Configuration
# تم تغيير اسم الصفحة هنا ليتطابق مع طلب تيك توك
st.set_page_config(page_title="Casa Ads Performance Optimizer", layout="wide")

# --- SIDEBAR: CONNECTION SIMULATION ---
# استبدال شعار تيك توك بشعار احترافي أو نص لتجنب مشاكل العلامة التجارية في الفيديو
st.sidebar.title("📊 Control Center")

if "connected" not in st.session_state:
    st.session_state.connected = False

if not st.session_state.connected:
    st.sidebar.warning("Ad Account not linked")
    if st.sidebar.button("🔗 Connect Ad Account"):
        with st.sidebar.spinner("Authenticating via Secure Gateway..."):
            time.sleep(2)
            st.session_state.connected = True
            st.sidebar.success("Successfully Connected!")
            st.sidebar.info("Account ID: 709123456789")
            st.rerun()
else:
    st.sidebar.success("✅ Connected to Ads API")
    st.sidebar.write("**Account:** Casa Cosmetique Official")
    if st.sidebar.button("🔌 Disconnect"):
        st.session_state.connected = False
        st.rerun()

# --- MAIN DASHBOARD ---
# تغيير العنوان الرئيسي ليتطابق مع اسم التطبيق الجديد
st.title("🚀 Casa Ads Performance Optimizer")
st.write("Real-time Action Plan for Campaign Scaling and Budget Optimization")

if not st.session_state.connected:
    st.info("Please click 'Connect Ad Account' in the sidebar to visualize your advertising data.")
    st.stop()

# --- 2. Realistic 7-Day Performance Data ---
data_7_days = {
    'Campaign_Name': ['Cream', 'Oil Skin Care', 'Fourmi_Creme_Promo', 'Body_Gommage', 'BackFree_Spray'],
    'Ad_Group_ID': ['ID_9928374', 'ID_8827361', 'ID_7726352', 'ID_6625343', 'ID_5524334'],
    'Spend_7D': [5200, 3800, 1200, 900, 2500],
    'Conversions': [58, 35, 3, 2, 22],
    'CPA_DH': [89, 108, 400, 450, 113],
    'ROAS': [5.1, 4.2, 0.9, 0.7, 3.8],
    'Best_Age': ['25-34', '35-44', '18-24', '18-24', '25-44'],
    'Top_City': ['Casablanca', 'Marrakech', 'Rabat', 'Agadir', 'Tangier']
}

df = pd.DataFrame(data_7_days)

# --- 3. The Action Center: Scale / Keep / Turn Off ---
st.subheader("⚡ Immediate Management Decisions")
cols = st.columns(len(df))

for i, row in df.iterrows():
    with cols[i]:
        if row['ROAS'] >= 3.5:
            st.success(f"🔥 **SCALE**")
            st.markdown(f"**{row['Campaign_Name']}**")
            st.caption(f"ID: {row['Ad_Group_ID']}")
            st.write(f"**Action:** Budget +20%")
            
        elif row['ROAS'] >= 2.5:
            st.info(f"✅ **KEEP**")
            st.markdown(f"**{row['Campaign_Name']}**")
            st.caption(f"ID: {row['Ad_Group_ID']}")
            st.write(f"**Action:** Stable")
            
        else:
            st.error(f"🛑 **TURN OFF**")
            st.markdown(f"**{row['Campaign_Name']}**")
            st.caption(f"ID: {row['Ad_Group_ID']}")
            st.write(f"**Action:** Stop Now")

st.divider()

# --- 4. Deep Insights ---
c1, c2 = st.columns(2)
with c1:
    st.subheader("📊 Winning Ages per Campaign")
    fig_age = px.bar(df, x='Campaign_Name', y='Conversions', color='Best_Age', barmode='group')
    st.plotly_chart(fig_age, use_container_width=True)

with c2:
    st.subheader("📍 Geographic Sales Distribution")
    fig_city = px.pie(df, values='Conversions', names='Top_City', hole=0.4)
    st.plotly_chart(fig_city, use_container_width=True)

# --- 5. Full Report ---
st.subheader("📋 Master Breakdown Table (Last 7 Days)")
st.dataframe(df[['Campaign_Name', 'Ad_Group_ID', 'Spend_7D', 'Conversions', 'ROAS', 'Best_Age', 'Top_City']], use_container_width=True)
