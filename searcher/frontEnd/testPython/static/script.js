function buscarRespuesta() {
    var pregunta = document.getElementById('pregunta').value;
    var xhr = new XMLHttpRequest();
    xhr.open('POST', '/buscar', true);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.onreadystatechange = function() {
        if (xhr.readyState == XMLHttpRequest.DONE) {
            if (xhr.status == 200) {
                var respuesta = xhr.responseText;

                // Crear un nuevo div para la respuesta
                var divRespuesta = document.createElement('div');
                divRespuesta.innerHTML = 'Respuesta: ' + respuesta;

                // Limpiar el div #resultado y agregar el nuevo div
                var resultado = document.getElementById('resultado');
                resultado.innerHTML = '';
                resultado.appendChild(divRespuesta);
            } else {
                console.error('Error al buscar respuesta:', xhr.status);
            }
        }
    };
    xhr.send(JSON.stringify({pregunta: pregunta}));

    // Limpiar la caja de texto para la próxima pregunta
    document.getElementById('pregunta').value = '';
}