import streamlit as st
import pandas as pd
import csv
from datetime import datetime
import os
import pytz  # Import the pytz library

# Define the Indian Standard Time zone
IST = pytz.timezone('Asia/Kolkata')

# Initialize session state (no change here)
if 'last_timestamps' not in st.session_state:
    st.session_state.last_timestamps = {
        'MTW': None,
        'Car': None,
        '3W': None,
        'Buses': None,
        'Cycles': None
    }

if 'vehicle_counts' not in st.session_state:
    st.session_state.vehicle_counts = {
        'MTW': 0,
        'Car': 0,
        '3W': 0,
        'Buses': 0,
        'Cycles': 0
    }

def log_to_csv(school_name, vehicle_type, timestamp, time_diff, count):
    """Log vehicle data to CSV file"""
    filename = f"{school_name.replace(' ', '_')}_vehicle_log.csv"
    
    # Check if file exists to determine if we need headers
    file_exists = os.path.isfile(filename)
    
    # Prepare data
    data = {
        'School_Name': school_name,
        'Vehicle_Type': vehicle_type,
        'Timestamp': timestamp.strftime('%Y-%m-%d %H:%M:%S'),
        'Time_Since_Last_Press': time_diff,
        'Total_Count': count
    }
    
    # Write to CSV
    with open(filename, 'a', newline='') as csvfile:
        fieldnames = ['School_Name', 'Vehicle_Type', 'Timestamp', 'Time_Since_Last_Press', 'Total_Count']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        # Write header if file is new
        if not file_exists:
            writer.writeheader()
        
        writer.writerow(data)

def format_time_diff(time_diff):
    """Format time difference in readable format"""
    if time_diff is None:
        return "First press"
    
    total_seconds = int(time_diff.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    
    if hours > 0:
        return f"{hours}h {minutes}m {seconds}s"
    elif minutes > 0:
        return f"{minutes}m {seconds}s"
    else:
        return f"{seconds}s"

# Streamlit App (no change here)
st.title("🚗 Vehicle Tracking Timer")
st.markdown("---")

# School name input (no change here)
school_name = st.text_input("Enter School Name:", placeholder="e.g., ABC Public School")

if not school_name:
    st.warning("Please enter a school name to continue.")
    st.stop()

# Display current counts (no change here)
st.subheader("📊 Current Vehicle Counts")
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric("MTW (Motorcycles)", st.session_state.vehicle_counts['MTW'])
with col2:
    st.metric("Cars", st.session_state.vehicle_counts['Car'])
with col3:
    st.metric("3W (Auto)", st.session_state.vehicle_counts['3W'])
with col4:
    st.metric("Buses", st.session_state.vehicle_counts['Buses'])
with col5:
    st.metric("Cycles", st.session_state.vehicle_counts['Cycles'])

st.markdown("---")

# Timer buttons (The only major change is here)
st.subheader("⏱️ Vehicle Timer Buttons")

# Create buttons in columns for better layout
col1, col2, col3, col4, col5 = st.columns(5)

vehicle_types = ['MTW', 'Car', '3W', 'Buses', 'Cycles']
button_colors = ['🏍️', '🚗', '🛺', '🚌', '🚲']

for i, (vehicle_type, emoji) in enumerate(zip(vehicle_types, button_colors)):
    with [col1, col2, col3, col4, col5][i]:
        if st.button(f"{emoji} {vehicle_type}", key=vehicle_type, use_container_width=True):
            # Get the current time and make it timezone-aware (IST)
            current_time = datetime.now(IST)
            
            last_time = st.session_state.last_timestamps[vehicle_type]
            
            # Calculate time difference
            time_diff = None
            if last_time:
                # Ensure the time difference is calculated between timezone-aware objects
                time_diff = current_time - last_time
            
            # Update count
            st.session_state.vehicle_counts[vehicle_type] += 1
            
            # Log to CSV
            log_to_csv(
                school_name, 
                vehicle_type, 
                current_time, 
                format_time_diff(time_diff), 
                st.session_state.vehicle_counts[vehicle_type]
            )
            
            # Update last timestamp
            st.session_state.last_timestamps[vehicle_type] = current_time
            
            # Show success message
            time_diff_str = format_time_diff(time_diff)
            st.success(f"✅ {vehicle_type} logged! Time since last press: {time_diff_str}")
            st.rerun()

st.markdown("---")

# Display last press times (slight change here to handle time zone)
st.subheader("🕐 Last Press Times")
for vehicle_type in vehicle_types:
    last_time = st.session_state.last_timestamps[vehicle_type]
    if last_time:
        # Get the current time for the "ago" calculation
        current_time_ist = datetime.now(IST)
        time_ago = current_time_ist - last_time
        st.write(f"**{vehicle_type}**: {last_time.strftime('%H:%M:%S')} ({format_time_diff(time_ago)} ago)")
    else:
        st.write(f"**{vehicle_type}**: Not pressed yet")

# Reset functionality (no change here)
st.markdown("---")
col1, col2, col3 = st.columns([1, 1, 1])

with col2:
    if st.button("🔄 Reset All Counters", type="secondary", use_container_width=True):
        st.session_state.last_timestamps = {key: None for key in st.session_state.last_timestamps}
        st.session_state.vehicle_counts = {key: 0 for key in st.session_state.vehicle_counts}
        st.success("All counters have been reset!")
        st.rerun()

# Display CSV file info (no change here, as the timestamp is already formatted)
if school_name:
    filename = f"{school_name.replace(' ', '_')}_vehicle_log.csv"
    if os.path.isfile(filename):
        st.markdown("---")
        st.subheader("📄 Log File Information")
        
        try:
            df = pd.read_csv(filename)
            st.write(f"**File**: `{filename}`")
            st.write(f"**Total entries**: {len(df)}")
            
            # Show recent entries
            if len(df) > 0:
                st.write("**Recent entries**:")
                st.dataframe(df.tail(5), use_container_width=True)
                
                # Download button
                csv_data = df.to_csv(index=False)
                st.download_button(
                    label="📥 Download CSV",
                    data=csv_data,
                    file_name=filename,
                    mime="text/csv"
                )
        except Exception as e:
            st.error(f"Error reading CSV file: {e}")

# Instructions (no change here)
with st.expander("ℹ️ How to use this app"):
    st.markdown("""
    1. **Enter School Name**: Type the name of your school in the input field
    2. **Press Vehicle Buttons**: Click on the appropriate vehicle type button when a vehicle passes
    3. **View Logs**: The app automatically logs each button press with:
       - Timestamp of the press
       - Time elapsed since the last press of the same vehicle type
       - Running count of vehicles per type
    4. **Download Data**: You can download the CSV file containing all logged data
    5. **Reset Counters**: Use the reset button to clear all counters and start fresh
    
    **Vehicle Types:**
    - **MTW**: Motorcycles/Two-wheelers 🏍️
    - **Car**: Cars 🚗
    - **3W**: Three-wheelers/Auto rickshaws 🛺
    - **Buses**: Buses 🚌
    - **Cycles**: Bicycles 🚲
    """)
