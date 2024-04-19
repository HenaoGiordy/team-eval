from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm
from .models import  *

# Register your models here.
class MyUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = User

class CustomUserAdmin(UserAdmin):
    form = MyUserChangeForm
    fieldsets = UserAdmin.fieldsets + (
            (None, {'fields': ('role',)}),
    )

admin.site.register(User, CustomUserAdmin)
admin.site.register(Curso)
admin.site.register(PerfilEstudiante)
admin.site.register(PerfilProfesor)
admin.site.register(Rubrica)
admin.site.register(Criterio)
admin.site.register(Calificacion)
admin.site.register(Grupo)
