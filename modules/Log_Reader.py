import os
import fnmatch
import re
import pandas as pd  # Importer Pandas pour utiliser les DataFrames

class LogReader:
    def __init__(self, repertoire):
        """
        Constructeur qui initialise l'objet avec le chemin du répertoire contenant les fichiers de logs.
        """
        self.repertoire = repertoire  # Attribut pour stocker le chemin du répertoire
        self.lignes_extraites = []  # Liste pour accumuler les lignes extraites
        self.df_logs = pd.DataFrame(columns=['DateHeure', 'Evenement', 'Utilisateur', 'AdresseIP'])  # DataFrame pour stocker les informations extraites

    def trouver_fichiers_logs(self, pattern="secure*"):
        """
        Parcourt le répertoire et renvoie une liste de fichiers de logs correspondant au pattern spécifié.

        Paramètres :
        pattern (str) : Pattern pour filtrer les fichiers (par défaut 'secure*' pour les fichiers qui commencent par 'secure').

        Retourne :
        list : Liste des fichiers trouvés correspondant au pattern dans le répertoire.
        """
        fichiers_logs = []
        try:
            # Parcourt le répertoire et récupère tous les fichiers correspondant au pattern donné
            for fichier in os.listdir(self.repertoire):
                if fnmatch.fnmatch(fichier, pattern):
                    fichiers_logs.append(os.path.join(self.repertoire, fichier))
            return fichiers_logs
        except FileNotFoundError:
            print(f"Erreur : Le répertoire {self.repertoire} n'a pas été trouvé.")
            return []

    def lire_et_extraire_logs(self, fichier_log):
        """
        Lit un fichier de logs ligne par ligne, extrait les informations clés avec une regex,
        et stocke ces informations dans une liste de dictionnaires.

        Paramètres :
        fichier_log (str) : Chemin vers le fichier de logs à lire.
        """
        # Expression rationnelle pour capturer les informations
        regex = r"([A-Za-z]{3} \d{2} \d{2}:\d{2}:\d{2}) .* (Invalid user|Failed password) (\w+) from (\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"

        try:
            with open(fichier_log, 'r') as f:
                for ligne in f:
                    match = re.search(regex, ligne)
                    if match:
                        date_heure = match.group(1)
                        evenement = match.group(2)
                        utilisateur = match.group(3)
                        adresse_ip = match.group(4)

                        # Accumuler les informations sous forme de dictionnaire dans une liste
                        nouvelle_ligne = {
                            'DateHeure': date_heure,
                            'Evenement': evenement,
                            'Utilisateur': utilisateur,
                            'AdresseIP': adresse_ip
                        }
                        self.lignes_extraites.append(nouvelle_ligne)

            print(f"Le fichier {fichier_log} a été lu et les informations ont été extraites avec succès.")

        except FileNotFoundError:
            print(f"Erreur : Le fichier {fichier_log} n'a pas été trouvé.")

    def creer_dataframe(self):
        """
        Crée un DataFrame Pandas à partir des lignes extraites et l'affecte à l'attribut df_logs.
        """
        if self.lignes_extraites:
            self.df_logs = pd.DataFrame(self.lignes_extraites)
            self.lignes_extraites.clear()  # Effacer la liste des lignes extraites
            print("Le DataFrame a été créé avec succès.")
        else:
            print("Aucune ligne n'a été extraite. Le DataFrame est vide.")

    def afficher_dataframe(self):
        """
        Affiche le DataFrame contenant les informations extraites des logs.
        """
        print("\nDataFrame des logs extraits:")
        print(self.df_logs)
        