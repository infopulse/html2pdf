# setup guide
1. Run the linux server (guide created for ubuntu 22.04)
2. Clone the repository
3. Create a virtual environment `python3 -m venv .venv`
4. Install the requirements `pip install -r requirements.txt` in the virtual environment
5. Install the Playwright browser `playwright install chromium`
6. Copy the `html2pdf.service` file to `/etc/systemd/system/`
7. Update the `html2pdf.service` file with the correct configuration
8. Reload the systemd daemon `sudo systemctl daemon-reload`
9. Start the service `sudo systemctl start html2pdf`
10. Enable the service `sudo systemctl enable html2pdf`
11. Configure the nginx server to proxy the service to the correct port (127.0.0.1:8123)
12. Restart the nginx server `sudo systemctl restart nginx`
