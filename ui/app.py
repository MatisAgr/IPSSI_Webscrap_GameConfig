import streamlit as st
import os
import sys
import json
import glob
import time
from pathlib import Path

# Ajouter le chemin parent pour importer les scrapers
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from scrapers.instant_gaming import InstantGaming
from scrapers.pcpartpicker import PCPartPickerScraper, PCConfiguration

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
    .config-builder-container {
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
    
    .config-details-container {
        background-color: #2D2D2D;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.2);
    }
    
    .component-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
        gap: 16px;
        margin-top: 20px;
    }
    
    .component-card {
        background-color: #1E1E1E;
        border-radius: 10px;
        padding: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        display: flex;
        flex-direction: column;
        transition: transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out;
    }
    
    .component-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 15px rgba(0, 0, 0, 0.2);
    }
    
    .component-card img {
        width: 100%;
        height: 150px;
        object-fit: contain;
        background-color: #2D2D2D;
        border-radius: 8px;
        margin-bottom: 10px;
        padding: 10px;
    }
    
    .component-header {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        margin-bottom: 8px;
    }
    
    .component-name {
        font-weight: bold;
        font-size: 1.1rem;
        margin-right: 8px;
        flex: 3;
    }
    
    .component-price {
        font-weight: bold;
        color: #4CAF50;
        flex: 1;
        text-align: right;
    }
    
    .component-details {
        margin-top: 8px;
        font-size: 0.9rem;
        color: #AAA;
        flex-grow: 1;
    }
    
    .component-category {
        background-color: #FF4B4B;
        color: white;
        padding: 3px 8px;
        border-radius: 4px;
        font-size: 0.8rem;
        display: inline-block;
        margin-bottom: 8px;
    }
    
    .buy-button {
        display: inline-block;
        background-color: #4CAF50;
        color: white;
        padding: 8px 12px;
        border-radius: 4px;
        text-decoration: none;
        margin-top: 10px;
        text-align: center;
        transition: background-color 0.2s;
    }
    
    .buy-button:hover {
        background-color: #45a049;
    }
    
    .config-summary {
        background-color: #1E1E1E;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 15px;
    }
    
    .section-divider {
        margin: 30px 0;
        border-top: 1px solid #444;
    }
    
    .alternatives-title {
        margin-top: 30px;
        margin-bottom: 20px;
        color: #FF4B4B;
    }

    .game-details-container {
        background-color: #1E1E1E;
        border-radius: 10px;
        padding: 1.5rem;
        margin-top: 2rem;
        margin-bottom: 2rem;
    }

    .game-header {
        display: flex;
        align-items: center;
        margin-bottom: 1.5rem;
    }

    .game-header img {
        width: 150px; /* Ajustez la taille selon vos besoins */
        height: auto;
        border-radius: 8px;
        margin-right: 1.5rem;
        object-fit: cover;
    }

    .game-title-price {
        flex-grow: 1;
    }

    .game-title-price h3 {
        color: #FF4B4B;
        margin-bottom: 0.5rem;
    }

    .game-price {
        font-size: 1.3rem;
        color: #4CAF50;
        font-weight: bold;
    }

    .specs-columns {
        display: flex;
        gap: 2rem;
    }

    .specs-column {
        flex: 1;
        background-color: #2D2D2D;
        padding: 1rem;
        border-radius: 8px;
    }

    .specs-column h4 {
        color: #FF4B4B;
        border-bottom: 2px solid #FF4B4B;
        padding-bottom: 0.5rem;
        margin-bottom: 1rem;
    }

    .specs-column p {
        margin-bottom: 0.5rem;
        line-height: 1.6;
    }
    .specs-column strong {
        color: #FFFFFF;
    }
    .specs-column span {
        color: #CCCCCC;
    }


</style>
""", unsafe_allow_html=True)


# Titre de l'application
st.markdown('<div class="main-title">🎮 GameConfig Hub</div>', unsafe_allow_html=True)

# Description
st.markdown('<div class="description">Trouvez vos jeux préférés et les configurations PC recommandées</div>', unsafe_allow_html=True)

# Section de création de configuration PC pour un jeu
st.markdown("## 🔨 Créer une Configuration PC")
st.write("Créez une configuration PC compatible avec votre jeu préféré")

# Formulaire pour la création de configuration
with st.form(key="config_form"):
    game_name = st.text_input("Nom du jeu", placeholder="Ex: Cyberpunk 2077")
    
    col1, col2 = st.columns(2)
    
    with col1:
        config_type = st.radio(
            "Type de configuration",
            ["Minimale", "Recommandée"],
            index=1
        )
    
    with col2:
        include_alternatives = st.checkbox("Inclure les composants alternatifs", value=True)
        headless_mode = st.checkbox("Mode sans interface (plus rapide)", value=False)
    
    submit_config = st.form_submit_button("Générer ma configuration PC")

    if submit_config and game_name:
            # Créer un emplacement pour le statut que nous pourrons mettre à jour
            status_placeholder = st.empty()
            
            # Afficher un message de chargement
            status_placeholder.info(f"⏳ Recherche de '{game_name}' sur Instant Gaming...")
            
            # Utiliser le scraper Instant Gaming pour récupérer les données du jeu
            ig_scraper = InstantGaming(headless=headless_mode, game_name=game_name)
            
            if not ig_scraper.access_site():
                status_placeholder.error("Impossible d'accéder au site Instant Gaming.")
            else:
                success = True
                
                if not ig_scraper.accept_cookies():
                    st.warning("Problème avec l'acceptation des cookies, mais on continue...")
                
                if not ig_scraper.search_game():
                    status_placeholder.error("Impossible de rechercher le jeu.")
                    success = False
                    
                if success and not ig_scraper.click_first_result():
                    status_placeholder.error("Impossible de sélectionner le jeu.")
                    success = False
                    
                if success:
                    game_data = ig_scraper.extract_system_requirements()
                    ig_scraper.quit()
                    
                    # Remplacer le message de chargement par un message de succès
                    status_placeholder.success(f"✅ Recherche de '{game_name}' terminée avec succès!")
                    
                    if not game_data:
                        st.error("Impossible d'extraire les spécifications du jeu.")
                    else:
                        # Récupérer le chemin du fichier JSON
                        project_root = Path(parent_dir)
                        data_folder = os.path.join(project_root, "data", "instantgaming")
                        
                        # Trouver le fichier le plus récent pour ce jeu
                        json_files = [f for f in os.listdir(data_folder) if f.endswith('.json') and game_data["game"].replace(":", "").replace(" ", "_").replace("/", "_").lower() in f.lower()]
                        if json_files:
                            json_path = os.path.join(data_folder, sorted(json_files)[-1])  # Prendre le plus récent
                            
                            # Créer un nouvel emplacement pour le statut de la génération de configuration
                            config_status = st.empty()
                            config_status.info("⏳ Création de la configuration PC en cours...")
                            
                            pp_scraper = PCPartPickerScraper()
                            
                            use_recommended = config_type == "Recommandée"
                            
                            try:
                                if use_recommended:
                                    pc_config = pp_scraper.create_recommended_configuration(
                                        json_path, 
                                        include_alternatives=include_alternatives
                                    )
                                else:
                                    pc_config = pp_scraper.create_minimal_configuration(
                                        json_path, 
                                        include_alternatives=include_alternatives
                                    )
                                
                                # Fermer le navigateur
                                pp_scraper.close()
                                
                                # Remplacer le message de chargement par un message de succès
                                config_status.success(f"✅ Configuration PC {config_type.lower()} créée avec succès!")
                                
                                # Sauvegarder la configuration
                                data_dir = os.path.join(project_root, "data", "pcpartpicker")
                                os.makedirs(data_dir, exist_ok=True)
                                
                                config_type_abbrev = "rec" if use_recommended else "min"
                                alt_suffix = "_avec_alternatives" if include_alternatives else ""
                                
                                game_name_sanitized = game_data["game"].replace(":", "").replace(" ", "_").replace("/", "_").lower()
                                json_config_path = os.path.join(data_dir, f"{game_name_sanitized}_{config_type_abbrev}{alt_suffix}_{pc_config.game_uuid}.json")
                                
                                pc_config.save_to_json(json_config_path)
                                
                                # Afficher les détails de la configuration avec un design amélioré
                                st.markdown(f"<h3>Détails de la configuration</h3>", unsafe_allow_html=True)
                                
                                # Utiliser un conteneur Streamlit pour les informations générales
                                with st.container():
                                    st.markdown(f"""
                                    <div class="config-details-container">
                                        <h4>{pc_config.name}</h4>
                                        <div class="config-summary">
                                            <p>Prix total: <span class="config-price">{pc_config.get_total_price()}</span></p>
                                            <p>Configuration {config_type.lower()} pour {game_data['game']}</p>
                                        </div>
                                    </div>
                                    """, unsafe_allow_html=True)
                                    
                                    # Déterminer le nombre de colonnes (3 colonnes par défaut)
                                    num_components = len(pc_config.components)
                                    num_cols = min(3, max(1, num_components))  # Au moins 1, au plus 3 colonnes
                                    
                                    # Créer des colonnes Streamlit au lieu d'une grille HTML
                                    cols = st.columns(num_cols)
                                    
                                    # Distribuer les composants dans les colonnes
                                    for i, (category, component) in enumerate(pc_config.components.items()):
                                        col_idx = i % num_cols  # Distribution circulaire
                                        
                                        with cols[col_idx]:
                                            name = component.get('name', 'N/A')
                                            price = component.get('price', 'N/A')
                                            image_url = component.get('image_url', '')
                                            merchant = component.get('merchant', 'N/A')
                                            buy_link = component.get('buy_link', '')
                                            
                                            # Image placeholder si pas d'image disponible
                                            if not image_url:
                                                image_url = "https://www.svgrepo.com/show/508699/landscape-placeholder.svg"
                                            
                                            # Utiliser un conteneur avec bordure pour créer une "carte"
                                            with st.container(border=True):
                                                # Catégorie
                                                st.markdown(f"<div class='component-category'>{category}</div>", unsafe_allow_html=True)
                                                
                                                # Image
                                                st.image(image_url, use_column_width=True)
                                                
                                                # Nom et prix
                                                st.markdown(f"**{name}**")
                                                st.markdown(f"<span class='component-price'>Prix: {price}</span>", unsafe_allow_html=True)
                                                
                                                # Détails supplémentaires
                                                st.markdown(f"Fournisseur: {merchant}")
                                                
                                                # Bouton d'achat
                                                if buy_link and price != "N/A":
                                                    st.markdown(f"<a href='{buy_link}' target='_blank' class='buy-button'>Acheter</a>", unsafe_allow_html=True)
                                
                                # Afficher les composants alternatifs si demandé
                                if include_alternatives and pc_config.alternative_components:
                                    st.markdown('<h3 class="alternatives-title">Composants alternatifs</h3>', unsafe_allow_html=True)
                                    
                                    for category, alternatives in pc_config.alternative_components.items():
                                        st.markdown(f"<h4>Alternatives pour {category}</h4>", unsafe_allow_html=True)
                                        
                                        # Déterminer le nombre de colonnes pour les alternatives
                                        num_alts = len(alternatives)
                                        num_alt_cols = min(3, max(1, num_alts))
                                        
                                        # Créer des colonnes pour les alternatives
                                        alt_cols = st.columns(num_alt_cols)
                                        
                                        # Distribuer les alternatives dans les colonnes
                                        for i, alt in enumerate(alternatives):
                                            alt_col_idx = i % num_alt_cols
                                            
                                            with alt_cols[alt_col_idx]:
                                                name = alt.get('name', 'N/A')
                                                price = alt.get('price', 'N/A')
                                                image_url = alt.get('image_url', '')
                                                merchant = alt.get('merchant', 'N/A')
                                                buy_link = alt.get('buy_link', '')
                                                
                                                # Image placeholder si pas d'image disponible
                                                if not image_url:
                                                    image_url = "https://www.svgrepo.com/show/508699/landscape-placeholder.svg"
                                                
                                                # Utiliser un conteneur avec bordure
                                                with st.container(border=True):
                                                    # Catégorie
                                                    st.markdown(f"<div class='component-category'>{category} (Alternative)</div>", unsafe_allow_html=True)
                                                    
                                                    # Image
                                                    st.image(image_url, use_column_width=True)
                                                    
                                                    # Nom et prix
                                                    st.markdown(f"**{name}**")
                                                    st.markdown(f"<span class='component-price'>Prix: {price}</span>", unsafe_allow_html=True)
                                                    
                                                    # Détails supplémentaires
                                                    st.markdown(f"Fournisseur: {merchant}")
                                                    
                                                    # Bouton d'achat
                                                    if buy_link and price != "N/A":
                                                        st.markdown(f"<a href='{buy_link}' target='_blank' class='buy-button'>Acheter</a>", unsafe_allow_html=True)
                                
                            except Exception as e:
                                st.error(f"Erreur lors de la création de la configuration PC: {str(e)}")
                        else:
                            st.error("Impossible de trouver les données du jeu.")
            ig_scraper.quit()