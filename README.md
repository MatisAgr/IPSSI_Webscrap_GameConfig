<div align="center">
   
# GameConfig Hub
   
Tisma : [![wakatime](https://wakatime.com/badge/user/a16f794f-b91d-4818-8dfc-d768ce605ece/project/3065f372-fd39-450c-a413-16c785a3e1cd.svg)](https://wakatime.com/badge/user/a16f794f-b91d-4818-8dfc-d768ce605ece/project/3065f372-fd39-450c-a413-16c785a3e1cd)

</div>



## Description

GameConfig Hub est une application web conçue pour aider les joueurs à trouver et à créer des configurations PC optimisées pour leurs jeux préférés. L'application récupère les informations sur les jeux et leurs configurations système requises (minimale et recommandée) depuis Instant Gaming, puis recherche les composants correspondants sur PCPartPicker pour estimer un coût et proposer des options.

> [!NOTE]
> Une tentative d'amélioration de la précision de la recherche de composants sur PCPartPicker en naviguant directement vers les catégories spécifiques (ex: `/cpu/`, `/video-card/`) puis en utilisant le filtre de la page catégorie a été implémentée. Cependant, cette méthode a conduit à des bannissements d'IP par le site. Par conséquent, le scraper utilise une méthode de recherche plus générale pour éviter ce problème, ce qui peut parfois entraîner des résultats moins précis pour certains composants.


## Fonctionnalités

*   **Recherche de jeux** : Intégration avec Instant Gaming pour trouver des informations sur les jeux.
*   **Extraction des configurations requises** : Récupère les spécifications minimales et recommandées pour un jeu donné.
*   **Génération de configurations PC** : Utilise PCPartPicker pour :
    *   Trouver des composants PC (CPU, GPU, RAM, Stockage, OS, etc.) correspondant aux spécifications.
    *   Proposer des composants alternatifs.
    *   Estimer le prix total de la configuration.
*   **Sauvegarde et historique** : Les configurations générées sont sauvegardées au format JSON et peuvent être consultées ultérieurement.
*   **Interface utilisateur conviviale** : Construite avec Streamlit pour une navigation et une utilisation faciles.

## Structure du Projet

Le projet est organisé comme suit :

*   `scrapers/` : Contient les modules de web scraping.
    *   `instant_gaming.py` : Scraper pour le site Instant Gaming (recherche de jeux, extraction des configurations).
    *   `pcpartpicker.py` : Scraper pour le site PCPartPicker (recherche de composants, prix).
*   `ui/` : Contient les fichiers de l'interface utilisateur Streamlit.
    *   `app.py` : Point d'entrée principal de l'application Streamlit (page d'accueil).
    *   `pages/` : Contient les différentes pages de l'application (détails de configuration, historique).
        *   `detail_config.py` : Affiche les détails d'une configuration PC sélectionnée.
        *   `historique.py` : Affiche l'historique des configurations sauvegardées.
    *   `styles/` : Contient les fichiers CSS pour personnaliser l'apparence de l'application.
        *   `style.css` : Feuille de style principale.
*   `data/` : Dossier où sont stockées les données.
    *   `instantgaming/` : Sauvegarde les informations des jeux récupérées (fichiers JSON).
    *   `pcpartpicker/` : Sauvegarde les configurations PC générées (fichiers JSON).
*   `utils/` : Contient des modules utilitaires.
    *   `debug_color.py` : Fonctions pour afficher des messages de débogage colorés dans la console.
*   `requirements.txt` : Liste les dépendances Python du projet.
*   `README.md` : Ce fichier.

## Installation

1.  **Clonez le dépôt** (si ce n'est pas déjà fait) :
    ```bash
    git clone https://github.com/MatisAgr/IPSSI_Webscrap_GameConfig.git
    cd IPSSI_Webscrap_GameConfig
    ```

2.  **Installez les dépendances** :
    ```bash
    pip install -r requirements.txt
    ```
    Les principales dépendances sont :
    *   `selenium`
    *   `webdriver-manager`
    *   `streamlit`
    *   `requests`
    *   `pandas`

## Utilisation

Pour lancer l'application Streamlit, exécutez la commande suivante à la racine du projet :

```bash
python ./main.py
```

L'application s'ouvrira automatiquement dans votre navigateur web par défaut. Vous pourrez alors :

- Entrer le nom d'un jeu.
- Choisir le type de configuration (minimale ou recommandée).
- Optionnellement, inclure des composants alternatifs.
- Lancer la génération de la configuration.
- Consulter les détails de la configuration générée et les composants alternatifs.
- Accéder à l'historique des configurations sauvegardées.
