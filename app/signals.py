from .models import User, PerfilEstudiante, PerfilProfesor
from django.contrib.auth.models import Group
from django.dispatch import receiver
from django.db.models.signals import post_save

@receiver(post_save, sender=User)
def asignar_grupo_administrador(sender, instance, *args, **kwards):
    if instance.role != "":
        if  instance.role=='ADMIN':
            try:
                grupo = Group.objects.get(name='administradores')
            except Group.DoesNotExist:
                grupo = Group.objects.create(name='administradores')
                instance.groups.add(grupo)
    
        if instance.role=='ESTUDIANTE':
            try:
                grupo = Group.objects.get(name='Estudiantes')
            except Group.DoesNotExist:
                grupo = Group.objects.create(name='Estudiantes')
            instance.groups.add(grupo)
    
        if instance.role=='PROFESOR':
            try:
                grupo = Group.objects.get(name='Profesores')
            except Group.DoesNotExist:
                grupo = Group.objects.create(name='Profesores')
            instance.groups.add(grupo)
    

@receiver(post_save, sender=User)
def crear_perfil(sender, instance, created, *args, **kwards):
    if instance.role != "":
        if instance.role == 'ESTUDIANTE':
            if not PerfilEstudiante.pk: 
                PerfilEstudiante.objects.create(user=instance,nombre=instance.username)
        if instance.role == 'PROFESOR':
            if not PerfilProfesor.pk:
                PerfilProfesor.objects.create(user=instance,nombre=instance.username)
    


    


        
        
        