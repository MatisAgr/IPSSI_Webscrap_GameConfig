from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from pathlib import Path
import time
import json
import os
import uuid

# Récupère le nom du jeu vidéo (utilise une valeur par défaut pour le moment)
def get_game_name():
    game_name = "GTA 5" 
    print("\n" + "="*50)
    print("RECHERCHE DE JEU VIDÉO")
    print("="*50)
    print(f"Jeu recherché: {game_name}")
    return game_name

class InstantGaming:
    # Initialise la classe avec les options de configuration
    def __init__(self, headless=False, game_name=None):
        self.driver = None
        self.headless = headless
        self.game_name = game_name
        
    # Configure le driver et accède au site web d'Instant Gaming
    def access_site(self):
        try:
            chrome_options = Options()
            if self.headless:
                chrome_options.add_argument("--headless")
            chrome_options.add_argument("--window-size=1920,1080")
            
            self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
            
            print("Accès au site web Instant Gaming...")
            self.driver.get("https://www.instant-gaming.com/fr/")
            
            time.sleep(3)
            
            print(f"Titre de la page: {self.driver.title}")
            
            return True
            
        except Exception as e:
            print(f"Une erreur s'est produite: {e}")
            return False

    # Accepte le bandeau de cookies sur le site
    def accept_cookies(self):
        try:
            print("Recherche de la bannière de cookies...")
            wait = WebDriverWait(self.driver, 10)
            accept_button = wait.until(
                EC.element_to_be_clickable((By.XPATH, "//div[@id='cookies-banner']//button[text()='Tout accepter']"))
            )
            print("Bouton 'Tout accepter' trouvé, clic en cours...")
            accept_button.click()
            print("Cookies acceptés avec succès.")
            return True
        except Exception as e:
            print(f"Erreur lors de l'acceptation des cookies: {e}")
            return False
    
    # Recherche un jeu dans la barre de recherche
    def search_game(self):
        try:
            print(f"Recherche du jeu: {self.game_name}")
            
            # Partie recherche
            wait = WebDriverWait(self.driver, 5)
            search_icon = wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, ".icon-search-input"))
            )
            print("Icône de recherche trouvée, clic en cours...")
            search_icon.click()
            
            search_input = wait.until(
                EC.element_to_be_clickable((By.ID, "ig-header-search-box-input"))
            )
            
            search_input.clear()
            
            search_input.send_keys(self.game_name)
            print(f"Texte saisi dans la barre de recherche: '{self.game_name}'")
            
            time.sleep(0.5)
            
            # Partie filtrage PC
            print("Application du filtre PC...")
            
            # Cliquer sur le filtre Systèmes
            system_filter = wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, ".select2-selection.select2-selection--single"))
            )
            print("Filtre Systèmes trouvé, clic en cours...")
            system_filter.click()
            
            # Attendre que la liste déroulante apparaisse et cliquer sur l'option PC
            pc_option = wait.until(
                EC.element_to_be_clickable((By.XPATH, "//li[@role='option' and contains(text(), 'PC')]"))
            )
            print("Option PC trouvée, clic en cours...")
            pc_option.click()
            
            print("Filtre PC appliqué avec succès")
            
            # Attendre que les résultats se mettent à jour
            time.sleep(2)
            
            return True
        except Exception as e:
            print(f"Erreur lors de la recherche ou du filtrage: {e}")
            return False
        
    # Clique sur le premier résultat de la recherche
    def click_first_result(self):
        try:
            print("Recherche du premier résultat...")
            
            wait = WebDriverWait(self.driver, 10)
            first_result = wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, ".search.listing-items .item:first-child a.cover"))
            )
            
            try:
                parent_div = first_result.find_element(By.XPATH, "..")
                title_element = parent_div.find_element(By.CSS_SELECTOR, ".title")
                game_title = title_element.get_attribute("title")
                print(f"Premier jeu trouvé: '{game_title}'")
            except Exception as e:
                print("Impossible de récupérer le titre du jeu:", e)
            
            first_result.click()
            print("Clic sur le premier résultat effectué")
            
            time.sleep(2)
            print(f"Page chargée: {self.driver.title}")
            
            return True
        except Exception as e:
            print(f"Erreur lors de la sélection du premier résultat: {e}")
            return False
        
    # Extrait les configurations système minimale et recommandée du jeu
    def extract_system_requirements(self):
        try:
            print("Extraction des configurations système...")
            
            # Récupérer l'URL de l'image du jeu
            try:
                wait = WebDriverWait(self.driver, 5)
                image_element = wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".presentation picture.banner img"))
                )
                image_url = image_element.get_attribute("src")
                print(f"URL de l'image récupérée: {image_url}")
            except Exception as e:
                print(f"Impossible de récupérer l'image du jeu: {e}")
                image_url = ""
                
            # Récupérer le prix du jeu
            try:
                price_element = self.driver.find_element(By.CSS_SELECTOR, ".total")
                price = price_element.text
                print(f"Prix récupéré: {price}")
            except Exception as e:
                print(f"Impossible de récupérer le prix du jeu: {e}")
                price = ""
            
            # Fonction pour nettoyer les spécifications hardware
            def clean_hardware_spec(key, value):
                # Dictionnaire de termes à supprimer par type de composant
                terms_to_remove = {
                    "Graphics": ["NVIDIA", "GeForce", "AMD", "Radeon", "Intel", "512MB VRAM", "1GB VRAM", "2GB VRAM", "4GB VRAM", "8GB VRAM", "16GB VRAM", "32GB VRAM", "(", ")", "VRAM", "12 GB", "10 GB", "16 GB", "20 GB", "24 GB", "8 GB", "4 GB", "2 GB", "1 GB", "512 MB", "6 GB", "3 GB"],
                    "Processor": ["Intel", "AMD", "Core"],
                    "Memory": ["RAM", "GB", "MB"],
                    # ...autres types de composants au besoin
                }
                
                # Si c'est de la mémoire, traitement spécial
                if key == "Memory":
                    # Traitement spécial pour la mémoire - extraire juste le nombre
                    import re
                    # Chercher tous les nombres dans la valeur
                    numbers = re.findall(r'\d+', value)
                    if numbers:
                        # Prendre le premier nombre trouvé
                        memory_value = numbers[0]
                        # Retourner simplement la valeur numérique avec DDR
                        cleaned_value = f"{memory_value} DDR".strip()
                        print(f"Mémoire spéciale: '{value}' -> '{cleaned_value}'")
                        return cleaned_value
                
                # Pour les autres types de composants
                if key in terms_to_remove:
                    original_value = value
                    for term in terms_to_remove[key]:
                        # Supprimer le terme uniquement s'il est un mot complet (éviter les sous-chaînes)
                        value = value.replace(f"{term} ", "").replace(f" {term}", "").replace(f"{term}", "")
                    value = " ".join(value.split())  # Nettoyer les espaces excédentaires
                    if original_value != value:
                        print(f"Nettoyé: '{original_value}' -> '{value}'")
                
                # Ajouter "DDR" uniquement aux spécifications de mémoire (cas où la méthode spéciale n'a pas été utilisée)
                if key == "Memory" and "DDR" not in value:
                    original_value = value
                    value = f"{value} DDR".strip()
                    print(f"Mémoire modifiée: '{original_value}' -> '{value}'")
                
                return value
            
            # Récupération des spécifications techniques
            wait = WebDriverWait(self.driver, 10)
            specs_container = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".specs-container.listing-slider"))
            )
            
            special_fields = ["OS", "Processor", "Memory", "Graphics", "Storage", "Sound Card"]
            
            # Fonction pour vérifier si une valeur contient des alternatives
            def has_alternatives(value):
                return "|" in value or "/" in value or " or " in value or " ou " in value
            
            # Fonction pour extraire les alternatives
            def extract_alternatives(value):
                result = [value]
                
                # Traiter chaque type de séparateur l'un après l'autre
                # Pour éviter les interactions complexes entre différents séparateurs
                for separator in ["|", "/", " or ", " ou "]:
                    new_result = []
                    for item in result:
                        if separator in item:
                            parts = item.split(separator)
                            new_result.extend([part.strip() for part in parts if part.strip()])
                        else:
                            new_result.append(item)
                    result = new_result
                
                # Éliminer les doublons tout en préservant l'ordre
                seen = set()
                unique_result = []
                for item in result:
                    if item not in seen:
                        seen.add(item)
                        unique_result.append(item)
                
                return unique_result
            
            minimal_section = specs_container.find_element(By.CSS_SELECTOR, ".minimal")
            minimal_items = minimal_section.find_elements(By.CSS_SELECTOR, "ul.specs li")
            
            minimal_specs = {}
            for item in minimal_items:
                text = item.text
                if ":" in text:
                    key, value = text.split(":", 1)
                    key = key.strip()
                    value = value.strip()
                    
                    if key in special_fields and has_alternatives(value):
                        options = extract_alternatives(value)
                        options_dict = {}
                        for i, opt in enumerate(options, 1):
                            # Nettoyer chaque option avant de l'ajouter
                            clean_opt = clean_hardware_spec(key, opt)
                            options_dict[str(i)] = clean_opt
                        minimal_specs[key] = options_dict
                    else:
                        # Nettoyer également les valeurs non alternatives
                        minimal_specs[key] = clean_hardware_spec(key, value)
            
            recommended_section = specs_container.find_element(By.CSS_SELECTOR, ".recommended")
            recommended_items = recommended_section.find_elements(By.CSS_SELECTOR, "ul.specs li")
            
            recommended_specs = {}
            for item in recommended_items:
                text = item.text
                if ":" in text:
                    key, value = text.split(":", 1)
                    key = key.strip()
                    value = value.strip()
                    
                    if key in special_fields and has_alternatives(value):
                        options = extract_alternatives(value)
                        options_dict = {}
                        for i, opt in enumerate(options, 1):
                            # Nettoyer chaque option avant de l'ajouter
                            clean_opt = clean_hardware_spec(key, opt)
                            options_dict[str(i)] = clean_opt
                        recommended_specs[key] = options_dict
                    else:
                        # Nettoyer également les valeurs non alternatives
                        recommended_specs[key] = clean_hardware_spec(key, value)
            
            game_title = self.driver.title.split("-")[0].strip()
            system_requirements = {
                "game": game_title,
                "image_url": image_url,
                "price": price,
                "minimal": minimal_specs,
                "recommended": recommended_specs
            }
            
            print("Configurations système extraites avec succès!")
            
            self.save_requirements_to_json(system_requirements)
            
            return system_requirements
        
        except Exception as e:
            print(f"Erreur lors de l'extraction des configurations système: {e}")
            return None
        
    def save_requirements_to_json(self, data):
        try:
            # Récupérer le nom du jeu et le nettoyer pour l'utiliser dans un nom de fichier
            game_name = data["game"].replace(":", "").replace(" ", "_").replace("/", "_").lower()
            
            # Générer un UUID unique
            unique_id = str(uuid.uuid4())
            
            # Ajouter l'UUID comme première clé du dictionnaire de données
            # Créer un nouveau dictionnaire avec l'UUID en premier (ordre préservé depuis Python 3.7+)
            updated_data = {
                "uuid": unique_id,
                **data  # Décompresse le dictionnaire existant après la première clé
            }
            
            # Construire le nom du fichier avec le format: nom_du_jeu_uuid.json
            filename_base = f"{game_name}_{unique_id}"
            
            project_root = Path(__file__).parent.parent
            data_folder = os.path.join(project_root, "data", "instantgaming")
            
            if not os.path.exists(data_folder):
                os.makedirs(data_folder)
                print(f"Dossier '{data_folder}' créé")
            
            filename = os.path.join(data_folder, f"{filename_base}.json")
            
            with open(filename, "w", encoding="utf-8") as json_file:
                json.dump(updated_data, json_file, indent=4, ensure_ascii=False)
            
            print(f"Configurations système enregistrées dans le fichier '{filename}'")
            return True
        
        except Exception as e:
            print(f"Erreur lors de l'enregistrement des configurations: {e}")
            return False
    
    # Ferme le navigateur Chrome
    def quit(self):
        if self.driver:
            self.driver.quit()
            print("Navigateur fermé.")

if __name__ == "__main__":
    game_name = get_game_name()
    
    instant_gaming = InstantGaming(headless=False, game_name=game_name)
    
    if instant_gaming.access_site():
        print("Navigation réussie!")
        
        instant_gaming.accept_cookies()
        
        # Recherche et filtre dans une seule fonction
        instant_gaming.search_game()
        
        instant_gaming.click_first_result()
        
        system_requirements = instant_gaming.extract_system_requirements()
        
        input("Appuyez sur Entrée pour fermer le navigateur...")
        
    instant_gaming.quit()