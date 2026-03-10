# Migration pour ajouter les champs Le Dome aux categories et niveaux.
# Tous les champs ont des valeurs par defaut, pas de data migration necessaire.
# Migration to add Le Dome fields to categories and levels.
# All fields have defaults, no data migration needed.

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("badge_generator", "0001_initial"),
    ]

    operations = [
        # Champs pour BadgeCategory.
        # BadgeCategory fields.
        migrations.AddField(
            model_name="badgecategory",
            name="abbreviation",
            field=models.CharField(
                blank=True,
                default="",
                help_text="Abréviation courte, par exemple Cp, Sf, Se",
                max_length=5,
                verbose_name="Abréviation",
            ),
        ),
        migrations.AddField(
            model_name="badgecategory",
            name="text_color",
            field=models.CharField(
                default="#473467",
                help_text="Code couleur hexadécimal pour le texte et les illustrations",
                max_length=7,
                verbose_name="Couleur du texte",
            ),
        ),
        migrations.AddField(
            model_name="badgecategory",
            name="illustration_svg",
            field=models.TextField(
                blank=True,
                default="",
                help_text="Code SVG de l'illustration centrale du badge",
                verbose_name="Illustration SVG",
            ),
        ),
        # Champs pour BadgeLevel.
        # BadgeLevel fields.
        migrations.AddField(
            model_name="badgelevel",
            name="posture_text",
            field=models.CharField(
                blank=True,
                default="",
                help_text="Texte affiché en bas du badge, ex: JE DÉCOUVRE",
                max_length=50,
                verbose_name="Texte de posture",
            ),
        ),
        migrations.AddField(
            model_name="badgelevel",
            name="stroke_width",
            field=models.PositiveIntegerField(
                default=3,
                help_text="Épaisseur du trait de bordure en pixels",
                verbose_name="Épaisseur du trait",
            ),
        ),
    ]
