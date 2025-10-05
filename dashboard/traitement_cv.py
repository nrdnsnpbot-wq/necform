import pytesseract
from pdf2image import convert_from_bytes
from PIL import Image
import re
import json
from groq import Groq
import ast
from dotenv import load_dotenv
import os 

load_dotenv()
api_key = os.getenv("GROQ_API_KEY")

client = Groq(api_key=api_key)

import docx2txt
import textract
from PIL import Image
import pytesseract
from pdf2image import convert_from_bytes

def extract_text_from_file(cv_file):
    text = ""
    filename = cv_file.name.lower()

    try:
        # 1️⃣ Cas Word (.docx / .doc)
        if filename.endswith(".docx"):
            text = docx2txt.process(cv_file)
            if not text.strip():  # fallback si docx2txt échoue
                text = textract.process(cv_file).decode("utf-8", errors="ignore")

        elif filename.endswith(".doc"):
            text = textract.process(cv_file).decode("utf-8", errors="ignore")

        # 2️⃣ Cas PDF (OCR obligatoire)
        elif filename.endswith(".pdf"):
            images = convert_from_bytes(cv_file.read())
            for image in images:
                text += pytesseract.image_to_string(image, lang="fra+eng")

        # 3️⃣ Cas image (jpg, png, etc.)
        else:
            image = Image.open(cv_file)
            text = pytesseract.image_to_string(image, lang="fra+eng")

    except Exception as e:
        print("❌ Erreur lors de l'extraction :", e)
        text = ""

    return text.strip()

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

def _extract_json_substring(text):
    """Tente d'extraire le bloc JSON dans une réponse qui peut contenir du texte."""
    # Supprime balises de code communes
    text = text.strip()
    text = text.replace("```json", "").replace("```", "")

    # Cherche le premier '{' et le dernier '}' pour extraire un JSON potentiel
    start = text.find('{')
    end = text.rfind('}')
    if start != -1 and end != -1 and end > start:
        return text[start:end+1]
    return text

def _normalize_experience_item(item):
    """Retourne un dict {poste, entreprise, periode, details} quel que soit le format d'entrée."""
    if isinstance(item, dict):
        # Cherche clés possibles (FR/EN), assure chaînes propres
        def get(*keys):
            for k in keys:
                if k in item and item[k]:
                    return str(item[k]).strip()
            # lowercase keys fallback
            for k, v in item.items():
                if k.lower() in [kk.lower() for kk in keys] and v:
                    return str(v).strip()
            return ""
        poste = get("poste", "title", "poste_title", "position", "job")
        entreprise = get("entreprise", "company", "employer", "organisation")
        periode = get("periode", "period", "dates", "date")
        details = get("details", "description", "missions", "details")
        return {"poste": poste, "entreprise": entreprise, "periode": periode, "details": details}

    if isinstance(item, str):
        # heuristique: split lignes non vides
        lines = [l.strip() for l in item.splitlines() if l.strip()]
        # détecte années/periodes (ex: 07/2021, 2021, 2018-2020)
        periode_match = re.search(r'(\d{2}[/\-]\d{4}|\d{4}(?:\s*-\s*\d{4})?)', item)
        periode = periode_match.group(0) if periode_match else ""
        entreprise = ""
        poste = ""
        details = ""

        if len(lines) >= 3:
            # hypothèse: ligne 1 = entreprise (souvent en maj), ligne 2 = titre, reste = détails
            entreprise = lines[0] if lines[0].isupper() else ""
            if entreprise:
                poste = lines[1]
                details = "\n".join(lines[2:])
            else:
                poste = lines[0]
                details = "\n".join(lines[1:])
        elif len(lines) == 2:
            poste, details = lines[0], lines[1]
        elif len(lines) == 1:
            posta = lines[0]
            # si contient virgule ou ' - ' on tente de scinder
            if " - " in lines[0]:
                parts = lines[0].split(" - ", 1)
                poste, entreprise = parts[0], parts[1]
            elif "," in lines[0]:
                parts = lines[0].split(",", 1)
                poste, details = parts[0], parts[1]
            else:
                poste = lines[0]
        return {"poste": poste.strip(), "entreprise": entreprise.strip(), "periode": periode.strip(), "details": details.strip()}

    # fallback vide
    return {"poste": "", "entreprise": "", "periode": "", "details": ""}

def extraire_infos_depuis_cv(cv_file):
    texte_de_cv = extract_text_from_file(cv_file)  # ta fonction OCR/lecture existante
    # Échapper accolades pour éviter conflits avec .format()
    safe_text = texte_de_cv.replace("{", "{{").replace("}", "}}")

    prompt_template = """
IMPORTANT : Réponds uniquement avec du JSON valide.
Pas de texte ou d'explication en dehors du JSON.

Tu es un assistant Python spécialisé dans l'extraction d'informations depuis des CV.
Le texte brut extrait du CV est le suivant :
\"\"\"{texte_cv}\"\"\"

Ta tâche est d'extraire les informations suivantes.  
⚠️ IMPORTANT : 
    - Ne résume rien.  
    - Ne supprime rien.  
    - Garde tout le contenu détaillé des expériences (technos, missions, puces, phrases).  
    - Copie intégralement les descriptions et listes telles qu’elles apparaissent dans le CV.

Champs attendus :
- "nom" (string)
- "prenom" (string)
- "posttitle" (string)
- "contact" (liste d’objets) → chaque objet contient :
    - "type" (ex: "email", "téléphone", "adresse")
    - "valeur" (string)
- "competences" (liste d’objets) → chaque objet contient :
    - "titre" (ex: "DevOps", "Développement", "Cloud")
    - "details" (liste de string → ex: ["Java", "Spring", "Docker", "Kubernetes"])
- "certificats" (liste de string)
- "formations" (liste d’objets) → chaque objet contient :
    - "diplome"
    - "ecole"
    - "lieu"
    - "periode"
    - "details"
- "experience" (liste d’objets) → chaque objet contient :
    - "poste"
    - "entreprise"
    - "lieu"
    - "periode"
    - "details" (⚠️ texte brut intégral, même long, sans résumé)
- "Langues" (liste de string)
- "Description" (string)
- "linkedin" (string)

Retourne uniquement un JSON strictement valide, sous cette forme :

{{
    "nom": "",
    "prenom": "",
    "posttitle": "",
    "contact": [
        {{
            "type": "email",
            "valeur": ""
        }},
        {{
            "type": "téléphone",
            "valeur": ""
        }}
    ],
    "competences": [
        {{
            "titre": "",
            "details": ["", ""]
        }}
    ],
    "certificats": [],
    "formations": [
        {{
            "diplome": "",
            "ecole": "",
            "lieu": "",
            "periode": "",
            "details": ""
        }}
    ],
    "experience": [
        {{
            "poste": "",
            "entreprise": "",
            "lieu": "",
            "periode": "",
            "details": ""
        }}
    ],
    "Langues": [],
    "Description": "",
    "linkedin": ""
}}
"""

    prompt = prompt_template.format(texte_cv=safe_text)

    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "Tu es un assistant expert en extraction d'informations de CV."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
        )

        content = response.choices[0].message.content.strip()
        json_sub = _extract_json_substring(content)

        data = None
        try:
            data = json.loads(json_sub)
        except Exception:
            clean = json_sub.replace("“", '"').replace("”", '"').replace("`", '"')
            try:
                data = json.loads(clean)
            except Exception:
                try:
                    data = ast.literal_eval(clean)
                except Exception as e:
                    print("❌ Impossible de parser JSON reçu :", e)
                    print("Contenu brut reçu :", content)
                    return None

        # Normalisation expérience
        if "experience" in data:
            exps = data.get("experience") or []
            normalized = []
            for item in exps:
                normalized.append(_normalize_experience_item(item))
            data["experience"] = normalized

        # Normalisation des contacts (si jamais renvoyé en liste brute)
        if "contact" in data:
            contacts = []
            if isinstance(data["contact"], list):
                for c in data["contact"]:
                    if isinstance(c, str):
                        # heuristique simple
                        if "@" in c:
                            contacts.append({"type": "email", "valeur": c})
                        elif any(ch.isdigit() for ch in c):
                            contacts.append({"type": "téléphone", "valeur": c})
                        else:
                            contacts.append({"type": "autre", "valeur": c})
                    elif isinstance(c, dict):
                        contacts.append(c)
            elif isinstance(data["contact"], str):
                contacts.append({"type": "autre", "valeur": data["contact"]})
            data["contact"] = contacts

        return data

    except Exception as e:
        print("❌ Erreur appel LLM :", e)
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