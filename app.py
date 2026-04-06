import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Page Configuration
st.set_page_config(page_title="Casa Cosmetique | 7-Day Performance Optimizer", layout="wide")

st.title("🚀 TikTok Ads Performance Optimizer (Last 7 Days)")
st.write("Real-time Action Plan for Campaign Scaling and Budget Optimization")

# --- 2. Mock Data: Realistic 7-Day Performance for your products ---
# We include Ad Group IDs and Campaign Names as requested
data_7_days = {
    'Campaign_Name': ['Acne_Cream_CBO', 'Saad_Oil_ABO', 'Fourmi_Creme_Promo', 'Gommage_Body_Test', 'BackFree_Spray'],
    'Ad_Group_ID': ['172839405', '182940506', '192050607', '202160708', '212270809'],
    'Status': ['Active', 'Active', 'Active', 'Active', 'Active'],
    'Spend_7D': [4500, 3200, 1500, 800, 2200],
    'Conversions': [45, 30, 4, 1, 20],
    'CPA_DH': [100, 106, 375, 800, 110],
    'ROAS': [4.8, 3.9, 1.1, 0.5, 3.5],
    'Best_Age': ['25-34', '35-44', '18-24', '18-24', '25-44'],
    'Best_Gender': ['Female', 'Female', 'Female', 'Female', 'Female'],
    'Top_City': ['Casablanca', 'Marrakech', 'Rabat', 'Agadir', 'Tangier']
}

df = pd.DataFrame(data_7_days)

# --- 3. The Action Center: Scale / Keep / Turn Off ---
st.subheader("⚡ Immediate Management Decisions")
cols = st.columns(len(df))

for i, row in df.iterrows():
    with cols[i]:
        # Logic for Decision Making
        if row['ROAS'] >= 3.5:
            st.success(f"🔥 **SCALE**")
            st.markdown(f"**{row['Campaign_Name']}**")
            st.caption(f"ID: {row['Ad_Group_ID']}")
            st.write(f"**Action:** Increase Budget +20%")
            st.write(f"**Daily Budget:** {row['CPA_DH'] * 10} DH")
            
        elif row['ROAS'] >= 2.5:
            st.info(f"✅ **KEEP RUNNING**")
            st.markdown(f"**{row['Campaign_Name']}**")
            st.caption(f"ID: {row['Ad_Group_ID']}")
            st.write(f"**Action:** Maintain Stability")
            st.write(f"**Daily Budget:** {row['CPA_DH'] * 5} DH")
            
        else:
            st.error(f"🛑 **TURN OFF**")
            st.markdown(f"**{row['Campaign_Name']}**")
            st.caption(f"ID: {row['Ad_Group_ID']}")
            st.write(f"**Action:** Stop Immediately")
            st.write(f"**Budget:** 0 DH")

st.divider()

# --- 4. Deep Insights: Age, Gender, and City Analysis ---
c1, c2 = st.columns(2)

with c1:
    st.subheader("📊 Conversion by Age Group")
    fig_age = px.bar(df, x='Campaign_Name', y='Conversions', color='Best_Age', 
                     barmode='group', title="Winning Ages per Campaign")
    st.plotly_chart(fig_age, use_container_width=True)
    
    st.subheader("📍 Top Cities by Sales")
    fig_city = px.pie(df, values='Conversions', names='Top_City', hole=0.4,
                      title="Geographic Conversion Distribution")
    st.plotly_chart(fig_city, use_container_width=True)

with c2:
    st.subheader("💡 Targeting Strategy (To Exclude)")
    # Logic to identify what to stop
    st.info("""
    **Optimization Guide:**
    1. **Exclude Ages:** 18-24 in 'Fourmi_Creme' & 'Gommage' (High CPA).
    2. **Exclude Interests:** News, Entertainment (Low ROAS).
    3. **Winner Profile:** Females (25-44) based in Casablanca/Marrakech.
    4. **Budget Scaling:** Apply +20% every 48 hours for ROAS > 3.5.
    """)
    
    st.subheader("📈 ROAS vs Spend Analysis")
    fig_scatter = px.scatter(df, x='Spend_7D', y='ROAS', size='Conversions', 
                             hover_name='Campaign_Name', color='ROAS',
                             title="Larger Bubbles = More Profit")
    st.plotly_chart(fig_scatter, use_container_width=True)

# --- 5. Full Raw Data Report ---
st.subheader("📋 Granular 7-Day Performance Table")
st.dataframe(df[['Campaign_Name', 'Ad_Group_ID', 'Spend_7D', 'Conversions', 'CPA_DH', 'ROAS', 'Best_Age', 'Top_City']], use_container_width=True)
