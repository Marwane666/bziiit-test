document.getElementById('chat-form').addEventListener('submit', async (event) => {
    event.preventDefault();
    const query = document.getElementById('query').value;
    const responseDiv = document.getElementById('response');

    const response = await fetch('/query', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query }),
    });

    const data = await response.json();
    responseDiv.innerHTML = data.response;
});
