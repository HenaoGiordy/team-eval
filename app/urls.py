from django.urls import path
from . import views


urlpatterns= [
    path('', views.login_register, name="login"),
    path('estudiante/', views.estudiante, name="estudiante"),
    path('estudiante/curso/<int:cursoid>', views.estudiante_curso, name="estudiante_curso"),
    path('estudiante/curso/evaluar/<int:estudianteid>/<int:cursoid>/<int:grupoid>', views.evaluar, name="evaluar"),
    path('profesor/', views.profesor, name="profesor"),
    path('logout/', views.logout_usuario, name="logout"),
    path('administrador/', views.administrador, name="administrador"),
    path('administrador/gestion_de_docentes', views.administrador_gestion_de_docentes, name="administrador_gestion_de_docentes"),
    path('administrador/gestion_de_estudiantes', views.administrador_gestion_de_estudiantes, name="administrador_gestion_de_estudiantes"),
    path('administrador/gestion_de_cursos', views.administrador_gestion_de_cursos, name="administrador_gestion_de_cursos"),
    path('administrador/gestion_de_evaluacion', views.administrador_gestion_de_evaluacion, name="administrador_gestion_de_evaluacion"),
    path('obtener_detalles_usuario/<int:user_id>/', views.obtener_detalles_usuario, name='obtener_detalles_usuario'),
    path('obtener_detalles_estudiante/<int:user_id>/', views.obtener_detalles_estudiante, name='obtener_detalles_estudiante'),
]