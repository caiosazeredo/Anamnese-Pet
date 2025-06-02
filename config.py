# config.py - Configuração corrigida para PyMySQL
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Configuração base da aplicação"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Configuração do banco de dados
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///petanamnese.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Configurações básicas do SQLAlchemy para PyMySQL
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
        'pool_size': int(os.environ.get('DB_POOL_SIZE') or 5),
        'max_overflow': int(os.environ.get('DB_MAX_OVERFLOW') or 10),
    }
    
    # Configurações de Upload
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER') or 'uploads'
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH') or 16 * 1024 * 1024)  # 16MB
    
    # Configurações de Email
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    
    # Configurações de Segurança
    WTF_CSRF_ENABLED = os.environ.get('WTF_CSRF_ENABLED', 'true').lower() in ['true', 'on', '1']
    SESSION_COOKIE_SECURE = False  # Será True apenas em produção
    SESSION_COOKIE_HTTPONLY = True
    PERMANENT_SESSION_LIFETIME = int(os.environ.get('SESSION_LIFETIME') or 3600)  # 1 hora
    
    # Configurações do administrador
    ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL') or 'admin@senac.br'
    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD') or 'admin123'

class DevelopmentConfig(Config):
    """Configuração para desenvolvimento"""
    DEBUG = True
    
    # Para desenvolvimento local, usar SQLite se não houver DATABASE_URL
    if not os.environ.get('DATABASE_URL'):
        SQLALCHEMY_DATABASE_URI = 'sqlite:///petanamnese_dev.db'
    
    # Configurações específicas para desenvolvimento
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'echo': False,  # Set to True para debug de SQL
    }

class ProductionConfig(Config):
    """Configuração para produção"""
    DEBUG = False
    SESSION_COOKIE_SECURE = True
    
    # Configurações otimizadas para produção com MySQL/MariaDB
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
        'pool_size': int(os.environ.get('DB_POOL_SIZE') or 10),
        'max_overflow': int(os.environ.get('DB_MAX_OVERFLOW') or 20),
        'connect_args': {
            'connect_timeout': int(os.environ.get('DB_CONNECT_TIMEOUT') or 60),
            'read_timeout': int(os.environ.get('DB_READ_TIMEOUT') or 60),
            'write_timeout': int(os.environ.get('DB_WRITE_TIMEOUT') or 60),
            'charset': 'utf8mb4',
            'use_unicode': True,
        }
    }
    
    # Adicionar SSL apenas se especificado
    if os.environ.get('DB_USE_SSL', 'false').lower() == 'true':
        SQLALCHEMY_ENGINE_OPTIONS['connect_args']['ssl_disabled'] = False
        if os.environ.get('DB_SSL_CA'):
            SQLALCHEMY_ENGINE_OPTIONS['connect_args']['ssl_ca'] = os.environ.get('DB_SSL_CA')
        if os.environ.get('DB_SSL_CERT'):
            SQLALCHEMY_ENGINE_OPTIONS['connect_args']['ssl_cert'] = os.environ.get('DB_SSL_CERT')
        if os.environ.get('DB_SSL_KEY'):
            SQLALCHEMY_ENGINE_OPTIONS['connect_args']['ssl_key'] = os.environ.get('DB_SSL_KEY')

class TestingConfig(Config):
    """Configuração para testes"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    SESSION_COOKIE_SECURE = False

# Dicionário de configurações disponíveis
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

def get_config():
    """Retorna a configuração baseada na variável de ambiente FLASK_ENV"""
    env = os.environ.get('FLASK_ENV', 'development')
    return config.get(env, DevelopmentConfig)