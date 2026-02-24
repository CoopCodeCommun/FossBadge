from django.db import models
from pictures.models import PictureField
from solo.models import SingletonModel
import xml.etree.ElementTree as ET


# Create your models here.
class Marker(models.Model):
    name = models.CharField(max_length=255)
    icon = PictureField(upload_to='marker/icon/', blank=True, null=True,
                        width_field='avatar_width', height_field='avatar_height')
    avatar_width = models.PositiveIntegerField(blank=True, null=True, editable=False)
    avatar_height = models.PositiveIntegerField(blank=True, null=True, editable=False)
    lat = models.FloatField()
    lng = models.FloatField()

    def __str__(self):
        return f"Marker: {self.name} at ({self.lat}, {self.lng})"

    @classmethod
    def import_from_kml(cls, kml_file_path):
        """
        Importe des marqueurs à partir d'un fichier KML.
        Import markers from a KML file.
        """
        # On utilise ElementTree pour lire le fichier XML du KML
        # We use ElementTree to read the KML XML file
        tree = ET.parse(kml_file_path)
        root = tree.getroot()

        # Le namespace KML est standard pour les fichiers Google Maps / Google Earth
        # The KML namespace is standard for Google Maps / Google Earth files
        kml_namespace = {"kml": "http://www.opengis.net/kml/2.2"}

        nombre_de_marqueurs_importes = 0

        # On cherche tous les éléments 'Placemark' dans le fichier
        # We look for all 'Placemark' elements in the file
        liste_des_emplacements = root.findall(".//kml:Placemark", kml_namespace)

        for emplacement in liste_des_emplacements:
            element_nom = emplacement.find("kml:name", kml_namespace)
            element_coordonnees = emplacement.find(".//kml:coordinates", kml_namespace)

            # On ne traite l'emplacement que s'il a un nom et des coordonnées
            # We only process the location if it has a name and coordinates
            if element_nom is not None and element_coordonnees is not None:
                nom_du_marqueur = element_nom.text.strip()
                texte_coordonnees = element_coordonnees.text.strip()

                # Les coordonnées KML sont au format : longitude,latitude,altitude (séparées par des virgules)
                # KML coordinates are in format: longitude,latitude,altitude (separated by commas)
                parties_coordonnees = texte_coordonnees.split(",")
                
                if len(parties_coordonnees) >= 2:
                    try:
                        # On convertit les textes en nombres flottants
                        # We convert strings to floating point numbers
                        longitude = float(parties_coordonnees[0])
                        latitude = float(parties_coordonnees[1])

                        # Création du marqueur en base de données
                        # Creating the marker in the database
                        cls.objects.create(
                            name=nom_du_marqueur,
                            lat=latitude,
                            lng=longitude
                        )
                        nombre_de_marqueurs_importes = nombre_de_marqueurs_importes + 1
                    except ValueError:
                        # Si la conversion échoue, on passe au suivant
                        # If conversion fails, we move to the next one
                        continue

        return nombre_de_marqueurs_importes


class MapViewConfig(SingletonModel):
    center_lat = models.FloatField(default=45.766543)
    center_lng = models.FloatField(default=4.879528)

    class Meta:
        verbose_name = 'Map View Configuration'
        verbose_name_plural = 'Map View Configurations'

    def __str__(self):
        return f"Map View Configuration"