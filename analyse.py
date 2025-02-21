import argparse
import emoji
from colorama import Fore, Style, init, Back
from modules.log_reader import LogReader
from modules.log_analyzer import LogAnalyzer
from modules.log_ai import LogAI  # Importer la classe LogAI pour l'option GPT
from modules.notification import Notification  # Import de la classe Notification
from modules.notification_slack import SlackNotification  # Pour l'envoi de notifications Slack
import schedule
import time  # Nécessaire pour le délai entre les exécutions
from datetime import datetime # pour afficher l'heure entre les exécutions

init(autoreset=True)

banner = f"""{Fore.CYAN}
  _            _____  _____                     _               _____ 
 | |          / ____|/ ____|                   | |        /\\   |_   _|
 | |     ___ | |  __| |  __ _   _  __ _ _ __ __| |______ /  \\    | |  
 | |    / _ \\| | |_ | | |_ | | | |/ _` | '__/ _` |______/ /\\ \\   | |  
 | |___| (_) | |__| | |__| | |_| | (_| | | | (_| |     / ____ \\ _| |_ 
 |______\\___/ \\_____|\\_____|\\__,_|\\__,_|_|  \\__,_|    /_/    \\_\\_____|

 By Houssam GOURINE & Lorenzo GIUSTINO with love <3
{Style.RESET_ALL}                                                               
"""
def analyser_logs(args):
    """
    Fonction principale d'analyse des logs. Cette fonction sera appelée à chaque exécution programmée.
    Elle prend les arguments fournis en ligne de commande via l'objet args.
    """
    print(f"{banner} \n🔎 Démarrage de l'analyse des logs à {datetime.now()}")

    # Créer une instance de LogReader avec le chemin du répertoire
    lecteur = LogReader(args.repertoire)

    # Trouver tous les fichiers de logs correspondant au pattern dans le répertoire
    fichiers_logs = lecteur.trouver_fichiers_logs(pattern=args.pattern)

    # Si des fichiers de logs sont trouvés, les lire un par un et extraire les informations
    if fichiers_logs:
        for fichier_log in fichiers_logs:
            print(f"\n{Fore.GREEN}[+]Lecture du fichier :{Style.RESET_ALL} {fichier_log}")

        # Option 1 : Utiliser GPT pour analyser les logs avec OpenAI (si --use-gpt est spécifié)
        if args.use_gpt:
            print(f"\n{Fore.GREEN}[+]Analyse des logs avec GPT via l'API OpenAI...{Style.RESET_ALL}")

            # Lire les logs bruts pour l'analyse avec GPT
            lecteur.lire_logs_bruts(fichier_log)
            # Créer une instance de LogAI avec la liste de logs
            analyseur_ai = LogAI(lecteur.lignes_extraites_brut[:10])  # Limiter à 10 lignes pour l'exemple

            # Analyser les logs avec OpenAI GPT
            try:
                analyseur_ai.analyser_logs_avec_gpt()
                print(f"\n{Fore.GREEN}[+]Résultat de l'analyse par GPT en JSON :{Style.RESET_ALL}")
                print(analyseur_ai.dump_reponse())  # Afficher la réponse JSON
            except ValueError as e:
                print(e)

        # Analyse traditionnelle des logs
        else:
            # Lecture et extraction de toutes les données de tous les fichiers
            for fichier_log in fichiers_logs:
                lecteur.lire_et_extraire_logs(fichier_log)
            print("\nAnalyse des logs avec les méthodes traditionnelles...")
            lecteur.creer_dataframe()

            # Créer une instance de LogAnalyzer pour analyser les logs
            analyseur = LogAnalyzer(lecteur.df_logs)

            # Analyser la fréquence des adresses IP dans l'intervalle de temps spécifié
            lignes_suspectes = analyseur.analyser_frequence_ips(intervalle_temps=args.intervalle, seuil_alerte=args.seuil)

            if lignes_suspectes:
                if args.graphe:
                    # Afficher un graphe des événements critiques
                    analyseur.afficher_evenements_par_date()

                if args.notifier:
                    # Envoyer une notification par email si des événements critiques sont détectés
                    print(f"\n{Fore.RED}[🚨]Événements critiques détectés, envoi d'une notification par email...{Style.RESET_ALL}")

                    # Créer une instance de Notification avec le fichier de configuration
                    notification = Notification()

                    # Envoyer la notification avec les événements critiques
                    notification.envoyer_notification_evenements_critiques(lignes_suspectes[:10])

                if args.slack:
                    print(f"\n{Fore.RED}[🚨]Évènements critiques détectés, envoi d'une notification via Slack...{Style.RESET_ALL}")
                    slack_notif = SlackNotification()  # Utilise l'URL par défaut
                    
                    message_slack = "Alerte : Évènements critiques détectés dans les logs.\n"
                    for log in lignes_suspectes:
                        message_slack += f"- {log}\n"
                    slack_notif.envoyer_notification(message_slack)

                if args.persister:
                    # Persister les événements critiques dans une base de données SQLite
                    print(f"{Fore.RED}[+]Persistance des événements critiques dans une base de données SQLite...{Style.RESET_ALL}")
                    analyseur.persister_evenements_critique()
            else:
                print(f"{Fore.GREEN}Aucun événement critique détecté.{Style.RESET_ALL}")

            # Afficher le DataFrame contenant les informations extraites
            # lecteur.afficher_dataframe()
    else:
        print(f"⚠️Aucun fichier de logs correspondant au pattern '{args.pattern}' n'a été trouvé dans le répertoire.")

def main():
    # Gestion des arguments en ligne de commande
    parser = argparse.ArgumentParser(description="Script d'analyse de logs")
    parser.add_argument("repertoire", help="Chemin vers le répertoire contenant les fichiers de logs", type=str)
    parser.add_argument("--pattern", help="Pattern pour filtrer les fichiers de logs (par défaut 'secure*')", type=str, default="secure*")
    parser.add_argument("--seuil", help="Seuil d'alerte pour les adresses IP suspectes", type=int, default=2)
    parser.add_argument("--intervalle", help="Intervalle de temps pour l'analyse des accès (par défaut '1min')", type=str, default="1min",)
    parser.add_argument("--use-gpt", help="Utiliser GPT pour l'analyse des logs avec OpenAI", action="store_true", default=False)
    parser.add_argument("--notifier", help="Notifier les évènements critiques par e-mail", action="store_true", default=False)
    parser.add_argument("--graphe", help="Afficher un graphe des évènements critiques", action="store_true",default=False)
    parser.add_argument("--slack", help="Notifier les évènements critiques via Slack", action="store_true", default=False)
    parser.add_argument("--persister", help="Persister les évènements critiques dans SQLite", action="store_true", default=False)
    parser.add_argument("--planifier", help="Planification du script, indiquer le nombre de minutes entre chaque exécution", type=int)
    args = parser.parse_args()

    # Si l'option --planifier est utilisée, planifier l'exécution du script
    if args.planifier:
        print(f"\n{Fore.GREEN}[+] 📅 Planification du script toutes les {args.planifier} minutes.")

        # Planifier l'analyse des logs en fonction de l'intervalle spécifié
        schedule.every(args.planifier).minutes.do(analyser_logs, args=args)

        # Boucle infinie pour exécuter les tâches planifiées
        while True:
            schedule.run_pending()
            time.sleep(1)
    else:
        # Si la planification n'est pas spécifiée, exécuter une seule fois
        analyser_logs(args)

if __name__ == "__main__":
    main()
