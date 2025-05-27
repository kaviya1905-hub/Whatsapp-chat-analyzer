import streamlit as st
import pandas as pd
import re
from datetime import datetime

st.title("WhatsApp Chat Analyzer")

uploaded_file = st.file_uploader("Upload your WhatsApp chat (.txt)", type=["txt"])

def preprocess_chat(raw_text):
    # Updated regex to allow unicode whitespace between time and am/pm
    pattern = r'(\d{1,2}/\d{1,2}/\d{2,4}), (\d{1,2}:\d{2}\s*(?:AM|PM|am|pm)) - (.*?): (.*)'
    
    messages = []
    current_message = None

    lines = raw_text.split('\n')
    
    # Optional: Debug print first 10 lines (you can remove later)
    for i, line in enumerate(lines[:10]):
        st.write(f"Line {i+1}: {line}")

    for line in lines:
        match = re.match(pattern, line)
        if match:
            date_str = match.group(1)
            time_str = match.group(2)
            user = match.group(3)
            message = match.group(4)

            # Try parsing timestamp (same as before)
            timestamp = None
            for fmt in ('%m/%d/%y %I:%M %p', '%d/%m/%y %I:%M %p', '%d/%m/%Y %I:%M %p'):
                try:
                    timestamp = datetime.strptime(f"{date_str} {time_str.strip()}", fmt)
                    break
                except ValueError:
                    continue

            if current_message:
                messages.append(current_message)

            current_message = {
                "timestamp": timestamp,
                "user": user,
                "message": message
            }
        else:
            # continuation lines
            if current_message:
                current_message["message"] += '\n' + line

    if current_message:
        messages.append(current_message)

    df = pd.DataFrame(messages)
    return df


if uploaded_file:
    # Read file as string
    raw_text = uploaded_file.read().decode('utf-8')
    
    # Preprocess chat
    df = preprocess_chat(raw_text)
    
    st.success("File uploaded and processed successfully!")
    st.write("Columns detected in DataFrame:", df.columns.tolist())

    st.dataframe(df.head(20))

    # Save to session state for further use if needed
    st.session_state['chat_df'] = df

    # Check if the 'user' column exists and df is not empty before analysis
    if 'user' in df.columns and not df.empty:
        # 1. Who texted the most?
        user_counts = df['user'].value_counts()
        st.subheader("Messages sent by each user")
        st.bar_chart(user_counts)
        
        # 2. When was the group active?
        df['hour'] = df['timestamp'].dt.hour
        hourly_counts = df.groupby('hour').size()
        st.subheader("Group activity by hour of day")
        st.bar_chart(hourly_counts)
        
        df['date'] = df['timestamp'].dt.date
        daily_counts = df.groupby('date').size()
        st.subheader("Group activity by date")
        st.line_chart(daily_counts)
    else:
        st.warning("No valid 'user' column found or the uploaded file is empty.")
