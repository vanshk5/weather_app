# retrain.py
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
import joblib
import config  # make sure config.MODEL_PATH points to your model file

# --- Load dataset ---
data = pd.read_csv("src/toronto_weather_history.csv")

# Features and label
X = data[['Temp', 'Humidity', 'Precip', 'Weather']]
y = data['RainTomorrowMorning']

# Split into train and test
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Preprocessing
numeric_features = ['Temp', 'Humidity', 'Precip']
categorical_features = ['Weather']

preprocessor = ColumnTransformer([
    ('num', StandardScaler(), numeric_features),
    ('cat', OneHotEncoder(handle_unknown='ignore'), categorical_features)
])

# Pipeline
model = Pipeline([
    ('preprocessor', preprocessor),
    ('classifier', LogisticRegression(max_iter=500))
])

# Train model
model.fit(X_train, y_train)

# Evaluate
y_pred = model.predict(X_test)
print(classification_report(y_test, y_pred))

# Save model
joblib.dump(model, config.MODEL_PATH)
print(f"Model saved to {config.MODEL_PATH}")
