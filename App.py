import streamlit as st
import cv2
import numpy as np
import pandas as pd
from PIL import Image
import traceback

# --- 1. CONFIGURAÇÃO DA PÁGINA (Deve ser o primeiro comando) ---
st.set_page_config(page_title="OOF2 Live - ICME", layout="wide")

st.markdown("""
    <style>
    .main {background-color: #f8f9fa;}
    h1 {color: #0a2240;}
    .api-box {background-color: #e8f4f8; padding: 10px; border-radius: 5px; border-left: 5px solid #0056b3; margin-bottom: 15px;}
    </style>
""", unsafe_allow_html=True)

# --- 2. DICIONÁRIO DE IDIOMAS (PT e EN) ---
locales = {
    "PT": {
        "title": "⚙️ OOF2 Live: Arquitetura ICME",
        "subtitle": "Geração Autónoma de Malha Acoplada ao JARVIS-DFT (NIST)",
        "sidebar_lang": "🌐 Idioma da Interface",
        "jarvis_toggle": "Ativar Ligação NIST JARVIS-DFT",
        "jarvis_input": "Pesquisar Fórmula (ex: Fe4N, Ti, Al):",
        "jarvis_success": "Material Encontrado",
        "jarvis_error": "Material não encontrado na base de dados DFT.",
        "sidebar_param": "Parâmetros de Segmentação",
        "threshold": "Limiar (Threshold) Visual",
        "custom_e": "Módulo de Young Original (GPa)",
        "custom_m": "Fator de Sensibilidade ao Dano (m)",
        "upload": "Carregue a micrografia (FDM ou MEV)",
        "metrics_title": "### Diagnóstico de Integridade Microestrutural",
        "m_porosity": "Porosidade Extraída",
        "m_porosity_d": "Defeito Volumétrico",
        "m_young": "Módulo de Young Efetivo",
        "m_young_d": "Perda de Rigidez",
        "m_nodes": "Complexidade da Malha",
        "m_nodes_d": "Nós Gerados",
        "img_raw": "**1. Microestrutura Bruta**",
        "img_bin": "**2. Fase de Defeitos Isolada**",
        "img_mesh": "**3. Gémeo Digital (OOF2)**",
        "export_title": "### Relatório de Engenharia Integrada",
        "btn_download": "📥 Descarregar Tensor (CSV)",
        "waiting": "A aguardar o carregamento da micrografia para inicializar o mapeamento..."
    },
    "EN": {
        "title": "⚙️ OOF2 Live: ICME Architecture",
        "subtitle": "Autonomous Mesh Generation Coupled with JARVIS-DFT (NIST)",
        "sidebar_lang": "🌐 Interface Language",
        "jarvis_toggle": "Enable NIST JARVIS-DFT Connection",
        "jarvis_input": "Search Formula (e.g., Fe4N, Ti, Al):",
        "jarvis_success": "Material Found",
        "jarvis_error": "Material not found in DFT database.",
        "sidebar_param": "Segmentation Parameters",
        "threshold": "Visual Threshold",
        "custom_e": "Original Young's Modulus (GPa)",
        "custom_m": "Damage Sensitivity Factor (m)",
        "upload": "Upload micrograph (FDM or SEM)",
        "metrics_title": "### Microstructural Integrity Diagnosis",
        "m_porosity": "Extracted Porosity",
        "m_porosity_d": "Volumetric Defect",
        "m_young": "Effective Young's Modulus",
        "m_young_d": "Stiffness Loss",
        "m_nodes": "Mesh Complexity",
        "m_nodes_d": "Generated Nodes",
        "img_raw": "**1. Raw Microstructure**",
        "img_bin": "**2. Isolated Defect Phase**",
        "img_mesh": "**3. Digital Twin (OOF2)**",
        "export_title": "### Integrated Engineering Report",
        "btn_download": "📥 Download Tensor (CSV)",
        "waiting": "Waiting for micrograph upload to initialize mapping..."
    }
}

# --- 3. SELEÇÃO DE IDIOMA ---
st.sidebar.markdown("**🌐 Idioma / Language**")
selected_lang_code = st.sidebar.selectbox(
    "",
    ["PT", "EN"],
    format_func=lambda x: {"PT": "🇵🇹 Português", "EN": "🇬🇧 English"}[x]
)
t = locales[selected_lang_code]

st.title(t["title"])
st.subheader(t["subtitle"])

# --- 4. FUNÇÃO MOCK DA API JARVIS ---
def fetch_jarvis_data(formula):
    db = {
        "Fe4N": {"K": 158.2, "G": 65.4, "nome": "Nitreto de Ferro"},
        "Ti": {"K": 108.4, "G": 43.9, "nome": "Titânio Alfa"},
        "Al": {"K": 77.3, "G": 26.1, "nome": "Alumínio CFC"}
    }
    return db.get(formula, None)

# --- 5. INTERFACE LATERAL ---
usar_jarvis = st.sidebar.checkbox(t["jarvis_toggle"], value=True)

e_base = 0.0
material_nome = "Manual"

if usar_jarvis:
    st.sidebar.markdown('<div class="api-box"><b>Status:</b> 🟢 API Ready</div>', unsafe_allow_html=True)
    formula_quimica = st.sidebar.text_input(t["jarvis_input"], "Fe4N")
    
    jarvis_data = fetch_jarvis_data(formula_quimica)
    if jarvis_data:
        K = jarvis_data["K"]
        G = jarvis_data["G"]
        e_base = (9 * K * G) / ((3 * K) + G)
        material_nome = jarvis_data["nome"]
        st.sidebar.success(f"✅ {t['jarvis_success']}: {material_nome}")
        st.sidebar.info(f"**E0:** {e_base:.2f} GPa")
    else:
        st.sidebar.error(t["jarvis_error"])
        e_base = 1.0 # Valor seguro para evitar divisão por zero
else:
    e_base = st.sidebar.number_input(t["custom_e"], min_value=0.1, value=114.0)
    material_nome = "Custom Input"

st.sidebar.markdown("---")
st.sidebar.header(t["sidebar_param"])
threshold_value = st.sidebar.slider(t["threshold"], min_value=0, max_value=255, value=120)
m_factor = st.sidebar.slider(t["custom_m"], min_value=1.0, max_value=6.0, value=2.7)

# --- 6. NÚCLEO DE PROCESSAMENTO ---
uploaded_file = st.file_uploader(t["upload"], type=["png", "jpg", "jpeg"])

if uploaded_file is not None:
    try:
        # Segurança: Usar Try/Except garante que se a imagem for corrompida a aplicação não bloqueia
        image = Image.open(uploaded_file)
        img_array = np.array(image.convert('RGB'))
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        
        _, binary = cv2.threshold(gray, threshold_value, 255, cv2.THRESH_BINARY)
        
        contours, _ = cv2.findContours(binary, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        oof2_mesh = img_array.copy()
        cv2.drawContours(oof2_mesh, contours, -1, (0, 255, 0), 2)

        total_pixels = binary.size
        solid_pixels = cv2.countNonZero(binary)
        void_pixels = total_pixels - solid_pixels
        
        porosity_fraction = void_pixels / total_pixels
        porosity_percentage = porosity_fraction * 100
        
        # Evita divisões ou potências perigosas
        porosity_fraction = min(porosity_fraction, 0.99)
        e_efetivo = e_base * ((1 - porosity_fraction) ** m_factor)
        queda_percentual = ((e_base - e_efetivo) / e_base) * 100

        # RESULTADOS VISUAIS
        st.write(t["metrics_title"])
        col_m1, col_m2, col_m3 = st.columns(3)
        col_m1.metric(label=t["m_porosity"], value=f"{porosity_percentage:.2f} %", delta=t["m_porosity_d"], delta_color="inverse")
        col_m2.metric(label=t["m_young"], value=f"{e_efetivo:.2f} GPa", delta=f"-{queda_percentual:.1f}% ({t['m_young_d']})", delta_color="inverse")
        col_m3.metric(label=t["m_nodes"], value=f"{len(contours)*4}", delta=t["m_nodes_d"], delta_color="normal")

        st.write("---")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.write(t["img_raw"])
            st.image(image, use_container_width=True)
        with col2:
            st.write(t["img_bin"])
            st.image(binary, use_container_width=True)
        with col3:
            st.write(t["img_mesh"])
            st.image(oof2_mesh, use_container_width=True)
            
        # EXPORTAÇÃO
        st.write(t["export_title"])
        df_resultados = pd.DataFrame({
            "Material": [material_nome],
            "Threshold": [threshold_value],
            "Porosity_%": [round(porosity_percentage, 2)],
            "E0_GPa": [round(e_base, 2)],
            "Effective_E_GPa": [round(e_efetivo, 3)],
            "Stiffness_Loss_%": [round(queda_percentual, 2)],
            "m_Factor": [m_factor]
        })
        st.dataframe(df_resultados, use_container_width=True)
        
        csv = df_resultados.to_csv(index=False).encode('utf-8')
        st.download_button(label=t["btn_download"], data=csv, file_name='oof2_live_export.csv', mime='text/csv')

    except Exception as e:
        st.error(f"Ocorreu um erro no processamento da imagem. Detalhe técnico: {e}")
        st.text(traceback.format_exc())
else:
    st.info(t["waiting"])
