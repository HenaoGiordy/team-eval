from django.urls import path
from . import views


urlpatterns= [
    path('', views.login_register, name="login"),
    path('login/request-username/', views.request_username, name='request_username'),
    path('login/change-password/', views.change_password, name='change_password'),
    path('estudiante/', views.estudiante, name="estudiante"),
    path('estudiante/curso/<int:cursoid>', views.estudiante_curso, name="estudiante_curso"),
    path('estudiante/curso/evaluar/<int:estudianteid>/<int:cursoid>/<int:grupoid>', views.evaluar, name="evaluar"),
    path('estudiante/retroalimentacion', views.estudiante_retroalimentacion, name="estudiante_retroalimentacion"),
    path('profesor/', views.profesor, name="profesor"),
    path('profesor/gestion_cursos', views.profesor_cursos, name="profesor_cursos"),
    path('profesor/detalle_curso/<int:curso_id>', views.detalle_curso, name="detalle_curso"),
    path('profesor/gestion_de_estudiantes', views.profesor_gestion_de_estudiantes, name="profesor_gestion_de_estudiantes"),
    path('profesor/crear_evaluacion/<int:curso_id>', views.profesor_evaluacion_curso, name="crear_evaluacion"),
    path('profesor/rubrica_curso', views.profesor_rubrica_curso, name="profesor_rubrica_curso"),
    path('profesor/grupos_curso', views.profesor_grupos_curso, name="profesor_grupos_curso"),
    path('profesor/gestion_rubricas', views.profesor_gestion_rubricas, name="profesor_gestion_rubricas"),
    path('profesor/grupo', views.profesor_grupo, name="profesor_grupo"),
    path('profesor/informes', views.profesor_informes, name="profesor_informes"),    path('logout/', views.logout_usuario, name="logout"),
    path('administrador/', views.administrador, name="administrador"),
    path('administrador/gestion_de_docentes', views.administrador_gestion_de_docentes, name="administrador_gestion_de_docentes"),
    path('administrador/gestion_de_estudiantes', views.administrador_gestion_de_estudiantes, name="administrador_gestion_de_estudiantes"),
    path('administrador/gestion_de_cursos', views.administrador_gestion_de_cursos, name="administrador_gestion_de_cursos"),
    path('administrador/gestion_de_evaluacion', views.administrador_gestion_de_evaluacion, name="administrador_gestion_de_evaluacion"),
    path('obtener_detalles_usuario/<int:user_id>/', views.obtener_detalles_usuario, name='obtener_detalles_usuario'),
    path('obtener_detalles_estudiante/<int:user_id>/', views.obtener_detalles_estudiante, name='obtener_detalles_estudiante'),
    path('obtener_detalles_curso/<int:curso_id>/', views.obtener_detalles_curso, name='obtener_detalles_curso'),
    path('filtrar/', views.filtrar_datos, name='filtrar_datos')
]