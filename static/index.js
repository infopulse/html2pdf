document.getElementById('parse-btn').addEventListener('click', function() {
    const parseBtn = document.getElementById('parse-btn');
    parseBtn.disabled = true; // Disable the button
     parseBtn.classList.add('disabled'); // Add disabled class

    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    const urls = document.getElementById('urls').value.split('\n');

    const data = {
        username: username,
        password: password,
        links: urls
    };

    fetch('/html2pdf', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(response => {
        if (response.ok) {
            return response.blob();
        } else {
            return response.json().then(err => { throw new Error(err.message); });
        }
    })
    .then(blob => {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'output.zip'; // Set the file name
        document.body.appendChild(a);
        a.click();
        a.remove();
        window.URL.revokeObjectURL(url);
    })
    .catch((error) => {
        console.error('Error:', error);
    })
    .finally(() => {
        parseBtn.disabled = false; // Re-enable the button
        parseBtn.classList.remove('disabled'); // Remove disabled class
    });
});