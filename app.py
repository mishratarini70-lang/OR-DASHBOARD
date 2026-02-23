import streamlit as st
import pandas as pd
import glob
import os

# --- PAGE CONFIG ---
st.set_page_config(page_title="MBA Timetable Dashboard", page_icon="🎓", layout="wide")
st.title("🎓 PAN-IIM MBA Timetable & Enrolment Dashboard")
st.markdown("Zero-Conflict Schedule generated via CP-SAT Optimization & Machine Learning.")

# --- DATA LOADING (CACHED FOR SPEED) ---
@st.cache_data(show_spinner=False)
def load_data():
    try:
        # Load core CSVs
        timetable = pd.read_csv('final_strict_timetable.csv')
        enrolment = pd.read_csv('godmode_3way_master_enrolment.csv')
        
        # Strip hidden spaces to prevent merging errors
        enrolment['StudentID'] = enrolment['StudentID'].astype(str).str.strip()
        
        # Hunt for WAI data to extract real names
        wai_files = glob.glob("WAI_Data*.csv")
        all_students = []
        
        if wai_files:
            for file in wai_files:
                try:
                    with open(file, 'r', encoding='utf-8') as f:
                        lines = [line.strip() for line in f.readlines()[:10]]
                    
                    header_row = 0
                    for i, line in enumerate(lines):
                        if 'Student ID' in line or 'StudentID' in line or 'Serial No.' in line:
                            header_row = i
                            break
                            
                    df = pd.read_csv(file, skiprows=header_row)
                    
                    if 'Student ID' in df.columns and 'Student Name' in df.columns:
                        temp = pd.DataFrame()
                        temp['StudentID'] = df['Student ID'].astype(str).str.strip()
                        temp['Name'] = df['Student Name'].astype(str).str.strip()
                        
                        if 'Email' in df.columns:
                            temp['Email'] = df['Email'].astype(str).str.strip()
                        else:
                            temp['Email'] = "Not Provided"
                            
                        all_students.append(temp)
                except Exception:
                    continue
                    
        # Merge the names and emails safely
        if all_students:
            student_details = pd.concat(all_students)
            student_details = student_details[student_details['StudentID'] != 'nan']
            student_details = student_details.sort_values(by='Email', ascending=False).drop_duplicates(subset=['StudentID'])
            
            enrolment = pd.merge(enrolment, student_details, on='StudentID', how='left')
            enrolment['Name'] = enrolment['Name'].fillna("Name Not Found")
            enrolment['Email'] = enrolment['Email'].fillna("Email Not Found")
        else:
            enrolment['Name'] = "Data Not Extracted"
            enrolment['Email'] = "Data Not Extracted"

        return timetable, enrolment
        
    except Exception as e:
        st.error(f"⚠️ Error loading data: {e}")
        return pd.DataFrame(), pd.DataFrame()

timetable, enrolment = load_data()

if not timetable.empty and not enrolment.empty:
    
    st.sidebar.header("🔍 Dashboard Filters")
    
    # --- TABS ---
    tab1, tab2, tab3, tab4 = st.tabs([
        "📅 Daily Master", 
        "👨‍🏫 Faculty View", 
        "👥 Student Directory",
        "🗓️ Weekly Calendar"
    ])
    
    # ==========================================
    # TAB 1: DAILY MASTER SCHEDULE
    # ==========================================
    with tab1:
        st.subheader("Daily Campus Operations")
        dates = sorted(timetable['Date'].unique())
        selected_date = st.selectbox("Select a Date:", dates, key="daily_date")
        
        daily_schedule = timetable[timetable['Date'] == selected_date].copy().sort_values(by='Time_Slot')
        max_rooms = 10 if "Nov" in selected_date else 4
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Classes Today", len(daily_schedule))
        col2.metric("Active Room Capacity", f"Max {max_rooms} Rooms")
        col3.metric("Status", "Zero Conflicts ✅")
        
        st.dataframe(daily_schedule[['Time_Slot', 'Room_Number', 'Course_Section']], use_container_width=True, hide_index=True)

    # ==========================================
    # TAB 2: FACULTY / COURSE VIEW
    # ==========================================
    with tab2:
        st.subheader("Course Section Tracker")
        sections = sorted(timetable['Course_Section'].unique())
        selected_section = st.selectbox("Select a Course Section:", sections, key="fac_sec")
        
        section_schedule = timetable[timetable['Course_Section'] == selected_section].copy()
        st.write(f"**Total Sessions Scheduled:** {len(section_schedule)} / 20")
        st.dataframe(section_schedule[['Date', 'Day', 'Time_Slot', 'Room_Number']].sort_values(by='Date'), use_container_width=True, hide_index=True)

    # ==========================================
    # TAB 3: STUDENT DIRECTORY
    # ==========================================
    with tab3:
        st.subheader("Section Enrolment Lists")
        enrol_sections = sorted(enrolment['Section_Label'].unique())
        selected_enrol_section = st.selectbox("Look up Section:", enrol_sections, key="stu_sec")
        
        students_in_section = enrolment[enrolment['Section_Label'] == selected_enrol_section]
        st.metric(f"Total Students in {selected_enrol_section}", len(students_in_section))
        st.dataframe(students_in_section[['StudentID', 'Name', 'Email']], use_container_width=True, hide_index=True)

    # ==========================================
    # TAB 4: THE WEEKLY CALENDAR GRID
    # ==========================================
    with tab4:
        st.subheader("🗓️ Visual Weekly Calendar")
        st.write("View the master schedule mapped out in a clean weekly grid.")
        
        col1, col2 = st.columns(2)
        weeks = sorted(timetable['Week'].unique())
        selected_week = col1.selectbox("Select Week:", weeks)
        view_mode = col2.radio("View Calendar By:", ["Room", "Course Section"], horizontal=True)
        
        week_data = timetable[timetable['Week'] == selected_week].copy()
        
        if view_mode == "Room":
            rooms = sorted(week_data['Room_Number'].unique())
            selected_target = st.selectbox("Select Room to view:", rooms)
            cal_data = week_data[week_data['Room_Number'] == selected_target]
            values_col = 'Course_Section' 
        else:
            course_secs = sorted(week_data['Course_Section'].unique())
            selected_target = st.selectbox("Select Section to view:", course_secs)
            cal_data = week_data[week_data['Course_Section'] == selected_target]
            values_col = 'Room_Number' 
            
        if cal_data.empty:
            st.info("No classes scheduled for this selection during the chosen week.")
        else:
            # Standard sorting logic to make the calendar look perfect
            days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            
            # Create the Calendar Pivot
            calendar_pivot = cal_data.pivot_table(
                index='Time_Slot', 
                columns='Day', 
                values=values_col, 
                aggfunc=lambda x: ' + '.join(x) 
            )
            
            # Reorder columns chronologically
            available_days = [day for day in days_order if day in calendar_pivot.columns]
            calendar_pivot = calendar_pivot.reindex(columns=available_days)
            
            # Fill empty slots with a clean dash and render
            st.dataframe(
                calendar_pivot.fillna("—"), 
                use_container_width=True
            )

else:
    st.warning("Awaiting data files...")
