@login_required
def telecharger_cv(request):
    if request.method == "POST":
        user = request.user

        # 🔹 Récupérer les valeurs
        nom = request.POST.get("nom", "").strip()
        prenom = request.POST.get("prenom", "").strip()
        titre_poste = request.POST.get("posttitle", "").strip()
        informations = request.POST.get("Informations", "").strip()
        competences = request.POST.get("competences", "").strip()
        certificats = request.POST.get("certificats", "").strip()
        experience = request.POST.get("experience", "").strip()
        langues = request.POST.get("Langues", "").strip()
        description = request.POST.get("Description", "").strip()
        modele_option = request.POST.get("modele_option", "choisir")
        rajouter = request.POST.get("rajouter", "").strip()
        theme = request.POST.get("theme", "theme1")
        infos_entreprise = request.POST.get("infos_entreprise", "non")

        # ✅ Style personnalisé
        font_family = request.POST.get("font_family", "Helvetica")
        font_size = int(request.POST.get("font_size", 13))
        color_titles = request.POST.get("color_titles", "#000000")
        color_details = request.POST.get("color_details", "#333333")

        # 🔹 Enregistrer le candidat
        candidat = Candidat.objects.create(
            user=user,
            nom=nom,
            prenom=prenom,
            titre_poste=titre_poste,
            description_profil=description,
            langues=langues,
            experience=experience,
            certificats=certificats,
            competences=competences,
            informations_contact=informations,
        )

        # 🔹 Charger le fond
        from reportlab.lib.utils import ImageReader
        if modele_option == "upload" and request.FILES.get("modele_file"):
            uploaded_file = request.FILES["modele_file"]
            theme_img = ImageReader(uploaded_file)
        else:
            theme_img_path = os.path.join(
                settings.BASE_DIR, "dashboard", "static", "themes", f"{theme}.png"
            )
            if not os.path.exists(theme_img_path):
                return HttpResponse("Template image introuvable", status=404)
            theme_img = ImageReader(theme_img_path)

        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            leftMargin=2*cm,
            rightMargin=2*cm,
            topMargin=7*cm,
            bottomMargin=3*cm
        )

        # Styles dynamiques
        styles = getSampleStyleSheet()
        style_titles = ParagraphStyle("titles", parent=styles["Normal"],
                                      fontName=font_family, fontSize=font_size,
                                      textColor=color_titles, leading=font_size+5)
        style_details = ParagraphStyle("details", parent=styles["Normal"],
                                       fontName=font_family, fontSize=font_size,
                                       textColor=color_details, leading=font_size+5)

        def make_list(label, value):
            """Affiche une section seulement si non vide"""
            if not value:
                return []
            items = [Paragraph(f"<b>{label} :</b>", style_titles)]
            separators = [",", "\n", ";"]
            for sep in separators:
                if sep in value:
                    parts = [p.strip() for p in value.split(sep) if p.strip()]
                    break
            else:
                parts = [value.strip()]
            for line in parts:
                items.append(Paragraph(f"- {line}", style_details))
            items.append(Spacer(1, 12))
            return items

        story = []

        # Champs simples uniquement s’ils ne sont pas vides
        if nom:
            story.append(Paragraph(f"<b>Nom :</b> {nom}", style_titles))
        if prenom:
            story.append(Paragraph(f"<b>Prénom :</b> {prenom}", style_titles))
        if titre_poste:
            story.append(Paragraph(f"<b>Titre du poste :</b> {titre_poste}", style_titles))

        story.append(Spacer(1, 12))

        # Champs multi-lignes
        story += make_list("Informations", informations)
        story += make_list("Compétences", competences)
        story += make_list("Expérience", experience)
        story += make_list("Certificats", certificats)
        story += make_list("Langues", langues)
        story += make_list("Description", description)
        story += make_list("Autres", rajouter)

        # ✅ fond + logo + footer
        def draw_background(canvas, doc):
            width, height = A4
            canvas.drawImage(theme_img, 0, 0, width=width, height=height)
            if user.logo:
                logo_path = os.path.join(settings.MEDIA_ROOT, str(user.logo))
                if os.path.exists(logo_path):
                    canvas.drawImage(
                        logo_path,
                        (width - 4*cm)/2, height - 5*cm,
                        width=4*cm, height=4*cm,
                        preserveAspectRatio=True, mask="auto"
                    )
            if infos_entreprise == "oui":
                canvas.setFont("Helvetica-Bold", 9)
                footer_text = f"{user.company_name or ''} | {user.company_address or ''} | {user.company_phone or ''}"
                if user.company_kbis:
                    footer_text += f" | KBIS: {user.company_kbis}"
                canvas.drawCentredString(width/2, 1.5*cm, footer_text)

        doc.build(story, onFirstPage=draw_background, onLaterPages=draw_background)

        # 🔹 Stats
        user.cv_download_count += 1
        user.nombre_cv_total += 1
        user.nombre_cv_peut_telecharger -= 1
        debut_mois = user.abonnement_debut.replace(day=1)
        if candidat.date_creation.date() >= debut_mois:
            user.nombre_cv_mois += 1
        user.save()

        # 🔹 Réponse
        buffer.seek(0)
        filename = f"{user.company_name or 'Entreprise'}_{nom or ''}_{prenom or ''}.pdf"
        response = HttpResponse(buffer, content_type="application/pdf")
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response

    return HttpResponse("Méthode non autorisée", status=405)

