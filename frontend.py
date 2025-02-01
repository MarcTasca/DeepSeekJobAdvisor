import streamlit as st
import json
from emailer import EmailMaker

# Sample Data
with open("files_cleaned/conversation.json", "r") as f:
    conversation = json.load(f)
# reverse the order of conversation
conversation = conversation[::-1]

with open("files/jobseeker.json", "r") as f:
    candidate_profile = json.load(f)

em = EmailMaker()
selected_jobs = em.suggest_jobs()

# Streamlit UI
st.title("Candidate Job Matching App")

# Display Conversation
st.subheader("Conversation")
conversation_box = "\n".join([f"---\n{msg['sender']} at {msg['send_date_time']}:\n{msg['body']}\n" for msg in conversation])
st.text_area("Conversation", conversation_box, height=300)

# Show Selected Jobs
st.subheader("Selected Jobs")
for job in selected_jobs:
    st.json(job)

# Display Candidate Profile
st.subheader("Candidate Profile")
st.json(candidate_profile)

# Email Section
st.subheader("Generated Email")
email_body = ""

if st.button("Generate Email"):
    email_body = em.generate_email()
    st.text_area("Modify Email Content:", email_body, height=200)

# Send Email Button
if st.button("Send Email ✉️"):
    st.success("✅ Email Sent Successfully!")  # Placeholder action