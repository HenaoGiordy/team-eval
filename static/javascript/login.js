//Función que permite desaparecer la alerta de usuario o password incorrecto
// Selecciona todos los elementos con la clase "alert"
let alerts = document.querySelectorAll('.alert');

// Itera sobre cada elemento seleccionado
alerts.forEach(alert => {
    // Después de la duración de la animación slideDown, añade la clase hide
    setTimeout(() => {
        alert.classList.add('hide');
    }, 3000);

    // Después de la duración de la animación de transición, elimina el elemento del DOM
    setTimeout(() => {
        alert.remove();
    }, 4500); // El tiempo total sería 3000 (para la animación) + 1000 (espera extra)
});

//Bloquear el retroceso en lo página
window.location.hash="";
window.location.hash="Again-No-back-button";//esta linea es necesaria para chrome
window.onhashchange=function(){window.location.hash="";}

//Ventana modal Docente
document.querySelectorAll('.btn-edit').forEach(btn => {
    btn.addEventListener('click', () => {
        const userId = btn.getAttribute('data-id');
        fetch(`/obtener_detalles_usuario/${userId}/`)
            .then(response => {
                
                if (!response.ok) {
                    throw new Error('Hubo un problema al obtener los detalles del usuario');
                }
                return response.json();
            })
            .then(data => {
                document.getElementById('edit-user').value = data.id;
                document.getElementById('edit-nombre').value = data.nombre;
                document.getElementById('edit-apellidos').value = data.apellidos;
                document.getElementById('edit-documento').value = data.documento;
                document.getElementById('edit-email').value = data.email;
                document.getElementById('edit-estado').value = data.estado == true ? "True" : "False"
            })
            .catch(error => console.error('Error:', error));
    });
});

//Muestra el archivo seleccionado al subirlo localmente

//Ventana modal Estudiante
document.querySelectorAll('.btn-edit-estudiante').forEach(btn => {
    btn.addEventListener('click', () => {
        const userId = btn.getAttribute('data-id');
        fetch(`/obtener_detalles_estudiante/${userId}/`)
            .then(response => {
                
                if (!response.ok) {
                    throw new Error('Hubo un problema al obtener los detalles del estudiante');
                }
                return response.json();
            })
            .then(data => {
                document.getElementById('edit-user').value = data.id;
                document.getElementById('edit-nombre-estudiante').value = data.nombre;
                document.getElementById('edit-apellidos-estudiante').value = data.apellidos;
                document.getElementById('edit-documento-estudiante').value = data.documento;
                document.getElementById('edit-email-estudiante').value = data.email;
                document.getElementById('edit-estado-estudiante').value = data.estado == true ? "True" : "False"
            })
            .catch(error => console.error('Error:', error));
    });
});

//Ventana modal Curso
document.querySelectorAll('.btn-edit-curso').forEach(btn => {
    btn.addEventListener('click', () => {
        const cursoId = btn.getAttribute('data-id');
        fetch(`/obtener_detalles_curso/${cursoId}/`)
        
            .then(response => {
                console.log(response)
                if (!response.ok) {
                    throw new Error('Hubo un problema al obtener los detalles del curso');
                }
                return response.json();
            })
            .then(data => {
                document.getElementById('edit-curso').value = data.id;
                document.getElementById('edit-codigo-curso').value = data.codigo;
                document.getElementById('edit-nombre-curso').value = data.nombre;
                document.getElementById('edit-codigo-docente').value = data.profesor_codigo;
                document.getElementById('edit-periodo-curso').value = data.periodo;
            })
            .catch(error => console.error('Error:', error));
    });
});