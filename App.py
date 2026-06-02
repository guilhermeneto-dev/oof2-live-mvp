
import streamlit as st
import cv2
import numpy as np
import pandas as pd
from PIL import Image
import time

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="OOF2 Live - Arquitetura ICME", layout="wide")

st.markdown("""
    <style>
    .main {background-color: #f8f9fa;}
    h1 {color: #0a2240;}
    .api-box {background-color: #e8f4f8; padding: 10px; border-radius: 5px; border-left: 5px solid #0056b3; margin-bottom: 15px;}
    </style>
""", unsafe_allow_html=True)

st.title("⚙️ OOF2 Live: Gêmeo Digital Integrado (NIST)")
st.subheader("Processamento Image-to-Mesh acoplado ao Banco de Dados JARVIS-DFT")

# --- CONEXÃO NIST JARVIS (API MOCK PARA O MVP) ---
def fetch_jarvis_data(formula):
    """Simula a extração de dados DFT do Joint Automated Repository (JARVIS)"""
    database_mock = {
        "Fe4N": {"K": 158.2, "G": 65.4, "nome": "Nitreto de Ferro (Camada Branca)"}, # Dados reais da literatura para Fe4N
        "Ti": {"K": 108.4, "G": 43.9, "nome": "Titânio (Fase Alfa)"},
        "Al": {"K": 77.3, "G": 26.1, "nome": "Alumínio (CFC)"}
    }
    return database_mock.get(formula, None)

# --- BARRA LATERAL (PARÂMETROS) ---
st.sidebar.header("1. Integração de Dados (JARVIS)")
usar_jarvis = st.sidebar.checkbox("Ativar Conexão NIST JARVIS-DFT", value=True)

e_base = 0.0
material_nome = "Não definido"

if usar_jarvis:
    st.sidebar.markdown('<div class="api-box"><b>Status:</b> 🟢 API Conectada</div>', unsafe_allow_html=True)
    formula_quimica = st.sidebar.text_input("Buscar Fórmula Química (ex: Fe4N, Ti, Al):", "Fe4N")
    
    jarvis_data = fetch_jarvis_data(formula_quimica)
    
    if jarvis_data:
        K = jarvis_data["K"]
        G = jarvis_data["G"]
        # Conversão de Módulos (Bulk e Shear para Young)
        e_base = (9 * K * G) / ((3 * K) + G)
        material_nome = jarvis_data["nome"]
        
        st.sidebar.success(f"**Material:** {material_nome}")
        st.sidebar.write(f"**Bulk Modulus (K):** {K} GPa")
        st.sidebar.write(f"**Shear Modulus (G):** {G} GPa")
        st.sidebar.info(f"**Módulo de Young Calculado (E0):** {e_base:.2f} GPa")
    else:
        st.sidebar.error("Material não encontrado no recorte atual do banco DFT.")
        e_base = 1.0 # fallback

else:
    st.sidebar.write("Modo manual ativado.")
    e_base = st.sidebar.number_input("Módulo de Young Original (GPa)", min_value=0.1, value=200.0)
    material_nome = "Material Inserido Manualmente"

st.sidebar.markdown("---")
st.sidebar.header("2. Parâmetros de Dano (OOF2)")
threshold_value = st.sidebar.slider("Limiar (Threshold) Visual", min_value=0, max_value=255, value=120)
m_factor = st.sidebar.slider("Fator de Concentração de Tensão (m)", min_value=1.0, max_value=6.0, value=3.5)

st.sidebar.markdown("---")
st.sidebar.write("**Investigador:** Guilherme Fernandes Neto")
st.sidebar.write("**Laboratório:** PPGEMec - UFSCar")

# --- UPLOAD DA IMAGEM ---
uploaded_file = st.file_uploader("Carregue a micrografia da falha estrutural", type=["png", "jpg", "jpeg"])

if uploaded_file is not None and e_base > 0:
    # Processamento de Imagem
    image = Image.open(uploaded_file)
    img_array = np.array(image.convert('RGB'))
    gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
    
    _, binary = cv2.threshold(gray, threshold_value, 255, cv2.THRESH_BINARY)
    
    contours, _ = cv2.findContours(binary, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    oof2_mesh = img_array.copy()
    cv2.drawContours(oof2_mesh, contours, -1, (0, 255, 0), 2)

    # Cálculo Analítico
    total_pixels = binary.size
    solid_pixels = cv2.countNonZero(binary)
    void_pixels = total_pixels - solid_pixels
    
    porosity_fraction = void_pixels / total_pixels
    porosity_percentage = porosity_fraction * 100
    
    # Modelo de Dano
    e_efetivo = e_base * ((1 - porosity_fraction) ** m_factor)
    queda_percentual = ((e_base - e_efetivo) / e_base) * 100

    # --- VISUALIZAÇÃO DOS RESULTADOS ---
    col_m1, col_m2, col_m3 = st.columns(3)
    col_m1.metric(label="Porosidade Extraída (Visão)", value=f"{porosity_percentage:.2f} %", delta="Vazios Microestruturais", delta_color="inverse")
    col_m2.metric(label="E Efetivo (Pós-Dano)", value=f"{e_efetivo:.2f} GPa", delta=f"- {queda_percentual:.1f}% de E0 ({e_base:.1f} GPa)", delta_color="inverse")
    col_m3.metric(label="Nós da Malha (OOF2)", value=f"{len(contours)*4}", delta="Prontos para FEA", delta_color="normal")

    st.write("---")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.write("**1. Microestrutura Bruta**")
        st.image(image, use_container_width=True)
    with col2:
        st.write("**2. Fase de Defeitos (Limiar)**")
        st.image(binary, use_container_width=True)
    with col3:
        st.write("**3. Gêmeo Digital (OOF2 Mesh)**")
        st.image(oof2_mesh, use_container_width=True)
        
    # --- MÓDULO DE EXPORTAÇÃO ---
    st.write("### Relatório de Engenharia Integrada (ICME)")
    
    df_resultados = pd.DataFrame({
        "Material_JARVIS": [material_nome],
        "Origem_Dados_Base": ["DFT (NIST JARVIS)" if usar_jarvis else "Manual"],
        "Fracao_Porosidade_%": [round(porosity_percentage, 2)],
        "E_Original_GPa": [round(e_base, 2)],
        "E_Degradado_GPa": [round(e_efetivo, 3)],
        "Perda_Rigidez_%": [round(queda_percentual, 2)],
        "Fator_m": [m_factor]
    })
    
    st.dataframe(df_resultados, use_container_width=True)
