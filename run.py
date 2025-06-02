# run.py - Script de execução atualizado
"""
Script de execução do Sistema PetAnamnese
Use este arquivo para executar o sistema com comandos especiais
"""

import os
import sys

# Adicionar o diretório atual ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db, Usuario, init_db
from werkzeug.security import generate_password_hash

def create_admin():
    """Criar usuário administrador"""
    with app.app_context():
        admin_email = app.config.get('ADMIN_EMAIL', 'admin@senac.br')
        admin_password = app.config.get('ADMIN_PASSWORD', 'admin123')
        
        if not Usuario.query.filter_by(email=admin_email).first():
            admin = Usuario(
                nome='Administrador Sistema',
                email=admin_email,
                senha=generate_password_hash(admin_password),
                tipo_usuario='Administrador'
            )
            db.session.add(admin)
            db.session.commit()
            print(f'✅ Usuário admin criado: {admin_email} / {admin_password}')
        else:
            print('ℹ️  Usuário admin já existe')

def test_database():
    """Testar conexão com banco de dados"""
    with app.app_context():
        try:
            # Testar conexão básica
            db.session.execute('SELECT 1').fetchone()
            print('✅ Conexão com banco OK!')
            
            # Verificar se as tabelas existem
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            
            if tables:
                print(f'📊 {len(tables)} tabelas encontradas:')
                for table in sorted(tables):
                    print(f'   - {table}')
            else:
                print('⚠️  Nenhuma tabela encontrada. Execute a inicialização.')
                
            return True
            
        except Exception as e:
            print(f'❌ Erro de conexão: {e}')
            print('\n🔧 Verifique:')
            print('1. Se o arquivo .env está configurado corretamente')
            print('2. Se o banco de dados está acessível')
            print('3. Se as credenciais estão corretas')
            return False

def init_database():
    """Inicializar banco de dados"""
    with app.app_context():
        try:
            print('🔄 Criando estrutura do banco...')
            init_db()
            print('✅ Banco inicializado com sucesso!')
            return True
        except Exception as e:
            print(f'❌ Erro ao inicializar banco: {e}')
            return False

def show_help():
    """Mostrar ajuda"""
    print("""
🚀 SISTEMA PETANAMNESE - SENAC RJ

📋 Comandos disponíveis:

python run.py                 -> Executar sistema
python run.py test            -> Testar conexão banco
python run.py admin           -> Criar usuário admin
python run.py init            -> Inicializar banco de dados
python run.py help            -> Mostrar esta ajuda

🌐 Após executar, acesse: http://localhost:5000
🔐 Login padrão: admin@senac.br / admin123

📞 Suporte: Verifique o README.md para mais informações

💡 Dica: Para desenvolvimento local, copie o conteúdo do arquivo .env criado
""")

if __name__ == '__main__':
    # Verificar argumentos
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == 'test':
            print('🔍 Testando conexão com banco de dados...')
            if test_database():
                print('\n✅ Sistema pronto para uso!')
            else:
                print('\n❌ Configure o banco antes de continuar')
                
        elif command == 'admin':
            print('👤 Criando usuário administrador...')
            create_admin()
            
        elif command == 'init':
            print('🔄 Inicializando banco de dados...')
            if init_database():
                print('👤 Criando usuário admin...')
                create_admin()
            
        elif command == 'help':
            show_help()
            
        else:
            print(f'❌ Comando desconhecido: {command}')
            show_help()
    else:
        # Executar sistema normalmente
        print('🚀 Iniciando Sistema PetAnamnese...')
        print('📊 Testando conexão...')
        
        # Verificar se banco existe, senão inicializar
        try:
            with app.app_context():
                db.session.execute('SELECT 1').fetchone()
                print('✅ Banco OK!')
        except:
            print('🔄 Inicializando banco pela primeira vez...')
            if init_database():
                print('✅ Banco inicializado!')
            else:
                print('❌ Erro na inicialização!')
                sys.exit(1)
        
        print('👤 Verificando usuário admin...')
        create_admin()
        
        print('🌐 Sistema disponível em: http://localhost:5000')
        print('🔐 Login: admin@senac.br / admin123')
        print('🛑 Pressione Ctrl+C para parar\n')
        
        # Executar Flask
        try:
            port = int(os.environ.get('PORT', 5000))
            host = os.environ.get('HOST', '0.0.0.0')
            debug = os.environ.get('FLASK_ENV') == 'development'
            
            app.run(debug=debug, host=host, port=port)
        except KeyboardInterrupt:
            print('\n👋 Sistema finalizado pelo usuário')
        except Exception as e:
            print(f'\n❌ Erro ao executar sistema: {e}')