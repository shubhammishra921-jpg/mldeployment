import streamlit as st

st.set_page_config(page_title="Study Hours Predictor", page_icon="📚", layout="centered")

st.title("📚 Study Hours Pass/Fail Predictor")
st.write("Enter the number of hours studied to predict the exam result.")

# User input slider
hours = st.slider("Select Study Hours:", min_value=0.0, max_value=15.0, value=4.0, step=0.5)

# Simple prediction logic (passing threshold is 5 hours)
pass_threshold = 5.0

if st.button("Predict Result"):
    if hours >= pass_threshold:
        st.success(f"🎉 **PASS!** Studying for {hours} hours is enough.")
    else:
        st.error(f"⚠️ **FAIL!** Studying for {hours} hours is too low. Aim for 5+ hours.")