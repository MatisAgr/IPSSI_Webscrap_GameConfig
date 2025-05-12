import streamlit as st
import os
import sys
from pathlib import Path
import base64

# Ajouter le chemin parent pour importer les modules nécessaires
parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(parent_dir)

# Configuration de la page
st.set_page_config(
    page_title="GameConfig - Détails de configuration",
    page_icon="🎮",
    layout="wide",
)

# Style CSS minimal (seulement pour des classes génériques)
st.markdown("""
<style>
    /* Style général */
    .section-header {
        color: #333;
        border-left: 5px solid #FF4B4B;
        padding-left: 10px;
        margin: 30px 0 20px 0;
    }
    
    /* Style pour le bouton d'achat */
    .buy-button {
        display: inline-block;
        background-color: #4CAF50;
        color: white !important;
        padding: 8px 12px;
        border-radius: 5px;
        text-decoration: none;
        text-align: center;
        font-weight: bold;
        width: 100%;
        margin-top: 10px; /* Espace au-dessus du bouton */
    }
    
    /* Style pour la catégorie */
    .category-badge {
        background-color: #FF4B4B;
        color: white;
        padding: 5px 10px;
        border-radius: 5px;
        font-weight: bold;
        display: inline-block;
        margin-bottom: 10px;
    }
    
    /* Prix en vert */
    .price-value {
        color: #4CAF50;
        font-weight: bold;
    }

    /* Style pour les images des composants dans les cartes */
    /* Cible les images à l'intérieur des conteneurs bordés (cartes) */
    div[data-testid="stVerticalBlockBorderWrapper"] img {
        max-height: 160px;      /* Hauteur maximale pour l'image */
        object-fit: contain;    /* Assure que l'image entière est visible et conserve son ratio */
        border-radius: 4px;     /* Coins arrondis pour l'image */
        margin-bottom: 10px;    /* Espace sous l'image */
        display: block;         /* Permet l'utilisation de margin auto pour le centrage */
        margin-left: auto;
        margin-right: auto;
    }

</style>
""", unsafe_allow_html=True)



# Vérifier si une configuration est sélectionnée
if 'selected_config' not in st.session_state:
    st.error("Aucune configuration sélectionnée. Veuillez aller à la page historique.")
    
    if st.button("Historique"):
        st.switch_page("historique.py")
else:
    # Récupérer la configuration sélectionnée
    config = st.session_state.selected_config
    
    # Titre de la page avec style personnalisé
    st.title(f"Détails de la configuration")
    
    # Container pour les informations générales
    with st.container():
        # En-tête avec le nom de la configuration
        st.header(config.get('name', 'Configuration sans nom'))
        
        # Informations générales dans une zone colorée
        with st.expander("Résumé de la configuration", expanded=True):
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**Prix total:**")
                st.markdown("**Jeu:**")
                st.markdown("**Type:**")
                st.markdown("**Date de création:**")
            
            with col2:
                st.markdown(f"<span class='price-value'>{config.get('total_price', 'Non disponible')}</span>", unsafe_allow_html=True)
                st.markdown(f"{config.get('game_name', 'Non spécifié')}")
                config_type = 'Configuration recommandée' if config.get('is_recommended', True) else 'Configuration minimale'
                st.markdown(config_type)
                st.markdown(f"{config.get('created_at', 'Non disponible')}")
    
    # Séparateur
    st.divider()
    
    # Section des composants principaux
    st.markdown('<h3 class="section-header">Composants principaux</h3>', unsafe_allow_html=True)
    
    # Afficher tous les composants dans une grille avec des colonnes Streamlit
    components = config.get('components', {})
    
    # Placeholder image pour les composants sans image
    placeholder_img = "https://www.svgrepo.com/show/508699/landscape-placeholder.svg"
    
    # Calculer le nombre de colonnes (max 3)
    num_cols = min(3, len(components))
    if num_cols == 0:
        num_cols = 1
    
    # Créer les colonnes
    cols = st.columns(num_cols, gap="medium") # Ajout de gap
    
    # Afficher chaque composant
    for i, (category, component) in enumerate(components.items()):
        col_index = i % num_cols
        name = component.get('name', 'N/A')
        price = component.get('price', 'N/A')
        merchant = component.get('merchant', 'N/A')
        image_url = component.get('image_url', '')
        buy_link = component.get('buy_link', '')
        
        # Utiliser l'image placeholder si aucune image n'est disponible
        if not image_url:
            image_url = placeholder_img
        
        # Afficher le composant dans la bonne colonne avec des composants Streamlit natifs
        with cols[col_index]:
            # Utiliser st.container(border=True) pour créer une carte
            with st.container(border=True):
                # Badge de catégorie
                st.markdown(f"<div class='category-badge'>{category}</div>", unsafe_allow_html=True)
                
                # Image du composant
                st.image(image_url, caption=None, use_container_width='auto') # Ajustement de l'image
                
                # Nom du composant
                st.markdown(f"**{name}**")
                
                # Prix du composant
                st.markdown(f"<span class='price-value'>Prix: {price}</span>", unsafe_allow_html=True)
                
                # Fournisseur
                st.markdown(f"Fournisseur: {merchant}")
                
                # Bouton d'achat s'il est disponible
                if buy_link and price != "N/A":
                    st.markdown(f"<a href='{buy_link}' target='_blank' class='buy-button'>Acheter</a>", unsafe_allow_html=True)
                
                # Espace entre les cartes
                st.write("")
    
    # Séparateur
    st.divider()
    
    
    # Afficher les composants alternatifs s'il y en a
    alternative_components = config.get('alternative_components', {})
    if alternative_components:
        st.markdown('<h3 class="section-header">Composants alternatifs</h3>', unsafe_allow_html=True)
        
        # Pour chaque catégorie avec alternatives
        for category, alternatives in alternative_components.items():
            # Créer un expander pour chaque catégorie d'alternatives
            with st.expander(f"Alternatives pour {category}"):
                # Calcul du nombre de colonnes pour les alternatives
                num_alt_cols = min(3, len(alternatives))
                if num_alt_cols == 0:
                    num_alt_cols = 1
                
                # Créer les colonnes pour cette catégorie
                alt_cols = st.columns(num_alt_cols, gap="medium") # Ajout de gap
                
                # Afficher chaque alternative dans une colonne
                for i, alt in enumerate(alternatives):
                    col_index = i % num_alt_cols
                    
                    with alt_cols[col_index]:
                        # Container pour créer une "card"
                        with st.container(border=True): # Ajout de border=True
                            # Badge de catégorie
                            st.markdown(f"<div class='category-badge'>{category} (Alt)</div>", unsafe_allow_html=True)
                            
                            # Extraire les détails
                            name = alt.get('name', 'N/A')
                            price = alt.get('price', 'N/A')
                            merchant = alt.get('merchant', 'N/A')
                            image_url = alt.get('image_url', '')
                            buy_link = alt.get('buy_link', '')
                            
                            # Utiliser l'image placeholder si nécessaire
                            if not image_url:
                                image_url = placeholder_img
                            
                            # Image du composant
                            st.image(image_url, caption=None, use_container_width='auto') # Ajustement de l'image
                            
                            # Nom du composant
                            st.markdown(f"**{name}**")
                            
                            # Prix du composant
                            st.markdown(f"<span class='price-value'>Prix: {price}</span>", unsafe_allow_html=True)
                            
                            # Fournisseur
                            st.markdown(f"Fournisseur: {merchant}")
                            
                            # Bouton d'achat s'il est disponible
                            if buy_link and price != "N/A":
                                st.markdown(f"<a href='{buy_link}' target='_blank' class='buy-button'>Acheter</a>", unsafe_allow_html=True)
    
    # Séparateur
    st.divider()
    
    # Section des boutons d'action
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Bouton de retour à l'accueil
        if st.button("Retour à l'accueil", key="return_home", use_container_width=True):
            # Effacer la configuration sélectionnée
            if 'selected_config' in st.session_state:
                del st.session_state['selected_config']
            # Rediriger vers la page d'accueil
            st.switch_page("app.py")
    
    with col2:
        # Bouton pour exporter la configuration
        if st.button("Exporter au format PDF", key="export_pdf", use_container_width=True):
            st.info("Fonctionnalité d'export PDF à implémenter.")
            
    with col3:
        # Bouton pour partager la configuration
        if st.button("Partager la configuration", key="share_config", use_container_width=True):
            st.info("Fonctionnalité de partage à implémenter.")