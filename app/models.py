from django.apps import apps
from django.contrib.auth.hashers import make_password
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.db.models import UniqueConstraint



# Create your models here.

class User(AbstractUser):
    ROLES = {"ADMIN" : "ADMIN", "ESTUDIANTE" : "ESTUDIANTE", "PROFESOR" : "PROFESOR"}

    role = models.CharField(max_length=50, choices=ROLES)
    
    username = models.IntegerField(
        _("Codigo"),
        unique=True,
        blank=False,
        help_text=_(
            "El código de usuario es único y de debe ser un valor numérico."
        ),
        error_messages={
            "unique": _("Ya existe un usuario con ese código"),
            "blank": _("Este campo no puede estar vacío.")
        },
    )
    first_name = models.CharField(_("first name"), max_length=150, blank=False)
    email = models.EmailField(_("email address"), blank=False)
    REQUIRED_FIELDS = ['first_name', 'email', 'role']
    
    def get_role(self):
        return self.role
    
    def __str__(self):
        return f"{self.username}"
    
class PerfilProfesor(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    nombre = models.TextField()
    def __str__(self):
        return self.nombre


class Rubrica(models.Model):
    nombre = models.TextField(max_length=50)
    is_used = models.BooleanField(default=False)
    def __str__(self):
        return f"{self.nombre}"

class Calificacion(models.Model):
    NUMEROS_ESCALA = {1 : 1, 2:2, 3:3, 4:4, 5:5, 6:6, 7:7, 8:8, 9:9, 10 : 10}
    calificacion = models.IntegerField(choices=NUMEROS_ESCALA)
    descripcion = models.TextField(max_length=100)
    rubrica = models.ForeignKey(Rubrica, on_delete=models.CASCADE)

class Criterio(models.Model):
    descripcion = models.TextField(max_length=200)
    peso = models.DecimalField(max_digits=2, decimal_places=2)
    rubrica = models.ForeignKey(Rubrica, on_delete=models.CASCADE)
    def __str__(self):
        return self.descripcion + f" Peso: {self.peso}" 
    

class Puntuacion(models.Model):
    nota = models.SmallIntegerField()
    retroalimentacion = models.TextField(max_length=200)
    criterio_evaluado = models.ForeignKey(Criterio, on_delete=models.CASCADE)
    def __str__(self):
        return self.criterio_evaluado + "Nota: "+ self.nota + ", Retroalimentación: " + self.retroalimentacion

class Curso(models.Model):
    PERIODOS = [("I", "I"), ("II", "II")]
    profesor = models.ForeignKey(PerfilProfesor, on_delete=models.CASCADE, blank=False)
    nombre = models.TextField(max_length=50, blank=False)
    codigo = models.TextField(max_length=20)
    fecha_curso = models.DateField()
    periodo = models.TextField(choices=PERIODOS)
    
    class Meta:
        constraints = [
            UniqueConstraint(fields=['codigo', 'periodo'], name='unique_codigo_periodo')
        ]
    def __str__(self):
        return self.nombre
    
    @property
    def get_periodo_academico(self):
        return f"{self.fecha_curso.strftime('%Y')} - {self.periodo}"
    
    @property
    def numero_estudiantes(self):
        return self.perfilestudiante_set.count()
    
    @property
    def numero_grupos(self):
        return self.grupo_set.count()


class PerfilEstudiante(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    nombre = models.TextField()
    cursos = models.ManyToManyField(Curso)
    def __str__(self):
        return self.nombre

class Evaluacion(models.Model):
    fecha_inicio = models.DateField(blank=False, null=False)
    fecha_fin = models.DateField(blank=False, null=False)
    rubrica = models.ForeignKey(Rubrica, on_delete=models.PROTECT, null=False, blank=False)
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE, null=False, blank=False)
    evaluadores = models.ManyToManyField(PerfilEstudiante, related_name='evaluaciones_hechas')
    evaluados = models.ManyToManyField(PerfilEstudiante, related_name='evaluaciones_recibidas')
    
    @property
    def numero_estudiantes_evaluados(self):
        return self.evaluados.count()

class Grupo(models.Model):
    nombre = models.TextField(max_length=50)
    proyecto_asignado = models.TextField(max_length=50)
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE)
    estudiantes = models.ManyToManyField(PerfilEstudiante)
    def __str__(self):
        return self.nombre 
    
