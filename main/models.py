from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Movil(models.Model):
    id = models.AutoField(primary_key=True)
    fecha = models.TextField()
    modelo = models.TextField()
    rom = models.JSONField()
    ram = models.JSONField()
    bateria = models.IntegerField()
    puntuacion = models.FloatField()
    precio = models.FloatField()
    imagen = models.TextField()

class Favorito(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    movil = models.ForeignKey(Movil, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'movil')

