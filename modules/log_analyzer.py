import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import sqlite3
from colorama import Fore, Style, init, Back
 
def parse_date(date_str):
    """
    Tente de parser la date au format avec année (ex. "Sep 29 2025 03:29:38"),
    sinon parse sans l'année.
    """
    try:
        return pd.to_datetime(date_str, format='%b %d %Y %H:%M:%S')
    except ValueError:
        dt = pd.to_datetime(date_str, format='%b %d %H:%M:%S')
        return dt.replace(year=pd.Timestamp.now().year)
 
class LogAnalyzer:
    def __init__(self, df_logs):
        """
        Initialise l'objet LogAnalyzer avec un DataFrame contenant les logs extraits.
        """
        self.df_logs = df_logs
 
    def analyser_frequence_ips(self, intervalle_temps='1min', seuil_alerte=10):
        """
        Analyse la fréquence d'accès des adresses IP sur un intervalle de temps donné.
        Si une IP dépasse le seuil d'accès, toutes ses entrées sont marqués en ajoutant " CRITICAL"
        dans la colonne Evenement. La fonction affiche ensuite les accès suspects et renvoie
        les évènements critiques détectés sous forme de dictionnaire.
        """
        if self.df_logs.empty:
            print("Le DataFrame est vide. Veuillez charger les logs avant l'analyse.")
            return None
 
        # Convertir la colonne 'DateHeure' en datetime en utilisant parse_date
        try:
            self.df_logs['DateHeure'] = self.df_logs['DateHeure'].apply(parse_date)
        except Exception as e:
            print(f" Erreur lors de la conversion des dates : {e}")
            return None
 
        # Grouper par adresse IP et par intervalle de temps
        acces_par_ip = (
            self.df_logs
                .set_index('DateHeure')
                .groupby([pd.Grouper(freq=intervalle_temps), 'AdresseIP'])
                .size()
        )
 
        # Filtrer les groupes qui dépassent le seuil d'alerte
        acces_suspects = acces_par_ip[acces_par_ip > seuil_alerte]
 
        if not acces_suspects.empty:
            print(f"\n{Fore.RED}🚨 Accès suspects détectés (plus de {seuil_alerte} accès par IP dans {intervalle_temps}) :{Style.RESET_ALL}")
            for (interval, ip), count in acces_suspects.items():
                print(f"- Intervalle: {interval}, IP: {ip}, Nombre d'accès: {count}")
                # Marquer les événements pour cette IP en ajoutant " CRITICAL" (si non déjà présent)
                idx = self.df_logs[self.df_logs['AdresseIP'] == ip].index
                self.df_logs.loc[idx, 'Evenement'] = self.df_logs.loc[idx, 'Evenement'].apply(
                    lambda x: x if "CRITICAL" in x.upper() else x + " CRITICAL"
                )
        else:
            print(f"Aucun accès suspect détecté dans l'intervalle de {intervalle_temps}.")
 
        # Recherche des événements critiques dans la colonne 'Evenement'
        evenements_critiques = self.df_logs[self.df_logs['Evenement'].str.contains("CRITICAL", case=False, na=False)]
        if not evenements_critiques.empty:
            print(f"\n{Fore.RED}🚨 Évènements CRITIQUES détectés :{Style.RESET_ALL}")
            print(evenements_critiques)
            return evenements_critiques.to_dict(orient='records')
        else:
            print("\nAucun évènement critique détecté.")
            return None
 
    def afficher_evenements_par_date(self):
        """
        Affiche un graphique de l'évolution des événements critiques par date.
        """
        if not self.df_logs.empty:
            try:
                # On suppose ici que les dates sont au format avec année.
                self.df_logs['DateHeure'] = pd.to_datetime(self.df_logs['DateHeure'], format='%b %d %Y %H:%M:%S')
            except Exception as e:
                print(f" ⚠️ Erreur lors de la conversion des dates : {e}")
                return
 
            # Compter le nombre d'événements critiques par jour
            evenements_par_date = self.df_logs.groupby(self.df_logs['DateHeure'].dt.date).size()
 
            plt.figure(figsize=(10, 6))
            plt.plot(evenements_par_date.index, evenements_par_date.values, marker='o', linestyle='-', color='blue')
            plt.title("Évolution des événements critiques par date")
            plt.xlabel("Date")
            plt.ylabel("Nombre d'événements critiques")
            plt.grid(True)
            plt.xticks(rotation=45)
            plt.tight_layout()
            plt.show()
        else:
            print("Aucun log à afficher.")
 


    def persister_evenements_critique(self):
        """
        Stock les événements critiques du DataFrame dans une base de données SQLite.
        Évite les doublons en vérifiant l'existence avant l'insertion.
        """
        if self.df_logs.empty:
            print("Le DataFrame est vide. Aucune donnée à stocker.")
            return

        try:
            cn = sqlite3.connect('logs_analyses.db')
            cur = cn.cursor()

            # Création de la table si elle n'existe pas
            cur.execute('''
                CREATE TABLE IF NOT EXISTS evenement_suspect (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date_heure DATETIME,
                    evenement TEXT,
                    utilisateur TEXT,
                    adresse_ip TEXT,
                    UNIQUE(date_heure, evenement, utilisateur, adresse_ip) -- Empêche les doublons
                )
            ''')
            cn.commit()
            print("[+] Table 'evenement_suspect' créée ou déjà existante.")

            count_inserts = 0
            for index, ligne in self.df_logs.iterrows():
                try:
                    # Verification que la date est bien formatée
                    if not isinstance(ligne['DateHeure'], datetime):
                        date_obj = parse_date(ligne['DateHeure'])
                    else:
                        date_obj = ligne['DateHeure']
                    date_formatted = date_obj.strftime('%Y-%m-%d %H:%M:%S')

                    # Vérification si l'événement existe déjà
                    cur.execute('''
                        SELECT COUNT(*) FROM evenement_suspect 
                        WHERE date_heure = ? AND evenement = ? AND utilisateur = ? AND adresse_ip = ?
                    ''', (date_formatted, ligne['Evenement'], ligne['Utilisateur'], ligne['AdresseIP']))
                    existe = cur.fetchone()[0]

                    if existe == 0:
                        # Insére seulement si l'événement n'existe pas
                        cur.execute('''
                            INSERT INTO evenement_suspect (date_heure, evenement, utilisateur, adresse_ip)
                            VALUES (?, ?, ?, ?)
                        ''', (date_formatted, ligne['Evenement'], ligne['Utilisateur'], ligne['AdresseIP']))
                        count_inserts += 1
                        print(f"[+] Insertion réussie pour la ligne {index}: {date_formatted}, {ligne['Evenement']}, {ligne['Utilisateur']}, {ligne['AdresseIP']}")
                    else:
                        print(f"[+] Ligne {index} déjà existante, non insérée.")

                except Exception as e:
                    print(f"Erreur lors de l'insertion de la ligne {index}: {e}")

            cn.commit()
            cn.close()
            print(f"Les événements critiques ont été persistés avec succès ({count_inserts} nouvelles lignes insérées).")

        except Exception as e:
            print(f" ⚠️ Erreur lors de la persistance des événements critiques : {e}")
