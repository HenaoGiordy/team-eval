from django.db import IntegrityError
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from app.models import User, PerfilEstudiante, Grupo, PerfilProfesor
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator

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

@login_required
def administrador_gestion_de_docentes(request):
    pagination = Paginator(PerfilProfesor.objects.all().order_by('-id'), 10)
    page = request.GET.get('page')
    docentes_lista = pagination.get_page(page)
    if request.method == "POST":
        
        try:
            
            if "codigo_buscar" in request.POST:
                try:
                    usuario = User.objects.get(username = request.POST.get("codigo_buscar"))
                    docentes_lista = PerfilProfesor.objects.filter(user = usuario)
                except:
                    messages.error(request, "No se encontró un docente con ese código")
            elif "guardar" in request.POST:
                first_name = request.POST.get('nombres')
                last_name = request.POST.get('apellidos')
                username = request.POST.get('documento-docente')
                email = request.POST.get('email')
                
                user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name,password=username, email=email, role="PROFESOR")
                return redirect(reverse('administrador_gestion_de_docentes'))
            
            elif "edit-user" in request.POST:
                user_id = request.POST.get('edit-user')
                usuario = User.objects.get(id=user_id)
                usuario.first_name = request.POST.get('edit-nombre')
                usuario.last_name = request.POST.get('edit-apellidos')
                usuario.username = request.POST.get('edit-documento')
                usuario.email = request.POST.get('edit-email')
                usuario.is_active = request.POST.get('edit-estado')
                usuario.save()
                messages.success(request, "Usuario actualizado correctamente")
                return redirect(reverse('administrador_gestion_de_docentes'))
            
        except IntegrityError:
            messages.error(request, "Ya existe un profesor con ese documento.")
        
        except ValueError  as e:
            messages.error(request, f"Error: debe proporcionar un código")
            
        except ValidationError as e:
            messages.error(request, f"El código debe ser mayor a 0: {e}")
        
        except Exception as e:
            messages.error(request, f"Error al procesar la solicitud: {e}")
    
    return render(request, 'administrador/gestion-de-docentes.html', { 'docentes_lista': docentes_lista})


def obtener_detalles_usuario(request, user_id):
    try:
        usuario = User.objects.get(id=user_id)
        perfil_profesor = PerfilProfesor.objects.get(user=usuario)
        detalles_usuario = {
            'id':user_id,
            'nombre': usuario.first_name,
            'apellidos': usuario.last_name,
            'documento': usuario.username,  # Suponiendo que el username es el documento
            'email': usuario.email,
            'estado': usuario.is_active
            # Agrega otros campos que desees editar
        }
        return JsonResponse(detalles_usuario)
    except User.DoesNotExist:
        return JsonResponse({'error': 'El usuario no existe'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    
def obtener_detalles_estudiante(request, user_id):
    try:
        usuario = User.objects.get(id=user_id)
        perfil_estudiante = PerfilEstudiante.objects.get(user=usuario)
        detalles_usuario = {
            'id':user_id,
            'nombre': usuario.first_name,
            'apellidos': usuario.last_name,
            'documento': usuario.username,  # Suponiendo que el username es el documento
            'email': usuario.email,
            'estado': usuario.is_active
            # Agrega otros campos que desees editar
        }
        return JsonResponse(detalles_usuario)
    except User.DoesNotExist:
        return JsonResponse({'error': 'El usuario no existe'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)





@login_required
def administrador_gestion_de_estudiantes(request):
    pagination = Paginator(PerfilEstudiante.objects.all().order_by('-id'), 10)
    page = request.GET.get('page')
    estudiantes_lista = pagination.get_page(page)
    if request.method == "POST":
        
        try:
            
            if "codigo_buscar" in request.POST:
                try:
                    usuario = User.objects.get(username = request.POST.get("codigo_buscar"))
                    estudiantes_lista = PerfilEstudiante.objects.filter(user = usuario)
                except:
                    messages.error(request, "No se encontró un estudiante con ese código")
            if "guardar-estudiante" in request.POST:
                first_name = request.POST.get('nombres-estudiante')
                last_name = request.POST.get('apellidos-estudiante')
                username = request.POST.get('codigo-estudiante')
                email = request.POST.get('email-estudiante')
                
                user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name,password=username, email=email, role="ESTUDIANTE")
                return redirect(reverse('administrador_gestion_de_estudiantes'))
            
            elif "edit-user" in request.POST:
                user_id = request.POST.get('edit-user')
                usuario = User.objects.get(id=user_id)
                usuario.first_name = request.POST.get('edit-nombre-estudiante')
                usuario.last_name = request.POST.get('edit-apellidos-estudiante')
                usuario.username = request.POST.get('edit-documento-estudiante')
                usuario.email = request.POST.get('edit-email-estudiante')
                usuario.is_active = request.POST.get('edit-estado-estudiante')
                usuario.save()
                messages.success(request, "Usuario actualizado correctamente")
                return redirect(reverse('administrador_gestion_de_estudiantes'))
            
        except IntegrityError:
            messages.error(request, "Ya existe un usuario con ese documento.")
        
        except ValueError  as e:
            messages.error(request, f"Error: debe proporcionar un código")
            
        except ValidationError as e:
            messages.error(request, f"El código debe ser mayor a 0: {e}")
        
        except Exception as e:
            messages.error(request, f"Error al procesar la solicitud: {e}")
    
    
    return render(request, 'administrador/gestion-de-estudiantes.html', {'estudiantes_lista': estudiantes_lista})

@login_required
def administrador_gestion_de_cursos(request):
    return render(request, 'administrador/gestion_de_cursos.html')

@login_required
def administrador_gestion_de_evaluacion(request):
    return render(request, 'administrador/gestion_de_evaluacion.html')