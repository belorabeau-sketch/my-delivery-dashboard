import streamlit as st
import pandas as pd
import plotly.express as px

# 1. إعداد الصفحة
st.set_page_config(page_title="Casa Cosmetique | 7-Day Optimizer", layout="wide")

st.title("🚀 مُحسن حملات تيك توك (آخر 7 أيام)")
st.write("تحليل الأداء واتخاذ قرارات الإيقاف والتحجيم (Scaling)")

# --- 2. محاكاة بيانات حقيقية لآخر 7 أيام لمنتجاتك ---
data_7_days = {
    'Campaign_Name': ['Acne_Cream_CBO', 'Saad_Oil_ABO', 'Fourmi_Creme_Promo', 'Gommage_Test', 'BackFree_Spray'],
    'Status': ['Active', 'Active', 'Active', 'Active', 'Active'],
    'Spend_7D': [4500, 3200, 1500, 800, 2200],
    'Conversions': [42, 28, 5, 2, 18],
    'CPA_DH': [107, 114, 300, 400, 122],
    'ROAS': [4.5, 3.9, 1.2, 0.8, 3.2],
    'Best_Age': ['25-34', '35-44', '18-24', 'All', '25-44'],
    'Worst_Interest': ['Gaming', 'News', 'Fast Food', 'All', 'Sports']
}

df = pd.DataFrame(data_7_days)

# --- 3. قسم التوصيات المباشرة (The Action Center) ---
st.subheader("💡 قرارات الإدارة الفورية")
cols = st.columns(len(df))

for i, row in df.iterrows():
    with cols[i]:
        # منطق اتخاذ القرار
        if row['ROAS'] >= 3.5:
            st.success(f"🔥 **SCALE**\n\n{row['Campaign_Name']}")
            st.write(f"Budget: +20%")
        elif row['ROAS'] >= 2.5:
            st.info(f"✅ **KEEP RUNNING**\n\n{row['Campaign_Name']}")
            st.write(f"Budget: Stable")
        else:
            st.error(f"🛑 **TURN OFF**\n\n{row['Campaign_Name']}")
            st.write(f"Budget: 0 DH")

st.divider()

# --- 4. تفاصيل الاستبعاد (Exclusions) والجماهير ---
c1, c2 = st.columns(2)

with c1:
    st.subheader("🚫 فئات يجب استبعادها فوراً (Exclude)")
    exclude_logic = df[df['ROAS'] < 2.0]
    if not exclude_logic.empty:
        for _, r in exclude_logic.iterrows():
            st.warning(f"في حملة **{r['Campaign_Name']}**: استبعد اهتمام **{r['Worst_Interest']}** وفئة **{r['Worst_Interest']}**")
    
    st.subheader("👥 الفئة العمرية الرابحة")
    fig_age = px.bar(df, x='Campaign_Name', y='Conversions', color='Best_Age', 
                     title="أكثر الأعمار شراءً لكل حملة")
    st.plotly_chart(fig_age, use_container_width=True)

with c2:
    st.subheader("💰 الميزانية اليومية المثالية للـ Scaling")
    # منطق حساب الميزانية المقترحة (مثال: CPA * 10)
    df['Suggested_Daily'] = df['CPA_DH'] * 5 
    fig_budget = px.pie(df[df['ROAS'] > 3], values='Suggested_Daily', names='Campaign_Name',
                        title="توزيع الميزانية المقترح للحملات الناجحة")
    st.plotly_chart(fig_budget, use_container_width=True)

# --- 5. جدول البيانات الخام لاتخاذ القرار اليدوي ---
st.subheader("📋 تقرير الأداء التفصيلي (Last 7 Days)")
st.table(df[['Campaign_Name', 'Spend_7D', 'Conversions', 'CPA_DH', 'ROAS', 'Best_Age']])
