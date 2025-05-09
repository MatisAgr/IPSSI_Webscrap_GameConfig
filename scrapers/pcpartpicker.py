from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import sys
import os
import json
from pathlib import Path

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.debug_color import debug_print

GLOBAL_WAIT = 1

class PCConfiguration:
    """Classe pour gérer une configuration PC avec ses composants et prix"""
    
    def __init__(self, name="Ma configuration", game_uuid=None):
        self.name = name
        self.game_uuid = game_uuid  # UUID du jeu pour la traçabilité
        self.components = {}  # Dictionnaire avec catégorie comme clé et composant comme valeur
        self.total_price = 0.0
        self.alternative_components = {}  # Pour stocker les composants alternatifs

    
    def add_component(self, category, component_info):
        """
        Ajoute un composant à la configuration
        
        Args:
            category (str): Catégorie du composant (CPU, GPU, etc.)
            component_info (dict): Informations sur le composant
        """
        self.components[category] = component_info
        self._update_total_price()
        debug_print(f"Composant ajouté: {category} - {component_info['name']}", level="success")
    
    def add_alternative_component(self, category, component_info):
        """
        Ajoute un composant alternatif à la configuration
        
        Args:
            category (str): Catégorie du composant (CPU, GPU, etc.)
            component_info (dict): Informations sur le composant alternatif
        """
        if category not in self.alternative_components:
            self.alternative_components[category] = []
        
        self.alternative_components[category].append(component_info)
        debug_print(f"Composant alternatif ajouté: {category} - {component_info['name']}", level="success")
    
    def remove_component(self, category):
        """
        Retire un composant de la configuration
        
        Args:
            category (str): Catégorie du composant à retirer
        """
        if category in self.components:
            removed = self.components[category]['name']
            del self.components[category]
            self._update_total_price()
            debug_print(f"Composant retiré: {category} - {removed}", level="info")
    
    def _update_total_price(self):
        """Met à jour le prix total de la configuration"""
        self.total_price = 0.0
        for category, component in self.components.items():
            if component['price'] != "N/A":
                # Extraire le prix numérique (enlever le symbole €)
                price_str = component['price'].replace('€', '').replace(',', '.')
                try:
                    self.total_price += float(price_str)
                except ValueError:
                    debug_print(f"Prix invalide pour {component['name']}: {component['price']}", level="warning")
    
    def get_total_price(self):
        """
        Obtient le prix total formaté
        
        Returns:
            str: Prix total formaté (ex: '1250,90€')
        """
        return f"{self.total_price:.2f}€".replace('.', ',')
    
    def save_to_json(self, filepath):
        """
        Sauvegarde la configuration dans un fichier JSON
        
        Args:
            filepath (str): Chemin du fichier de sauvegarde
        """
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump({
                'name': self.name,
                'game_uuid': self.game_uuid,  # Inclure l'UUID
                'components': self.components,
                'alternative_components': self.alternative_components,
                'total_price': self.get_total_price()
            }, f, ensure_ascii=False, indent=2)
        debug_print(f"Configuration sauvegardée dans {filepath}", level="success")   
         
    @classmethod
    def load_from_json(cls, filepath):
        """
        Charge une configuration depuis un fichier JSON
        
        Args:
            filepath (str): Chemin du fichier à charger
            
        Returns:
            PCConfiguration: L'objet configuration chargé
        """
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            config = cls(name=data['name'])
            for category, component in data['components'].items():
                config.add_component(category, component)
            debug_print(f"Configuration chargée depuis {filepath}", level="success")
            return config
    
    def get_summary(self):
        """
        Obtient un résumé texte de la configuration
        
        Returns:
            str: Résumé formaté
        """
        summary = [f"Configuration: {self.name}"]
        summary.append("=" * 40)
        
        for category, component in self.components.items():
            summary.append(f"{category}: {component['name']} - {component['price']}")
        
        summary.append("=" * 40)
        summary.append(f"Prix total: {self.get_total_price()}")
        
        return "\n".join(summary)

class PCPartPickerScraper:
    def __init__(self):
        # Configuration du navigateur Chrome
        chrome_options = Options()
        # Décommentez la ligne suivante pour exécuter en mode headless (sans interface)
        # chrome_options.add_argument("--headless")
        
        # Ajouter l'option pour maximiser la fenêtre
        chrome_options.add_argument("--start-maximized")
        
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        self.base_url = "https://fr.pcpartpicker.com"
        debug_print("Navigateur initialisé", level="success")
    
    def create_configuration(self, name, components_to_search):
        """
        Crée une configuration PC à partir d'une liste de composants à rechercher
        
        Args:
            name (str): Nom de la configuration
            components_to_search (dict): Dictionnaire avec comme clés les catégories
                                        et comme valeurs les termes de recherche
        
        Returns:
            PCConfiguration: L'objet configuration créé
        """        
        config = PCConfiguration(name=name)
        
        for category, search_term in components_to_search.items():
            debug_print(f"Recherche de {category}: {search_term}", level="info")
            results = self.search_component(search_term)
            
            if results:
                # Prendre le premier résultat
                component = results[0]
                
                # Obtenir plus de détails (prix et marchands)
                component_details = self.get_component_details(component['link'])
                
                # Utiliser les détails du meilleur prix
                if component_details['best_deal']:
                    component['price'] = component_details['best_deal']['price']
                    component['merchant'] = component_details['best_deal']['merchant']
                    component['buy_link'] = component_details['best_deal']['link']
                
                if component_details['image_url']:
                    component['image_url'] = component_details['image_url']    

                # Ajouter à la configuration
                config.add_component(category, component)
            else:
                debug_print(f"Aucun résultat pour {category}: {search_term}", level="warning")
        
        debug_print(f"Configuration créée: {name}", level="success")
        debug_print(f"Prix total: {config.get_total_price()}", level="success")
        
        return config
    
    #-------------------------------------------
    
    def create_minimal_configuration(self, json_path, include_alternatives=False):
        """
        Crée une configuration PC basée sur les spécifications minimales d'un jeu
        
        Args:
            json_path (str): Chemin vers le fichier JSON des spécifications du jeu
            include_alternatives (bool): Si True, inclut les composants alternatifs
            
        Returns:
            PCConfiguration: La configuration PC minimale créée
        """
        return self._create_game_configuration(json_path, use_recommended=False, include_alternatives=include_alternatives)
    
    def create_recommended_configuration(self, json_path, include_alternatives=False):
        """
        Crée une configuration PC basée sur les spécifications recommandées d'un jeu
        
        Args:
            json_path (str): Chemin vers le fichier JSON des spécifications du jeu
            include_alternatives (bool): Si True, inclut les composants alternatifs
            
        Returns:
            PCConfiguration: La configuration PC recommandée créée
        """
        return self._create_game_configuration(json_path, use_recommended=True, include_alternatives=include_alternatives)
    
    def _create_game_configuration(self, json_path, use_recommended=True, include_alternatives=False):
        """
        Méthode interne pour créer une configuration PC compatible avec les spécifications d'un jeu
        
        Args:
            json_path (str): Chemin vers le fichier JSON des spécifications du jeu
            use_recommended (bool): Si True, utilise les spécifications recommandées
            include_alternatives (bool): Si True, inclut les composants alternatifs
            
        Returns:
            PCConfiguration: La configuration PC créée
        """
        primary_components, alternative_components, game_name, game_uuid = create_config_from_game_requirements(
            json_path, use_recommended)
        
        specs_type = "recommandée" if use_recommended else "minimale"
        config_name = f"Config {specs_type} pour {game_name}"
        
        # Créer la configuration avec UUID et composants principaux
        config = PCConfiguration(name=config_name, game_uuid=game_uuid)
        
        # Ajouter les composants principaux
        for category, search_term in primary_components.items():
            debug_print(f"Recherche de composant principal {category}: {search_term}", level="info")
            results = self.search_component(search_term)
            
            if results and len(results) > 0:
                # Prendre le premier résultat
                component = results[0]
                
                # Obtenir plus de détails (prix et marchands)
                component_details = self.get_component_details(component['link'])
                
                # Utiliser les détails du meilleur prix
                if component_details['best_deal']:
                    component['price'] = component_details['best_deal']['price']
                    component['merchant'] = component_details['best_deal']['merchant']
                    component['buy_link'] = component_details['best_deal']['link']
                
                if component_details['image_url']:
                    component['image_url'] = component_details['image_url']    
    
                # Ajouter à la configuration
                config.add_component(category, component)
            else:
                # Créer un composant "virtuel" pour garantir que tous les composants sont inclus même sans résultats
                debug_print(f"Aucun résultat pour {category}: {search_term}, création d'un composant virtuel", level="warning")
                virtual_component = {
                    'name': f"{search_term} (non trouvé)",
                    'price': "N/A",
                    'link': "",
                    'merchant': "N/A",
                    'buy_link': "",
                    'image_url': ""
                }
                config.add_component(category, virtual_component)
        
        # Ajouter les composants alternatifs uniquement si demandé
        if include_alternatives:
            debug_print("Ajout des composants alternatifs à la configuration", level="info")
            for category, search_terms in alternative_components.items():
                for search_term in search_terms:
                    debug_print(f"Recherche de composant alternatif {category}: {search_term}", level="info")
                    results = self.search_component(search_term)
                    
                    if results and len(results) > 0:
                        # Prendre le premier résultat
                        component = results[0]
                        
                        # Obtenir plus de détails
                        component_details = self.get_component_details(component['link'])
                        
                        # Utiliser les détails du meilleur prix
                        if component_details['best_deal']:
                            component['price'] = component_details['best_deal']['price']
                            component['merchant'] = component_details['best_deal']['merchant']
                            component['buy_link'] = component_details['best_deal']['link']
                        
                        if component_details['image_url']:
                            component['image_url'] = component_details['image_url']
                        
                        # Ajouter comme composant alternatif
                        config.add_alternative_component(category, component)
                    else:
                        # Créer un composant alternatif "virtuel"
                        debug_print(f"Aucun résultat pour l'alternative {category}: {search_term}, création d'un composant virtuel", level="warning")
                        virtual_component = {
                            'name': f"{search_term} (non trouvé)",
                            'price': "N/A",
                            'link': "",
                            'merchant': "N/A",
                            'buy_link': "",
                            'image_url': ""
                        }
                        config.add_alternative_component(category, virtual_component)
        
        debug_print(f"Configuration {specs_type} créée: {config.name}", level="success")
        debug_print(f"UUID du jeu: {config.game_uuid}", level="success")
        debug_print(f"Prix total des composants principaux: {config.get_total_price()}", level="success")
        
        return config
    
    #-------------------------------------------
    
    def search_component(self, query):
        """
        Recherche un composant sur PCPartPicker
        
        Args:
            query (str): Le terme de recherche (ex: "intel i5", "nvidia rtx 3070")
            
        Returns:
            list: Liste de dictionnaires contenant les résultats de recherche
        """
        # Accéder à la page d'accueil
        debug_print(f"Accès à la page {self.base_url}", level="fetch")
        self.driver.get(self.base_url)
        
        try:
            # Gérer les éventuels popups de cookies ou autres notifications
            self._handle_popups()
            
            # Cliquer d'abord sur l'icône de recherche pour ouvrir le champ de recherche
            debug_print("Clic sur l'icône de recherche...", level="info")
            search_icon = WebDriverWait(self.driver, GLOBAL_WAIT).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, ".nav__search"))
            )
            search_icon.click()
            
            # Attendre que la barre de recherche soit chargée et visible
            debug_print("Attente de la barre de recherche...", level="info")
            search_input = WebDriverWait(self.driver, GLOBAL_WAIT).until(
                EC.presence_of_element_located((By.ID, "search_q"))
            )
            
            # Entrer le terme de recherche
            debug_print(f"Recherche de: '{query}'", level="fetch")
            search_input.clear()
            search_input.send_keys(query)
            
            # Cliquer sur le bouton recherche
            search_button = WebDriverWait(self.driver, GLOBAL_WAIT).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "form#site_search_nav button.button--primary"))
            )
            search_button.click()
            
            # Attendre que les résultats se chargent - CORRECTION ICI
            debug_print("Attente des résultats de recherche...", level="info")
            WebDriverWait(self.driver, GLOBAL_WAIT).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".search-results__pageContent"))
            )
            
            # Extraire les résultats de recherche
            return self._extract_search_results()
            
        except Exception as e:
            debug_print(f"Erreur lors de la recherche de composants: {e}", level="error")
            return []

    def _handle_popups(self):
        """Gère les popups éventuels comme les avertissements de cookies"""
        try:
            debug_print("Tentative de gestion du popup de cookies", level="info")
            # Cibler spécifiquement le bouton "Allow" dans la popup de cookies
            cookie_button = WebDriverWait(self.driver, GLOBAL_WAIT).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, ".cc-btn.cc-allow"))
            )
            debug_print("Bouton 'Allow' de cookies trouvé", level="debug")
            cookie_button.click()
            debug_print("Popup de cookies accepté avec succès", level="success")
        except Exception as e:
            # Pas de popup ou l'élément est différent, on continue
            debug_print(f"Aucun popup de cookies détecté ou problème: {e}", level="debug")
            pass  
    
    def _extract_search_results(self):
        """Extrait les détails des résultats de recherche"""
        results = []
        try:
            # Attendre que les résultats soient chargés
            debug_print("Attente supplémentaire pour le chargement complet...", level="debug")
            time.sleep(2)
            
            # Récupérer les éléments des résultats (structure correcte selon le HTML)
            result_elements = self.driver.find_elements(By.CSS_SELECTOR, ".search-results__pageContent ul.list-unstyled li")
            debug_print(f"Nombre d'éléments trouvés: {len(result_elements)}", level="info")
            
            for element in result_elements:
                try:
                    # Extraire les informations de chaque résultat
                    name_element = element.find_element(By.CSS_SELECTOR, ".search_results--link a")
                    name = name_element.text
                    link = name_element.get_attribute("href")
                    
                    # Essayer d'obtenir le prix (s'il est disponible)
                    try:
                        price_element = element.find_element(By.CSS_SELECTOR, ".search_results--price a")
                        price = price_element.text.strip()
                        price = self._normalize_price(price)  # Normaliser le format du prix
                    except:
                        price = "N/A"
                        debug_print(f"Erreur lors de l'extraction du prix: {e}", level="warning")
                    
                    results.append({
                        "name": name,
                        "link": link,
                        "price": price
                    })
                    debug_print(f"Élément extrait: {name}", level="debug")
                except Exception as e:
                    debug_print(f"Erreur lors de l'extraction d'un résultat: {e}", level="warning")
            
        except Exception as e:
            debug_print(f"Erreur lors de l'extraction des résultats: {e}", level="error")
        
        debug_print(f"Total de {len(results)} résultats extraits", level="success")
        return results

    def get_component_details(self, component_url):
        """
        Récupère les informations de prix et d'achat d'un composant à partir de son URL
        
        Args:
            component_url (str): L'URL du composant
            
        Returns:
            dict: Détails du composant (prix, marchands, image, etc.)
        """
        debug_print(f"Récupération des prix depuis: {component_url}", level="fetch")
        
        if not component_url:
            debug_print("URL du composant vide, retour des valeurs par défaut", level="warning")
            return {
                "price": "N/A",
                "best_deal": None,
                "merchant_options": [],
                "availability": "N/A",
                "image_url": ""
            }
        
        self.driver.get(component_url)
        
        # Augmenter le temps d'attente pour le chargement des images
        time.sleep(2)
        
        details = {
            "price": "N/A",  # Valeur par défaut "N/A" au lieu de None
            "best_deal": None,
            "merchant_options": [],
            "availability": "N/A",  # Valeur par défaut "N/A" au lieu de None
            "image_url": ""  # Chaîne vide au lieu de None
        }
        
        try:
            # Essayer d'extraire l'image du produit avec plusieurs méthodes
            try:
                # Attendre que la page soit suffisamment chargée
                WebDriverWait(self.driver, GLOBAL_WAIT).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".product__image-2024 img, #pp_main_product_image, .product__image img"))
                )
                
                # Essayer plusieurs sélecteurs pour l'image principale
                for selector in ["#pp_main_product_image", ".product__image-2024 img", ".product__image img"]:
                    try:
                        img_element = self.driver.find_element(By.CSS_SELECTOR, selector)
                        image_url = img_element.get_attribute("src")
                        
                        if image_url:
                            # Ajouter le protocole si nécessaire
                            if image_url.startswith("//"):
                                image_url = "https:" + image_url
                                
                            details["image_url"] = image_url
                            debug_print(f"Image trouvée avec sélecteur {selector}: {image_url}", level="success")
                            break
                    except:
                        continue
                
                # Si aucune image n'a été trouvée, essayer les miniatures
                if not details["image_url"]:
                    for selector in [".product__image-2024-thumbnails img", ".product__image-2024-mobile-list img"]:
                        try:
                            img_elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                            if img_elements:
                                image_url = img_elements[0].get_attribute("src")
                                if image_url.startswith("//"):
                                    image_url = "https:" + image_url
                                    
                                details["image_url"] = image_url
                                debug_print(f"Image miniature trouvée: {image_url}", level="success")
                                break
                        except:
                            continue
                
                # Dernier recours: chercher n'importe quelle image pertinente
                if not details["image_url"]:
                    all_images = self.driver.find_elements(By.TAG_NAME, "img")
                    for img in all_images:
                        src = img.get_attribute("src")
                        if src and ("product" in src.lower() or "static" in src.lower()):
                            if src.startswith("//"):
                                src = "https:" + src
                            details["image_url"] = src
                            debug_print(f"Image de secours trouvée: {src}", level="success")
                            break
                            
            except Exception as e:
                debug_print(f"Erreur lors de l'extraction de l'image: {e}", level="warning")
            
            # Extraire les informations de prix des marchands (code existant)
            try:
                # Récupérer tous les marchands du tableau de prix
                merchant_rows = self.driver.find_elements(By.CSS_SELECTOR, "#prices table tbody tr:not(.tr--noBorder)")
                debug_print(f"Nombre de marchands trouvés: {len(merchant_rows)}", level="info")
                
                for i, row in enumerate(merchant_rows):
                    try:
                        # Extraire les informations du marchand
                        merchant_name = row.find_element(By.CSS_SELECTOR, ".td__logo img").get_attribute("alt")
                        price_element = row.find_element(By.CSS_SELECTOR, ".td__finalPrice a")
                        price = price_element.text.strip()
                        price = self._normalize_price(price)  # Normaliser le format du prix
                        buy_link = price_element.get_attribute("href")  
                                              
                        merchant_info = {
                            "merchant": merchant_name,
                            "price": price,
                            "link": buy_link,
                        }
                        
                        details["merchant_options"].append(merchant_info)
                        
                        # Le premier marchand est considéré comme la meilleure offre
                        if i == 0:
                            details["best_deal"] = merchant_info
                            details["price"] = price
                            debug_print(f"Meilleure offre trouvée: {price} chez {merchant_name}", level="success")
                        
                    except Exception as e:
                        debug_print(f"Erreur lors de l'extraction d'un marchand: {e}", level="warning")
                
            except Exception as e:
                debug_print(f"Erreur lors de l'extraction des prix: {e}", level="error")
                # Fallback: essayer d'extraire seulement le prix principal
                try:
                    price_element = self.driver.find_element(By.CSS_SELECTOR, ".price__price")
                    details["price"] = self._normalize_price(price_element.text)
                    debug_print(f"Prix principal trouvé: {details['price']}", level="success")
                except:
                    details["price"] = "N/A"
                    debug_print("Prix non disponible", level="warning")
                    
        except Exception as e:
            debug_print(f"Erreur lors de l'extraction des détails du composant: {e}", level="error")
        
        return details


    def _normalize_price(self, price_text):
        """
        Normalise le format du prix de '€114.90+' vers '114,90€'
        
        Args:
            price_text (str): Prix au format original
            
        Returns:
            str: Prix au format normalisé ou 'N/A' si non disponible
        """
        if not price_text:
            return "N/A"
                
        # Supprimer le symbole € au début s'il existe
        if price_text.startswith('€'):
            price_text = price_text[1:]
                
        # Supprimer le signe + à la fin s'il existe
        if price_text.endswith('+'):
            price_text = price_text[:-1]
                
        # Remplacer le point par une virgule
        price_text = price_text.replace('.', ',')
            
        # Ajouter le symbole € à la fin
        return f"{price_text}€"

    def close(self):
        """Ferme le navigateur"""
        if self.driver:
            debug_print("Fermeture du navigateur...", level="info")
            self.driver.quit()
            debug_print("Navigateur fermé", level="success")
             
def create_config_from_game_requirements(json_path, use_recommended=True):
    """
    Crée une configuration PC basée sur les spécifications d'un jeu
    
    Args:
        json_path (str): Chemin vers le fichier JSON des spécifications du jeu
        use_recommended (bool): Si True, utilise les spécifications recommandées,
                              sinon utilise les spécifications minimales
    
    Returns:
        tuple: (Dict des composants principaux, Dict des composants alternatifs, nom du jeu, UUID du jeu)
    """
    debug_print(f"Lecture des spécifications du jeu depuis {json_path}", level="info")
    
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            game_data = json.load(f)
            
        # Extraction des informations du jeu
        game_name = game_data.get('game', 'Jeu inconnu')
        game_uuid = game_data.get('uuid', 'unknown')
        game_price = game_data.get('price', 'N/A')
        
        # Sélection des spécifications (recommandées ou minimales)
        specs_key = "recommended" if use_recommended else "minimal"
        specs = game_data.get(specs_key, {})
        
        debug_print(f"Création d'une configuration pour: {game_name} ({specs_key})", level="info")
        debug_print(f"Prix du jeu: {game_price}, UUID: {game_uuid}", level="info")
        
        # Mapping des composants principaux et alternatifs
        primary_components = {}
        alternative_components = {}
        
        # CPU (Processeur)
        if "Processor" in specs:
            processor = specs["Processor"]
            if isinstance(processor, dict):
                # Récupère les deux options
                option1 = processor.get("1") or processor.get("option1", "")
                option2 = processor.get("2") or processor.get("option2", "")
                
                # Option principale
                if option1:
                    primary_components["CPU"] = option1
                
                # Option alternative  
                if option2:
                    if "CPU" not in alternative_components:
                        alternative_components["CPU"] = []
                    alternative_components["CPU"].append(option2)
            else:
                primary_components["CPU"] = processor
                
        # GPU (Carte graphique)
        if "Graphics" in specs:
            graphics = specs["Graphics"]
            if isinstance(graphics, dict):
                # Récupère les deux options
                option1 = graphics.get("1") or graphics.get("option1", "")
                option2 = graphics.get("2") or graphics.get("option2", "")
                
                # Option principale
                if option1:
                    primary_components["GPU"] = option1
                
                # Option alternative
                if option2:
                    if "GPU" not in alternative_components:
                        alternative_components["GPU"] = []
                    alternative_components["GPU"].append(option2)
            else:
                primary_components["GPU"] = graphics
                
        # RAM (Mémoire)
        if "Memory" in specs:
            memory = specs["Memory"]
            primary_components["RAM"] = memory
            
        # Stockage
        if "Storage" in specs:
            storage = specs["Storage"]
            # Déterminer le type de stockage (SSD/HDD)
            if "SSD" in storage or "SSD" in specs.get("Additional Notes", ""):
                primary_components["SSD"] = f"SSD {storage.split()[0]}" if any(char.isdigit() for char in storage) else "SSD 1TB"
            else:
                primary_components["HDD"] = f"HDD {storage.split()[0]}" if any(char.isdigit() for char in storage) else "HDD 1TB"
        
        # Système d'exploitation
        if "OS" in specs:
            primary_components["OS"] = specs["OS"]
            
        debug_print("Composants principaux extraits:", level="success")
        for category, value in primary_components.items():
            debug_print(f"  - {category}: {value}", level="debug")
        
        debug_print("Composants alternatifs extraits:", level="success")
        for category, alternatives in alternative_components.items():
            for alt in alternatives:
                debug_print(f"  - {category} (alternative): {alt}", level="debug")
            
        return primary_components, alternative_components, game_name, game_uuid
        
    except Exception as e:
        debug_print(f"Erreur lors de la lecture du fichier de spécifications: {e}", level="error")
        return {}, {}, "Configuration par défaut", ""
       
if __name__ == "__main__":
    debug_print("Démarrage du programme PCPartPicker", level="info")
    scraper = PCPartPickerScraper()
    
    try:
        # Chemin vers un fichier JSON de spécifications de jeu
        project_root = Path(__file__).parent.parent
        
        # Liste tous les fichiers JSON dans le dossier instantgaming
        data_folder = os.path.join(project_root, "data", "instantgaming")
        json_files = []
        
        if os.path.exists(data_folder):
            json_files = [f for f in os.listdir(data_folder) if f.endswith('.json')]
        
        if json_files:
            json_path = os.path.join(data_folder, json_files[0])
            debug_print(f"Fichier trouvé: {json_path}", level="info")
            
            include_alternatives = True  # Cette option sera contrôlée par l'utilisateur
            
            debug_print(f"Création de la configuration recommandée", level="info")
            rec_config = scraper.create_recommended_configuration(json_path, include_alternatives=include_alternatives)
            print("\n== CONFIGURATION RECOMMANDÉE ==\n")
            print(rec_config.get_summary())
            
            # Création de la configuration minimale sans composants alternatifs
            debug_print(f"Création de la configuration minimale", level="info")
            min_config = scraper.create_minimal_configuration(json_path, include_alternatives=include_alternatives)
            print("\n== CONFIGURATION MINIMALE ==\n")
            print(min_config.get_summary())
            
            # Sauvegarde des configurations
            data_dir = os.path.join(project_root, "data", "pcpartpicker")
            os.makedirs(data_dir, exist_ok=True)
            
            # Générer des noms de fichiers avec l'UUID du jeu
            # Utiliser le nom du jeu et son UUID pour générer des noms uniques
            game_name = rec_config.name.replace("Config recommandée pour ", "").replace(" ", "_").lower()
            
            # Sauvegarder les deux configurations
            alt_suffix = "_avec_alternatives" if include_alternatives else ""
            json_rec_path = os.path.join(data_dir, f"{game_name}_rec{alt_suffix}_{rec_config.game_uuid}.json")
            json_min_path = os.path.join(data_dir, f"{game_name}_min{alt_suffix}_{min_config.game_uuid}.json")
            
            rec_config.save_to_json(json_rec_path)
            min_config.save_to_json(json_min_path)
            
        else:
            debug_print("Aucun fichier JSON trouvé, création d'une configuration par défaut", level="warning")
            components = {
                "CPU": "intel i5 12400F",
                "GPU": "nvidia rtx 3060",
                "Carte mère": "msi b660",
                "RAM": "corsair vengeance 16gb",
                "SSD": "samsung 970 evo plus 1tb",
            }
            
            config = scraper.create_configuration("PC Gamer Budget", components)
            print("\n" + config.get_summary() + "\n")
            
            data_dir = os.path.join(project_root, "data", "pcpartpicker")
            os.makedirs(data_dir, exist_ok=True)
            json_path = os.path.join(data_dir, "pc_gamer_budget_default.json")
            config.save_to_json(json_path)
        
    except Exception as e:
        debug_print(f"Erreur lors de la création de la configuration: {e}", level="error")
    
    finally:
        scraper.close()
        debug_print("Programme terminé.", level="success")

