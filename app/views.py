from datetime import datetime
from django.db import IntegrityError
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from app.exeptions import PeriodoIncorrecto, ProfesorInactivo
from app.models import  Calificacion, Criterio, Rubrica, User, PerfilEstudiante, Grupo, PerfilProfesor, Curso
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator

# Create your views here.

def login_register(request):
    if request.user.is_authenticated:
        return redirect_user_by_role(request.user)

    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect_user_by_role(user)
        else:
            messages.error(request, "Usuario/contraseña incorrectos")
    
    return render(request, 'login/login.html')

def redirect_user_by_role(user):
    if user.get_role() == 'ADMIN':
        return redirect('administrador')
    elif user.get_role() == 'ESTUDIANTE':
        return redirect('estudiante')
    elif user.get_role() == 'PROFESOR':
        return redirect('profesor')
    else:
        return redirect('login_register')

@login_required(redirect_field_name='login')
def logout_usuario(request):
    logout(request)
    
    return redirect('login')

# Vista recuperar contraseña (Login)

def login_recuperar_contraseña(request):
    return render(request, 'login/recuperar_contraseña.html')


#Vistas estudiante
@login_required
def estudiante(request):
    usuario = User.objects.get(username = request.user.username)
    perfil = PerfilEstudiante.objects.get(user = usuario)
    return render(request, 'estudiante/estudiante.html', {"cursos" : perfil.cursos.all(), "perfil": perfil})

#Retroalimentación estudiante
@login_required
def estudiante_retroalimentacion(request):
    return render(request, 'estudiante/retroalimentacion.html')

#Vista curso estudiante
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

#Inicio de vistas (sidebar)

#Gestión de cursos: 

#Lista de cursos

#Información del curso
@login_required
def profesor_cursos(request):
    user = request.user.id
    profesor = PerfilProfesor.objects.get(user = user)
    cursos = profesor.curso_set.all()
    
    return render(request, 'profesor/cursos.html', {"cursos": cursos})

#Lista de estudiantes del curso
@login_required
def detalle_curso(request, curso_id):
    curso = get_object_or_404(Curso, id=curso_id)
    estudiantes_lista = curso.perfilestudiante_set.all()
    estudiante = None  # Inicializa la variable estudiante
    
    if request.method == "POST":
        if "buscar-estudiante" in request.POST:
            codigo = request.POST.get("codigo_estudiante")
            try:
                user = User.objects.get(username=codigo)
                estudiante = PerfilEstudiante.objects.get(user=user)
            except User.DoesNotExist:
                # Manejar el caso donde el usuario no existe
                messages.error(request, "No se encontró el estudiante")
                estudiante = None
            except PerfilEstudiante.DoesNotExist:
                # Manejar el caso donde el perfil del estudiante no existe
                messages.error(request, "No se encontró el estudiante")
                estudiante = None
        
        if "agregar-estudiante" in request.POST:
            estudiante_id = request.POST.get("agregar-estudiante")
            estudiante = PerfilEstudiante.objects.get(id = estudiante_id)
            
            if estudiante:
                if curso in estudiante.cursos.all():
                    messages.warning(request, "El estudiante ya está inscrito en este curso")
                else:
                    estudiante.cursos.add(curso)
                    messages.success(request, "Estudiante agregado al curso exitosamente")
                    # Actualiza la lista de estudiantes
                    estudiantes_lista = curso.perfilestudiante_set.all()
            else:
                messages.error(request, "Debe buscar un estudiante antes de agregar")
            estudiante = None
        if "eliminar-estudiante" in request.POST:
            estudiante_id = request.POST.get("eliminar-estudiante")
            try:
                estudiante_a_eliminar = PerfilEstudiante.objects.get(user__id=estudiante_id)
                estudiante_a_eliminar.cursos.remove(curso)
                messages.success(request, "Estudiante eliminado del curso exitosamente")
                estudiantes_lista = curso.perfilestudiante_set.all()
            except PerfilEstudiante.DoesNotExist:
                messages.error(request, "No se encontró el estudiante para eliminar")
    
    return render(request, 'profesor/detalle_curso.html', {"curso": curso, "estudiante": estudiante, "estudiantes_lista" : estudiantes_lista})

@login_required
def profesor_gestion_de_estudiantes(request):
    return render(request, 'profesor/gestion_de_estudiantes.html')

#Configuración de evaluación del curso
@login_required
def profesor_evaluacion_curso(request):
    return render(request, 'profesor/evaluacion_curso.html')

#Definir rúbrica del curso
@login_required
def profesor_rubrica_curso(request):
    return render(request, 'profesor/rubrica_curso.html')

#Lista de grupos del curso
@login_required
def profesor_grupos_curso(request):
    return render(request, 'profesor/grupos_curso.html')

#Crear un grupo 
@login_required
def profesor_grupo(request):
    return render(request, 'profesor/grupo.html')
    
#Informes
@login_required
def profesor_informes(request):
    return render(request, 'profesor/informes.html')

#Gestión de rúbricas
@login_required
def profesor_gestion_rubricas(request):
    return render(request, 'profesor/gestion_rubricas.html')


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
                
                if int(username) <0 :
                    raise ValidationError(username)
                
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
            messages.error(request, "Ya existe un usuario con ese documento.")
        
        except ValueError  as e:
            messages.error(request, f"Error: debe proporcionar un código")
            
        except ValidationError as e:
            messages.error(request, f"El código debe ser mayor a 0: {e}")
        
        except Exception as e:
            messages.error(request, f"Error al procesar la solicitud: {e}")
    
    return render(request, 'administrador/gestion-de-docentes.html', { 'docentes_lista': docentes_lista})

@login_required
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

@login_required
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
                
                if int(username) <0 :
                    raise ValidationError(username)
                
                user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name,password=username, email=email, role="ESTUDIANTE")
                messages.success(request, "Estudiante guardado correctamente")
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
                messages.success(request, "Estudiante actualizado correctamente")
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
def obtener_detalles_curso(request, curso_id):
    try:
        curso = Curso.objects.get(id=curso_id)
        detalles_curso= {
            'id':curso_id,
            'nombre': curso.nombre,
            'profesor_codigo': curso.profesor.user.username,
            'codigo': curso.codigo,  
            'periodo': curso.periodo,
            # Agrega otros campos que desees editar
        }
        return JsonResponse(detalles_curso)
    except Curso.DoesNotExist:
        return JsonResponse({'error': 'El usuario no existe'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def administrador_gestion_de_cursos(request):
    pagination = Paginator(Curso.objects.all().order_by('-id'), 10)
    page = request.GET.get('page')
    cursos_lista = pagination.get_page(page)
    
    if request.method == "POST":
        
        try:
            if "codigo_buscar" in request.POST:
                
                curso = Curso.objects.filter(codigo = request.POST.get("codigo_buscar"))
                if not curso:
                    raise ValueError("No se encontró el curso")
                cursos_lista = curso

            
            if "guardar-curso" in request.POST:
                codigo = request.POST.get("codigo-curso")
                codigo_docente = request.POST.get("codigo-docente")
                nombre = request.POST.get("nombre-curso")
                periodo = request.POST.get("periodo-curso")
                
                usuario = User.objects.get(username = codigo_docente)
                docente = PerfilProfesor.objects.get(user = usuario)
                
                if not docente.user.is_active:
                    raise ProfesorInactivo("El profesor se encuentra inactivo")
                
                if periodo not in ["I", "II"]:
                    raise PeriodoIncorrecto("Ingrese un periodo correctamente")
                
                fecha_actual = datetime.now()
                curso = Curso.objects.create(profesor=docente, nombre=nombre, codigo=codigo, periodo = periodo, fecha_curso = fecha_actual)
                return redirect(reverse("administrador_gestion_de_cursos"))
    
            if "edit-curso" in request.POST:
                
                curso_id = request.POST.get("edit-curso")
                curso = Curso.objects.get(id=curso_id)
                periodo = request.POST.get("edit-periodo-curso")
                curso.codigo = request.POST.get("edit-codigo-curso")
                curso.nombre = request.POST.get("edit-nombre-curso")
                codigo_profesor = User.objects.get(username= request.POST.get("edit-codigo-docente"))
                profesor = PerfilProfesor.objects.get(user=codigo_profesor)
                
                if not profesor.user.is_active:
                    raise ProfesorInactivo("El profesor se encuentra inactivo")
                
                if periodo not in ["I", "II"]:
                    raise PeriodoIncorrecto("Ingrese un periodo correctamente")
                curso.profesor = profesor
                
                curso.periodo = periodo
                curso.save()
                messages.success(request, "Curso modificado con éxito")
                
        except ProfesorInactivo as e:
            messages.error(request, e)
        except IntegrityError:
            messages.error(request, "Ya hay un curso con ese código")
        except PeriodoIncorrecto as e:
            messages.error(request, e)
        except PerfilProfesor.DoesNotExist:
            messages.error(request, "No hay un profesor con ese código")
        except User.DoesNotExist:
            messages.error(request, "No hay un profesor con ese código")
        except ValueError as e:
            messages.error(request, e )
        except:
            messages.error(request, "Por favor digite el formulario correctamente")

    return render(request, 'administrador/gestion_de_cursos.html', {'cursos_lista': cursos_lista})


@login_required
def administrador_gestion_de_evaluacion(request):
    
    pagination = Paginator(Rubrica.objects.all().order_by('-id'), 5)
    page = request.GET.get('page')
    rubrica_lista = pagination.get_page(page)
    
    if request.method == 'POST':
        try:
            if "guardar" in request.POST:
                nombre_rubrica = request.POST.get('nombre_rubrica')
                descripciones_criterios = request.POST.getlist('descripcion_criterio[]')
                pesos_criterios = request.POST.getlist('peso_criterio[]')
                escalas = request.POST.getlist('escala[]')
                descripciones_escalas = request.POST.getlist('descripcion_escala[]')
                
                
                if not nombre_rubrica or not nombre_rubrica.strip():
                    messages.error(request,"No puede estar vacío el campó de la rúbrica")
                    return redirect('administrador_gestion_de_evaluacion')
                
                if  not descripciones_escalas or not descripciones_criterios:
                    messages.error(request, "No pueden estar vacíos")
                    return redirect('administrador_gestion_de_evaluacion')
                
                nombre_rubrica = nombre_rubrica.lower()
                
                # Crear la rúbrica
                rubrica = Rubrica.objects.create(nombre=nombre_rubrica)

                # Crear los criterios
                for descripcion, peso in zip(descripciones_criterios, pesos_criterios):
                    Criterio.objects.create(descripcion=descripcion, peso=peso, rubrica=rubrica)

                # Crear las calificaciones (escalas)
                for escala, descripcion in zip(escalas, descripciones_escalas):
                    Calificacion.objects.create(calificacion=escala, descripcion=descripcion, rubrica=rubrica)

                messages.success(request, 'Rúbrica creada exitosamente.')
                return redirect('administrador_gestion_de_evaluacion')

            if "buscar" in request.POST:
                
                nombre_rubrica = request.POST.get("nombre_rubrica")
                nombre_rubrica = nombre_rubrica.lower()
                rubrica_lista = Rubrica.objects.filter(nombre = nombre_rubrica)
        
        except Rubrica.DoesNotExist:
            messages.error(request, "No se encontró la rúbrica")
        
    return render(request, 'administrador/gestion_de_evaluacion.html', {'rubrica_lista' : rubrica_lista})