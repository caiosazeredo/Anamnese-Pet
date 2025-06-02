# scripts/setup_production.py
"""
Script para configurar ambiente de produção
"""
import os
import subprocess
import secrets

def setup_production():
    """Configura ambiente de produção"""
    
    print("Configurando ambiente de produção...")
    
    # Gerar chave secreta
    secret_key = secrets.token_urlsafe(32)
    
    # Criar arquivo .env de produção
    env_content = f"""
FLASK_ENV=production
SECRET_KEY={secret_key}
DATABASE_URL=mysql+pymysql://petanamnese_user:senha_segura@localhost/petanamnese

# Configurações de segurança
SECURITY_CSRF_ENABLED=True
WTF_CSRF_ENABLED=True

# Configurações de email
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=sistema@senac.br
MAIL_PASSWORD=senha_do_app

# Configurações de backup
BACKUP_ENABLED=True
BACKUP_SCHEDULE=daily
BACKUP_RETENTION_DAYS=30
"""
    
    with open('.env.production', 'w') as f:
        f.write(env_content.strip())
    
    print("Arquivo .env.production criado!")
    
    # Configurar nginx (exemplo)
    nginx_config = """
server {
    listen 80;
    server_name petanamnese.senac.br;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location /static {
        alias /var/www/petanamnese/static;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
"""
    
    # Salvar configuração do nginx
    with open('nginx_petanamnese.conf', 'w') as f:
        f.write(nginx_config)
    
    print("Configuração do nginx criada!")
    
    # Configurar systemd service
    service_config = """
[Unit]
Description=PetAnamnese Flask App
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/petanamnese
Environment="PATH=/var/www/petanamnese/venv/bin"
ExecStart=/var/www/petanamnese/venv/bin/gunicorn --workers 3 --bind 127.0.0.1:5000 run:app
Restart=always

[Install]
WantedBy=multi-user.target
"""
    
    with open('petanamnese.service', 'w') as f:
        f.write(service_config)
    
    print("Arquivo de serviço systemd criado!")
    
    print("\nPróximos passos para produção:")
    print("1. Copiar arquivos para /var/www/petanamnese")
    print("2. sudo cp petanamnese.service /etc/systemd/system/")
    print("3. sudo cp nginx_petanamnese.conf /etc/nginx/sites-available/")
    print("4. sudo ln -s /etc/nginx/sites-available/petanamnese /etc/nginx/sites-enabled/")
    print("5. sudo systemctl enable petanamnese")
    print("6. sudo systemctl start petanamnese")
    print("7. sudo systemctl reload nginx")

