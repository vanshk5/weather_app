# app.py
import streamlit as st
import joblib
import pandas as pd
import altair as alt
from fetch_weather import get_current_weather, get_hourly_history
import config
from datetime import datetime, timedelta

# --- Load trained model ---
model = joblib.load(config.MODEL_PATH)

st.title(" Toronto Advanced Rain Prediction App")
st.write("Predict whether it will rain tomorrow morning and see last 24 hours weather trends.")

# Fetch weather button
if st.button("Get Current Weather & Predict"):
    # Get live current weather
    weather_data = get_current_weather()
    
    if weather_data:
        temp, humidity, precip, condition = weather_data
        
        # Show current weather
        st.subheader(" Current Weather")
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
        
        # Predict rain probability
        prediction = model.predict(input_df)[0]
        probability = model.predict_proba(input_df)[0][1]
        
        st.subheader(" Rain Prediction")
        if prediction == 1:
            st.success(f"Rain likely tomorrow morning! ({probability:.0%} chance)")
        else:
            st.info(f"No rain expected tomorrow morning. ({probability:.0%} chance)")
        
        # --- Fetch last 24 hours historical data ---
        df_last_24h = get_hourly_history(hours=24)
        if df_last_24h.empty:
            st.warning("Failed to fetch last 24 hours data. Showing current weather only.")
        else:
            st.subheader(" Last 24 Hours Weather Trends")
            
            # Temperature chart
            temp_chart = alt.Chart(df_last_24h).mark_line(point=True).encode(
                x='datetime:T',
                y='Temp:Q',
                tooltip=['datetime', 'Temp']
            ).properties(title='Temperature (°C)')
            st.altair_chart(temp_chart, use_container_width=True)
            
            # Humidity chart
            humidity_chart = alt.Chart(df_last_24h).mark_line(point=True, color='blue').encode(
                x='datetime:T',
                y='Humidity:Q',
                tooltip=['datetime', 'Humidity']
            ).properties(title='Humidity (%)')
            st.altair_chart(humidity_chart, use_container_width=True)
            
            # Precipitation chart
            precip_chart = alt.Chart(df_last_24h).mark_bar(color='green').encode(
                x='datetime:T',
                y='Precip:Q',
                tooltip=['datetime', 'Precip']
            ).properties(title='Precipitation (mm)')
            st.altair_chart(precip_chart, use_container_width=True)
            
            # Summary stats
            st.subheader(" Last 24 Hours Summary")
            st.write(f"Max Temp: {df_last_24h['Temp'].max():.1f}°C")
            st.write(f"Min Temp: {df_last_24h['Temp'].min():.1f}°C")
            st.write(f"Average Humidity: {df_last_24h['Humidity'].mean():.1f}%")
            st.write(f"Total Precipitation: {df_last_24h['Precip'].sum():.1f} mm")
        
        # Probability progress bar
        st.subheader(" Probability of Rain Tomorrow Morning")
        st.progress(int(probability * 100))
        
    else:
        st.error("Failed to fetch live weather. Please try again later.")
