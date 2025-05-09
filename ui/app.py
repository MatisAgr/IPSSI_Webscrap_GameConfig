import streamlit as st
import os
import sys
import json
import glob

# Configuration de la page
st.set_page_config(
    page_title="GameConfig - Accueil",
    page_icon="🎮",
    layout="wide",
)

# Style CSS personnalisé
st.markdown("""
<style>
    .main-title {
        font-size: 3rem;
        font-weight: bold;
        color: #FF4B4B;
        text-align: center;
        margin-bottom: 1.5rem;
    }
    .description {
        font-size: 1.2rem;
        text-align: center;
        margin-bottom: 2rem;
    }
    .search-container {
        background-color: #1E1E1E;
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
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
</style>
""", unsafe_allow_html=True)

# Titre de l'application
st.markdown('<div class="main-title">🎮 GameConfig Hub</div>', unsafe_allow_html=True)

# Description
st.markdown('<div class="description">Trouvez vos jeux préférés et les configurations PC recommandées</div>', unsafe_allow_html=True)

# Barre de recherche directe
st.markdown('<div class="search-container">', unsafe_allow_html=True)
col1, col2 = st.columns([4, 1])
with col1:
    search_query = st.text_input("Rechercher un jeu sur InstantGaming", placeholder="Entrez le nom d'un jeu...", label_visibility="collapsed")
with col2:
    search_button = st.button("Rechercher", use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

# Traitement de la recherche
if search_button and search_query:
    # Stocker la requête dans la session state
    st.session_state.search_query = search_query
    # Rediriger vers la page de recherche
    st.switch_page("pages/recherche_jeux.py")

# Section des configurations historiques
st.markdown("## 💾 Historique des configurations")

# Chemin vers le dossier data contenant les fichiers JSON
data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")

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
                    with col_btn2:
                        if st.button(f"Mettre à jour", key=f"update_{i}"):
                            # Stocker la configuration à mettre à jour et rediriger
                            st.session_state.config_to_update = {
                                'filepath': config['filepath'],
                                'data': config['data']
                            }
                            st.switch_page("pages/configurations.py")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #888;">
    <p>Les données sont collectées depuis InstantGaming et PCPartPicker</p>
</div>
""", unsafe_allow_html=True)