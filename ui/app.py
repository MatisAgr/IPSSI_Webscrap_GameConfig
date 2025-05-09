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

# Style CSS personnalisé (chargé depuis un fichier externe)
def load_css(css_file):
    with open(css_file, 'r') as f:
        return f'<style>{f.read()}</style>'

# Chemin vers le fichier CSS
css_path = os.path.join(os.path.dirname(__file__), "styles", "style.css")
# Chargement du CSS
st.markdown(load_css(css_path), unsafe_allow_html=True)


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
        headless_mode = st.checkbox("Mode sans interface", value=False)
    
    submit_config = st.form_submit_button("Générer ma configuration PC")

    if submit_config and game_name:
        # Phase 1: Recherche du jeu sur Instant Gaming
        status_placeholder = st.empty()
        game_data = None
        success = False
        
        # Premier spinner pour la recherche du jeu
        with st.spinner(f"Recherche de '{game_name}' sur Instant Gaming..."):
            try:
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
                
                # Fermer le navigateur à la fin de cette phase
                ig_scraper.quit()
                
            except Exception as e:
                st.error(f"Une erreur s'est produite lors de la recherche du jeu: {str(e)}")
                if 'ig_scraper' in locals():
                    ig_scraper.quit()
        
        # Affichage du résultat de la première phase
        if success and game_data:
            status_placeholder.success(f"✅ Recherche de '{game_name}' terminée avec succès!")
            
            # Phase 2: Création de la configuration PC
            # Récupérer le chemin du fichier JSON
            project_root = Path(parent_dir)
            data_folder = os.path.join(project_root, "data", "instantgaming")
            
            # Trouver le fichier le plus récent pour ce jeu
            json_files = [f for f in os.listdir(data_folder) if f.endswith('.json') and game_data["game"].replace(":", "").replace(" ", "_").replace("/", "_").lower() in f.lower()]
            
            if json_files:
                json_path = os.path.join(data_folder, sorted(json_files)[-1])  # Prendre le plus récent
                
                # Deuxième spinner pour la génération de configuration
                config_status = st.empty()
                
                # Ce spinner est séparé du premier (pas imbriqué)
                with st.spinner("Création de la configuration PC en cours..."):
                    try:
                        pp_scraper = PCPartPickerScraper()
                        use_recommended = config_type == "Recommandée"
                    
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
                        
                        # Fermer le navigateur de PCPartPicker
                        pp_scraper.close()
                        
                        # Message de succès pour la génération de configuration
                        config_status.success(f"✅ Configuration PC {config_type.lower()} créée avec succès!")
                        
                        # Sauvegarder la configuration
                        data_dir = os.path.join(project_root, "data", "pcpartpicker")
                        os.makedirs(data_dir, exist_ok=True)
                        
                        config_type_abbrev = "rec" if use_recommended else "min"
                        alt_suffix = "_avec_alternatives" if include_alternatives else ""
                        
                        game_name_sanitized = game_data["game"].replace(":", "").replace(" ", "_").replace("/", "_").lower()
                        json_config_path = os.path.join(data_dir, f"{game_name_sanitized}_{config_type_abbrev}{alt_suffix}_{pc_config.game_uuid}.json")
                        
                        pc_config.save_to_json(json_config_path)
                        
                        # Phase 3: Affichage des résultats (en dehors du spinner)
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
                                        st.image(image_url, use_container_width=True)
                                        
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
                                            st.image(image_url, use_container_width=True)
                                            
                                            # Nom et prix
                                            st.markdown(f"**{name}**")
                                            st.markdown(f"<span class='component-price'>Prix: {price}</span>", unsafe_allow_html=True)
                                            
                                            # Détails supplémentaires
                                            st.markdown(f"Fournisseur: {merchant}")
                                            
                                            # Bouton d'achat
                                            if buy_link and price != "N/A":
                                                st.markdown(f"<a href='{buy_link}' target='_blank' class='buy-button'>Acheter</a>", unsafe_allow_html=True)
                    
                    except Exception as e:
                        config_status.error(f"Erreur lors de la création de la configuration PC: {str(e)}")
                        if 'pp_scraper' in locals():
                            pp_scraper.close()
            else:
                st.error("Impossible de trouver les données du jeu.")
        elif not success:
            st.error("La recherche du jeu a échoué.")
        elif not game_data:
            st.error("Impossible d'extraire les spécifications du jeu.")