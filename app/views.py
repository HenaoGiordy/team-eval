from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from app.models import User, PerfilEstudiante, Grupo


# Create your views here.

def login_register(request):
    
    user = request.user
    
    if user.is_authenticated:
        
        if user.get_role() == 'ADMIN':
            return redirect('administrador/')
        if user.get_role() == 'ESTUDIANTE':
            return redirect('estudiante/')
        if user.get_role() == 'PROFESOR':
            return redirect('profesor/')
    
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, "Usuario/contraseña  incorrecto")
            return redirect('/')
        
        user = authenticate(request, username=username, password=password)
        
        
        if user is not None:
            login(request, user)
            if user.get_role() == 'ADMIN':
                return redirect('administrador/')
            if user.get_role() == 'ESTUDIANTE':
                return redirect('estudiante/')
            if user.get_role() == 'PROFESOR':
                return redirect('profesor/')
        else:
            messages.error(request, "Usuario/contraseña  incorrecto")
            
    return render(request, 'login/login.html')

@login_required(redirect_field_name='login')
def logout_usuario(request):
    logout(request)
    
    return redirect('login')


#Vistas estudiante
@login_required
def estudiante(request):
    usuario = User.objects.get(username = request.user.username)
    perfil = PerfilEstudiante.objects.get(user = usuario)
    return render(request, 'estudiante/estudiante.html', {"cursos" : perfil.cursos.all(), "perfil": perfil})

#vista curso estudiante
@login_required
def estudiante_curso(request, cursoid):
    usuario = User.objects.get(username = request.user.username)
    
    perfil = PerfilEstudiante.objects.get(user = usuario)
    
    
    curso = perfil.cursos.get(id = cursoid)
    try:
        grupo = perfil.grupo_set.get(curso = cursoid)
        estudiantes_grupo = grupo.estudiantes.all().exclude(user = perfil.user)
    except:
        messages.error(request, "Aún no estás en un grupo para este curso")
        return redirect('/estudiante/')
    
    
    
    return render(request, 'estudiante/curso.html', {'curso': curso, 'grupo': grupo, 'estudiantes': estudiantes_grupo})


@login_required
def evaluar(request, estudianteid, cursoid, grupoid):
    
    usuario = User.objects.get(username = request.user.username)
    
    perfil = PerfilEstudiante.objects.get(user = usuario)
    
    curso = perfil.cursos.get(id = cursoid)
    
    rubrica = curso.rubrica
    
    criterios = rubrica.criterios.all()
    
    escalaCalificacion = rubrica.escalaCalificacion.all()
    
    grupo = perfil.grupo_set.get(curso = cursoid)
    
    # estudiantes_grupo = grupo.estudiantes.all().exclude(user = perfil.user)
    
    estudiante_evaluado = grupo.estudiantes.get(id = estudianteid)
    
    
    return render(request, 'estudiante/evaluar.html', {'curso': curso, 'estudiante_evaluado': estudiante_evaluado, 'estudiante_evaluador' : perfil,  'grupo': grupo,
                                                       'rubrica' : rubrica, "criterios" : criterios, "escalacalificacion" : escalaCalificacion }  )



#Vistas del profesor
# @login_required
def profesor(request):
    return render(request, 'profesor/profesor.html')

@login_required
def administrador(request):
    return render(request, 'administrador/administrador.html')