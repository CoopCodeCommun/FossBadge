from django.db import models
from pictures.models import PictureField
from solo.models import SingletonModel


# Create your models here.
class Marker(models.Model):
    name = models.CharField(max_length=255)
    icon = PictureField(upload_to='marker/icon/', blank=True, null=True,
                        width_field='avatar_width', height_field='avatar_height')
    lat = models.FloatField()
    lng = models.FloatField()

    def __str__(self):
        return f"Marker at ({self.lat}, {self.lng})"


class MapViewConfig(SingletonModel):
    center_lat = models.FloatField(default=45.766543)
    center_lng = models.FloatField(default=4.879528)

    class Meta:
        verbose_name = 'Map View Configuration'
        verbose_name_plural = 'Map View Configurations'

    def __str__(self):
        return f"Map View Configuration"