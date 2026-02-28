from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Station(models.Model):
    name = models.CharField(max_length=255, unique=True)
    latitude = models.FloatField()
    longitude = models.FloatField()

    def __str__(self):
        return self.name


class Route(models.Model):
    source = models.ForeignKey(Station, on_delete=models.CASCADE, related_name="route_source")
    destination = models.ForeignKey(Station, on_delete=models.CASCADE, related_name="route_destination")
    distance = models.IntegerField()

    class Meta:
        unique_together = ("source", "destination")

    def __str__(self):
        return f"{self.source.name} - {self.destination.name}"