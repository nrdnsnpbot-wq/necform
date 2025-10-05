import pytesseract
from pdf2image import convert_from_bytes
from PIL import Image
import re
import json
from groq import Groq

from dotenv import load_dotenv
import os
load_dotenv()
api_key = os.getenv("GROQ_API_KEY")

client = Groq(api_key=api_key)

def extract_text_from_file(cv_file):
    text = ""

    if cv_file.name.endswith(".pdf"):
        images = convert_from_bytes(cv_file.read())
        for image in images:
            text += pytesseract.image_to_string(image)
    else:
        image = Image.open(cv_file)
        text = pytesseract.image_to_string(image)

    return text

def parse_text(text):
    nom = re.search(r"Nom[:\s]*([A-Z][a-z]+)", text)
    prenom = re.search(r"Prénom[:\s]*([A-Z][a-z]+)", text)
    linkedin = re.search(r"(https?://www\.linkedin\.com/in/[^\s]+)", text)
    competences = re.findall(r"\b(Python|Django|React|SQL|Machine Learning|Flask|Java)\b", text, re.I)
    certificats = re.findall(r"(Certificat\s+\w+)", text)

    return {
        "nom": nom.group(1) if nom else "",
        "prenom": prenom.group(1) if prenom else "",
        "competences": ", ".join(set(competences)),
        "certificats": ", ".join(certificats),
        "linkedin": linkedin.group(1) if linkedin else "",
    }

def extraire_infos_depuis_cv(cv_file):
    texte_de_cv = extract_text_from_file(cv_file)
    prompt = f"""
    IMPORTANT : Réponds uniquement avec du JSON valide. 
    Pas de texte ou d'explication en dehors du JSON. 

    Tu es un assistant Python spécialisé dans l'extraction d'informations depuis des CV.
    Le texte brut extrait du CV est le suivant :
    \"\"\"{texte_de_cv}\"\"\"

    Ta tâche est d'extraire les informations suivantes, même si elles ne sont pas toutes présentes.
    Si une information n’est pas trouvée, mets simplement une chaîne vide ("") ou une liste vide ([]).

    - "nom" (string)
    - "prenom" (string)
    - "posttitle" (string) → titre du poste recherché ou actuel
    - "Informations" (string) → coordonnées (téléphone, email, adresse…)
    - "competences" (liste de string)
    - "certificats" (liste de string)
    - "experience" (liste de string) → expériences professionnelles
    - "Langues" (liste de string)
    - "Description" (string) → résumé / profil personnel
    - "linkedin" (string) → ou autre lien de portfolio/profil pro/email si LinkedIn absent

    Retourne uniquement le JSON suivant et rien d’autre :

    {{
      "nom": "...",
      "prenom": "...",
      "posttitle": "...",
      "Informations": "...",
      "competences": ["...", "..."],
      "certificats": ["...", "..."],
      "experience": ["...", "..."],
      "Langues": ["...", "..."],
      "Description": "...",
      "linkedin": "..."
    }}
    """

    try:
        response = client.chat.completions.create(
            model="llama3-70b-8192",  
            messages=[
                {"role": "system", "content": "Tu es un assistant expert en extraction d'informations de CV."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1
        )

        content = response.choices[0].message.content.strip()
        data = json.loads(content)
        return data

    except json.JSONDecodeError as e:
        print("❌ Erreur JSON :", e)
        print("Contenu reçu :", content)
        return None
    except Exception as e:
        print(" Erreur d'exécution LLaMA :", e)
        return None
    
def formatter_resultat_cv(cv_file):
    """
    Prend un dictionnaire contenant les infos extraites du CV
    et retourne une liste ordonnée : [nom, prenom, competences, certificats, linkedin]
    """
    data = extraire_infos_depuis_cv(cv_file)
    if not data:
        return ["", "", [], [], ""]
    
    nom = data.get("nom", "")
    prenom = data.get("prenom", "")
    competences = data.get("competences", [])
    certificats = data.get("certificats", [])
    linkedin = data.get("linkedin", "")

    return [nom, prenom, competences, certificats, linkedin]

"""with open("cv.pdf", "rb") as f:
    resultats = formatter_resultat_cv(f)
    print(resultats)"""