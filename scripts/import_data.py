# scripts/import_data.py
"""
Script para importar dados de planilhas Excel
"""
import pandas as pd
from models import Tutor, Pet, Aluno, db
from app import create_app

def import_tutores_from_excel(file_path):
    """Importa tutores de uma planilha Excel"""
    app = create_app()
    
    with app.app_context():
        df = pd.read_excel(file_path)
        
        for _, row in df.iterrows():
            # Verificar se tutor já existe
            existing = Tutor.query.filter_by(cpf=row['CPF']).first()
            if existing:
                print(f"Tutor {row['Nome']} já existe, pulando...")
                continue
            
            tutor = Tutor(
                nome=row['Nome'],
                cpf=row['CPF'],
                telefone=row['Telefone'],
                endereco=row['Endereco'],
                bairro=row['Bairro'],
                cidade=row['Cidade'],
                email=row.get('Email', ''),
                rg=row.get('RG', '')
            )
            
            db.session.add(tutor)
            print(f"Importando tutor: {tutor.nome}")
        
        try:
            db.session.commit()
            print("Importação concluída com sucesso!")
        except Exception as e:
            db.session.rollback()
            print(f"Erro na importação: {e}")

def import_alunos_from_excel(file_path):
    """Importa alunos de uma planilha Excel"""
    app = create_app()
    
    with app.app_context():
        df = pd.read_excel(file_path)
        
        for _, row in df.iterrows():
            # Verificar se aluno já existe
            existing = Aluno.query.filter_by(cpf=row['CPF']).first()
            if existing:
                print(f"Aluno {row['Nome']} já existe, pulando...")
                continue
            
            aluno = Aluno(
                nome=row['Nome'],
                cpf=row['CPF'],
                telefone=row.get('Telefone', ''),
                email=row.get('Email', ''),
                endereco=row.get('Endereco', ''),
                bairro=row.get('Bairro', ''),
                cidade=row.get('Cidade', ''),
                data_nascimento=pd.to_datetime(row.get('Data_Nascimento'), errors='coerce')
            )
            
            db.session.add(aluno)
            print(f"Importando aluno: {aluno.nome}")
        
        try:
            db.session.commit()
            print("Importação de alunos concluída!")
        except Exception as e:
            db.session.rollback()
            print(f"Erro na importação: {e}")
