document.getElementById('parse-btn').addEventListener('click', function() {
    const parseBtn = document.getElementById('parse-btn');
    parseBtn.disabled = true; // Disable the button
    parseBtn.classList.add('disabled'); // Add disabled class
    parseBtn.classList.add('loading'); // Add loading class

    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    const urls = document.getElementById('urls').value.split('\n');

    const linksContainer = document.createElement('div');
    const label = document.createElement('label');
    label.innerText = 'Results:';
    linksContainer.classList = 'result-links-list form-group';
    linksContainer.appendChild(label); // Append the label to the container

    // Add the links container to the UI
    const formRoot = document.querySelector('.login-box');
    formRoot.appendChild(linksContainer);

    // Helper function to process a single link
    const processLink = async (link, index) => {
        const linkStatus = document.createElement('p'); // Create a paragraph to show status
        linkStatus.textContent = `Processing link ${index + 1}...`;
        linksContainer.appendChild(linkStatus); // Show processing status

        const data = {
            username: username,
            password: password,
            links: [link]
        };

        await fetch('https://jhvb0axfuj.execute-api.eu-north-1.amazonaws.com/manual-deploy/html2pdf-backend', {
            method: 'POST',
            body: JSON.stringify(data),
            headers: {
                'Content-Type': 'application/json'
            }
        })
            .then(response => response.json()) // Parse the response as JSON
            .then(data => {
                const processedLink = data.links[0]; // Assuming the response contains the processed link
                linkStatus.textContent = `Processed link ${index + 1}:`; // Update the status
                linkStatus.classList = 'success';
                const linkElement = document.createElement('a'); // Create an anchor element
                linkElement.href = processedLink; // Set the href attribute
                linkElement.textContent = `Download PDF for link ${index + 1}`; // Link text
                linkElement.target = '_blank'; // Open in a new tab
                linksContainer.appendChild(linkElement); // Append the link to the container
                linksContainer.appendChild(document.createElement('br')); // Line break
            })
            .catch((error) => {
                console.error('Error processing link:', error);
                linkStatus.classList = 'error';
                linkStatus.textContent = `Error processing link ${index + 1}`; // Update the status to error
            });
    };

    // Process each link sequentially
    urls.forEach(async (url, index) => {
        await processLink(url, index);
        if (index === urls.length - 1) {
            parseBtn.disabled = false;
            parseBtn.classList.remove('disabled');
            parseBtn.classList.remove('loading');
        }
    });
});
