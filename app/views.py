from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from app.models import User

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
            if user.get_role() == 'Administrador':
                return redirect('admin/')
            if user.get_role() == 'Estudiante':
                return redirect('estudiante/')
            if user.get_role() == 'Profesor':
                return redirect('profesor/')
        else:
            messages.error(request, "El usuario o contraseña no coinciden")
            
    return render(request, 'login/login.html')


def estudiante(request):
    return render(request, 'estudiante/estudiante.html')