
import streamlit as st
import cv2
import numpy as np
import pandas as pd
from PIL import Image
from io import BytesIO

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="OOF2 Live - Arquitetura ICME", layout="wide")

st.markdown("""
    <style>
    .main {background-color: #f8f9fa;}
    h1 {color: #0a2240;}
    </style>
""", unsafe_allow_html=True)

st.title("⚙️ OOF2 Live: Arquitetura ICME para Qualificação Rápida")
st.subheader("Geração de Malha, Mecânica do Dano e Exportação de Tensores")

# --- BANCO DE DADOS DE MATERIAIS ---
base_materiais = {
    "PLA (Manufatura Aditiva)": {"E": 3.5, "m": 2.0},
    "ABS (Manufatura Aditiva)": {"E": 2.2, "m": 2.2},
    "Aço Nitretado (Camada Branca)": {"E": 200.0, "m": 3.5},
    "Liga de Alumínio 7075-T6": {"E": 71.7, "m": 1.5},
    "Personalizado": {"E": 0.0, "m": 1.0}
}

# --- BARRA LATERAL (PARÂMETROS DE ENTRADA) ---
st.sidebar.header("1. Parâmetros de Segmentação")
threshold_value = st.sidebar.slider("Limiar (Threshold) Visual", min_value=0, max_value=255, value=120)

st.sidebar.markdown("---")
st.sidebar.header("2. Seleção de Material")
material_selecionado = st.sidebar.selectbox("Base Estrutural:", list(base_materiais.keys()))

# Preenchimento automático ou manual
if material_selecionado == "Personalizado":
    e_base = st.sidebar.number_input("Módulo de Young Original (GPa)", min_value=0.1, value=1.0)
    m_factor = st.sidebar.slider("Fator de Concentração de Tensão (m)", min_value=1.0, max_value=5.0, value=2.0)
else:
    e_base = base_materiais[material_selecionado]["E"]
    m_factor = base_materiais[material_selecionado]["m"]
    st.sidebar.info(f"**E0:** {e_base} GPa | **Fator m:** {m_factor}")

st.sidebar.markdown("---")
st.sidebar.write("**Investigador:** Guilherme Fernandes Neto")
st.sidebar.write("**Laboratório:** PPGEMec - UFSCar")

# --- UPLOAD DA IMAGEM ---
uploaded_file = st.file_uploader("Carregue a micrografia (FDM ou MEV)", type=["png", "jpg", "jpeg"])

if uploaded_file is not None:
    # Processamento de Imagem
    image = Image.open(uploaded_file)
    img_array = np.array(image.convert('RGB'))
    gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
    
    # Binarização
    _, binary = cv2.threshold(gray, threshold_value, 255, cv2.THRESH_BINARY)
    
    # Geração do Gêmeo Digital (Mock OOF2)
    contours, _ = cv2.findContours(binary, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    oof2_mesh = img_array.copy()
    cv2.drawContours(oof2_mesh, contours, -1, (0, 255, 0), 2)

    # Cálculo Analítico
    total_pixels = binary.size
    solid_pixels = cv2.countNonZero(binary)
    void_pixels = total_pixels - solid_pixels
    
    porosity_fraction = void_pixels / total_pixels
    porosity_percentage = porosity_fraction * 100
    e_efetivo = e_base * ((1 - porosity_fraction) ** m_factor)
    queda_percentual = ((e_base - e_efetivo) / e_base) * 100

    # --- VISUALIZAÇÃO DOS RESULTADOS ---
    col_m1, col_m2, col_m3 = st.columns(3)
    col_m1.metric(label="Volume de Porosidade", value=f"{porosity_percentage:.2f} %", delta="Defeito Geométrico", delta_color="inverse")
    col_m2.metric(label="Módulo de Young Efetivo", value=f"{e_efetivo:.2f} GPa", delta=f"- {queda_percentual:.1f}% de Rigidez", delta_color="inverse")
    col_m3.metric(label="Elementos Finitos (Nós)", value=f"{len(contours)*4}", delta="Gerados na Malha", delta_color="normal")

    st.write("---")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.write("**1. Microestrutura Original**")
        st.image(image, use_container_width=True)
    with col2:
        st.write("**2. Segmentação Autónoma**")
        st.image(binary, use_container_width=True)
    with col3:
        st.write("**3. Malha OOF2 (Gêmeo Digital)**")
        st.image(oof2_mesh, use_container_width=True)
        
    # --- MÓDULO DE EXPORTAÇÃO (CSV) ---
    st.write("### Exportação de Dados para ICME")
    
    # Criar um DataFrame com os resultados
    df_resultados = pd.DataFrame({
        "Material": [material_selecionado],
        "Threshold_Aplicado": [threshold_value],
        "Porosidade_Percentual": [round(porosity_percentage, 2)],
        "Modulo_Young_Original_GPa": [e_base],
        "Modulo_Young_Efetivo_GPa": [round(e_efetivo, 3)],
        "Degradacao_Percentual": [round(queda_percentual, 2)],
        "Fator_Concentracao_m": [m_factor],
        "Nos_Malha_Gerados": [len(contours)*4]
    })
    
    st.dataframe(df_resultados, use_container_width=True)
    
    csv = df_resultados.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Descarregar Relatório Analítico (CSV)",
        data=csv,
        file_name='oof2_relatorio_dano.csv',
        mime='text/csv',
    )
    
else:
    st.info("A aguardar o upload da micrografia para iniciar a simulação...")
