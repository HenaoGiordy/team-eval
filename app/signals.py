from .models import User, PerfilEstudiante, PerfilProfesor
from django.contrib.auth.models import Group
from django.dispatch import receiver
from django.db.models.signals import post_save

@receiver(post_save, sender=User)
def asignar_grupo_administrador(sender, instance, *args, **kwards):
    if instance.role != "":
        if  instance.role=='ADMIN':
            try:
                grupo = Group.objects.get(name='Administradores')
            except Group.DoesNotExist:
                grupo = Group.objects.create(name='Administradores')
            instance.groups.add(grupo)


@receiver(post_save, sender=User)
def asignar_grupo_estudiante(sender, instance, *args, **kwards):
    if instance.role != "":
        if instance.role=='ESTUDIANTE':
            try:
                grupo = Group.objects.get(name='Estudiantes')
            except Group.DoesNotExist:
                grupo = Group.objects.create(name='Estudiantes')  
            instance.groups.add(grupo)
            
            try:
                estudiante = PerfilEstudiante.objects.get(user_id = instance.pk)
            except PerfilEstudiante.DoesNotExist:
                PerfilEstudiante.objects.create(user=instance,nombre=instance.username)
            

@receiver(post_save, sender=User)
def asignar_grupo_profesor(sender, instance, *args, **kwards):
    if instance.role != "":
        if instance.role=='PROFESOR':
            try:
                grupo = Group.objects.get(name='Profesores')
            except Group.DoesNotExist:
                grupo = Group.objects.create(name='Profesores')
            instance.groups.add(grupo)
            
            try:
                profesor = PerfilProfesor.objects.get(user_id = instance.pk)
            except PerfilProfesor.DoesNotExist:
                PerfilProfesor.objects.create(user=instance,nombre=instance.username)    