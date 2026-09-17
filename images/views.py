import base64
import json
import math
import uuid

from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404, redirect, render

from .models import CroppedImage


def index(request):
    """
    Page principale.

    GET :
        Affiche le cropper et la liste des images enregistrées.

    POST :
        Crée une nouvelle image ou modifie un crop existant.
    """

    if request.method == "POST":

        original = request.FILES.get("original")
        cropped_data = request.POST.get("cropped")

        crop_x = request.POST.get("crop_x")
        crop_y = request.POST.get("crop_y")
        crop_width = request.POST.get("crop_width")
        crop_height = request.POST.get("crop_height")
        image_transform = request.POST.get("image_transform")

        image_id = request.POST.get("image_id")

        # ---------------------------------------------------------
        # Vérifications
        # ---------------------------------------------------------

        if not cropped_data:
            return render(
                request,
                "images/index.html",
                {
                    "images": CroppedImage.objects.all(),
                    "error": "Veuillez d'abord recadrer l'image.",
                },
            )

        if not all(
            value is not None
            for value in [
                crop_x,
                crop_y,
                crop_width,
                crop_height,
            ]
        ):
            return render(
                request,
                "images/index.html",
                {
                    "images": CroppedImage.objects.all(),
                    "error": "Les coordonnées du crop sont manquantes.",
                },
            )

        # ---------------------------------------------------------
        # Décodage de l'image cropée
        # ---------------------------------------------------------

        try:

            header, encoded = cropped_data.split(",", 1)

            image_data = base64.b64decode(encoded)

        except (ValueError, base64.binascii.Error):

            return render(
                request,
                "images/index.html",
                {
                    "images": CroppedImage.objects.all(),
                    "error": "L'image cropée est invalide.",
                },
            )

        try:
            image_transform = json.loads(image_transform)
        except (TypeError, json.JSONDecodeError):
            image_transform = []

        # ---------------------------------------------------------
        # Conversion des coordonnées
        # ---------------------------------------------------------

        try:

            crop_x = float(crop_x)
            crop_y = float(crop_y)
            crop_width = float(crop_width)
            crop_height = float(crop_height)

        except (TypeError, ValueError):

            return render(
                request,
                "images/index.html",
                {
                    "images": CroppedImage.objects.all(),
                    "error": "Les coordonnées du crop sont invalides.",
                },
            )


        # Vérification des valeurs numériques

        if not all(
            math.isfinite(value)
            for value in [
                crop_x,
                crop_y,
                crop_width,
                crop_height,
            ]
        ):

            return render(
                request,
                "images/index.html",
                {
                    "images": CroppedImage.objects.all(),
                    "error": "Les coordonnées du crop sont invalides.",
                },
            )


        # Vérification de la taille du crop

        if crop_width <= 0 or crop_height <= 0:

            return render(
                request,
                "images/index.html",
                {
                    "images": CroppedImage.objects.all(),
                    "error": "Les dimensions du crop sont invalides.",
                },
            )

        # ---------------------------------------------------------
        # MODIFICATION d'un crop existant
        # ---------------------------------------------------------

        if image_id:

            image = get_object_or_404(
                CroppedImage,
                pk=image_id,
            )

            # On ne remplace PAS l'original.
            #
            # On remplace uniquement le crop.

            filename = f"{uuid.uuid4()}.png"

            cropped_file = ContentFile(
                image_data,
                name=filename,
            )

            # Suppression de l'ancien fichier cropé
            if image.cropped:
                image.cropped.delete(save=False)

            # Nouveau crop
            image.cropped.save(
                filename,
                cropped_file,
                save=False,
            )

            # Nouvelles coordonnées
            image.crop_x = crop_x
            image.crop_y = crop_y
            image.crop_width = crop_width
            image.crop_height = crop_height
            image.image_transform = image_transform

            image.save()

            return redirect("images:index")

        # ---------------------------------------------------------
        # CRÉATION d'une nouvelle image
        # ---------------------------------------------------------

        if not original:

            return render(
                request,
                "images/index.html",
                {
                    "images": CroppedImage.objects.all(),
                    "error": "Veuillez sélectionner une image originale.",
                },
            )

        # ---------------------------------------------------------
        # Création de l'objet
        # ---------------------------------------------------------

        image = CroppedImage()

        image.original.save(
            original.name,
            original,
            save=False,
        )

        # ---------------------------------------------------------
        # Enregistrement du crop
        # ---------------------------------------------------------

        filename = f"{uuid.uuid4()}.png"

        cropped_file = ContentFile(
            image_data,
            name=filename,
        )

        image.cropped.save(
            filename,
            cropped_file,
            save=False,
        )

        # ---------------------------------------------------------
        # Coordonnées
        # ---------------------------------------------------------

        image.crop_x = crop_x
        image.crop_y = crop_y
        image.crop_width = crop_width
        image.crop_height = crop_height
        image.image_transform = image_transform

        # ---------------------------------------------------------
        # Sauvegarde
        # ---------------------------------------------------------

        image.save()

        return redirect("images:index")

    # -------------------------------------------------------------
    # GET
    # -------------------------------------------------------------

    images = CroppedImage.objects.all()

    return render(
        request,
        "images/index.html",
        {
            "images": images,
        },
    )
