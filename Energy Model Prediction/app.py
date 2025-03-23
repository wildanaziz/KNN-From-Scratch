import streamlit as st
import numpy as np
import pandas as pd

# Fungsi Euclidean Distance
def euclidean_distance(x1, x2):
    return np.sqrt(np.sum((x1 - x2) ** 2, axis=1))

# Kelas KNN untuk regresi
class KNNRegresi:
    def __init__(self, n_neighbors=3):
        self.n_neighbors = n_neighbors
    
    def fit(self, X_train, y_train):
        self.X_train = np.array(X_train)
        self.y_train = np.array(y_train)
    
    def predict(self, X_test):
        X_test = np.array(X_test)
        predictions = []
        for x in X_test:
            distances = euclidean_distance(self.X_train, x)
            nearest_indices = distances.argsort()[:self.n_neighbors]
            nearest_values = self.y_train[nearest_indices]
            predictions.append(np.mean(nearest_values, axis=0))
        return np.array(predictions)

# Load dataset
data_path = "dataset/ENB2012_data.xlsx"
df = pd.read_excel(data_path)
df.rename(columns={
    'X1': 'Relative_Compactness', 'X2': 'Surface_Area', 'X3': 'Wall_Area', 'X4': 'Roof_Area',
    'X5': 'Overall_Height', 'X6': 'Orientation', 'X7': 'Glazing_Area',
    'X8': 'Glazing_Area_Distribution', 'Y1': 'Heating Load', 'Y2': 'Cooling Load'
}, inplace=True)
df = df.loc[(df[['Glazing_Area', 'Glazing_Area_Distribution']] != 0).all(axis=1)]

# Persiapan data
X = df.drop(columns=['Orientation', 'Heating Load', 'Cooling Load']).values
y = df[['Heating Load', 'Cooling Load']].values

# Normalisasi
data_mean, data_std = X.mean(axis=0), X.std(axis=0)
X = (X - data_mean) / data_std

# Split data
np.random.seed(123)
indices = np.random.permutation(len(X))
split = int(len(X) * 0.8)
X_train, X_test = X[indices[:split]], X[indices[split:]]
y_train, y_test = y[indices[:split]], y[indices[split:]]

# Train model
knn = KNNRegresi(n_neighbors=3)
knn.fit(X_train, y_train)

# Streamlit UI
st.title("Energy Efficiency Prediction Using KNN")
st.write("Masukkan parameter bangunan untuk memprediksi Heating Load dan Cooling Load")

# Input pengguna
relative_compactness = st.slider("Kompak Relatif", 0.6, 1.0, 0.75)
surface_area = st.slider("Luas Permukaan (m²)", 510.0, 800.0, 500.0)
wall_area = st.slider("Luas Dinding (m²)", 240.0, 416.0, 300.0)
roof_area = st.slider("Luas Atap (m²)", 110.0, 220.0, 200.0)
overall_height = st.slider("Tinggi Keseluruhan (m)", 3.0, 7.0, 5.0)
glazing_area = st.slider("Luas Kaca (m²)", 0.1, 0.4, 0.1)
glazing_area_distribution = st.slider("Distribusi Luas Kaca", 0.0, 5.0, 3.0)

if st.button("Predict"):
    input_data = np.array([[relative_compactness, surface_area, wall_area, roof_area, 
                             overall_height, glazing_area, glazing_area_distribution]])
    input_data = (input_data - data_mean) / data_std  # Normalisasi input
    prediction = knn.predict(input_data)
    
    st.write(f"Predicted Heating Load: {prediction[0][0]:.2f}")
    st.write(f"Predicted Cooling Load: {prediction[0][1]:.2f}")