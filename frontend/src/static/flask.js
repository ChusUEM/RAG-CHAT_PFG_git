document.getElementById('questionForm').addEventListener('submit', function(event) {
    // Prevenir la recarga de la página
    event.preventDefault();

    // Obtener la pregunta del formulario
    var question = document.getElementById('question').value;

    fetch('http://localhost:5000/ask', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({question: question}),
    })
    .then(response => response.json())
    .then(data => {
        // Mostrar la respuesta en la caja de texto de la respuesta
        document.getElementById('answer').value = data.response; // Cambiado de data.answer a data.response
    })
    .catch((error) => console.error('Error:', error));
});