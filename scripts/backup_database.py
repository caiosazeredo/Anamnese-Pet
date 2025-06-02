# scripts/backup_database.py
"""
Script para backup automático do banco de dados
"""
import os
import subprocess
from datetime import datetime
from pathlib import Path

def backup_database():
    """Cria backup do banco de dados MySQL"""
    
    # Configurações do banco
    db_host = os.getenv('DB_HOST', 'localhost')
    db_user = os.getenv('DB_USER', 'root')
    db_password = os.getenv('DB_PASSWORD')
    db_name = os.getenv('DB_NAME', 'petanamnese')
    
    # Diretório de backup
    backup_dir = Path('backups')
    backup_dir.mkdir(exist_ok=True)
    
    # Nome do arquivo de backup
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = backup_dir / f'petanamnese_backup_{timestamp}.sql'
    
    # Comando mysqldump
    cmd = [
        'mysqldump',
        '-h', db_host,
        '-u', db_user,
        f'-p{db_password}',
        '--single-transaction',
        '--routines',
        '--triggers',
        db_name
    ]
    
    try:
        with open(backup_file, 'w') as f:
            subprocess.run(cmd, stdout=f, check=True)
        
        print(f"Backup criado com sucesso: {backup_file}")
        
        # Compactar o backup
        import gzip
        import shutil
        
        with open(backup_file, 'rb') as f_in:
            with gzip.open(f"{backup_file}.gz", 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        
        # Remover arquivo não compactado
        backup_file.unlink()
        
        print(f"Backup compactado: {backup_file}.gz")
        
        # Limpar backups antigos (manter apenas os últimos 30 dias)
        cleanup_old_backups(backup_dir)
        
    except subprocess.CalledProcessError as e:
        print(f"Erro ao criar backup: {e}")
    except Exception as e:
        print(f"Erro inesperado: {e}")

def cleanup_old_backups(backup_dir, days=30):
    """Remove backups antigos"""
    from datetime import timedelta
    
    cutoff_date = datetime.now() - timedelta(days=days)
    
    for backup_file in backup_dir.glob('*.sql.gz'):
        if backup_file.stat().st_mtime < cutoff_date.timestamp():
            backup_file.unlink()
            print(f"Backup antigo removido: {backup_file}")

if __name__ == '__main__':
    backup_database()

