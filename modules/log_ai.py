from openai import OpenAI
import configparser
import json
 
class LogAI:
    def __init__(self, logs):
        """
        Initialise la classe avec une liste de lignes de log et lit la clé API OpenAI.

        Paramètres :
        logs (list) : Une liste contenant plusieurs lignes de logs à analyser.
        """
        self.logs = logs
 
        # Initialisation du client avec la clé API
        self.client = OpenAI(
            api_key=self.__lire_cle_api()
        )
 
        self.reponse_gpt_json = None
 
    def __lire_cle_api(self):
        """
        Lit la clé API OpenAI à partir du fichier de configuration 'config.ini'.
 
        Retourne :
        str : La clé API OpenAI.
        """
        config = configparser.ConfigParser()
        config.read('config.ini') 
 
        try:
            api_key = config['openai']['api_key']
            return api_key
        except KeyError:
            raise KeyError("La clé API OpenAI n'a pas été trouvée dans 'config.ini'. Vérifiez le fichier.")
 
    def analyser_logs_avec_gpt(self):
        """
        Utilise l'API d'OpenAI pour analyser les logs d'authentification et détecter des comportements suspects,
        en demandant une réponse structurée en JSON.
 
        Retourne :
        dict : Un dictionnaire contenant le resultat des logs sous forme JSON.
        """
        # Convertir la liste de logs en une chaîne de caractères
        logs_str = "\n".join(self.logs)
 
        # Demander à GPT de formater la réponse en JSON
        prompt = f"""
        Voici des logs d'authentification. Analyse-les et formate la réponse en JSON,sans accent pour tout les mots et je souhaite que les reponses soit technique.
        Les tentatives d'instrusions seront plusieurs tentatives avec la même adresse IP, n'utilise pas le mot securité dans tes reponses.
        Pour chaque ligne de log enleve les accents afin que ma reponse en JSON soit bien interpreté, indique si c'est une tentative d'intrusion sous la forme :
        [{{
            "log": "<contenu_du_log>",
            "intrusion_detectee": <True/False>,
            "raison": "<explication>"
            "remediation : "<explication>"
        }}]
 
        Logs :
        {logs_str}
        """
 
        # Appel à l'API OpenAI pour interroger GPT
        reponse = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": prompt}
            ],
            max_tokens=4096,
            temperature=0.3
        )
 
        # Retourne la réponse générée par GPT
        reponse_gpt = reponse.choices[0].message.content
 
        # Tenter de convertir la réponse en JSON
        try:
            self.reponse_gpt_json = json.loads(reponse_gpt)
        except json.JSONDecodeError:
            raise ValueError("La réponse de GPT n'est pas un JSON valide. Voici la réponse brute :\n" + reponse_gpt)
 
    def dump_reponse(self):
        """
        Écrit la réponse JSON générée par GPT en texte.
 
        Paramètres :
        chemin_fichier (str) : Le chemin du fichier où écrire la réponse JSON.
        """
        if self.reponse_gpt_json:
            return json.dumps(self.reponse_gpt_json, indent=4)
        else:
            raise ValueError("Aucune réponse JSON n'a été générée.")
