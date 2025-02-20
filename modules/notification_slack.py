import requests
import json
from colorama import Fore, Style, init, Back

class SlackNotification:
    """
    Permet d'envoyer des notifications sur un channel Slack
    via un webhook.
    """
    def __init__(self, webhook_url="https://hooks.slack.com/services/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"):
        """
        Initialise la classe SlackNotification avec l'URL du webhook Slack.
        """
        self.webhook_url = webhook_url
 
    def envoyer_notification(self, message):
        """
        Envoie une notification Slack.
        """
        payload = {"text": message}
        headers = {"Content-Type": "application/json"}
 
        try:
            response = requests.post(
                self.webhook_url,
                headers=headers,
                data=json.dumps(payload)
            )
            if response.status_code != 200:
                raise ValueError(
                    f"Erreur {response.status_code} lors de l'envoi : {response.text}"
                )
            print("Notification Slack envoyée avec succès.")
        except Exception as e:
            print(f"Erreur lors de l'envoi de la notification Slack : {e}")