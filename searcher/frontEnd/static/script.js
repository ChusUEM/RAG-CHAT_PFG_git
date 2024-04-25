function buscarRespuesta() {
    var pregunta = document.getElementById('pregunta').value;
    var xhr = new XMLHttpRequest();
    xhr.open('POST', '/buscar', true);
    xhr.setRequestHeader('Content-Type', 'application/json');

    // Crear un nuevo div para el mensaje de carga
    var divCarga = document.createElement('div');
    divCarga.id = 'carga';
    divCarga.innerHTML = 'Cargando...';

    // Agregar el div de carga al div #respuesta
    var respuestas = document.getElementById('respuesta');
    respuestas.appendChild(divCarga);

    xhr.onreadystatechange = function() {
        if (xhr.readyState == XMLHttpRequest.DONE) {
            // Eliminar el div de carga
            var divCarga = document.getElementById('carga');
            respuestas.removeChild(divCarga);

            if (xhr.status == 200) {
                var data = JSON.parse(xhr.responseText);
                var respuesta = data.respuesta;
                var enlaces = data.enlaces;

                // Crear un nuevo div para la pregunta
                var divPregunta = document.createElement('div');
                divPregunta.innerHTML = '<strong>Pregunta recibida: </strong>' + pregunta;

                // Crear un nuevo div para la respuesta
                var divRespuesta = document.createElement('div');
                divRespuesta.innerHTML = '<strong>Respuesta emitida: </strong>' + respuesta;

                // Crear un nuevo div para los enlaces
                var divEnlaces = document.createElement('div');
                divEnlaces.innerHTML = '<strong>Para más información, consulte estos enlaces: </strong>';
                for (var i = 0; i < enlaces.length; i++) {
                    var a = document.createElement('a');
                    a.href = enlaces[i].url;
                    a.textContent = enlaces[i].title;
                    divEnlaces.appendChild(a);
                }

                // Agregar los nuevos divs al div #respuesta
                respuestas.appendChild(divPregunta);
                respuestas.appendChild(divRespuesta);
                respuestas.appendChild(divEnlaces);
            } else {
                console.error('Error al buscar respuesta:', xhr.status);
            }
        }
    };
    xhr.send(JSON.stringify({pregunta: pregunta}));

    // Limpiar la caja de texto para la próxima pregunta
    document.getElementById('pregunta').value = '';
}