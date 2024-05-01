(function () {
    'use strict'
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    tooltipTriggerList.forEach(function (tooltipTriggerEl) {
      new bootstrap.Tooltip(tooltipTriggerEl)
    })
  })()

  function desplazar() {
    // Obtener el elemento de la lista de usuarios
    var gestionUsuarios = document.getElementById('gestion-usuarios');
    // Verificar si los elementos Docentes y Estudiantes ya están presentes en la lista
    var docentes = document.getElementById('docentes');
    var estudiantes = document.getElementById('estudiantes');
    // Si los elementos ya están presentes, eliminarlos de la lista
    if (docentes && estudiantes) {
        docentes.parentNode.removeChild(docentes);
        estudiantes.parentNode.removeChild(estudiantes);
    } else {
        // Si los elementos no están presentes, crearlos y agregarlos a la lista
        // Crear los elementos para Docentes y Estudiantes
        docentes = document.createElement('li');
        estudiantes = document.createElement('li');
        // Configurar los atributos y contenido de los elementos
        docentes.setAttribute('class', 'elemento-sidebar');
        docentes.setAttribute('id', 'docentes');
        docentes.innerHTML = '<a class="item-sidebar py-2" href="/administrador/docentes">Docentes</a>';
        estudiantes.setAttribute('class', 'elemento-sidebar');
        estudiantes.setAttribute('id', 'estudiantes');
        estudiantes.innerHTML = '<a class="item-sidebar py-2" href="#">Estudiantes</a>';
        // Insertar los elementos en la lista después de Gestión de usuarios
        gestionUsuarios.parentNode.insertBefore(docentes, gestionUsuarios.nextSibling);
        gestionUsuarios.parentNode.insertBefore(estudiantes, gestionUsuarios.nextSibling);
    }
}



