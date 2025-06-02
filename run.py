# run.py - Script de execução simplificado
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
        if not Usuario.query.filter_by(email='admin@senac.br').first():
            admin = Usuario(
                nome='Administrador Sistema',
                email='admin@senac.br',
                senha=generate_password_hash('admin123'),
                tipo_usuario='Administrador'
            )
            db.session.add(admin)
            db.session.commit()
            print('✅ Usuário admin criado: admin@senac.br / admin123')
        else:
            print('ℹ️  Usuário admin já existe')

def test_database():
    """Testar conexão com banco de dados"""
    with app.app_context():
        try:
            # Testar conexão
            result = db.session.execute('SELECT 1').fetchone()
            print('✅ Conexão com banco OK!')
            
            # Verificar tabelas
            tables = db.session.execute("""
                SELECT TABLE_NAME 
                FROM INFORMATION_SCHEMA.TABLES 
                WHERE TABLE_SCHEMA = 'defaultdb'
                AND TABLE_NAME LIKE '%'
                ORDER BY TABLE_NAME
            """).fetchall()
            
            print(f'📊 {len(tables)} tabelas encontradas:')
            for table in tables:
                print(f'   - {table[0]}')
                
            return True
            
        except Exception as e:
            print(f'❌ Erro de conexão: {e}')
            print('\n🔧 Verifique:')
            print('1. Se o servidor Aiven está ativo')
            print('2. Se as credenciais no .env estão corretas')
            print('3. Se o script SQL foi executado')
            return False

def show_help():
    """Mostrar ajuda"""
    print("""
🚀 SISTEMA PETANAMNESE - SENAC RJ

📋 Comandos disponíveis:

python run.py                 -> Executar sistema
python run.py test            -> Testar conexão banco
python run.py admin           -> Criar usuário admin
python run.py help            -> Mostrar esta ajuda

🌐 Após executar, acesse: http://localhost:5000
🔐 Login padrão: admin@senac.br / admin123

📞 Suporte: Verifique o README.md para mais informações
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
            
        elif command == 'help':
            show_help()
            
        else:
            print(f'❌ Comando desconhecido: {command}')
            show_help()
    else:
        # Executar sistema normalmente
        print('🚀 Iniciando Sistema PetAnamnese...')
        print('📊 Testando conexão...')
        
        if test_database():
            print('✅ Banco OK! Criando usuário admin...')
            create_admin()
            print('🌐 Sistema disponível em: http://localhost:5000')
            print('🔐 Login: admin@senac.br / admin123')
            print('🛑 Pressione Ctrl+C para parar\n')
            
            # Executar Flask
            app.run(debug=True, host='0.0.0.0', port=5000)
        else:
            print('❌ Erro na conexão. Configure o banco primeiro!')
            print('💡 Execute: python run.py test')
