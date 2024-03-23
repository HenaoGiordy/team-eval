from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Administrador, User, Profesor, Estudiante

# Register your models here.
class CustonUserAdmin(UserAdmin):
    pass

admin.site.register(User, CustonUserAdmin)
admin.site.register(Profesor, CustonUserAdmin)
admin.site.register(Estudiante, CustonUserAdmin)
admin.site.register(Administrador, CustonUserAdmin)
