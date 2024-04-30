from django.urls import path
from . import views


urlpatterns= [
    path('', views.login_register, name="login"),
    path('estudiante/', views.estudiante, name="estudiante"),
    path('estudiante/curso/<int:cursoid>', views.estudiante_curso, name="estudiante_curso"),
    path('estudiante/curso/evaluar/<int:estudianteid>/<int:cursoid>/<int:grupoid>', views.evaluar, name="evaluar"),
    path('profesor/', views.profesor, name="profesor"),
    path('logout/', views.logout_usuario, name="logout"),
    path('administrador/', views.administrador, name="administrador")
]