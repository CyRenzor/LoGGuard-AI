import os
import fnmatch
import re
import pandas as pd 
from colorama import Fore, Style, init, Back

 
class LogReader:
    def __init__(self, repertoire):
        """
        initialise l'objet avec le chemin du répertoire contenant les fichiers de logs.
        """
        self.repertoire = repertoire  # Chemin du répertoire
        self.lignes_extraites_dict = []  # Liste pour accumuler les lignes extraites sous forme de dictionnaires
        self.lignes_extraites_brut = []  # Liste pour accumuler les lignes extraites en brut
        self.df_logs = pd.DataFrame(columns=['DateHeure', 'Evenement', 'Utilisateur', 'AdresseIP'])  # DataFrame pour stocker les infos
 
    def trouver_fichiers_logs(self, pattern="secure*"):
        """
        Parcourt le répertoire et renvoie une liste de fichiers de logs correspondant au pattern spécifié.
        """
        fichiers_logs = []
        try:
            for fichier in os.listdir(self.repertoire):
                if fnmatch.fnmatch(fichier, pattern):
                    fichiers_logs.append(os.path.join(self.repertoire, fichier))
            return fichiers_logs
        except FileNotFoundError:
            print(f"\n{Fore.RED} ⚠️Erreur:{Style.RESET_ALL} Le répertoire {self.repertoire} n'a pas été trouvé.")
            return []
 
    def lire_logs_bruts(self, fichier_log):
        """
        Lit un fichier de logs ligne par ligne et stocke le résultat dans une liste brute.
        """
        try:
            with open(fichier_log, 'r') as f:
                for ligne in f:
                    self.lignes_extraites_brut.append(ligne)
            print(f"Le fichier {fichier_log} a été lu avec succès.")
        except FileNotFoundError:
            print(f"\n{Fore.RED} ⚠️Erreur:{Style.RESET_ALL}Le fichier {fichier_log} n'a pas été trouvé.")
 
    def lire_et_extraire_logs(self, fichier_log):
        """
        Lit un fichier de logs ligne par ligne, extrait les informations clés avec une regex,
        et stocke ces informations dans une liste de dictionnaires.
        """
        regex = r"^([A-Za-z]{3}\s+\d{1,2}\s+(?:\d{4}\s+)?\d{2}:\d{2}:\d{2}).*?\s+(Invalid user|Failed password|authentication failure).*?\s+(\w+)\s+from\s+(\d{1,3}(?:\.\d{1,3}){3})(?:\s+port\s+\d+.*)?$"
 
 
        try:
            with open(fichier_log, 'r') as f:
                for ligne in f:
                    match = re.search(regex, ligne)
                    if match:
                        date_heure = match.group(1)       
                        evenement = match.group(2)        
                        utilisateur = match.group(3)      
                        adresse_ip = match.group(4)       
 
                        nouvelle_ligne = {
                            'DateHeure': date_heure,
                            'Evenement': evenement,
                            'Utilisateur': utilisateur,
                            'AdresseIP': adresse_ip
                        }
                        self.lignes_extraites_dict.append(nouvelle_ligne)
            print(f"Le fichier {fichier_log} a été lu et les informations ont été extraites avec succès.")
        except FileNotFoundError:
            print(f"⚠️ Erreur : Le fichier {fichier_log} n'a pas été trouvé.")
 
    def creer_dataframe(self):
        """
        Crée un DataFrame Pandas à partir des lignes extraites et l'affecte à l'attribut df_logs.
        """
        if self.lignes_extraites_dict:
            self.df_logs = pd.DataFrame(self.lignes_extraites_dict)
            self.lignes_extraites_dict.clear()  # Efface la liste une fois le DataFrame créé
            print(f"\n{Fore.GREEN}[+]Le DataFrame a été créé avec succès.{Style.RESET_ALL}")
        else:
            print("Aucune ligne n'a été extraite. Le DataFrame est vide.")
 
    def afficher_dataframe(self):
        """
        Affiche le DataFrame contenant les informations extraites des logs.
        """
        print(f"\n{Fore.GREEN}[+]DataFrame des logs extraits:{Style.RESET_ALL}")
        print(self.df_logs)
 
 