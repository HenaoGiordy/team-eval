from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from app.models import User, PerfilEstudiante, Grupo

# Create your views here.
def login_register(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, "El usuario no fue encontrado")
            return redirect('/')
        
        user = authenticate(request, username=username, password=password)
        
        
        if user is not None:
            login(request, user)
            if user.get_role() == 'ADMIN':
                return redirect('admin/')
            if user.get_role() == 'ESTUDIANTE':
                return redirect('estudiante/')
            if user.get_role() == 'PROFESOR':
                return redirect('profesor/')
        else:
            messages.error(request, "El usuario o contraseña no coinciden")
            
    return render(request, 'login/login.html')

def logout_usuario(request):
    logout(request)
    
    return redirect('login')


#Vistas estudiante
def estudiante(request):
    usuario = User.objects.get(username = request.user.username)
    perfil = PerfilEstudiante.objects.get(nombre = usuario.username)
    return render(request, 'estudiante/estudiante.html', {"cursos" : perfil.cursos.all()})

#vista curso estudiante
def estudiante_curso(request, cursoid):
    usuario = User.objects.get(username = request.user.username)
    
    perfil = PerfilEstudiante.objects.get(nombre = usuario.username)
    
    curso = perfil.cursos.get(id = cursoid)
    
    grupo = perfil.grupo_set.get(curso = cursoid)
    
    estudiantes_grupo = grupo.estudiantes.all().exclude(user = perfil.user)
    
    return render(request, 'estudiante/curso.html', {'curso': curso, 'grupo': grupo, 'estudiantes': estudiantes_grupo})



def evaluar(request, estudianteid, cursoid, grupoid):
    
    usuario = User.objects.get(username = request.user.username)
    
    perfil = PerfilEstudiante.objects.get(nombre = usuario.username)
    
    curso = perfil.cursos.get(id = cursoid)
    
    rubrica = curso.rubrica
    
    criterios = rubrica.criterios.all()
    
    escalaCalificacion = rubrica.escalaCalificacion.all()
    
    grupo = perfil.grupo_set.get(curso = cursoid)
    
    # estudiantes_grupo = grupo.estudiantes.all().exclude(user = perfil.user)
    
    estudiante_evaluado = grupo.estudiantes.get(id = estudianteid)
    
    
    return render(request, 'estudiante/evaluar.html', {'curso': curso, 'estudiante_evaluado': estudiante_evaluado, 'estudiante_evaluador' : perfil,  'grupo': grupo,
                                                       'rubrica' : rubrica, "criterios" : criterios, "escalacalificacion" : escalaCalificacion }  )

def profesor(request):
    return render(request, 'profesor/profesor.html')