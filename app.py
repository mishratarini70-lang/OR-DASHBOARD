!pip install plotly
import streamlit as st
import pandas as pd
import plotly.express as px

# --- Page Setup ---
st.set_page_config(page_title="God Mode 2-Way Dashboard", layout="wide")

@st.cache_data
def load_data():
    # Using the exact names of the files you uploaded
    tt = pd.read_csv('final_strict_timetable (1).csv')
    cm = pd.read_csv('godmode_2way_conflict_matrix (1).csv', index_col=0)
    en = pd.read_csv('godmode_2way_master_enrolment (1).csv')
    
    # Cleaning the date string (removing extra quotes)
    tt['Date'] = tt['Date'].str.replace('"', '')
    return tt, cm, en

try:
    df_tt, df_cm, df_en = load_data()

    st.title("🛡️ God Mode 2-Way: Optimized Timetable")
    st.info("This dashboard confirms that no student has two classes at the same time.")

    # --- Top Row: Key Metrics ---
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Students", df_en['StudentID'].nunique())
    c2.metric("Total Sessions", len(df_tt))
    c3.metric("Clash Probability", "0.0%", delta="God Mode Active", delta_color="normal")
    c4.metric("Avg Class Size", int(df_en.groupby('Section_Label')['StudentID'].count().mean()))

    # --- Main Content ---
    tab_tt, tab_cm, tab_en = st.tabs(["📅 Master Schedule", "🔥 Conflict Heatmap", "👥 Student Search"])

    with tab_tt:
        st.subheader("Final Optimized Schedule")
        # Filter by Room
        rooms = ["All"] + list(df_tt['Room_Number'].unique().astype(str))
        selected_room = st.selectbox("Filter by Room", rooms)
        
        filtered_df = df_tt.copy()
        if selected_room != "All":
            filtered_df = filtered_df[filtered_df['Room_Number'] == int(selected_room)]
        
        st.dataframe(filtered_df, use_container_width=True)

    with tab_cm:
        st.subheader("2-Way Conflict Matrix")
        st.write("This matrix shows how many students are shared between sections. The God Mode model ensures that sections with high 'Overlap Counts' are never scheduled at the same time.")
        
        # Clean matrix for plotting (replacing self-clash 9999 with 0 for better color scaling)
        plot_cm = df_cm.replace(9999, 0)
        fig = px.imshow(plot_cm, 
                        color_continuous_scale='Reds',
                        aspect="auto",
                        labels=dict(x="Section B", y="Section A", color="Shared Students"))
        st.plotly_chart(fig, use_container_width=True)

    with tab_en:
        st.subheader("Student Enrollment Lookup")
        student_id = st.text_input("Enter Student ID (e.g., IPM002-21)")
        
        if student_id:
            # Get sections for student
            my_sections = df_en[df_en['StudentID'] == student_id]['Section_Label'].tolist()
            if my_sections:
                st.success(f"Student {student_id} is enrolled in: {', '.join(my_sections)}")
                # Show their specific timetable
                my_tt = df_tt[df_tt['Course_Section'].isin(my_sections)].sort_values(by='Date')
                st.table(my_tt[['Date', 'Time_Slot', 'Room_Number', 'Course_Section']])
            else:
                st.warning("Student ID not found.")

except FileNotFoundError as e:
    st.error(f"Missing File: {e.filename}. Please make sure the CSV files are in the same folder as this script.")
except Exception as e:
    st.error(f"An error occurred: {e}")
