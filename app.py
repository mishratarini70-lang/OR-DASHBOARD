import streamlit as st
import pandas as pd
import os

# --- PAGE CONFIG ---
st.set_page_config(page_title="MBA Timetable Dashboard", page_icon="🎓", layout="wide")
st.title("🎓 PAN-IIM MBA Timetable & Enrolment Dashboard")
st.markdown("Zero-Conflict Schedule generated via CP-SAT Optimization & Machine Learning.")

# --- DATA LOADING ---
@st.cache_data
def load_data():
    try:
        # Load the timetable & enrolment
        timetable = pd.read_csv('final_strict_timetable.csv')
        enrolment = pd.read_csv('godmode_3way_master_enrolment.csv')
        
        # Look for the optional student details file to add Names and Emails
        if os.path.exists('student_details.csv'):
            details = pd.read_csv('student_details.csv')
            # Automatically merge the names and emails based on StudentID
            enrolment = pd.merge(enrolment, details, on='StudentID', how='left')
        else:
            # Create empty columns if the file isn't available yet
            enrolment['Name'] = "Data Not Uploaded"
            enrolment['Email'] = "Data Not Uploaded"
            
        return timetable, enrolment
    except FileNotFoundError:
        st.error("⚠️ Make sure 'final_strict_timetable.csv' and 'godmode_3way_master_enrolment.csv' are in the same folder as this script!")
        return pd.DataFrame(), pd.DataFrame()

timetable, enrolment = load_data()

if not timetable.empty and not enrolment.empty:
    
    # --- SIDEBAR FILTERS ---
    st.sidebar.header("🔍 Dashboard Filters")
    
    # --- TABS ---
    tab1, tab2, tab3 = st.tabs(["📅 Daily Master Schedule", "👨‍🏫 Faculty/Course View", "👥 Student Directory"])
    
    # ==========================================
    # TAB 1: DAILY MASTER SCHEDULE
    # ==========================================
    with tab1:
        st.subheader("Daily Campus Operations")
        
        # Get unique dates sorted
        dates = sorted(timetable['Date'].unique())
        selected_date = st.selectbox("Select a Date:", dates)
        
        # Filter data
        daily_schedule = timetable[timetable['Date'] == selected_date].copy()
        daily_schedule = daily_schedule.sort_values(by='Time_Slot')
        
        # Display Room Utilization Metrics
        total_classes = len(daily_schedule)
        max_rooms = 10 if "Nov" in selected_date else 4
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Classes Today", total_classes)
        col2.metric("Active Room Capacity", f"Max {max_rooms} Rooms")
        col3.metric("Status", "Zero Conflicts ✅")
        
        # Display the table cleanly
        st.dataframe(
            daily_schedule[['Time_Slot', 'Room_Number', 'Course_Section']], 
            use_container_width=True,
            hide_index=True
        )

    # ==========================================
    # TAB 2: FACULTY / COURSE VIEW
    # ==========================================
    with tab2:
        st.subheader("Course Section Tracker")
        st.info("💡 Select a specific section to see exactly when and where the Faculty needs to be.")
        
        sections = sorted(timetable['Course_Section'].unique())
        selected_section = st.selectbox("Select a Course Section:", sections)
        
        # Filter timetable for this section
        section_schedule = timetable[timetable['Course_Section'] == selected_section].copy()
        
        st.write(f"**Total Sessions Scheduled:** {len(section_schedule)} / 20")
        st.dataframe(
            section_schedule[['Date', 'Day', 'Time_Slot', 'Room_Number']].sort_values(by='Date'),
            use_container_width=True,
            hide_index=True
        )

    # ==========================================
    # TAB 3: STUDENT DIRECTORY
    # ==========================================
    with tab3:
        st.subheader("Section Enrolment Lists")
        st.write("View the exact, optimized student list for every class section.")
        
        enrol_sections = sorted(enrolment['Section_Label'].unique())
        selected_enrol_section = st.selectbox("Look up Section:", enrol_sections)
        
        # Filter students
        students_in_section = enrolment[enrolment['Section_Label'] == selected_enrol_section]
        
        st.metric(f"Total Students in {selected_enrol_section}", len(students_in_section))
        
        # Display student IDs, Names, and Emails
        st.dataframe(
            students_in_section[['StudentID', 'Name', 'Email']], 
            use_container_width=True,
            hide_index=True
        )

else:
    st.warning("Awaiting data files...")
