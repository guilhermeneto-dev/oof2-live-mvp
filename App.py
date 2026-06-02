```
import streamlit as st
import cv2
import numpy as np
import pandas as pd
from PIL import Image

# --- DICIONÁRIO DE TRADUÇÕES (INTERNACIONALIZAÇÃO) ---
locales = {
    "PT": {
        "title": "⚙️ OOF2 Live: Arquitetura ICME",
        "subtitle": "Geração de Malha Autónoma e Mecânica do Dano Contínuo",
        "sidebar_lang": "🌐 Idioma da Interface",
        "sidebar_param": "1. Parâmetros de Segmentação",
        "threshold": "Limiar (Threshold) Visual",
        "sidebar_mat": "2. Seleção de Material",
        "mat_label": "Base Estrutural:",
        "custom_e": "Módulo de Young Original (GPa)",
        "custom_m": "Fator de Concentração de Tensão (m)",
        "investigator": "**Investigador:** Guilherme Fernandes Neto",
        "lab": "**Laboratório:** PPGEMec - UFSCar",
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
        "img_mesh": "**3. Malha OOF2 Acoplada**",
        "export_title": "### Relatório de Engenharia Integrada (ICME)",
        "btn_download": "📥 Descarregar Tensor de Dano (CSV)",
        "waiting": "A aguardar o upload da micrografia para inicializar o mapeamento microestrutural...",
        "materials": {
            "Ti": "Titânio Ti-6Al-4V (Aeroespacial AM)",
            "Al": "Liga de Alumínio 7075-T6 (Aviação)",
            "Fe": "Aço Nitretado (Camada Branca)",
            "PLA": "PLA (Polímero FDM)",
            "Custom": "Personalizado"
        }
    },
    "EN": {
        "title": "⚙️ OOF2 Live: ICME Architecture",
        "subtitle": "Autonomous Mesh Generation and Continuum Damage Mechanics",
        "sidebar_lang": "🌐 Interface Language",
        "sidebar_param": "1. Segmentation Parameters",
        "threshold": "Visual Threshold",
        "sidebar_mat": "2. Material Selection",
        "mat_label": "Structural Base:",
        "custom_e": "Original Young's Modulus (GPa)",
        "custom_m": "Stress Concentration Factor (m)",
        "investigator": "**Investigator:** Guilherme Fernandes Neto",
        "lab": "**Laboratory:** PPGEMec - UFSCar",
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
        "img_mesh": "**3. Coupled OOF2 Mesh**",
        "export_title": "### Integrated Engineering Report (ICME)",
        "btn_download": "📥 Download Damage Tensor (CSV)",
        "waiting": "Waiting for micrograph upload to initialize microstructural mapping...",
        "materials": {
            "Ti": "Titanium Ti-6Al-4V (Aerospace AM)",
            "Al": "Aluminum Alloy 7075-T6 (Aviation)",
            "Fe": "Nitrided Steel (White Layer)",
            "PLA": "PLA (FDM Polymer)",
            "Custom": "Custom"
        }
    },
    "FR": {
        "title": "⚙️ OOF2 Live : Architecture ICME",
        "subtitle": "Génération de Maillage Autonome et Mécanique de l'Endommagement",
        "sidebar_lang": "🌐 Langue de l'Interface",
        "sidebar_param": "1. Paramètres de Segmentation",
        "threshold": "Seuil Visuel (Threshold)",
        "sidebar_mat": "2. Sélection du Matériau",
        "mat_label": "Base Structurelle :",
        "custom_e": "Module de Young Original (GPa)",
        "custom_m": "Facteur de Concentration de Contrainte (m)",
        "investigator": "**Chercheur :** Guilherme Fernandes Neto",
        "lab": "**Laboratoire :** PPGEMec - UFSCar",
        "upload": "Télécharger la micrographie (FDM ou MEB)",
        "metrics_title": "### Diagnostic d'Intégrité Microstructurelle",
        "m_porosity": "Porosité Extraite",
        "m_porosity_d": "Défaut Volumétrique",
        "m_young": "Module de Young Effectif",
        "m_young_d": "Perte de Rigidité",
        "m_nodes": "Complexité du Maillage",
        "m_nodes_d": "Nœuds Générés",
        "img_raw": "**1. Microstructure Brute**",
        "img_bin": "**2. Phase de Défaut Isolée**",
        "img_mesh": "**3. Maillage OOF2 Couplé**",
        "export_title": "### Rapport d'Ingénierie Intégré (ICME)",
        "btn_download": "📥 Télécharger le Tenseur d'Endommagement (CSV)",
        "waiting": "En attente du téléchargement de la micrographie pour initialiser la cartographie...",
        "materials": {
            "Ti": "Titane Ti-6Al-4V (Aérospatiale FA)",
            "Al": "Alliage d'Aluminium 7075-T6 (Aviation)",
            "Fe": "Acier Nitruré (Couche Blanche)",
            "PLA": "PLA (Polymère FDM)",
            "Custom": "Personnalisé"
        }
    },
    "IT": {
        "title": "⚙️ OOF2 Live: Architettura ICME",
        "subtitle": "Generazione Autonoma di Mesh e Meccanica del Danno Continuo",
        "sidebar_lang": "🌐 Lingua dell'Interfaccia",
        "sidebar_param": "1. Parametri di Segmentazione",
        "threshold": "Soglia Visiva (Threshold)",
        "sidebar_mat": "2. Selezione del Materiale",
        "mat_label": "Base Strutturale:",
        "custom_e": "Modulo di Young Originale (GPa)",
        "custom_m": "Fattore di Concentrazione delle Tensioni (m)",
        "investigator": "**Ricercatore:** Guilherme Fernandes Neto",
        "lab": "**Laboratorio:** PPGEMec - UFSCar",
        "upload": "Carica la micrografia (FDM o SEM)",
        "metrics_title": "### Diagnosi di Integrità Microstrutturale",
        "m_porosity": "Porosità Estratta",
        "m_porosity_d": "Difetto Volumetrico",
        "m_young": "Modulo di Young Effettivo",
        "m_young_d": "Perdita di Rigidità",
        "m_nodes": "Complessità della Mesh",
        "m_nodes_d": "Nodi Generati",
        "img_raw": "**1. Microstruttura Grezza**",
        "img_bin": "**2. Fase di Difetto Isolata**",
        "img_mesh": "**3. Mesh OOF2 Accoppiata**",
        "export_title": "### Rapporto di Ingegneria Integrata (ICME)",
        "btn_download": "📥 Scarica Tensore di Danno (CSV)",
        "waiting": "In attesa del caricamento della micrografia per inizializzare la mappatura...",
        "materials": {
            "Ti": "Titanio Ti-6Al-4V (Aerospaziale AM)",
            "Al": "Lega di Alluminio 7075-T6 (Aviazione)",
            "Fe": "Acciaio Nitrurato (Coltre Bianca)",
            "PLA": "PLA (Polimero FDM)",
            "Custom": "Personalizzato"
        }
    },
    "DE": {
        "title": "⚙️ OOF2 Live: ICME-Architektur",
        "subtitle": "Autonome Netzgenerierung und Kontinuums-Schädigungsmechanik",
        "sidebar_lang": "🌐 Oberflächensprache",
        "sidebar_param": "1. Segmentierungsparameter",
        "threshold": "Visueller Schwellenwert",
        "sidebar_mat": "2. Materialauswahl",
        "mat_label": "Strukturelle Basis:",
        "custom_e": "Ursprüngliches Elastizitätsmodul (GPa)",
        "custom_m": "Spannungskonzentrationsfaktor (m)",
        "investigator": "**Forscher:** Guilherme Fernandes Neto",
        "lab": "**Labor:** PPGEMec - UFSCar",
        "upload": "Mikroaufnahme hochladen (FDM oder REM)",
        "metrics_title": "### Diagnose der mikrostrukturellen Integrität",
        "m_porosity": "Extrahierte Porosität",
        "m_porosity_d": "Volumetrischer Defekt",
        "m_young": "Effektives Elastizitätsmodul",
        "m_young_d": "Steifigkeitsverlust",
        "m_nodes": "Netzkomplexität",
        "m_nodes_d": "Generierte Knoten",
        "img_raw": "**1. Rohe Mikrostruktur**",
        "img_bin": "**2. Isolierte Defektphase**",
        "img_mesh": "**3. Gekoppeltes OOF2-Netz**",
        "export_title": "### Integrierter Engineering-Bericht (ICME)",
        "btn_download": "📥 Schadens-Tensor herunterladen (CSV)",
        "waiting": "Warten auf den Upload der Mikroaufnahme zur Initialisierung der Kartierung...",
        "materials": {
            "Ti": "Titan Ti-6Al-4V (Luft- und Raumfahrt AM)",
            "Al": "Aluminiumlegierung 7075-T6 (Luftfahrt)",
            "Fe": "Nitrierter Stahl (Weiße Schicht)",
            "PLA": "PLA (FDM-Polymer)",
            "Custom": "Benutzerdefiniert"
        }
    }
}

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="OOF2 Live", layout="wide")

st.markdown("""
    <style>
    .main {background-color: #f8f9fa;}
    h1 {color: #0a2240;}
    </style>
""", unsafe_allow_html=True)

# --- SELEÇÃO DE IDIOMA ---
st.sidebar.markdown(f"**{locales['PT']['sidebar_lang']}**")
selected_lang_code = st.sidebar.selectbox(
    "",
    ["PT", "EN", "FR", "IT", "DE"],
    format_func=lambda x: {"PT": "🇵🇹 Português", "EN": "🇬🇧 English", "FR": "🇫🇷 Français", "IT": "🇮🇹 Italiano", "DE": "🇩🇪 Deutsch"}[x]
)

# Carrega o dicionário do idioma selecionado
t = locales[selected_lang_code]

st.title(t["title"])
st.subheader(t["subtitle"])

# --- BANCO DE DADOS DE MATERIAIS ---
# Usamos chaves internas em inglês e exibimos traduzidas
base_materiais = {
    "Ti": {"E": 114.0, "m": 2.7}, 
    "Al": {"E": 71.7, "m": 1.5},
    "Fe": {"E": 200.0, "m": 3.5},
    "PLA": {"E": 3.5, "m": 2.0},
    "Custom": {"E": 0.0, "m": 1.0}
}

# --- BARRA LATERAL ---
st.sidebar.header(t["sidebar_param"])
threshold_value = st.sidebar.slider(t["threshold"], min_value=0, max_value=255, value=120)

st.sidebar.markdown("---")
st.sidebar.header(t["sidebar_mat"])

# Cria uma lista de materiais traduzida para o selectbox
opcoes_mat = list(base_materiais.keys())
nomes_exibicao = [t["materials"][k] for k in opcoes_mat]
material_selecionado = st.sidebar.selectbox(t["mat_label"], opcoes_mat, format_func=lambda x: t["materials"][x])

if material_selecionado == "Custom":
    e_base = st.sidebar.number_input(t["custom_e"], min_value=0.1, value=1.0)
    m_factor = st.sidebar.slider(t["custom_m"], min_value=1.0, max_value=6.0, value=2.0)
else:
    e_base = base_materiais[material_selecionado]["E"]
    m_factor = base_materiais[material_selecionado]["m"]
    st.sidebar.info(f"**E0:** {e_base} GPa | **m:** {m_factor}")

st.sidebar.markdown("---")
st.sidebar.write(t["investigator"])
st.sidebar.write(t["lab"])

# --- UPLOAD DA IMAGEM ---
uploaded_file = st.file_uploader(t["upload"], type=["png", "jpg", "jpeg"])

if uploaded_file is not None:
    # Processamento de Imagem
    image = Image.open(uploaded_file)
    img_array = np.array(image.convert('RGB'))
    gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
    
    # Binarização
    _, binary = cv2.threshold(gray, threshold_value, 255, cv2.THRESH_BINARY)
    
    # Geração do Gêmeo Digital
    contours, _ = cv2.findContours(binary, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    oof2_mesh = img_array.copy()
    cv2.drawContours(oof2_mesh, contours, -1, (0, 255, 0), 2)

    # Cálculo Analítico
    total_pixels = binary.size
    solid_pixels = cv2.countNonZero(binary)
    void_pixels = total_pixels - solid_pixels
    
    porosity_fraction = void_pixels / total_pixels
    porosity_percentage = porosity_fraction * 100
    
    # Modelo de Degradação
    e_efetivo = e_base * ((1 - porosity_fraction) ** m_factor)
    queda_percentual = ((e_base - e_efetivo) / e_base) * 100

    # --- VISUALIZAÇÃO DOS RESULTADOS ---
    st.write(t["metrics_title"])
    col_m1, col_m2, col_m3 = st.columns(3)
    col_m1.metric(label=t["m_porosity"], value=f"{porosity_percentage:.2f} %", delta=t["m_porosity_d"], delta_color="inverse")
    col_m2.metric(label=t["m_young"], value=f"{e_efetivo:.2f} GPa", delta=f"- {queda_percentual:.1f}% ({t['m_young_d']})", delta_color="inverse")
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
        
    # --- MÓDULO DE EXPORTAÇÃO ---
    st.write(t["export_title"])
    
    df_resultados = pd.DataFrame({
        "Material": [t["materials"][material_selecionado]],
        "Threshold": [threshold_value],
        "Porosity_%": [round(porosity_percentage, 2)],
        "E0_GPa": [e_base],
        "Effective_E_GPa": [round(e_efetivo, 3)],
        "Stiffness_Loss_%": [round(queda_percentual, 2)],
        "m_Factor": [m_factor],
        "Mesh_Nodes": [len(contours)*4]
    })
    
    st.dataframe(df_resultados, use_container_width=True)
    
    csv = df_resultados.to_csv(index=False).encode('utf-8')
    st.download_button(
        label=t["btn_download"],
        data=csv,
        file_name='oof2_live_export.csv',
        mime='text/csv',
    )
    
else:
    st.info(t["waiting"])

```
