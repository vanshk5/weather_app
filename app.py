import streamlit as st
import joblib
import pandas as pd
import altair as alt
from fetch_weather import get_current_weather, get_hourly_history
import config

# Load trained model
model = joblib.load(config.MODEL_PATH)

st.title("Rain Prediction App")
st.write("Enter a city to get current weather, rain prediction, and last 24 hours trends.")

# City input
city_input = st.text_input("Enter city (e.g., Toronto,CA):", "Toronto,CA")

if st.button("Get Weather & Predict"):
    city = city_input.strip()
    weather_data = get_current_weather(city)

    if weather_data:
        temp, humidity, precip, condition = weather_data

        # Display current weather
        st.subheader("Current Weather")
        st.write(f"Temperature: {temp}°C")
        st.write(f"Humidity: {humidity}%")
        st.write(f"Condition: {condition}")
        st.write(f"Precipitation: {precip} mm")

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

        st.subheader("Rain Prediction")
        if prediction == 1:
            st.success(f"Rain likely tomorrow morning! ({probability:.0%} chance)")
        else:
            st.info(f"No rain expected tomorrow morning. ({probability:.0%} chance)")

        # Last 24 hours data
        df_last_24h = get_hourly_history(city, hours=24)
        if df_last_24h.empty:
            st.warning("Failed to fetch last 24 hours data. Showing current weather only.")
        else:
            st.subheader("Last 24 Hours Weather Trends")

            # Format datetime for charts
            df_last_24h['datetime_local'] = df_last_24h['datetime'].dt.tz_localize(None)

            # Temperature chart
            temp_chart = alt.Chart(df_last_24h).mark_line(point=True).encode(
                x=alt.X('datetime_local:T', title='Time', axis=alt.Axis(format='%b %d %H:%M')),
                y=alt.Y('Temp:Q', title='Temperature (°C)'),
                tooltip=['datetime_local', 'Temp']
            ).properties(title='Temperature (°C)')
            st.altair_chart(temp_chart, use_container_width=True)

            # Humidity chart
            humidity_chart = alt.Chart(df_last_24h).mark_line(point=True, color='blue').encode(
                x=alt.X('datetime_local:T', title='Time', axis=alt.Axis(format='%b %d %H:%M')),
                y=alt.Y('Humidity:Q', title='Humidity (%)'),
                tooltip=['datetime_local', 'Humidity']
            ).properties(title='Humidity (%)')
            st.altair_chart(humidity_chart, use_container_width=True)

            # Precipitation chart
            precip_chart = alt.Chart(df_last_24h).mark_bar(color='green').encode(
                x=alt.X('datetime_local:T', title='Time', axis=alt.Axis(format='%b %d %H:%M')),
                y=alt.Y('Precip:Q', title='Precipitation (mm)'),
                tooltip=['datetime_local', 'Precip']
            ).properties(title='Precipitation (mm)')
            st.altair_chart(precip_chart, use_container_width=True)

            # Summary stats
            st.subheader("Last 24 Hours Summary")
            st.write(f"Max Temp: {df_last_24h['Temp'].max():.1f}°C")
            st.write(f"Min Temp: {df_last_24h['Temp'].min():.1f}°C")
            st.write(f"Average Humidity: {df_last_24h['Humidity'].mean():.1f}%")
            st.write(f"Total Precipitation: {df_last_24h['Precip'].sum():.1f} mm")

        # Clean color-coded probability bar
        st.subheader("Probability of Rain Tomorrow Morning")
        st.write(f"Chance of rain: {probability:.0%}")

        if probability < 0.3:
            color = "#28a745"  # Green
        elif probability < 0.7:
            color = "#ffc107"  # Yellow
        else:
            color = "#dc3545"  # Red

        st.markdown(
            f"""
            <div style="width: 100%; height: 25px; background-color: {color}; border-radius: 5px;"></div>
            """,
            unsafe_allow_html=True
        )

    else:
        st.error("Failed to fetch weather for this city. Please check the city name and try again.")

