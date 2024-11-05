document.getElementById('parse-btn').addEventListener('click', function() {
    const parseBtn = document.getElementById('parse-btn');
    parseBtn.disabled = true; // Disable the button
     parseBtn.classList.add('disabled'); // Add disabled class

    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    const urls = document.getElementById('urls').value.split('\n');

    const data = {
        email: username,
        password: password,
        urls: urls
    };

    fetch('/parse', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        console.log('Success:', data);
    })
    .catch((error) => {
        console.error('Error:', error);
    });
});