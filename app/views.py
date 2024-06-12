import csv
from django.db import transaction
from datetime import datetime
from decimal import InvalidOperation
from django.db import IntegrityError
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.db.models import ProtectedError, Sum, Count, FloatField, F,ExpressionWrapper, Avg
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from TeamEval import settings
from app.exeptions import AlreadyExist, AutorNoAutorizado, EmptyField, EstudianteInactivo, GrupoHasEvaluated, InvalidDate, NumberError, PeriodoIncorrecto, ProfesorInactivo, RubricaEnUso, RubricaNoEncontrada
from app.forms import MinimalPasswordChangeForm, UsernameForm
from app.models import  Calificacion, Criterio, Evaluacion, Resultado, Retroalimentracion, Rubrica, User, PerfilEstudiante, Grupo, PerfilProfesor, Curso
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.core.mail import send_mail
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
        return redirect('administrador_gestion_de_docentes')
    elif user.get_role() == 'ESTUDIANTE':
        return redirect('estudiante')
    elif user.get_role() == 'PROFESOR':
        return redirect('profesor_cursos')
    else:
        return redirect('login_register')

def request_username(request):
    if request.method == 'POST': 
        form = UsernameForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            try:
                user = User.objects.get(username=username)
                # Generar el token y el UID
                token = default_token_generator.make_token(user)
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                
                # Construir el enlace
                link = request.build_absolute_uri(
                    reverse('change_password') + f'?uid={uid}&token={token}'
                )
                
                # Enviar el correo electrónico
                subject = 'Restablecimiento de contraseña'
                message = render_to_string('login/password_reset_email.html', {
                    'user': user,
                    'link': link,  # Pasar el enlace sin escapar
                })
                send_mail(subject, message, settings.EMAIL_HOST_USER, [user.email])
                
                messages.success(request, f'Se ha enviado un enlace de restablecimiento de contraseña a tu correo electrónico {user.email}.')
                return redirect('login')
            except User.DoesNotExist:
                messages.error(request, 'El nombre de usuario no existe.')
            
    else:
        form = UsernameForm()

    return render(request, 'login/request_username.html', {'form': form})

def change_password(request):
    uidb64 = request.GET.get('uid')
    token = request.GET.get('token')
    
    # Verificar que uidb64 no sea None antes de decodificar
    if uidb64 is not None:
        try:
            uid = urlsafe_base64_decode(uidb64)
            user = User.objects.get(pk=uid)
        
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None
            
    else:
        user = None
        
    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            form = MinimalPasswordChangeForm(user, request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, 'Tu contraseña ha sido cambiada con éxito.')
                return redirect('login')
        else:
            form = MinimalPasswordChangeForm(user)
    else:
        messages.error(request, 'El enlace de restablecimiento de contraseña no es válido o ha expirado.')
        return redirect('request_username')

    return render(request, 'login/change_password.html', {'form': form})


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
    return render(request, 'estudiante/estudiante.html', {"cursos" : perfil.cursos.filter(has_finished=False), "perfil": perfil})

#Retroalimentación estudiante
@login_required
def estudiante_retroalimentacion(request):
    usuario = User.objects.get(username = request.user.username)
    perfil_estudiante = PerfilEstudiante.objects.get(user = usuario)
    evaluaciones = Evaluacion.objects.filter(resultado__evaluado=perfil_estudiante).distinct()
    grupos = Grupo.objects.filter(estudiantes=perfil_estudiante)
    return render(request, 'estudiante/retroalimentacion.html', {"evaluaciones": evaluaciones, "grupos": grupos})

@login_required
def estudiante_ver_resultado(request, evaluacionid):
    usuario = User.objects.get(username = request.user.username)
    perfil_estudiante = PerfilEstudiante.objects.get(user = usuario)
    evaluacion = Evaluacion.objects.get(id = evaluacionid)
    
    #NO TOCAR ESTA CONSULTA
    resultados = Resultado.objects.filter(
        evaluado=perfil_estudiante,
        evaluacion=evaluacion
    ).values(
        'criterio_evaluado__descripcion',
        'criterio_evaluado__peso'
    ).annotate(
        promedio_notas=Avg('nota__calificacion', output_field=FloatField())
    ).annotate(
        valor_ponderado=ExpressionWrapper(F('promedio_notas') * F('criterio_evaluado__peso'), output_field=FloatField())
    )
        
    nota_final = resultados.aggregate(nota_final=Sum('valor_ponderado'))['nota_final']
    
    comentarios = Retroalimentracion.objects.filter(estudiante_retroalimentacion=perfil_estudiante, evaluacion=evaluacion)
    
    return render(request, "estudiante/ver_resultados.html", {"resultados" : resultados, "evaluacion": evaluacion, "nota_final": nota_final, "comentarios": comentarios,})

#Vista curso estudiante
@login_required
def estudiante_curso(request, cursoid):
    usuario = User.objects.get(username=request.user.username)
    perfil = PerfilEstudiante.objects.get(user=usuario)
    curso = perfil.cursos.get(id=cursoid)
    fecha_hoy = datetime.now().date()
    try:
        grupo = perfil.grupo_set.get(curso=cursoid)
        estudiantes_grupo = grupo.estudiantes.all().exclude(user=perfil.user)
        # Evaluaciones
        evaluaciones = grupo.curso.evaluacion_set.all()
        
        evaluaciones_status = []
        for evaluacion in evaluaciones:
            evaluados = Resultado.objects.filter(evaluacion=evaluacion, evaluador=perfil).values_list('evaluado_id', flat=True)
            todos_evaluados = set(estudiantes_grupo.values_list('id', flat=True)) == set(evaluados)
            evaluaciones_status.append({
                'evaluacion': evaluacion,
                'todos_evaluados': todos_evaluados
            })
    except:
        messages.error(request, "Aún no estás en un grupo para este curso")
        return redirect('/estudiante/')
    
    return render(request, 'estudiante/curso.html', {
        'curso': curso,
        'grupo': grupo,
        'estudiantes': estudiantes_grupo,
        'evaluaciones_status': evaluaciones_status,
        'fecha_hoy': fecha_hoy
    })


@login_required
def evaluar(request, evaluacionid, grupoid):
    # Evaluador
    usuario = User.objects.get(username=request.user.username)
    perfil_evaluador = PerfilEstudiante.objects.get(user=usuario)
    # Rúbrica
    evaluacion = Evaluacion.objects.get(id=evaluacionid)
    rubrica = evaluacion.rubrica
    # Criterios
    criterios = rubrica.criterio_set.all()
    # Escala
    rubrica = rubrica.calificacion_set.all()
    # Grupo
    grupo = Grupo.objects.get(id=grupoid)
    # Curso
    curso = grupo.curso
    # Estudiantes del grupo que no han sido evaluados
    estudiantes_evaluados = Resultado.objects.filter(evaluacion=evaluacion, evaluador=perfil_evaluador).values_list('evaluado_id', flat=True)
    estudiantes = grupo.estudiantes.all().exclude(id__in=estudiantes_evaluados).exclude(id=perfil_evaluador.id)

    try:
        if request.method == "POST":
            calificaciones = request.POST.getlist("calificacion[]")
            criterios_evaluados = request.POST.getlist("criterios[]")
            retro_alimentacion = request.POST.get("retroalimentacion")
            evaluadoid = request.POST.get("evaluado")

            if not evaluadoid:
                raise EmptyField("Ingrese un estudiante")

            if not evaluadoid.isdigit():
                raise NumberError("Selecciona un estudiante")

            try:
                evaluado = PerfilEstudiante.objects.get(id=evaluadoid)
            except PerfilEstudiante.DoesNotExist:
                messages.error(request, "El estudiante que intentas evaluar, por alguna razón no aparece.")

            for califica in calificaciones:
                if califica == "Seleccionar una calificación":
                    raise EmptyField("Debes asignar una calificación")
                if not califica.isdigit():
                    raise EmptyField("No se puede introducir letras al valor de la calificación ni dejarlo vacío")

            for calificacionid, criterioid in zip(calificaciones, criterios_evaluados):
                calificacion = Calificacion.objects.get(id=calificacionid)
                criterio = Criterio.objects.get(id=criterioid)
                Resultado.objects.create(nota=calificacion, criterio_evaluado=criterio, evaluacion=evaluacion, evaluado=evaluado, evaluador=perfil_evaluador)
            
            Retroalimentracion.objects.create(estudiante_retroalimentacion=evaluado, retroalimentacion=retro_alimentacion, evaluacion=evaluacion)
            grupo.has_evaluated = True
            evaluacion.save()
            grupo.save()
            messages.success(request, "Evaluación enviada")
            
    except IntegrityError:
        messages.error(request, "Ya has evaluado a este estudiante")
    except EmptyField as e:
        messages.error(request, e)
    except NumberError as e:
        messages.error(request, e)
        
    #Redirigir a la vistaevaluaciones cuando no hayan estudiantes por evaluar
    if not estudiantes.exists():
        evaluacion.evaluados += 1
        evaluacion.save()
        return redirect(reverse("estudiante_curso", args=[curso.id]))
            
    return render(request, 'estudiante/evaluar.html', {
        "evaluador": perfil_evaluador,
        "curso": curso,
        "estudiantes": estudiantes,
        "evaluacion": evaluacion,
        "criterios": criterios,
        "rubrica": rubrica,
        "grupo": grupo
    })

#Vistas del profesor

#Inicio de vistas (sidebar)

#Gestión de cursos: 

#Lista de cursos

#Información del curso
@login_required
def profesor_cursos(request):
    user = request.user.id
    profesor = PerfilProfesor.objects.get(user = user)
    cursos = profesor.curso_set.filter(has_finished=False)
    
    return render(request, 'profesor/cursos.html', {"cursos": cursos})

def filtrar_datos(request):
    query = request.GET.get('q', '')
    if query:
        resultados = Rubrica.objects.filter(nombre__icontains=query)  
    else:
        resultados = Rubrica.objects.none()
    
    data = list(resultados.values('id', 'nombre', 'autor__first_name')) 
    return JsonResponse(data, safe=False)

#Lista de estudiantes del curso
@login_required
def detalle_curso(request, curso_id):
    curso = get_object_or_404(Curso, id=curso_id)
    estudiantes_lista = curso.perfilestudiante_set.all().order_by("-id")
    pagination = Paginator(estudiantes_lista, 10)
    page = request.GET.get('page')
    estudiantes_lista_paginada = pagination.get_page(page)
    estudiante = None
    
    if request.method == "POST":
        if "buscar-estudiante" in request.POST:
            codigo = request.POST.get("codigo_estudiante")
            try:
                user = User.objects.get(username=codigo)
                estudiante = PerfilEstudiante.objects.get(user=user)
                
                if not estudiante.user.is_active:
                    raise EstudianteInactivo("Estudiante no está activo")

                if estudiante.cursos.get(id = curso_id):
                    messages.warning(request, "El estudiante ya está en el curso")
                    estudiantes_lista_paginada = PerfilEstudiante.objects.filter(user=user)
                    estudiante = None
                    
            except EstudianteInactivo as e:
                messages.error(request, e)
                estudiante = None
                
            except User.DoesNotExist:
                # Manejar el caso donde el usuario no existe
                messages.error(request, "No se encontró un estudiante con ese código")
                estudiante = None
            except PerfilEstudiante.DoesNotExist:
                # Manejar el caso donde el perfil del estudiante no existe
                messages.error(request, "No se encontró un estudiante con ese código")
                estudiante = None
            except Curso.DoesNotExist:
                    pass
                
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
                    estudiantes_lista_paginada = curso.perfilestudiante_set.all()
            else:
                messages.error(request, "Debe buscar un estudiante antes de agregar")
            estudiante = None
        if "eliminar-estudiante" in request.POST:
            estudiante_id = request.POST.get("eliminar-estudiante")
            try:
                estudiante_a_eliminar = PerfilEstudiante.objects.get(user__id=estudiante_id)
                
                grupos_asociados = Grupo.objects.filter(curso=curso)
                
                for grupo in grupos_asociados:
                    if grupo.has_evaluated and estudiante_a_eliminar in grupo.estudiantes.all():
                        raise GrupoHasEvaluated("No puedes eliminar al estudiante, porque el grupo ya ha evaluado.")
                    grupo.estudiantes.remove(estudiante_a_eliminar)
                
                estudiante_a_eliminar.cursos.remove(curso)
                messages.success(request, "Estudiante eliminado del curso exitosamente")
                estudiantes_lista_paginada = curso.perfilestudiante_set.all()
                
            except PerfilEstudiante.DoesNotExist:
                messages.error(request, "No se encontró el estudiante para eliminar")
            except GrupoHasEvaluated as e:
                messages.warning(request, e)
                
        if "finalizar-curso" in request.POST:
            curso_id = request.POST.get("finalizar-curso")
            curso = Curso.objects.get(id = curso_id)

            curso.has_finished = True
            curso.save()
            messages.success(request, f"El curso {curso.nombre} ha finalizado con éxito.")
            return redirect("profesor_cursos")
        
        if "guardar-cvs" in request.POST:
            archivo = request.FILES.get("csv-estudiantes")
            
            if not archivo:
                messages.error(request, "No se ha seleccionado ningún archivo.")
                return render(request, 'profesor/detalle_curso.html', {"curso": curso, "estudiantes_lista_paginada": estudiantes_lista_paginada, "estudiante": estudiante})
            
            decoded_file = archivo.read().decode('utf-8').splitlines()
            
            reader = csv.DictReader(decoded_file, delimiter=';')
            
            # Limpiar el BOM si está presente, archivos excel
            fieldnames = reader.fieldnames
            if fieldnames and fieldnames[0].startswith('\ufeff'):
                fieldnames[0] = fieldnames[0][1:]
            
            # Verificar si los nombres de columna son correctos
            if fieldnames != ["codigo estudiantil", "nombre estudiante", "apellidos estudiante", "correo electronico"]:
                messages.error(request, "El formato del archivo CSV no es válido.")
                return render(request, 'profesor/detalle_curso.html', {"curso": curso, "estudiantes_lista_paginada": estudiantes_lista_paginada, "estudiante": estudiante})
            
            estudiantes_creados = 0
            estudiantes_add = 0
            estudiantes_en_cursos = 0
            with transaction.atomic():
                for row in reader:
                    codigo = row.get('codigo estudiantil')
                    nombre = row.get('nombre estudiante')
                    apellidos = row.get('apellidos estudiante')
                    email = row.get('correo electronico')
                    
                    if not (codigo and nombre and apellidos and email):
                        messages.error(request, f"Faltan datos en la fila: {row}")
                        continue

                    user, created = User.objects.get_or_create(
                        username=codigo,
                        defaults={'first_name': nombre, 'last_name': apellidos, 'email': email, 'role': User.ROLES['ESTUDIANTE']}
                    )
                    
                    if created:
                        user.set_password(codigo)
                        user.save()
                        estudiantes_creados += 1
                    else:
                        user.is_active = True
                        user.save()
                        pass
                    
                    perfil_estudiante, _ = PerfilEstudiante.objects.get_or_create(user=user)
                    if perfil_estudiante.cursos.filter(id = curso.id).exists():
                        estudiantes_en_cursos += 1
                    else:
                        perfil_estudiante.cursos.add(curso)
                        estudiantes_add += 1

                messages.success(request, f"{estudiantes_creados} estudiantes creados, {estudiantes_add} añadidos, {estudiantes_en_cursos} ya estaban en el curso.")
                estudiantes_lista = curso.perfilestudiante_set.all().order_by("-id")
                pagination = Paginator(estudiantes_lista, 10)
                page = request.GET.get('page')
                estudiantes_lista_paginada = pagination.get_page(page)

            
    return render(request, 'profesor/detalle_curso.html', {"curso": curso, "estudiantes_lista_paginada" : estudiantes_lista_paginada, "estudiante" : estudiante})

#Configuración de evaluación del curso
@login_required
def profesor_evaluacion_curso(request, curso_id):
    curso = Curso.objects.get(id = curso_id)
    evaluaciones = Evaluacion.objects.filter(curso=curso).order_by("-id")
    nombre_evaluacion = request.POST.get("nombre-evaluacion")
    nombre_rubrica = request.POST.get("rubrica")
    fecha_inicio = request.POST.get("fecha-inicio")
    fecha_fin = request.POST.get("fecha-fin")
    rubrica_id = request.POST.get("guardar-evaluacion")
    fecha_actual = datetime.now().date()
    
    for evaluacion in evaluaciones:
        evaluacion.fecha_inicio = evaluacion.fecha_inicio.strftime('%Y-%m-%d')
        evaluacion.fecha_fin = evaluacion.fecha_fin.strftime('%Y-%m-%d')
    
    try:
        if request.method == "POST":
            if "guardar-evaluacion" in request.POST:
                rubrica = Rubrica.objects.get(id = rubrica_id)
                if nombre_rubrica != rubrica.nombre +"-" +rubrica.autor.first_name:
                    raise RubricaNoEncontrada("No se encontró una rúbrica con ese nombre")
                
                fecha_incio_validacion = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
                fecha_fin_validacion = datetime.strptime(fecha_fin, '%Y-%m-%d').date()
                
                if fecha_incio_validacion < fecha_actual:
                    raise InvalidDate("La fecha inicial no puede ser inferior a la fecha actual")
                if fecha_fin_validacion < fecha_actual:
                    raise InvalidDate("la fecha final no puede ser inferior o igual a la fecha actual.")
                
                
                rubrica.is_used = True
                rubrica.save()
                Evaluacion.objects.create(fecha_inicio = fecha_inicio, fecha_fin = fecha_fin, curso = curso, rubrica = rubrica, nombre = nombre_evaluacion)
                messages.success(request, "Evaluación creada correctamente")
                return redirect(reverse("crear_evaluacion", args=[curso.id]))
            
            if "edit-evaluacion" in request.POST:
                evaluacion_id = request.POST.get("edit-evaluacion")
                evaluacion_nombre = request.POST.get("evaluacion-nombre")
                evaluacion_fecha_fin = request.POST.get("evaluacion-fecha-fin")
                
                evaluacion_edit = Evaluacion.objects.get(id = evaluacion_id)
                
                evaluacion_fecha_fin = datetime.strptime(evaluacion_fecha_fin, '%Y-%m-%d').date()
                
                if evaluacion_fecha_fin < fecha_actual:
                    raise InvalidDate("la fecha final no puede ser inferior o igual a la fecha actual.")
                if evaluacion_fecha_fin < evaluacion_edit.fecha_inicio:
                    raise InvalidDate("La fecha final no puede ser inferior a la fecha inicial")
                    
                evaluacion_edit.fecha_fin = evaluacion_fecha_fin
                evaluacion_edit.nombre = evaluacion_nombre
                evaluacion_edit.save()
                
                
                messages.success(request, "La evaluación se ha editado satisfactoriamente.")
                return redirect(reverse("crear_evaluacion", args=[curso.id]))
            
    except InvalidDate as e:
        messages.error(request, e)
    except RubricaNoEncontrada as e:
        messages.error(request, e)
    except Exception as e:
        messages.error(request, "No se encontró una rúbrica con ese nombre")
    return render(request, 'profesor/evaluacion_curso.html', {"curso": curso, "evaluaciones" : evaluaciones})

@login_required
def profesor_gestion_de_estudiantes(request):
    return render(request, 'profesor/gestion_de_estudiantes.html')

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
def profesor_grupo(request, curso_id):
    curso_actual = curso_id
    curso = Curso.objects.get(id = curso_id)
    grupos = Grupo.objects.filter(curso = curso_id)
    try:
        if request.method == "POST":
            if "add-estudiante" in request.POST:
                codigo = request.POST.get("codigo_estudiante")
                grupo_id = request.POST.get("add-estudiante")
                if not codigo:
                    raise EmptyField("Ingrese el código")
                try:
                    user = User.objects.get(username=codigo)
                    estudiante = PerfilEstudiante.objects.get(user=user, cursos= curso)
                    
                    if Grupo.objects.filter(curso=curso, estudiantes=estudiante).exists():
                        raise AlreadyExist("El estudiante ya se encuentra agregado en el grupo")
                    
                    grupo = Grupo.objects.get(id = grupo_id)
                    grupo.estudiantes.add(estudiante)
                    messages.success(request, "Estudiante agregado al grupo exitosamente")
                    
                except User.DoesNotExist:
                    messages.error(request, "No se encontró un estudiante con ese código")
                except PerfilEstudiante.DoesNotExist:
                    messages.error(request, "No se encontró un estudiante con ese código")
                except Grupo.DoesNotExist:
                    messages.error(request, "No se encontró el grupo")
                except AlreadyExist as e:
                    messages.warning(request, e)
                
            if "guardar" in request.POST:
                
                nombre_grupo = request.POST.get("nombre-grupo")
                nombre_proyecto = request.POST.get("nombre-proyecto")
                
                if not nombre_grupo  or not nombre_proyecto :
                    raise EmptyField("Escribe nombre de grupo y nombre de proyecto")
            
                Grupo.objects.create(nombre=nombre_grupo, proyecto_asignado=nombre_proyecto, curso=curso) 
                messages.success(request, "Grupo creado correctamente.")
            
            if "edit-info-grupo" in request.POST:
                nombre_grupo_edit = request.POST.get("nombre-grupo-edit").strip()
                nombre_proyecto_edit = request.POST.get("nombre-proyecto-edit").strip()
                grupo_id = request.POST.get("edit-info-grupo")
                
                if not nombre_grupo_edit  or not nombre_proyecto_edit :
                    raise EmptyField("Escribe nombre de grupo y nombre de proyecto")
                
                grupo = get_object_or_404(Grupo, id=grupo_id)
                grupo.nombre = nombre_grupo_edit
                grupo.proyecto_asignado = nombre_proyecto_edit
                messages.success(request, "Grupo actualizado correctamente")
                grupo.save()
                
            if "eliminar-estudiante-grupo" in request.POST:
                estudiante_codigo = request.POST.get("eliminar-estudiante-grupo")
                grupo_id = request.POST.get("grupo")
                if estudiante_codigo is None:
                    raise EmptyField("Estudiante no especificado")
                
                estudiante = get_object_or_404(PerfilEstudiante, id=estudiante_codigo)
                grupo = get_object_or_404(Grupo, id=grupo_id)
                
                if grupo.has_evaluated:
                    raise GrupoHasEvaluated("El grupo ya empezó a evaluar, no puedes eliminar estudiantes.")
                
                grupo.estudiantes.remove(estudiante)
                messages.success(request, "Estudiante eliminado del grupo exitosamente.")
                
            if "eliminar-grupo" in request.POST:
                grupo_id = request.POST.get("eliminar-grupo")
                
                if not grupo_id:
                    raise EmptyField("No se especificó el grupo.")
                try:
                    grupo = Grupo.objects.get(id = grupo_id)
                    if not grupo.estudiantes.exists():
                        grupo.delete()
                        messages.warning(request, "Se eliminó el grupo satisfactoriamente.")
                    else:
                        messages.error(request, "No se puede eliminar el grupo porque tiene estudiantes asignados.")
                except Grupo.DoesNotExist:
                    messages.error(request, "Ya no existe ese grupo.")
                
    except EmptyField as e:   
        messages.error(request, e)
        
    except GrupoHasEvaluated as e:
        messages.warning(request, e)
    return render(request, 'profesor/grupo.html', {"curso_actual" : curso_actual, "curso": curso, "grupos": grupos})

#Informes
@login_required
def profesor_informes(request):
    usuario = request.user
    profesor = PerfilProfesor.objects.get(user=usuario)
    cursos_list = Curso.objects.filter(profesor=profesor).annotate(num_evaluaciones=Count('evaluacion'))

    # Pagination
    paginator = Paginator(cursos_list, 10)
    page = request.GET.get('page')
    lista_cursos = paginator.get_page(page)
    if request.method == "POST":
        if "buscar" in request.POST:
            codigo = request.POST.get("codigo_curso")
            curso = Curso.objects.filter(codigo = codigo).annotate(num_evaluaciones=Count('evaluacion'))
            cursos_list = curso
            paginator = Paginator(cursos_list, 10)
            page = request.GET.get('page')
            lista_cursos = paginator.get_page(page)
            
    return render(request, 'profesor/informes.html', {"lista_cursos": lista_cursos})


@login_required
def ver_informe_curso(request, curso_id):
    curso = get_object_or_404(Curso, id=curso_id)
    evaluaciones = Evaluacion.objects.filter(curso=curso)
    
    return render(request, 'profesor/ver_informe_curso.html', {'curso': curso, 'evaluaciones': evaluaciones,})


@login_required
def ver_informe_evaluacion(request, curso_id, evaluacion_id):
    curso = get_object_or_404(Curso, id=curso_id)
    evaluacion = get_object_or_404(Evaluacion, id=evaluacion_id)
    grupos = Grupo.objects.filter(curso=curso).prefetch_related('estudiantes')

    # Obtener los criterios de la evaluación
    criterios = Criterio.objects.filter(rubrica=evaluacion.rubrica)
    
    resultados = Resultado.objects.filter(
        evaluacion=evaluacion
    ).values(
        'evaluado_id',
        'criterio_evaluado__descripcion',
        'criterio_evaluado__peso'
    ).annotate(
        promedio_notas=Avg('nota__calificacion', output_field=FloatField())
    ).annotate(
        valor_ponderado=ExpressionWrapper(F('promedio_notas') * F('criterio_evaluado__peso'), output_field=FloatField())
    )

    # Crear un diccionario para almacenar los totales por evaluado
    totales_por_evaluado = {}
    for resultado in resultados:
        evaluado_id = resultado['evaluado_id']
        valor_ponderado = resultado['valor_ponderado']
        if evaluado_id not in totales_por_evaluado:
            totales_por_evaluado[evaluado_id] = 0
        totales_por_evaluado[evaluado_id] += valor_ponderado

    context = {
        'curso': curso,
        'evaluacion': evaluacion,
        'grupos': grupos,
        'criterios': criterios,
        'resultados': resultados,
        'totales_por_evaluado': totales_por_evaluado
    }
    return render(request, 'profesor/ver_informe_evaluacion.html', context)

@login_required
def profesor_estudiantes_faltantes(request, curso_id, evaluacion_id):
    curso = get_object_or_404(Curso, id=curso_id)
    evaluacion = get_object_or_404(Evaluacion, id=evaluacion_id)
    grupos = Grupo.objects.filter(curso=curso).prefetch_related('estudiantes')
    
        # Retrieve all results for this evaluation
    resultados = Resultado.objects.filter(evaluacion=evaluacion)

    # Create a dictionary to track who has evaluated whom
    evaluaciones_dict = {}
    for resultado in resultados:
        evaluador_id = resultado.evaluador.id
        evaluado_id = resultado.evaluado.id
        if evaluador_id not in evaluaciones_dict:
            evaluaciones_dict[evaluador_id] = set()
        evaluaciones_dict[evaluador_id].add(evaluado_id)
    
    return render(request, 'profesor/estudiantes_faltantes.html',{"curso":curso,"evaluacion":evaluacion, "grupos":grupos, "evaluaciones_dict":evaluaciones_dict})

#Gestión de rúbricas
@login_required
def profesor_gestion_rubricas(request):
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
                    messages.error(request, "No puede estar vacío el campo de la rúbrica")
                    return redirect('profesor_gestion_rubricas')
                
                if not descripciones_criterios or not descripciones_escalas:
                    messages.error(request, "No pueden estar vacíos los campos de criterios ni escalas")
                    return redirect('profesor_gestion_rubricas')
                
                for calificacion in escalas:
                    try:
                        calificaciones = int(calificacion)
                    except:
                        messages.error(request, "Las calificaciones deben ser un valor entre 0-10")
                        return redirect('profesor_gestion_rubricas')
                # Verificar que la suma de los pesos sea igual a 1
                try:
                    suma_pesos = sum(float(peso) for peso in pesos_criterios)
                    if suma_pesos != 1.0:
                        messages.error(request, "La suma de los pesos de todos los criterios debe ser igual a 1")
                        return redirect('profesor_gestion_rubricas')
                except:
                    messages.error(request, "Debes introducir valores decimales en los criterios")
                    redirect('profesor_gestion_rubricas')
                
                
                nombre_rubrica = nombre_rubrica.lower()
                
                
                
                # Crear la rúbrica
                rubrica = Rubrica.objects.create(nombre=nombre_rubrica, autor = request.user)

                # Crear los criterios
                for descripcion, peso in zip(descripciones_criterios, pesos_criterios):
                    Criterio.objects.create(descripcion=descripcion, peso=peso, rubrica=rubrica)

                # Crear las calificaciones (escalas)
                for escala, descripcion in zip(escalas, descripciones_escalas):
                    Calificacion.objects.create(calificacion=escala, descripcion=descripcion, rubrica=rubrica)

                messages.success(request, 'Rúbrica creada correctamente.')
                return redirect('profesor_gestion_rubricas')

            if "buscar" in request.POST:
                nombre_rubrica = request.POST.get("nombre_rubrica")
                nombre_rubrica = nombre_rubrica.lower()
                rubrica_lista = Rubrica.objects.filter(nombre=nombre_rubrica)
                if not rubrica_lista:
                    messages.error(request, "No se encontraron rúbricas con ese nombre")
                    return redirect("profesor_gestion_rubricas")
            
            if "eliminar-rubrica" in request.POST:
                rubrica_id = request.POST.get("eliminar-rubrica")
                rubrica = Rubrica.objects.get(id=rubrica_id)
                
                if rubrica.autor != request.user:
                    raise AutorNoAutorizado("No estás autorizado para eliminar esta rúbrica")
                
                if rubrica.is_used:
                    raise RubricaEnUso("La rúbrica está siendo usada en una evaluación (No se puede eliminar)")
                
                rubrica.delete()
                messages.warning(request, "Rúbrica eliminada exitosamente")
                return redirect('profesor_gestion_rubricas')
            
            if "editar-rubrica" in request.POST:
                rubrica_id_editar = request.POST.get("editar-rubrica")

                # Prefix the input names with the rubrica_id
                nombre_rubrica_editar = request.POST.get(f'nombre_rubrica_edit_{rubrica_id_editar}')
                
                descripciones_criterios_editar = request.POST.getlist(f'descripcion_criterio_edit_{rubrica_id_editar}[]')
                
                pesos_criterios_editar = request.POST.getlist(f'peso_criterio_edit_{rubrica_id_editar}[]')
                
                escalas_editar = request.POST.getlist(f'escala_edit_{rubrica_id_editar}[]')
                
                descripciones_escalas_editar = request.POST.getlist(f'descripcion_escala_edit_{rubrica_id_editar}[]')

                rubrica_editar = Rubrica.objects.get(id=rubrica_id_editar)

                if rubrica_editar.autor != request.user:
                    raise AutorNoAutorizado("No estás autorizado para editar esta rúbrica")
                
                if rubrica_editar.is_used:
                    raise RubricaEnUso("La rúbrica está siendo usada en una evaluación (No se puede editar)")

                if not nombre_rubrica_editar or not nombre_rubrica_editar.strip():
                    messages.error(request, "No puede estar vacío el campo de la rúbrica")
                    return redirect('profesor_gestion_rubricas')

                if not descripciones_criterios_editar or not descripciones_escalas_editar:
                    messages.error(request, "No pueden estar vacíos los campos de criterios ni escalas")
                    return redirect('profesor_gestion_rubricas')

                # Verificar que la suma de los pesos sea igual a 1
                suma_pesos_editar = sum(float(peso) for peso in pesos_criterios_editar)

                if suma_pesos_editar != 1.0:
                    messages.error(request, "La suma de los pesos de todos los criterios debe ser igual a 1")
                    return redirect('profesor_gestion_rubricas')

                nombre_rubrica_editar = nombre_rubrica_editar.lower()

                # Actualizar la rúbrica
                rubrica_editar.nombre = nombre_rubrica_editar
                rubrica_editar.save()

                # Eliminar criterios y escalas antiguos
                rubrica_editar.criterio_set.all().delete()
                rubrica_editar.calificacion_set.all().delete()

                # Crear los nuevos criterios
                for descripcion, peso in zip(descripciones_criterios_editar, pesos_criterios_editar):
                    Criterio.objects.create(descripcion=descripcion, peso=float(peso), rubrica=rubrica_editar)

                # Crear las nuevas calificaciones (escalas)
                for escala, descripcion in zip(escalas_editar, descripciones_escalas_editar):
                    Calificacion.objects.create(calificacion=escala, descripcion=descripcion, rubrica=rubrica_editar)

                messages.success(request, "Rúbrica actualizada exitosamente.")
                return redirect('profesor_gestion_rubricas')

        except AutorNoAutorizado as e:
            messages.error(request, e)
        except Rubrica.DoesNotExist:
            messages.error(request, "No se encontró la rúbrica")
        except ProtectedError:
            messages.error(request, "La rúbrica está siendo usada en una evaluación (No se puede eliminar)")
        except RubricaEnUso as e:
            messages.error(request, e)
        except InvalidOperation:
            messages.error(request, "Debe ingresar un valor decimal")
        
        
    return render(request, 'profesor/gestion_rubricas.html', {'rubrica_lista': rubrica_lista})

#@login_required
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
                    messages.error(request, "No se encontró un docente con ese documento")
            elif "guardar" in request.POST:
                first_name = request.POST.get('nombres')
                last_name = request.POST.get('apellidos')
                username = request.POST.get('documento-docente')
                email = request.POST.get('email')
                
                if int(username) <0 :
                    raise ValidationError(username)
                
                user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name,password=username, email=email, role="PROFESOR")
                messages.success(request, "Docente guardado correctamente")
                return redirect(reverse('administrador_gestion_de_docentes'))
            
            elif "edit-user" in request.POST:
                user_id = request.POST.get('edit-user')
                usuario = User.objects.get(id=user_id)
                usuario.first_name = request.POST.get('edit-nombre')
                usuario.last_name = request.POST.get('edit-apellidos')
                usuario.username = request.POST.get('edit-documento')
                usuario.email = request.POST.get('edit-email')
                usuario.is_active = request.POST.get('edit-estado')
                
                profesor = PerfilProfesor.objects.get(user = user_id)
                cursos_activos = Curso.objects.filter(profesor=profesor, has_finished=False)

                if usuario.is_active == "False":
                    if cursos_activos.exists():
                        messages.warning(request, "El profesor tiene cursos Activos, no puede estar inactivo")
                        return redirect(reverse("administrador_gestion_de_docentes"))
                
                usuario.save()
                messages.success(request, "Docente actualizado correctamente")
                return redirect(reverse('administrador_gestion_de_docentes'))
            
        except IntegrityError:
            messages.error(request, "Ya existe un docente con ese documento")
        
        except ValueError  as e:
            messages.error(request, f"Debes escribir un número de documento.")
            
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
            
            if "guardar-cvs" in request.POST:
                archivo = request.FILES.get("csv-estudiantes")
                
                if not archivo:
                    messages.error(request, "No se ha seleccionado ningún archivo.")
                    return redirect(reverse('administrador_gestion_de_estudiantes'))                
                decoded_file = archivo.read().decode('utf-8').splitlines()
                
                reader = csv.DictReader(decoded_file, delimiter=';')
                
                # Limpiar el BOM si está presente, archivos excel
                fieldnames = reader.fieldnames
                if fieldnames and fieldnames[0].startswith('\ufeff'):
                    fieldnames[0] = fieldnames[0][1:]
                
                # Verificar si los nombres de columna son correctos
                if fieldnames != ["codigo estudiantil", "nombre estudiante", "apellidos estudiante", "correo electronico"]:
                    messages.error(request, "El formato del archivo CSV no es válido.")
                    return redirect(reverse('administrador_gestion_de_estudiantes'))                 
                estudiantes_creados = 0
                estudiantes_existentes = 0
                with transaction.atomic():
                    for row in reader:
                        codigo = row.get('codigo estudiantil')
                        nombre = row.get('nombre estudiante')
                        apellidos = row.get('apellidos estudiante')
                        email = row.get('correo electronico')
                        
                        if not (codigo and nombre and apellidos and email):
                            messages.error(request, f"Faltan datos en la fila: {row}")
                            continue

                        user, created = User.objects.get_or_create(
                            username=codigo,
                            defaults={'first_name': nombre, 'last_name': apellidos, 'email': email, 'role': User.ROLES['ESTUDIANTE']}
                        )
                        
                        if created:
                            user.set_password(codigo)
                            user.save()
                            estudiantes_creados += 1
                        else:
                            user.is_active = True
                            user.save()
                            estudiantes_existentes += 1
                        
                        

                    messages.success(request, f"{estudiantes_creados} estudiantes creados, {estudiantes_existentes} ya existían en la base de datos")
                
        except IntegrityError:
            messages.error(request, "Ya existe un estudiante con ese código.")
        
        except ValueError  as e:
            messages.error(request, f"Error: debe proporcionar un código")
            
        except ValidationError as e:
            messages.error(request, f"El código debe ser mayor a 0: {e}")
        
        except Exception as e:
            messages.error(request, f"Error al procesar la solicitud: {e}")
        pagination = Paginator(PerfilEstudiante.objects.all().order_by('-id'), 10)
        page = request.GET.get('page')
        estudiantes_lista = pagination.get_page(page)
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
                    raise ValueError("No se encontró un curso con ese código")
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
                messages.success(request, "Curso guardado correctamente")
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
                messages.success(request, "Curso actualizado correctamente")
                
        except ProfesorInactivo as e:
            messages.error(request, e)
        except IntegrityError:
            messages.error(request, "Ya hay un curso con ese código en el mismo periodo")
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
                    messages.error(request, "No puede estar vacío el campo de la rúbrica")
                    return redirect('administrador_gestion_de_evaluacion')
                
                for calificacion in escalas:
                    try:
                        calificaciones = int(calificacion)
                    except:
                        messages.error(request, "Las calificaciones deben ser un valor entre 0-10")
                        return redirect('administrador_gestion_de_evaluacion')
                
                if not descripciones_criterios or not descripciones_escalas:
                    messages.error(request, "No pueden estar vacíos los campos de criterios ni escalas")
                    return redirect('administrador_gestion_de_evaluacion')
                
                # Verificar que la suma de los pesos sea igual a 1
                try:
                    suma_pesos = sum(float(peso) for peso in pesos_criterios)
                    if suma_pesos != 1.0:
                        messages.error(request, "La suma de los pesos de todos los criterios debe ser igual a 1")
                        return redirect('administrador_gestion_de_evaluacion')
                except:
                    messages.error(request, "Debes introducir valores decimales en los criterios")
                    redirect('administrador_gestion_de_evaluacion')
                
                nombre_rubrica = nombre_rubrica.lower()
                
                # Crear la rúbrica
                rubrica = Rubrica.objects.create(nombre=nombre_rubrica, autor = request.user)

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
                rubrica_lista = Rubrica.objects.filter(nombre=nombre_rubrica)
                if not rubrica_lista:
                    messages.error(request, "No se encontraron rúbricas con ese nombre")
                    return redirect("administrador_gestion_de_evaluacion")
            
            if "eliminar-rubrica" in request.POST:
                rubrica_id = request.POST.get("eliminar-rubrica")
                rubrica = Rubrica.objects.get(id=rubrica_id)
                
                if rubrica.is_used:
                    raise RubricaEnUso("La rúbrica está siendo usada en una evaluación (No se puede eliminar)")
                
                rubrica.delete()
                messages.warning(request, "Rúbrica eliminada exitosamente")
                return redirect('administrador_gestion_de_evaluacion')
            
            if "editar-rubrica" in request.POST:
                rubrica_id_editar = request.POST.get("editar-rubrica")

                # Prefix the input names with the rubrica_id
                nombre_rubrica_editar = request.POST.get(f'nombre_rubrica_edit_{rubrica_id_editar}')
                
                descripciones_criterios_editar = request.POST.getlist(f'descripcion_criterio_edit_{rubrica_id_editar}[]')
                
                pesos_criterios_editar = request.POST.getlist(f'peso_criterio_edit_{rubrica_id_editar}[]')
                
                escalas_editar = request.POST.getlist(f'escala_edit_{rubrica_id_editar}[]')
                
                descripciones_escalas_editar = request.POST.getlist(f'descripcion_escala_edit_{rubrica_id_editar}[]')

                rubrica_editar = Rubrica.objects.get(id=rubrica_id_editar)

                if rubrica_editar.is_used:
                    raise RubricaEnUso("La rúbrica está siendo usada en una evaluación (No se puede editar)")

                if not nombre_rubrica_editar or not nombre_rubrica_editar.strip():
                    messages.error(request, "No puede estar vacío el campo de la rúbrica")
                    return redirect('administrador_gestion_de_evaluacion')

                if not descripciones_criterios_editar or not descripciones_escalas_editar:
                    messages.error(request, "No pueden estar vacíos los campos de criterios ni escalas")
                    return redirect('administrador_gestion_de_evaluacion')

                # Verificar que la suma de los pesos sea igual a 1
                suma_pesos_editar = sum(float(peso) for peso in pesos_criterios_editar)

                if suma_pesos_editar != 1.0:
                    messages.error(request, "La suma de los pesos de todos los criterios debe ser igual a 1")
                    return redirect('administrador_gestion_de_evaluacion')

                nombre_rubrica_editar = nombre_rubrica_editar.lower()

                # Actualizar la rúbrica
                rubrica_editar.nombre = nombre_rubrica_editar
                rubrica_editar.save()

                # Eliminar criterios y escalas antiguos
                rubrica_editar.criterio_set.all().delete()
                rubrica_editar.calificacion_set.all().delete()

                # Crear los nuevos criterios
                for descripcion, peso in zip(descripciones_criterios_editar, pesos_criterios_editar):
                    Criterio.objects.create(descripcion=descripcion, peso=float(peso), rubrica=rubrica_editar)

                # Crear las nuevas calificaciones (escalas)
                for escala, descripcion in zip(escalas_editar, descripciones_escalas_editar):
                    Calificacion.objects.create(calificacion=escala, descripcion=descripcion, rubrica=rubrica_editar)

                messages.success(request, "Rúbrica actualizada exitosamente.")
                return redirect('administrador_gestion_de_evaluacion')

        except Rubrica.DoesNotExist:
            messages.error(request, "No se encontró la rúbrica")
        except ProtectedError:
            messages.error(request, "La rúbrica está siendo usada en una evaluación (No se puede eliminar)")
        except RubricaEnUso as e:
            messages.error(request, e)
        except InvalidOperation:
            messages.error(request, "Debe ingresar un valor decimal")
        
    return render(request, 'administrador/gestion_de_evaluacion.html', {'rubrica_lista': rubrica_lista})