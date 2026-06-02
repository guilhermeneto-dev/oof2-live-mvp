import streamlit as st
import cv2
import numpy as np
from PIL import Image

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="OOF2 Live - Analítico", layout="wide")

st.markdown("""
    <style>
    .main {background-color: #f8f9fa;}
    h1 {color: #0a2240;}
    .metric-card {background-color: #ffffff; padding: 15px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);}
    </style>
""", unsafe_allow_html=True)

st.title("⚙️ OOF2 Live: Cálculo Analítico de Dano Estrutural")
st.subheader("Geração de Malha e Estimativa de Degradação do Módulo de Young")

# --- BARRA LATERAL (PARÂMETROS DE ENTRADA) ---
st.sidebar.header("1. Parâmetros de Visão")
threshold_value = st.sidebar.slider("Limiar (Threshold) de Segmentação", min_value=0, max_value=255, value=120)

st.sidebar.markdown("---")
st.sidebar.header("2. Propriedades do Material")
st.sidebar.write("Defina o material base da impressão (ex: PLA, ABS, PETG).")
e_base = st.sidebar.number_input("Módulo de Young Original (GPa)", min_value=0.1, max_value=200.0, value=3.5, step=0.1)
# Fator de sensibilidade do poro (m=2 é comum para defeitos esféricos/aleatórios em polímeros)
m_factor = st.sidebar.slider("Fator de Concentração de Tensão (m)", min_value=1.0, max_value=5.0, value=2.0, step=0.1)

st.sidebar.markdown("---")
st.sidebar.write("**Autor:** Guilherme Fernandes Neto")
st.sidebar.write("**Laboratório:** PPGEMec - UFSCar")

# --- UPLOAD DA IMAGEM ---
uploaded_file = st.file_uploader("Faça o upload da micrografia FDM (PNG/JPG)", type=["png", "jpg", "jpeg"])

if uploaded_file is not None:
    # 1. Processamento de Imagem
    image = Image.open(uploaded_file)
    img_array = np.array(image.convert('RGB'))
    gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
    
    # Binarização (Separar Fase Sólida dos Vazios)
    # Valores abaixo do threshold ficam pretos (0 - Vazios), acima ficam brancos (255 - Sólido)
    _, binary = cv2.threshold(gray, threshold_value, 255, cv2.THRESH_BINARY)
    
    # 2. O MOCK DO OOF2 (Geração da Malha)
    contours, _ = cv2.findContours(binary, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    oof2_mesh = img_array.copy()
    cv2.drawContours(oof2_mesh, contours, -1, (0, 255, 0), 2)

    # --- O MOTOR ANALÍTICO (O CÁLCULO DE DANO) ---
    total_pixels = binary.size
    # Conta os píxeis brancos (fase sólida)
    solid_pixels = cv2.countNonZero(binary)
    # A diferença são os píxeis pretos (porosidade/falhas)
    void_pixels = total_pixels - solid_pixels
    
    # Cálculo da Fração de Porosidade
    porosity_fraction = void_pixels / total_pixels
    porosity_percentage = porosity_fraction * 100
    
    # Estimativa de Degradação (Modelo Simplificado: E = E0 * (1 - p)^m)
    e_efetivo = e_base * ((1 - porosity_fraction) ** m_factor)
    queda_percentual = ((e_base - e_efetivo) / e_base) * 100

    # --- VISUALIZAÇÃO DOS RESULTADOS ---
    st.write("---")
    st.write("### Diagnóstico de Integridade Microestrutural")
    
    # Painel de Métricas (Dashboard)
    col_m1, col_m2, col_m3 = st.columns(3)
    col_m1.metric(label="Volume de Porosidade Detetada", value=f"{porosity_percentage:.2f} %", delta="Defeito Geométrico", delta_color="inverse")
    col_m2.metric(label="Módulo de Young Efetivo", value=f"{e_efetivo:.2f} GPa", delta=f"- {queda_percentual:.1f}% de Rigidez", delta_color="inverse")
    col_m3.metric(label="Malha OOF2", value=f"{len(contours)}", delta="Elementos Gerados", delta_color="normal")

    st.write("---")
    
    # Imagens
    col1, col2, col3 = st.columns(3)
    with col1:
        st.write("**1. Microestrutura Original**")
        st.image(image, use_container_width=True)
    with col2:
        st.write("**2. Segmentação (Vazios Isolados)**")
        st.image(binary, use_container_width=True)
    with col3:
        st.write("**3. Malha Gêmeo Digital (OOF2)**")
        st.image(oof2_mesh, use_container_width=True)
        
    st.success("✅ Cálculo analítico concluído. Os dados de degradação do tensor elástico estão prontos para exportação.")
else:
    st.info("Aguardando upload da micrografia para iniciar a extração de métricas...")
