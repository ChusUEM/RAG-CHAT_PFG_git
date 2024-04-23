import { useState } from 'react';
import axios from 'axios';

function Chat() {
    const [question, setQuestion] = useState('');
    const [response, setResponse] = useState('');

    const sendQuestion = async () => {
        const res = await axios.get('http://localhost:9200/my_index/_search', {
            params: {
                q: question
            }
        });
        const data = res.data;
        setResponse(data.hits.hits[0]._source);  // Asume que la respuesta está en el primer hit
    };

    return (
        <div>
            <input type="text" value={question} onChange={e => setQuestion(e.target.value)} />
            <button onClick={sendQuestion}>Enviar</button>
            <p>{response}</p>
        </div>
    );
}

export default Chat;