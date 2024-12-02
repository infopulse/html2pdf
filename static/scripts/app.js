document.getElementById('parse-btn').addEventListener('click', function() {
    const parseBtn = document.getElementById('parse-btn');
    parseBtn.disabled = true; // Disable the button
    parseBtn.classList.add('disabled'); // Add disabled class
    parseBtn.classList.add('loading'); // Add disabled class

    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    const urls = document.getElementById('urls').value.split('\n');

    const data = {
        username: username,
        password: password,
        links: urls
    };

    fetch('https://jhvb0axfuj.execute-api.eu-north-1.amazonaws.com/manual-deploy/html2pdf-backend', {
        method: 'POST',
        body: JSON.stringify(data),
        headers: {
            'Content-Type': 'application/json'
        }
    })
        .then(response => response.json()) // Ensure to parse the response as JSON
        .then(data => {
            // Handle the successful response here
            const links = data.links; // Assuming 'links' contains the array of URLs
            const linksContainer = document.createElement('div'); // Create a container for the links
            const label = document.createElement('label'); // Create a container for the links
            label.innerText = 'Results:';
            linksContainer.classList = 'result-links-list form-group';
            linksContainer.appendChild(label); // Append the link to the container

            links.forEach((link, index) => {
                const linkElement = document.createElement('a'); // Create an anchor element
                linkElement.href = link; // Set the href attribute
                linkElement.textContent = `Download PDF № ${index+1}`; // Link text
                linkElement.target = '_blank'; // Open the link in a new tab
                linksContainer.appendChild(linkElement); // Append the link to the container
                linksContainer.appendChild(document.createElement('br')); // Add a line break between links
            });
            const formRoot = document.querySelector('.login-box')
            formRoot.appendChild(linksContainer);
        })
        .catch((error) => {
            console.error('Error:', error);
        })
        .finally(() => {
            parseBtn.disabled = false; // Re-enable the button
            parseBtn.classList.remove('disabled'); // Remove disabled class
            parseBtn.classList.remove('loading'); // Remove disabled class
        });
});
