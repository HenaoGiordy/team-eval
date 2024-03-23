from .models import Administrador, Estudiante, Profesor, PerfilEstudiante, PerfilProfesor
from django.contrib.auth.models import Group
from django.dispatch import receiver
from django.db.models.signals import post_save

@receiver(post_save, sender=Administrador)
def asignar_grupo_administrador(sender, instance, created, *args, **kwards):
    if created:
        try:
            grupo = Group.objects.get(name='administradores')
        except Group.DoesNotExist:
            grupo = Group.objects.create(name='administradores')
        instance.groups.add(grupo)

@receiver(post_save, sender=Estudiante)
def asignar_grupo_estudiante(sender, instance, created, *args, **kwards):
    if created:
        try:
            grupo = Group.objects.get(name='estudiantes')
        except Group.DoesNotExist:
            grupo = Group.objects.create(name='estudiantes')
        instance.groups.add(grupo)

@receiver(post_save, sender=Estudiante)
def crear_perfil(sender, instance, created, *args, **kwards):
    if created and instance.role == 'Estudiante':
        PerfilEstudiante.objects.create(user=instance,nombre=instance.username)


@receiver(post_save, sender=Profesor)
def asignar_grupo_profesor(sender, instance, created, *args, **kwards):
    if created:
        try:
            grupo = Group.objects.get(name='profesores')
        except Group.DoesNotExist:
            grupo = Group.objects.create(name='profesores')
        instance.groups.add(grupo)
        
@receiver(post_save, sender=Profesor)
def crear_perfil(sender, instance, created, *args, **kwards):
    if created and instance.role == 'Profesor':
        PerfilEstudiante.objects.create(user=instance,nombre=instance.username)


        
        
        