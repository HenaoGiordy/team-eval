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


//Deseleccionar los demás items del sidebar cuando selecciono un link
function toggleRadio(input) {
  var inputs = document.getElementsByName('links');
  inputs.forEach(function(item) {
    if (item !== input) {
      item.checked = false;
    }
  });

}

//Bloquear el retroceso en lo página
window.location.hash="";
window.location.hash="Again-No-back-button";//esta linea es necesaria para chrome
window.onhashchange=function(){window.location.hash="";}

