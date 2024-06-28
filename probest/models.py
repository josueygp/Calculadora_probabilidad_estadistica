from django.db import models

# Create your models here.
class aplicacion(models.Model):
    id_aplicaciones= models.AutoField(primary_key=True)
    nombre= models.CharField(max_length=40)
    foto_portada= models.ImageField(upload_to='images/albums/', default='images/transparent.png')
    url= models.CharField(max_length=40, default='/')
    def __str__(self):
         return  self.nombre