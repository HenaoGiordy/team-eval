from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings



# Create your models here.

class User(AbstractUser):
    ROLES = {"ADMIN" : "Administrador", "ESTUDIANTE" : "Estudiante", "PROFESOR" : "Profesor"}
    base_role = ROLES["ADMIN"]

    role = models.CharField(max_length=50, choices=ROLES, editable=False)

    def save(self, *arg, **args):
        if not self.pk:
            self.role = self.base_role
            return super().save(*arg, **args)
    
    def get_role(self):
        return self.role

class Administrador(User):
    
    base_role = User.ROLES["ADMIN"]
    class Meta:
        proxy = True


class Estudiante(User):
    base_role = User.ROLES["ESTUDIANTE"]
    
    class Meta:
        proxy = True
        
   
class PerfilEstudiante(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    nombre = models.TextField()
    

class Profesor(User):
    base_role = User.ROLES["PROFESOR"]
    class Meta:
        proxy = True

class PerfilProfesor(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    nombre = models.TextField()
