// En static/js/script.js
function confirmarEliminacion(event) {
    event.preventDefault(); // Detener el envío del formulario por defecto

    const form = event.target; // Obtener el formulario que se está enviando
    const equipoNumero = form.querySelector('button[type="submit"]').closest('tr').querySelector('td:first-child').innerText;
    const equipoTipo = form.querySelector('button[type="submit"]').closest('tr').querySelector('td:nth-child(2)').innerText;

    Swal.fire({
        title: '¿Estás seguro?',
        html: `Estás a punto de eliminar el equipo <strong style="color: #dc3545;">#${equipoNumero} (${equipoTipo})</strong>. ¡Esta acción es irreversible!`,
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#dc3545', // Rojo para confirmar eliminación
        cancelButtonColor: '#6c757d', // Gris para cancelar
        confirmButtonText: 'Sí, eliminarlo',
        cancelButtonText: 'Cancelar'
    }).then((result) => {
        if (result.isConfirmed) {
            form.submit(); // Enviar el formulario si el usuario confirma
        }
    });
    return false; // Evita el envío por defecto del formulario
}