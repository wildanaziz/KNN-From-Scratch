import streamlit as st
import numpy as np
import joblib

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
            distances = np.sqrt(np.sum((self.X_train - x) ** 2, axis=1))
            nearest_indices = distances.argsort()[:self.n_neighbors]
            nearest_values = self.y_train[nearest_indices]
            predictions.append(np.mean(nearest_values, axis=0))
        return np.array(predictions)

# Load model KNN dan parameter normalisasi
knn = joblib.load('knn_model.pkl')
mean, std = joblib.load('scaler.pkl')

# Streamlit UI
st.title("Energy Efficiency Prediction Using KNN")
st.write("Wanna meet the devs? [Click Here](https://wildanaziz.vercel.app)")
st.write("Masukkan parameter bangunan untuk memprediksi Heating Load dan Cooling Load")


# Layout utama dengan 2 kolom (kolom 1 untuk input, kolom 2 untuk hasil prediksi)
col1, col2 = st.columns([3, 1])

# Kolom 1 (Input Parameter)
with col1:
    st.header("📌 Input Parameter")
    
    # Baris pertama (Kompak Relatif)
    with st.expander("ℹ️ **Apa itu Kompak Relatif?**"):
        st.write("Kompak relatif mengukur seberapa efisien bentuk bangunan dalam mempertahankan panas. Nilai lebih tinggi berarti lebih efisien.")
    relative_compactness = st.slider("Kompak Relatif", 0.6, 1.0, 0.75)

    # Dua kolom untuk sisa parameter
    col1a, col1b = st.columns(2)

    with col1a:  # Kolom kiri
        with st.expander("ℹ️ **Apa itu Luas Permukaan?**"):
            st.write("Luas permukaan adalah luas bangunan yang terlihat oleh matahari.")
        surface_area = st.slider("Luas Permukaan (m²)", 510.0, 800.0, 500.0)

        with st.expander("ℹ️ **Apa itu Luas Dinding?**"):
            st.write("Luas dinding adalah luas total dari semua dinding eksterior bangunan.")
        wall_area = st.slider("Luas Dinding (m²)", 240.0, 416.0, 300.0)

        with st.expander("ℹ️ **Apa itu Luas Atap?**"):
            st.write("Luas atap adalah luas permukaan bagian atas bangunan yang melindungi dari cuaca.")
        roof_area = st.slider("Luas Atap (m²)", 110.0, 220.0, 200.0)

    with col1b:  # Kolom kanan
        with st.expander("ℹ️ **Apa itu Tinggi Keseluruhan?**"):
            st.write("Tinggi keseluruhan adalah tinggi total bangunan dari dasar hingga puncak.")
        overall_height = st.slider("Tinggi Keseluruhan (m)", 3.0, 7.0, 5.0)

        with st.expander("ℹ️ **Apa itu Luas Kaca?**"):
            st.write("Luas kaca menunjukkan seberapa besar bagian bangunan yang terdiri dari kaca.")
        glazing_area = st.slider("Luas Kaca (m²)", 0.1, 0.4, 0.1)

        with st.expander("ℹ️ **Apa itu Distribusi Luas Kaca?**"):
            st.write("Distribusi luas kaca menunjukkan seberapa merata jendela tersebar di bangunan.")
        glazing_area_distribution = st.slider("Distribusi Luas Kaca", 0.0, 5.0, 3.0)



with col2:
    if st.button("Predict"):
        input_data = np.array([[relative_compactness, surface_area, wall_area, roof_area, 
                                 overall_height, glazing_area, glazing_area_distribution]])
        input_data = (input_data - mean) / std  # Normalisasi input
        prediction = knn.predict(input_data)
        heating_load = prediction[0][0]  # kWh/m²
        cooling_load = prediction[0][1]  # kWh/m²

        # Hitung biaya (Tarif listrik Rp 1.500 / kWh)
        tarif_per_kwh = 1500  # dalam Rupiah
        total_biaya = (heating_load + cooling_load) * tarif_per_kwh

        # Hitung kebutuhan daya dalam BTU/h
        kwh_to_btu = 3412  # 1 kWh = 3412 BTU/h
        # Kapasitas perangkat
        kapasitas_ac = 12000  # BTU/h per unit AC
        kapasitas_heater = 15000  # BTU/h per unit heater
        kebutuhan_pemanas = heating_load * kwh_to_btu  # dalam BTU/h
        kebutuhan_ac = cooling_load * kwh_to_btu  # dalam BTU/h

        # Hitung jumlah unit yang dibutuhkan
        total_ac = kebutuhan_ac / kapasitas_ac
        total_heater = kebutuhan_pemanas / kapasitas_heater

        # Pembulatan ke atas agar tidak kekurangan unit
        total_ac = int(np.ceil(total_ac))
        total_heater = int(np.ceil(total_heater))

        # Pembulatan ke atas agar tidak kekurangan unit
        total_ac = int(np.ceil(total_ac))
        total_heater = int(np.ceil(total_heater))

        # Logika tambahan: Jika Heating Load tinggi, maka kebutuhan AC rendah
        if heating_load > cooling_load:
            kebutuhan_ac *= 0.5  # Mengurangi kebutuhan AC jika pemanasan dominan
        elif cooling_load > heating_load:
            kebutuhan_pemanas *= 0.5  # Mengurangi kebutuhan pemanas jika pendinginan dominan

        # Tampilkan hasil
        st.success(f"🔥 **Beban Pemanasan:** {heating_load:.2f} kWh/m²")
        st.success(f"❄ **Beban Pendinginan:** {cooling_load:.2f} kWh/m²")

        st.info(f"💰 **Perkiraan Biaya Operasional:** Rp {total_biaya:,.0f} / bulan")

        if heating_load > cooling_load:
            st.warning(f"🔥 Total Heater yang Dibutuhkan: {total_heater} unit")
            st.success(f"❄ **Kebutuhan AC lebih rendah:** {total_ac} unit (karena pemanasan dominan)")
        else:
            st.warning(f"❄ **Total AC (Pendingin) yang dibutuhkan:** {total_ac} unit")
            st.success(f"🔥 **Kebutuhan Pemanas lebih rendah:** {total_heater} unit (karena pendinginan dominan)")