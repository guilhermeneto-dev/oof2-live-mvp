import streamlit as st
import cv2
import numpy as np
from PIL import Image

st.set_page_config(page_title="OOF2 Live - MVP", layout="wide")

st.markdown("""
    <style>
    .main {background-color: #f8f9fa;}
    h1 {color: #0a2240;}
    </style>
""", unsafe_allow_html=True)

st.title("⚙️ OOF2 Live: Micro-SHM em Manufatura Aditiva")
st.subheader("Geração Autônoma de Gêmeo Digital Microestrutural")

st.sidebar.header("Parâmetros do Algoritmo")
st.sidebar.write("Ajuste o filtro para isolar a porosidade da fase sólida.")
threshold_value = st.sidebar.slider("Threshold de Segmentação", min_value=0, max_value=255, value=120)

st.sidebar.markdown("---")
st.sidebar.write("**Autor:** Guilherme Fernandes Neto")
st.sidebar.write("**Laboratório:** PPGEMec - UFSCar")

uploaded_file = st.file_uploader("Faça o upload da micrografia (PNG/JPG)", type=["png", "jpg", "jpeg"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    img_array = np.array(image.convert('RGB'))
    gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
    
    _, binary = cv2.threshold(gray, threshold_value, 255, cv2.THRESH_BINARY)
    
    contours, _ = cv2.findContours(binary, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    
    oof2_mesh = img_array.copy()
    cv2.drawContours(oof2_mesh, contours, -1, (0, 255, 0), 2)

    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.write("### 1. Imagem Original")
        st.image(image, use_container_width=True)
        
    with col2:
        st.write("### 2. Visão Computacional")
        st.image(binary, use_container_width=True)
        
    with col3:
        st.write("### 3. Malha OOF2")
        st.image(oof2_mesh, use_container_width=True)
        
    st.success("✅ Simulação Concluída. Malha extraída com sucesso da microestrutura.")
else:
    st.info("Aguardando upload da imagem para iniciar a simulação...")
