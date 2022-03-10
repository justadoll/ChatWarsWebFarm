## (!) Edit all this files before copying
### 1) Gunicorn socket:
 * `sudo cp gunicorn.socket /etc/systemctl/system/ & sudo systemctl enable gunicorn.socket & sudo systemctl start gunicorn.socket`
### 2) Gunicorn service:
 * `sudo cp gunicorn.service /etc/systemctl/system/ & sudo systemctl enable gunicorn.service & sudo systemctl start gunicorn.service`
### 3) Nginx:
 * Generate certs via https://certbot.eff.org/
 * `sudo apt install nginx & sudo systemctl stop nginx`
 * Modify `default` file
 * Backup default nginx config file: `sudo mv /etc/nginx/sites-available/default default.bak`
 * Copy your config file: `sudo cp default /etc/nginx/sites-available/`
 * Finally, check confing and start nginx: `nginx -t & sudo systemctl start nginx`

