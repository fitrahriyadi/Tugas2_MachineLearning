import streamlit as st
import joblib
import pandas as pd
import numpy as np

# --- KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="Diamond Price Predictor - Fitrah",
    page_icon="💎",
    layout="wide"
)

# --- LOAD MODEL & DATA ---
@st.cache_resource
def load_assets():
    # Pastikan file model dan csv ada di folder yang sama
    model = joblib.load('diamond_best_model.pkl')
    df_sample = pd.read_csv('diamonds.csv')
    return model, df_sample

model, df_sample = load_assets()

# --- STYLE CSS CUSTOM ---
st.markdown("""
    <style>
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        background-color: #007bff;
        color: white;
        font-weight: bold;
    }
    .result-card {
        padding: 20px;
        background-color: white;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        text-align: center;
        margin-top: 10px;
        border: 1px solid #e0e0e0;
    }
    .actual-price {
        color: #28a745;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# --- HEADER ---
st.title("💎 AI Diamond Price Predictor")
st.markdown(f"**Nama:** Fitrah Riyadi | **NIM:** E1E123032")
st.divider()

# --- SIDEBAR: PILIHAN INPUT ---
st.sidebar.header("⚙️ Opsi Input Data")
input_mode = st.sidebar.radio("Pilih Metode Input:", ["Input Manual (Random)", "Ambil dari Dataset (Excel)"])

if input_mode == "Ambil dari Dataset (Excel)":
    st.sidebar.subheader("📂 Pilih Baris")
    excel_row = st.sidebar.number_input(
        "Nomor Baris di Excel", 
        min_value=2, 
        max_value=len(df_sample)+1, 
        value=2, 
        step=1
    )
    
    python_index = excel_row - 2
    st.sidebar.markdown(f"**Preview Data Baris {excel_row}:**")
    st.sidebar.dataframe(df_sample.iloc[[python_index]].T)

    if st.sidebar.button("📥 Muat Data ke Form"):
        row_data = df_sample.iloc[python_index]
        # Simpan ke session state agar form terisi
        st.session_state.carat = float(row_data['carat'])
        st.session_state.cut = row_data['cut']
        st.session_state.color = row_data['color']
        st.session_state.clarity = row_data['clarity']
        st.session_state.depth = float(row_data['depth'])
        st.session_state.table = float(row_data['table'])
        st.session_state.x = float(row_data['x'])
        st.session_state.y = float(row_data['y'])
        st.session_state.z = float(row_data['z'])
        st.session_state.actual_price = float(row_data['price'])
        st.sidebar.success(f"Data Baris {excel_row} Berhasil Dimuat!")
else:
    st.sidebar.info("Silakan masukkan nominal angka secara bebas pada form di sebelah kanan.")
    # Hapus data harga asli jika pindah ke mode manual agar tidak membingungkan
    if 'actual_price' in st.session_state:
        del st.session_state.actual_price

# Mapping Encoding (Sesuai urutan LabelEncoder di Google Colab)
cut_map = {'Fair': 0, 'Good': 1, 'Ideal': 2, 'Premium': 3, 'Very Good': 4}
color_map = {'D': 0, 'E': 1, 'F': 2, 'G': 3, 'H': 4, 'I': 5, 'J': 6}
clarity_map = {'I1': 0, 'IF': 1, 'SI1': 2, 'SI2': 3, 'VS1': 4, 'VS2': 5, 'VVS1': 6, 'VVS2': 7}

# --- TAMPILAN UTAMA ---
col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.subheader("📏 Dimensi & Berat")
    carat = st.number_input("Carat (Berat)", 0.1, 5.0, step=0.01, key='carat')
    
    sub_col1, sub_col2, sub_col3 = st.columns(3)
    x = sub_col1.number_input("Panjang (x)", 0.0, 15.0, key='x', format="%.2f")
    y = sub_col2.number_input("Lebar (y)", 0.0, 15.0, key='y', format="%.2f")
    z = sub_col3.number_input("Tinggi (z)", 0.0, 15.0, key='z', format="%.2f")
    
    depth = st.number_input("Depth %", 40.0, 80.0, key='depth', step=0.1)
    table = st.number_input("Table Width", 40.0, 95.0, key='table', step=0.1)

with col2:
    st.subheader("✨ Kualitas & Kejernihan")
    cut = st.selectbox("Kualitas Potongan (Cut)", list(cut_map.keys()), key='cut')
    color = st.selectbox("Warna (Color)", list(color_map.keys()), key='color')
    clarity = st.selectbox("Kejernihan (Clarity)", list(clarity_map.keys()), key='clarity')
    
    st.write("")
    if st.button("🚀 PREDIKSI HARGA SEKARANG"):
        # Susun input ke DataFrame sesuai urutan fitur saat training
        input_df = pd.DataFrame({
            'carat': [carat], 'cut': [cut_map[cut]], 'color': [color_map[color]],
            'clarity': [clarity_map[clarity]], 'depth': [depth], 'table': [table],
            'x': [x], 'y': [y], 'z': [z]
        })
        
        prediction = model.predict(input_df)[0]
        
        # Tampilkan Hasil Prediksi
        st.markdown(f"""
            <div class="result-card">
                <h3 style="color: #555;">Hasil Prediksi AI</h3>
                <h1 style="color: #007bff; font-size: 45px;">${max(0, prediction):,.2f}</h1>
            </div>
            """, unsafe_allow_html=True)
        
        # Tampilkan Harga Asli hanya jika mode "Ambil dari Dataset" aktif
        if input_mode == "Ambil dari Dataset (Excel)" and 'actual_price' in st.session_state:
            st.markdown(f"""
                <div style="text-align: center; margin-top: 10px;">
                    <p>Harga Asli di Dataset: <span class="actual-price">${st.session_state.actual_price:,.2f}</span></p>
                    <p style="font-size: 0.8em; color: gray;">Selisih: ${abs(prediction - st.session_state.actual_price):,.2f}</p>
                </div>
                """, unsafe_allow_html=True)
        st.balloons()

st.divider()
st.caption("Aplikasi Prediksi Harga Berlian - Fitrah Riyadi (E1E123032)")