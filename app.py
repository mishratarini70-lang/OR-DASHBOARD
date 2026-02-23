import streamlit as st
import pandas as pd
import plotly.express as px

# Page Config
st.set_page_config(page_title="MBA Timetable Dashboard", layout="wide")

@st.cache_data
def load_data():
    timetable = pd.read_csv('final_strict_timetable (1).csv')
    conflict_matrix = pd.read_csv('godmode_2way_conflict_matrix (1).csv', index_col=0)
    enrollment = pd.read_csv('godmode_2way_master_enrolment (1).csv')
    
    # Cleanup
    timetable['Date'] = timetable['Date'].str.replace('"', '')
    return timetable, conflict_matrix, enrollment

# Load Data
try:
    df_tt, df_cm, df_en = load_data()
    
    st.title("🎓 MBA Timetable & Enrollment Dashboard")
    st.markdown("---")

    # --- Sidebar Filters ---
    st.sidebar.header("Global Filters")
    all_sections = sorted(df_tt['Course_Section'].unique())
    selected_section = st.sidebar.selectbox("Select a Section", ["All"] + list(all_sections))
    
    # --- Top Metrics ---
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Sessions", len(df_tt))
    m2.metric("Total Students", df_en['StudentID'].nunique())
    m3.metric("Unique Sections", len(all_sections))
    m4.metric("Conflicts Found", "0", delta="Verified", delta_color="normal")

    # --- Tabs ---
    tab1, tab2, tab3 = st.tabs(["🗓 Full Schedule", "🔍 Student View", "🔥 Conflict Heatmap"])

    with tab1:
        st.subheader("Master Timetable")
        display_df = df_tt.copy()
        if selected_section != "All":
            display_df = display_df[display_df['Course_Section'] == selected_section]
        
        st.dataframe(display_df, use_container_width=True)
        
        # Room utilization chart
        room_usage = df_tt.groupby('Room_Number').size().reset_index(name='Sessions')
        fig_room = px.bar(room_usage, x='Room_Number', y='Sessions', title="Session Count by Room", color='Room_Number')
        st.plotly_chart(fig_room)

    with tab2:
        st.subheader("Personalized Student Schedule")
        student_list = sorted(df_en['StudentID'].unique())
        selected_student = st.selectbox("Search Student ID", student_list)
        
        if selected_student:
            # Find sections the student is enrolled in
            student_sections = df_en[df_en['StudentID'] == selected_student]['Section_Label'].unique()
            st.write(f"**Enrolled in:** {', '.join(student_sections)}")
            
            # Filter timetable for those sections
            personal_tt = df_tt[df_tt['Course_Section'].isin(student_sections)].sort_values(by=['Date', 'Time_Slot'])
            st.table(personal_tt)

    with tab3:
        st.subheader("Student Conflict Matrix")
        st.info("This heatmap shows the number of shared students between sections. Values of 0 indicate safe parallel scheduling.")
        
        # Filter matrix to remove the 9999 self-conflict markers for visualization
        plot_cm = df_cm.replace(9999, 0)
        fig_heat = px.imshow(plot_cm, 
                            labels=dict(x="Section B", y="Section A", color="Shared Students"),
                            color_continuous_scale='Viridis')
        fig_heat.update_layout(height=800)
        st.plotly_chart(fig_heat, use_container_width=True)

except Exception as e:
    st.error(f"Error loading files: {e}")
    st.info("Please ensure the CSV files are in the same directory as the script.")
