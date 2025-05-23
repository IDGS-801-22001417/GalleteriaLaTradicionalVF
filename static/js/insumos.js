

// Abrir el modal de abrirModalOrdenes
function abrirModalOrdenes() {
    // Mostrar el modal
    document.getElementById('modalOrdenes').style.display = 'flex';
}
// Cerrar el modal de registrar
function cerrarModalOrdenes() {
    // Ocultar el modal
    document.getElementById('modalOrdenes').style.display = 'none';
}


//Abrir modal de pagos al  proveedor
function abrirModalProveedor() {
    document.getElementById('modalProveedor').style.display = 'flex';
}
//Cerrar el modal de pagos al  proveedor
function cerrarModalProveedor() {
    document.getElementById('modalProveedor').style.display = 'none';
}

// Lógica para ocultar mensajes automáticamente
const messages = document.querySelectorAll('.auto-hide');
messages.forEach(function(message) {
    setTimeout(function() {
        message.style.transition = 'opacity 0.5s ease';
        message.style.opacity = '0';
        setTimeout(function() {
            message.remove();
        }, 500); // Espera a que termine la transición antes de eliminar
    }, 5000); // 5 segundos
});