import subprocess
import os

if __name__ == "__main__":
    # Chemin vers le script app.py de Streamlit
    # Assurez-vous que ce chemin est correct par rapport à l'emplacement de main.py
    streamlit_app_path = os.path.join(os.path.dirname(__file__), "ui", "app.py")

    # Commande pour lancer Streamlit
    command = ["streamlit", "run", streamlit_app_path]

    try:
        print(f"Lancement de l'application Streamlit depuis : {streamlit_app_path}")
        # Exécution de la commande
        subprocess.run(command, check=True)
    except FileNotFoundError:
        print("Erreur : La commande 'streamlit' n'a pas été trouvée. Assurez-vous que Streamlit est installé et dans votre PATH.")
    except subprocess.CalledProcessError as e:
        print(f"Erreur lors du lancement de l'application Streamlit : {e}")
    except Exception as e:
        print(f"Une erreur inattendue s'est produite : {e}")
