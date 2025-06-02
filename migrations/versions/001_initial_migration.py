# migrations/versions/001_initial_migration.py
"""
Migração inicial do Sistema PetAnamnese
Cria todas as tabelas principais do sistema

Revision ID: 001_initial
Revises: 
Create Date: 2025-01-30 10:00:00.000000
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers
revision = '001_initial'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    """Criar estrutura inicial do banco de dados"""
    
    # Tabela de cursos
    op.create_table('cursos',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('nome', sa.String(255), nullable=False),
        sa.Column('codigo_sga', sa.String(20), nullable=True),
        sa.Column('carga_horaria', sa.Integer(), nullable=False),
        sa.Column('tipo_curso', sa.Enum('Aperfeiçoamento', 'Socioprofissional'), nullable=False),
        sa.Column('eixo_tecnologico', sa.String(100), nullable=True),
        sa.Column('segmento', sa.String(100), nullable=True),
        sa.Column('ativo', sa.Boolean(), nullable=True, default=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('codigo_sga')
    )
    
    # Tabela de instrutores
    op.create_table('instrutores',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('nome', sa.String(255), nullable=False),
        sa.Column('cpf', sa.String(14), nullable=False),
        sa.Column('telefone', sa.String(20), nullable=True),
        sa.Column('email', sa.String(255), nullable=True),
        sa.Column('especialidade', sa.Text(), nullable=True),
        sa.Column('ativo', sa.Boolean(), nullable=True, default=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('cpf')
    )
    
    # Tabela de turmas
    op.create_table('turmas',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('codigo', sa.String(50), nullable=False),
        sa.Column('curso_id', sa.Integer(), nullable=False),
        sa.Column('instrutor_id', sa.Integer(), nullable=False),
        sa.Column('data_inicio', sa.Date(), nullable=False),
        sa.Column('data_fim', sa.Date(), nullable=False),
        sa.Column('horario_inicio', sa.Time(), nullable=True),
        sa.Column('horario_fim', sa.Time(), nullable=True),
        sa.Column('local', sa.String(255), nullable=True),
        sa.Column('max_alunos', sa.Integer(), nullable=True, default=30),
        sa.Column('ativa', sa.Boolean(), nullable=True, default=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['curso_id'], ['cursos.id'], ),
        sa.ForeignKeyConstraint(['instrutor_id'], ['instrutores.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('codigo')
    )
    
    # Tabela de alunos
    op.create_table('alunos',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('nome', sa.String(255), nullable=False),
        sa.Column('cpf', sa.String(14), nullable=False),
        sa.Column('rg', sa.String(20), nullable=True),
        sa.Column('data_nascimento', sa.Date(), nullable=True),
        sa.Column('telefone', sa.String(20), nullable=True),
        sa.Column('email', sa.String(255), nullable=True),
        sa.Column('endereco', sa.Text(), nullable=True),
        sa.Column('bairro', sa.String(100), nullable=True),
        sa.Column('cidade', sa.String(100), nullable=True),
        sa.Column('uf', sa.String(2), nullable=True, default='RJ'),
        sa.Column('cep', sa.String(10), nullable=True),
        sa.Column('ativo', sa.Boolean(), nullable=True, default=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('cpf')
    )
    
    # Tabela de relacionamento aluno-turma
    op.create_table('aluno_turma',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('aluno_id', sa.Integer(), nullable=False),
        sa.Column('turma_id', sa.Integer(), nullable=False),
        sa.Column('data_matricula', sa.Date(), nullable=True),
        sa.Column('situacao', sa.Enum('Matriculado', 'Aprovado', 'Reprovado', 'Desistente'), nullable=True, default='Matriculado'),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['aluno_id'], ['alunos.id'], ),
        sa.ForeignKeyConstraint(['turma_id'], ['turmas.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Tabela de tutores
    op.create_table('tutores',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('nome', sa.String(255), nullable=False),
        sa.Column('cpf', sa.String(14), nullable=False),
        sa.Column('rg', sa.String(20), nullable=True),
        sa.Column('endereco', sa.Text(), nullable=False),
        sa.Column('bairro', sa.String(100), nullable=False),
        sa.Column('cidade', sa.String(100), nullable=False),
        sa.Column('uf', sa.String(2), nullable=True, default='RJ'),
        sa.Column('cep', sa.String(10), nullable=True),
        sa.Column('telefone', sa.String(20), nullable=False),
        sa.Column('email', sa.String(255), nullable=True),
        sa.Column('observacoes', sa.Text(), nullable=True),
        sa.Column('ativo', sa.Boolean(), nullable=True, default=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('cpf')
    )
    
    # Tabela de pets
    op.create_table('pets',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tutor_id', sa.Integer(), nullable=False),
        sa.Column('nome', sa.String(255), nullable=False),
        sa.Column('idade', sa.Integer(), nullable=True),
        sa.Column('raca', sa.String(100), nullable=True),
        sa.Column('cor', sa.String(100), nullable=True),
        sa.Column('especie', sa.Enum('Canino', 'Felino', 'Outros'), nullable=False),
        sa.Column('porte', sa.Enum('Pequeno', 'Médio', 'Grande', 'Gigante'), nullable=True),
        sa.Column('pelagem', sa.Enum('Curta', 'Longa', 'Crespa', 'Lisa', 'Ondulada', 'Dupla'), nullable=True, default='Curta'),
        sa.Column('temperamento', sa.Enum('Manso', 'Agressivo', 'Agitado', 'Tímido'), nullable=True, default='Manso'),
        sa.Column('peso', sa.Numeric(5, 2), nullable=True),
        sa.Column('observacoes', sa.Text(), nullable=True),
        sa.Column('foto', sa.String(255), nullable=True),
        sa.Column('ativo', sa.Boolean(), nullable=True, default=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['tutor_id'], ['tutores.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Tabela de anamneses
    op.create_table('anamneses',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('pet_id', sa.Integer(), nullable=False),
        sa.Column('tutor_id', sa.Integer(), nullable=False),
        sa.Column('alergia', sa.Boolean(), nullable=True, default=False),
        sa.Column('curso_atendimento', sa.Enum('Banho e Tosa', 'Técnicas Avançadas de Tosa', 'Adestramento', 'Dog Walker'), nullable=False),
        sa.Column('cirurgia_recente', sa.Boolean(), nullable=True, default=False),
        sa.Column('pode_cortar_unha', sa.Boolean(), nullable=True, default=True),
        sa.Column('pode_perfume', sa.Boolean(), nullable=True, default=True),
        sa.Column('sofre_convulsao', sa.Boolean(), nullable=True, default=False),
        sa.Column('problema_cardiorespiatorio', sa.Boolean(), nullable=True, default=False),
        sa.Column('pulga_carrapato', sa.Boolean(), nullable=True, default=False),
        sa.Column('problema_articular', sa.Boolean(), nullable=True, default=False),
        sa.Column('pode_limpar_ouvido', sa.Boolean(), nullable=True, default=True),
        sa.Column('vacinado_multipla_antirrabica', sa.Boolean(), nullable=True, default=False),
        sa.Column('observacoes_alergia', sa.Text(), nullable=True),
        sa.Column('observacoes_cirurgia', sa.Text(), nullable=True),
        sa.Column('observacoes_gerais', sa.Text(), nullable=True),
        sa.Column('data_checkin_planejado', sa.Date(), nullable=True),
        sa.Column('hora_checkin_planejado', sa.Time(), nullable=True),
        sa.Column('termo_assinado', sa.Boolean(), nullable=True, default=False),
        sa.Column('assinatura_tutor', sa.Text(), nullable=True),
        sa.Column('data_assinatura', sa.DateTime(), nullable=True),
        sa.Column('ativa', sa.Boolean(), nullable=True, default=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['pet_id'], ['pets.id'], ),
        sa.ForeignKeyConstraint(['tutor_id'], ['tutores.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Tabela de procedimentos
    op.create_table('procedimentos',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('nome', sa.String(255), nullable=False),
        sa.Column('descricao', sa.Text(), nullable=True),
        sa.Column('curso_relacionado', sa.Integer(), nullable=True),
        sa.Column('ativo', sa.Boolean(), nullable=True, default=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['curso_relacionado'], ['cursos.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Tabela de aulas
    op.create_table('aulas',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('turma_id', sa.Integer(), nullable=False),
        sa.Column('data_aula', sa.Date(), nullable=False),
        sa.Column('hora_inicio', sa.Time(), nullable=True),
        sa.Column('hora_fim', sa.Time(), nullable=True),
        sa.Column('tema', sa.String(255), nullable=True),
        sa.Column('observacoes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['turma_id'], ['turmas.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Tabela de atendimentos
    op.create_table('atendimentos',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('pet_id', sa.Integer(), nullable=False),
        sa.Column('tutor_id', sa.Integer(), nullable=False),
        sa.Column('anamnese_id', sa.Integer(), nullable=False),
        sa.Column('turma_id', sa.Integer(), nullable=False),
        sa.Column('aula_id', sa.Integer(), nullable=True),
        sa.Column('data_checkin', sa.DateTime(), nullable=True),
        sa.Column('hora_checkin', sa.Time(), nullable=True),
        sa.Column('status_atendimento', sa.Enum('Aguardando', 'Em Atendimento', 'Finalizado', 'Cancelado'), nullable=True, default='Aguardando'),
        sa.Column('data_checkout', sa.DateTime(), nullable=True),
        sa.Column('hora_checkout', sa.Time(), nullable=True),
        sa.Column('intercorrencia', sa.Boolean(), nullable=True, default=False),
        sa.Column('observacoes_intercorrencia', sa.Text(), nullable=True),
        sa.Column('observacoes_dia', sa.Text(), nullable=True),
        sa.Column('assinatura_tutor', sa.Text(), nullable=True),
        sa.Column('assinatura_aluno1', sa.Text(), nullable=True),
        sa.Column('assinatura_aluno2', sa.Text(), nullable=True),
        sa.Column('assinatura_aluno3', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['anamnese_id'], ['anamneses.id'], ),
        sa.ForeignKeyConstraint(['aula_id'], ['aulas.id'], ),
        sa.ForeignKeyConstraint(['pet_id'], ['pets.id'], ),
        sa.ForeignKeyConstraint(['tutor_id'], ['tutores.id'], ),
        sa.ForeignKeyConstraint(['turma_id'], ['turmas.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Tabela de relacionamento atendimento-aluno
    op.create_table('atendimento_aluno',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('atendimento_id', sa.Integer(), nullable=False),
        sa.Column('aluno_id', sa.Integer(), nullable=False),
        sa.Column('funcao', sa.Enum('Principal', 'Auxiliar'), nullable=True, default='Auxiliar'),
        sa.Column('assinatura', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['aluno_id'], ['alunos.id'], ),
        sa.ForeignKeyConstraint(['atendimento_id'], ['atendimentos.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Tabela de relacionamento atendimento-procedimento
    op.create_table('atendimento_procedimento',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('atendimento_id', sa.Integer(), nullable=False),
        sa.Column('procedimento_id', sa.Integer(), nullable=False),
        sa.Column('realizado', sa.Boolean(), nullable=True, default=False),
        sa.Column('observacoes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['atendimento_id'], ['atendimentos.id'], ),
        sa.ForeignKeyConstraint(['procedimento_id'], ['procedimentos.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Tabela de usuários
    op.create_table('usuarios',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('nome', sa.String(255), nullable=False),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('senha', sa.String(255), nullable=False),
        sa.Column('tipo_usuario', sa.Enum('Administrador', 'Secretaria', 'Instrutor'), nullable=False),
        sa.Column('instrutor_id', sa.Integer(), nullable=True),
        sa.Column('ativo', sa.Boolean(), nullable=True, default=True),
        sa.Column('ultimo_login', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['instrutor_id'], ['instrutores.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )
    
    # Criar índices para melhor performance
    op.create_index('ix_pets_especie', 'pets', ['especie'])
    op.create_index('ix_pets_porte', 'pets', ['porte'])
    op.create_index('ix_pets_raca', 'pets', ['raca'])
    op.create_index('ix_atendimentos_data_checkin', 'atendimentos', ['data_checkin'])
    op.create_index('ix_atendimentos_status', 'atendimentos', ['status_atendimento'])
    op.create_index('ix_tutores_cpf', 'tutores', ['cpf'])
    op.create_index('ix_alunos_cpf', 'alunos', ['cpf'])
    op.create_index('ix_turmas_ativa', 'turmas', ['ativa'])

def downgrade():
    """Remover estrutura do banco de dados"""
    
    # Remover índices
    op.drop_index('ix_turmas_ativa', table_name='turmas')
    op.drop_index('ix_alunos_cpf', table_name='alunos')
    op.drop_index('ix_tutores_cpf', table_name='tutores')
    op.drop_index('ix_atendimentos_status', table_name='atendimentos')
    op.drop_index('ix_atendimentos_data_checkin', table_name='atendimentos')
    op.drop_index('ix_pets_raca', table_name='pets')
    op.drop_index('ix_pets_porte', table_name='pets')
    op.drop_index('ix_pets_especie', table_name='pets')
    
    # Remover tabelas (ordem inversa devido às foreign keys)
    op.drop_table('usuarios')
    op.drop_table('atendimento_procedimento')
    op.drop_table('atendimento_aluno')
    op.drop_table('atendimentos')
    op.drop_table('aulas')
    op.drop_table('procedimentos')
    op.drop_table('anamneses')
    op.drop_table('pets')
    op.drop_table('tutores')
    op.drop_table('aluno_turma')
    op.drop_table('alunos')
    op.drop_table('turmas')
    op.drop_table('instrutores')
    op.drop_table('cursos')