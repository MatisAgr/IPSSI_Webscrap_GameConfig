from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
import re
import sys
import os

# Ajouter le chemin du répertoire parent au path pour permettre l'import
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.debug_color import debug_print

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
            search_icon = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, ".nav__search"))
            )
            search_icon.click()
            
            # Attendre que la barre de recherche soit chargée et visible
            debug_print("Attente de la barre de recherche...", level="info")
            search_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "search_q"))
            )
            
            # Entrer le terme de recherche
            debug_print(f"Recherche de: '{query}'", level="fetch")
            search_input.clear()
            search_input.send_keys(query)
            
            # Cliquer sur le bouton recherche
            search_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "form#site_search_nav button.button--primary"))
            )
            search_button.click()
            
            # Attendre que les résultats se chargent - CORRECTION ICI
            debug_print("Attente des résultats de recherche...", level="info")
            WebDriverWait(self.driver, 10).until(
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
            cookie_button = WebDriverWait(self.driver, 5).until(
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
            dict: Détails du composant (prix, marchands, etc.)
        """
        debug_print(f"Récupération des prix depuis: {component_url}", level="fetch")
        self.driver.get(component_url)
        time.sleep(2)
        
        details = {
            "price": None,
            "best_deal": None,
            "merchant_options": [],
            "availability": None
        }
        
        try:
            # Extraire les informations de prix des marchands
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
                
# Exemple d'utilisation
if __name__ == "__main__":
    # Ce code ne s'exécute que si le fichier est lancé directement
    debug_print("Test du scraper PCPartPicker", level="info")
    scraper = PCPartPickerScraper()
    
    try:
        # TESTER LA RECHERCHE
        
        query = input("Entrez le terme de recherche (ex: 'intel i5', 'nvidia rtx 3070'): ")
        debug_print(f"Recherche de: {query}", level="info")
        results = scraper.search_component(query)
        
        # Afficher les résultats
        debug_print(f"Nombre de résultats: {len(results)}", level="success")
        for i, result in enumerate(results[:5], 1):  # Afficher max 5 résultats
            debug_print(f"Résultat {i}:", level="info")
            debug_print(f"  Nom: {result['name']}", level="info")
            debug_print(f"  Prix: {result['price']}", level="info")
            debug_print(f"  Lien: {result['link']}", level="debug")
        
        # Tester la récupération de détails pour le premier résultat
        if results:
            debug_print("Récupération des détails du premier résultat...", level="fetch")
            details = scraper.get_component_details(results[0]['link'])
            debug_print(f"  Prix: {details['price']}", level="info")
            debug_print("  Spécifications:", level="info")     
    except Exception as e:
        debug_print(f"Erreur lors du test: {e}", level="error")
    
    finally:
        # Toujours fermer le navigateur à la fin
        scraper.close()
        debug_print("Test terminé.", level="success")