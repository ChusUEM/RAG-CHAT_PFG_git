function buscarRespuesta() {
    var pregunta = document.getElementById('pregunta').value;

    // Verificar si la pregunta está vacía
    if (!pregunta.trim()) {
        var respuestas = document.getElementById('respuesta');
        var divPrincipal = document.createElement('div');
        divPrincipal.className = 'bloque-respuesta';
        divPrincipal.innerHTML = 'Tienes que introducir alguna pregunta para obtener una respuesta...';
        respuestas.appendChild(divPrincipal);
        return; // Salir de la función
    }

    var xhr = new XMLHttpRequest();
    xhr.open('POST', '/buscar', true);
    xhr.setRequestHeader('Content-Type', 'application/json');

    // Crear un nuevo div principal
    var divPrincipal = document.createElement('div');
    divPrincipal.id = 'respuesta' + Date.now(); // Asegurarse de que el id sea único
    divPrincipal.className = 'bloque-respuesta'; // Agregar la clase 'bloque-respuesta'

    // Crear un nuevo div para el bloque de respuesta
    var divBloque = document.createElement('div');

    // Crear un nuevo div para el mensaje de carga
    var divCarga = document.createElement('div');
    divCarga.id = 'carga';
    divCarga.innerHTML = 'Cargando...';

    // Agregar el div de carga al divBloque
    divBloque.appendChild(divCarga);

    // Agregar el divBloque al divPrincipal
    divPrincipal.appendChild(divBloque);

    var respuestas = document.getElementById('respuesta');

    xhr.onreadystatechange = function() {
        if (xhr.readyState == XMLHttpRequest.DONE) {
            // Eliminar el div de carga
            var divCarga = document.getElementById('carga');
            divBloque.removeChild(divCarga);

            if (xhr.status == 200) {
                var data = JSON.parse(xhr.responseText);
                var respuesta = data.respuesta[0];
                console.log(respuesta);
                var enlaces = data.enlaces;

                // Crear un nuevo div para la pregunta
                var divPregunta = document.createElement('div');
                divPregunta.innerHTML = '<strong>Pregunta recibida: </strong>' + pregunta;

                // Crear un nuevo div para la respuesta
                var divRespuesta = document.createElement('div');
                if (/\*\*([\s\S]*?)\*\*/.test(respuesta)) {
                    respuesta = respuesta.replace(/\*\*([\s\S]*?)\*\*/g, '<strong>$1</strong>');
                }
                divRespuesta.innerHTML = '<strong>Respuesta emitida: </strong>' + respuesta;

                // Crear un nuevo div para los enlaces
                var divEnlaces = document.createElement('div');
                divEnlaces.innerHTML = '<strong>Para más información, consulta: </strong>';
                for (var i = 0; i < enlaces.length; i++) {
                    var a = document.createElement('a');
                    a.href = enlaces[i].url;
                    a.textContent = enlaces[i].title;
                    divEnlaces.appendChild(a);

                    // Imprimir en la consola el enlace y el elemento 'a' creado
                    console.log("Enlace: ", enlaces[i]);
                    console.log("Elemento 'a' creado: ", a);

                // Agregar un espacio después de cada enlace
                divEnlaces.innerHTML += ' ';
                }

                // Agregar los nuevos divs al divBloque
                divBloque.appendChild(divPregunta);
                divBloque.appendChild(divRespuesta);
                divBloque.appendChild(divEnlaces);
            } else {
                console.error('Error al buscar respuesta:', xhr.status);
            }
        }
    };
    xhr.send(JSON.stringify({pregunta: pregunta}));

    // Agregar el divPrincipal al div #respuesta
    respuestas.appendChild(divPrincipal);

    // Limpiar la caja de texto para la próxima pregunta
    document.getElementById('pregunta').value = '';
}