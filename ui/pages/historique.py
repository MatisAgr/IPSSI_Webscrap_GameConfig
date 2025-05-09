import streamlit as st
import os
import sys
import json
import glob
from pathlib import Path

# Ajouter le chemin parent pour importer les modules nécessaires
parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(parent_dir)

# Configuration de la page
st.set_page_config(
    page_title="GameConfig - Historique des configurations",
    page_icon="🎮",
    layout="wide",
)

# Style CSS personnalisé
st.markdown("""
<style>
    .main-title {
        font-size: 2.5rem;
        font-weight: bold;
        color: #FF4B4B;
        margin-bottom: 1.5rem;
    }
    .config-card {
        background-color: #1E1E1E;
        border-radius: 10px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        transition: transform 0.2s;
    }
    .config-card:hover {
        transform: scale(1.02);
    }
    .config-title {
        font-size: 1.3rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    .config-price {
        font-size: 1.2rem;
        color: #4CAF50;
        font-weight: bold;
    }
    .component-row {
        padding: 5px 0;
        border-bottom: 1px solid #333;
    }
    .section-divider {
        margin: 30px 0;
        border-top: 1px solid #444;
    }
</style>
""", unsafe_allow_html=True)

# Titre de la page
st.markdown('<div class="main-title">💾 Historique des configurations</div>', unsafe_allow_html=True)

# Chemin vers le dossier data contenant les fichiers JSON
data_dir = os.path.join(parent_dir, "data", "pcpartpicker")

# Vérifier si le dossier existe
if not os.path.exists(data_dir):
    st.warning(f"Aucun dossier de données trouvé à l'emplacement : {data_dir}")
    st.info("Les configurations sauvegardées apparaîtront ici après leur création.")
else:
    # Rechercher tous les fichiers JSON dans le dossier data
    json_files = glob.glob(os.path.join(data_dir, "*.json"))
    
    if not json_files:
        st.info("Aucune configuration sauvegardée pour le moment. Les configurations que vous créerez apparaîtront ici.")
    else:
        # Afficher les configurations sauvegardées
        configs = []
        for json_file in json_files:
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                    configs.append({
                        'filename': os.path.basename(json_file),
                        'filepath': json_file,
                        'data': config_data
                    })
            except Exception as e:
                st.error(f"Erreur lors du chargement de {json_file}: {e}")
        
        # Diviser en deux colonnes pour afficher plus de configurations
        col1, col2 = st.columns(2)
        
        # Répartir les configurations entre les deux colonnes
        for i, config in enumerate(configs):
            # Alterner entre les deux colonnes
            with col1 if i % 2 == 0 else col2:
                with st.container():
                    st.markdown(f"""
                    <div class="config-card">
                        <div class="config-title">{config['data'].get('name', 'Configuration sans nom')}</div>
                        <div class="config-price">{config['data'].get('total_price', 'Prix non disponible')}</div>
                        <p>Composants: {len(config['data'].get('components', {}))} éléments</p>
                    """, unsafe_allow_html=True)
                    
                    # Afficher quelques composants clés (max 3)
                    key_components = ['CPU', 'GPU', 'RAM']
                    components = config['data'].get('components', {})
                    
                    for key in key_components:
                        if key in components:
                            component = components[key]
                            name = component.get('name', 'N/A')
                            price = component.get('price', 'N/A')
                            st.markdown(f"""
                            <div class="component-row">
                                <strong>{key}:</strong> {name} - {price}
                            </div>
                            """, unsafe_allow_html=True)
                    
                    st.markdown("</div>", unsafe_allow_html=True)
                    
                    # Boutons d'action
                    col_btn1, col_btn2 = st.columns(2)
                    with col_btn1:
                        if st.button(f"Voir détails", key=f"view_{i}"):
                            # Stocker la configuration sélectionnée et rediriger
                            st.session_state.selected_config = config['data']
                            st.switch_page("pages/detail_config.py")

# Bouton pour retourner à la page d'accueil
if st.button("Retour à l'accueil"):
    st.switch_page("app.py")