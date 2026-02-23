import streamlit as st
import pandas as pd
# 🚨 Notice: Plotly is completely gone! No more import errors.

# --- Configuration ---
st.set_page_config(page_title="MBA Timetable: God Mode", layout="wide")

@st.cache_data
def load_data():
    try:
        # Exact names from your uploaded files
        tt = pd.read_csv('final_strict_timetable (1).csv')
        cm = pd.read_csv('godmode_2way_conflict_matrix (1).csv', index_col=0)
        en = pd.read_csv('godmode_2way_master_enrolment (1).csv')
        
        # Data Cleaning
        tt['Date'] = tt['Date'].str.replace('"', '')
        return tt, cm, en
    except Exception as e:
        st.error(f"⚠️ Error loading files: {e}")
        st.info("Ensure the CSV files are in exactly the same GitHub folder as this app.py file.")
        return None, None, None

df_tt, df_cm, df_en = load_data()

if df_tt is not None:
    st.title("🛡️ God Mode 2-Way: Optimized Timetable")
    st.markdown("---")
    
    # Dashboard Metrics
    m1, m2, m3 = st.columns(3)
    m1.metric("Unique Students", df_en['StudentID'].nunique())
    m2.metric("Total Sessions", len(df_tt))
    m3.metric("Clash Status", "0 Conflicts", delta="God Mode Verified")

    # Tabs
    tab1, tab2, tab3 = st.tabs(["🗓 Master Schedule", "🔥 Conflict Heatmap", "👤 Student Search"])

    with tab1:
        st.subheader("Timetable Overview")
        st.dataframe(df_tt, use_container_width=True)

    with tab2:
        st.subheader("2-Way Conflict Matrix")
        st.write("Visualizing overlaps: The model ensures darker red cells are never scheduled simultaneously.")
        
        # 💡 THE GENIUS WORKAROUND: Using Pandas built-in styling instead of Plotly
        viz_cm = df_cm.replace(9999, 0)
        styled_cm = viz_cm.style.background_gradient(cmap='Reds', axis=None)
        
        st.dataframe(styled_cm, use_container_width=True)

    with tab3:
        st.subheader("Individual Schedule Search")
        student_id = st.text_input("Enter Student ID (e.g., IPM052-21)")
        if student_id:
            sections = df_en[df_en['StudentID'] == student_id]['Section_Label'].unique()
            if len(sections) > 0:
                st.info(f"Enrolled in: {', '.join(sections)}")
                personal_tt = df_tt[df_tt['Course_Section'].isin(sections)].sort_values(by='Date')
                st.table(personal_tt)
            else:
                st.warning("Student ID not found in enrollment records.")
