function buscarRespuesta() {
    var pregunta = document.getElementById('pregunta').value;
    var xhr = new XMLHttpRequest();
    xhr.open('POST', '/buscar', true);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.onreadystatechange = function() {
        if (xhr.readyState == XMLHttpRequest.DONE) {
            if (xhr.status == 200) {
                var data = JSON.parse(xhr.responseText);
                var respuesta = data.respuesta;
                var enlaces = data.enlaces;

                // Crear un nuevo div para la pregunta
                var divPregunta = document.createElement('div');
                divPregunta.textContent = 'La pregunta fue: ' + pregunta;

                // Crear un nuevo div para la respuesta
                var divRespuesta = document.createElement('div');
                divRespuesta.textContent = 'Respuesta emitida: ' + respuesta;

                // Crear un nuevo div para los enlaces
                var divEnlaces = document.createElement('div');
                divEnlaces.textContent = 'Para más información, puede consultar estos enlaces:';
                for (var i = 0; i < enlaces.length; i++) {
                    var a = document.createElement('a');
                    a.href = enlaces[i].url;
                    a.textContent = enlaces[i].title;
                    divEnlaces.appendChild(a);
                }

                // Agregar los nuevos divs al div #resultado
                var resultado = document.getElementById('resultado');
                resultado.appendChild(divPregunta);
                resultado.appendChild(divRespuesta);
                resultado.appendChild(divEnlaces);
            } else {
                console.error('Error al buscar respuesta:', xhr.status);
            }
        }
    };
    xhr.send(JSON.stringify({pregunta: pregunta}));

    // Limpiar la caja de texto para la próxima pregunta
    document.getElementById('pregunta').value = '';
}