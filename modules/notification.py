import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import configparser
import os
from colorama import Fore, Style, init, Back
 
class Notification:
    def __init__(self, config_path="config.ini"):
        """
        Lance la classe Notification en lisant la configuration SMTP
        et l'adresse du destinataire depuis un fichier de configuration.
        """
        if not os.path.exists(config_path):
            print(f"Fichier de configuration '{config_path}' introuvable.")
       
        self.config = configparser.ConfigParser()
        self.config.read(config_path)
 
        try:
            self.smtp_server   = self.config['smtp']['server']
            self.smtp_port     = int(self.config['smtp']['port'])
            self.smtp_user     = self.config['smtp']['user']
            self.smtp_password = self.config['smtp']['password']
            self.recipient     = self.config['email']['recipient']
        except KeyError as e:
            print(f"Clé manquante dans la configuration : {e}")
        except Exception as e:
            print(f"Erreur lors de la lecture du fichier de configuration : {e}")
 
    def envoyer_email(self, sujet, contenu):
        """
        Envoie un email avec le sujet et le contenu spécifiés, en utilisant
        les paramètres SMTP et l'adresse destinataire lus dans le fichier de configuration.
        """
        msg = MIMEMultipart()
        msg['From'] = self.smtp_user
        msg['To']   = self.recipient
        msg['Subject'] = sujet
 
        # Ajouter le corps du mail
        msg.attach(MIMEText(contenu, 'plain'))
 
        try:
            print(f"[+] Connexion au serveur SMTP : {self.smtp_server}:{self.smtp_port}")
            with smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=30) as serveur:
                serveur.ehlo()
                print("[+] Passage en mode TLS...")
                serveur.starttls()
                # Certains serveurs exigent un second EHLO après le STARTTLS
                serveur.ehlo()
 
                print(f"[+] Authentification en tant que {self.smtp_user}")
                serveur.login(self.smtp_user, self.smtp_password)
 
                print("[+] Envoi du message...")
                serveur.sendmail(self.smtp_user, self.recipient, msg.as_string())
 
            print(f"[+]Email envoyé avec succès à {self.recipient}")
 
        except Exception as e:
            print(f"Erreur lors de l'envoi de l'email : {e}")
 
    def envoyer_notification_evenements_critiques(self, logs_critiques):
        """
        Prépare et envoie un email contenant les événements critiques détectés dans les logs.
        """
        sujet = "Alerte : Événements critiques détectés dans les logs"
        contenu = "Bonjour,\n\nLes événements suivants ont été détectés comme critiques dans les logs :\n\n"
 
        for log in logs_critiques:
            contenu += f"- {log}\n"
 
        contenu += "\nVotre système de surveillance."
 
        self.envoyer_email(sujet, contenu)
