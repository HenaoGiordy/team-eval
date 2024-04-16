from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings



# Create your models here.

class User(AbstractUser):
    ROLES = {"ADMIN" : "ADMIN", "ESTUDIANTE" : "ESTUDIANTE", "PROFESOR" : "PROFESOR"}

    role = models.CharField(max_length=50, choices=ROLES)
    
    REQUIRED_FIELDS = ['role']

    
    def get_role(self):
        return self.role
    

class PerfilProfesor(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    nombre = models.TextField()
    def __str__(self):
        return self.nombre

class Curso(models.Model):
    profesor = models.ForeignKey(PerfilProfesor, on_delete=models.CASCADE)
    nombre = models.TextField(max_length=50)
    def __str__(self):
        return self.nombre

class PerfilEstudiante(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    nombre = models.TextField()
    cursos = models.ManyToManyField(Curso)
    def __str__(self):
        return self.nombre


    
    


    
    