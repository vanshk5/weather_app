# app.py
import streamlit as st
import joblib
import pandas as pd
from fetch_weather import get_current_weather
import config  # make sure config.MODEL_PATH points to 'model.joblib'

# --- Load trained model ---
model = joblib.load(config.MODEL_PATH)

# --- Streamlit UI ---
st.title(" Toronto Rain Prediction App")
st.write("This app predicts whether it will rain tomorrow morning based on live weather data.")

if st.button("Get Current Weather & Predict"):
    weather = get_current_weather()
    
    if weather:
        temp, humidity, precip, condition = weather
        
        # Show live weather
        st.subheader("Current Weather")
        st.write(f"**Temperature:** {temp}°C")
        st.write(f"**Humidity:** {humidity}%")
        st.write(f"**Condition:** {condition}")
        st.write(f"**Precipitation:** {precip} mm")
        
        # Prepare input for model
        input_df = pd.DataFrame({
            'Temp': [temp],
            'Humidity': [humidity],
            'Precip': [precip],
            'Weather': [condition]
        })
        
        # Predict rain tomorrow morning
        prediction = model.predict(input_df)[0]
        probability = model.predict_proba(input_df)[0][1]  # probability of rain
        
        st.subheader("Prediction")
        if prediction == 1:
            st.success(f" Rain likely tomorrow morning! (Probability: {probability:.2f})")
        else:
            st.info(f"☀ No rain expected tomorrow morning. (Probability: {probability:.2f})")
    else:
        st.error("Failed to fetch live weather. Please try again later.")
