# api_routes.py - Rotas da API para o Sistema PetAnamnese
"""
Rotas da API para comunicação AJAX
"""

from flask import Blueprint, request, jsonify, session
from models import db, Tutor, Pet, Aluno, AlunoTurma, Anamnese, Atendimento, AtendimentoAluno, Turma, Curso
from sqlalchemy import or_
from functools import wraps

# Criar blueprint para API
api = Blueprint('api', __name__, url_prefix='/api')

def login_required_api(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'success': False, 'message': 'Login necessário'}), 401
        return f(*args, **kwargs)
    return decorated_function

# =====================================================
# API DE TUTORES
# =====================================================

@api.route('/tutores/buscar', methods=['GET'])
@login_required_api
def api_buscar_tutores():
    termo = request.args.get('q', '')
    
    if len(termo) < 3:
        return jsonify([])
    
    tutores = Tutor.query.filter(
        Tutor.ativo == True,
        or_(
            Tutor.nome.contains(termo),
            Tutor.cpf.contains(termo)
        )
    ).limit(10).all()
    
    result = []
    for tutor in tutores:
        result.append({
            'id': tutor.id,
            'nome': tutor.nome,
            'cpf': tutor.cpf,
            'telefone': tutor.telefone,
            'cidade': tutor.cidade,
            'pets_count': len(tutor.pets)
        })
    
    return jsonify(result)

@api.route('/tutor/<int:tutor_id>', methods=['GET'])
@login_required_api
def api_get_tutor(tutor_id):
    tutor = Tutor.query.get_or_404(tutor_id)
    return jsonify({
        'id': tutor.id,
        'nome': tutor.nome,
        'cpf': tutor.cpf,
        'telefone': tutor.telefone,
        'endereco': tutor.endereco,
        'bairro': tutor.bairro,
        'cidade': tutor.cidade,
        'rg': tutor.rg,
        'email': tutor.email
    })

@api.route('/tutor/<int:tutor_id>', methods=['PUT'])
@login_required_api
def api_update_tutor(tutor_id):
    tutor = Tutor.query.get_or_404(tutor_id)
    data = request.get_json()
    
    try:
        tutor.nome = data.get('nome', tutor.nome)
        tutor.telefone = data.get('telefone', tutor.telefone)
        tutor.endereco = data.get('endereco', tutor.endereco)
        tutor.bairro = data.get('bairro', tutor.bairro)
        tutor.cidade = data.get('cidade', tutor.cidade)
        tutor.rg = data.get('rg', tutor.rg)
        tutor.email = data.get('email', tutor.email)
        
        db.session.commit()
        return jsonify({'success': True})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})

@api.route('/tutor/<int:tutor_id>', methods=['DELETE'])
@login_required_api
def api_delete_tutor(tutor_id):
    tutor = Tutor.query.get_or_404(tutor_id)
    
    # Verificar se há pets vinculados
    if tutor.pets:
        return jsonify({'success': False, 'message': 'Tutor possui pets cadastrados'})
    
    try:
        tutor.ativo = False
        db.session.commit()
        return jsonify({'success': True})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})

# =====================================================
# API DE PETS
# =====================================================

@api.route('/pets/<int:tutor_id>', methods=['GET'])
@login_required_api
def api_pets_tutor(tutor_id):
    pets = Pet.query.filter_by(tutor_id=tutor_id, ativo=True).all()
    return jsonify([{
        'id': p.id,
        'nome': p.nome,
        'raca': p.raca,
        'especie': p.especie,
        'porte': p.porte,
        'cor': p.cor,
        'idade': p.idade,
        'temperamento': p.temperamento,
        'pelagem': p.pelagem
    } for p in pets])

# =====================================================
# API DE ALUNOS
# =====================================================

@api.route('/alunos/buscar', methods=['GET'])
@login_required_api
def api_buscar_alunos():
    termo = request.args.get('q', '')
    turma_id = request.args.get('turma_id')
    excluir_matriculados = request.args.get('excluir_matriculados', 'false').lower() == 'true'
    
    if len(termo) < 2:
        return jsonify([])
    
    query = Aluno.query.filter(
        Aluno.ativo == True,
        or_(
            Aluno.nome.contains(termo),
            Aluno.cpf.contains(termo)
        )
    )
    
    # Excluir alunos já matriculados na turma
    if turma_id and excluir_matriculados:
        alunos_matriculados = db.session.query(AlunoTurma.aluno_id).filter_by(turma_id=turma_id).subquery()
        query = query.filter(~Aluno.id.in_(alunos_matriculados))
    
    alunos = query.limit(20).all()
    
    result = []
    for aluno in alunos:
        result.append({
            'id': aluno.id,
            'nome': aluno.nome,
            'cpf': aluno.cpf,
            'telefone': aluno.telefone,
            'email': aluno.email
        })
    
    return jsonify(result)

@api.route('/aluno', methods=['POST'])
@login_required_api
def api_create_aluno():
    data = request.get_json()
    
    # Verificar se CPF já existe
    if Aluno.query.filter_by(cpf=data['cpf']).first():
        return jsonify({'success': False, 'message': 'CPF já cadastrado'})
    
    try:
        aluno = Aluno(
            nome=data['nome'],
            cpf=data['cpf'],
            rg=data.get('rg'),
            telefone=data.get('telefone'),
            email=data.get('email'),
            endereco=data.get('endereco'),
            bairro=data.get('bairro'),
            cidade=data.get('cidade'),
            uf=data.get('uf', 'RJ'),
            cep=data.get('cep')
        )
        
        # Converter data de nascimento se fornecida
        if data.get('data_nascimento'):
            from datetime import datetime
            aluno.data_nascimento = datetime.strptime(data['data_nascimento'], '%Y-%m-%d').date()
        
        db.session.add(aluno)
        db.session.flush()  # Para obter o ID
        
        # Vincular às turmas se especificadas
        if data.get('turmas'):
            for turma_id in data['turmas']:
                matricula = AlunoTurma(
                    aluno_id=aluno.id,
                    turma_id=turma_id,
                    situacao='Matriculado'
                )
                db.session.add(matricula)
        
        db.session.commit()
        return jsonify({'success': True, 'aluno_id': aluno.id})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})

@api.route('/aluno/<int:aluno_id>', methods=['PUT'])
@login_required_api
def api_update_aluno(aluno_id):
    aluno = Aluno.query.get_or_404(aluno_id)
    data = request.get_json()
    
    try:
        aluno.nome = data.get('nome', aluno.nome)
        aluno.rg = data.get('rg', aluno.rg)
        aluno.telefone = data.get('telefone', aluno.telefone)
        aluno.email = data.get('email', aluno.email)
        aluno.endereco = data.get('endereco', aluno.endereco)
        aluno.bairro = data.get('bairro', aluno.bairro)
        aluno.cidade = data.get('cidade', aluno.cidade)
        aluno.uf = data.get('uf', aluno.uf)
        aluno.cep = data.get('cep', aluno.cep)
        
        # Atualizar data de nascimento se fornecida
        if data.get('data_nascimento'):
            from datetime import datetime
            aluno.data_nascimento = datetime.strptime(data['data_nascimento'], '%Y-%m-%d').date()
        
        # Atualizar vínculos com turmas
        if 'turmas' in data:
            # Remover matrículas existentes
            AlunoTurma.query.filter_by(aluno_id=aluno_id).delete()
            
            # Adicionar novas matrículas
            for turma_id in data['turmas']:
                matricula = AlunoTurma(
                    aluno_id=aluno_id,
                    turma_id=turma_id,
                    situacao='Matriculado'
                )
                db.session.add(matricula)
        
        db.session.commit()
        return jsonify({'success': True})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})

@api.route('/aluno/<int:aluno_id>/perfil', methods=['GET'])
@login_required_api
def api_aluno_perfil(aluno_id):
    aluno = Aluno.query.get_or_404(aluno_id)
    
    # Buscar turmas do aluno
    turmas = db.session.query(Turma, AlunoTurma).join(AlunoTurma).filter(
        AlunoTurma.aluno_id == aluno_id
    ).all()
    
    # Buscar atendimentos do aluno
    atendimentos = db.session.query(Atendimento).join(AtendimentoAluno).filter(
        AtendimentoAluno.aluno_id == aluno_id
    ).order_by(Atendimento.data_checkin.desc()).limit(5).all()
    
    perfil_html = f"""
    <div class="row">
        <div class="col-md-6">
            <h6>Dados Pessoais</h6>
            <p><strong>Nome:</strong> {aluno.nome}</p>
            <p><strong>CPF:</strong> {aluno.cpf}</p>
            <p><strong>RG:</strong> {aluno.rg or 'N/A'}</p>
            <p><strong>Telefone:</strong> {aluno.telefone or 'N/A'}</p>
            <p><strong>Email:</strong> {aluno.email or 'N/A'}</p>
        </div>
        <div class="col-md-6">
            <h6>Endereço</h6>
            <p><strong>Endereço:</strong> {aluno.endereco or 'N/A'}</p>
            <p><strong>Bairro:</strong> {aluno.bairro or 'N/A'}</p>
            <p><strong>Cidade:</strong> {aluno.cidade or 'N/A'}</p>
            <p><strong>UF:</strong> {aluno.uf or 'N/A'}</p>
        </div>
    </div>
    
    <hr>
    
    <h6>Turmas Matriculadas ({len(turmas)})</h6>
    <div class="list-group">
        {''.join([f'<div class="list-group-item d-flex justify-content-between"><span>{turma.codigo} - {turma.curso.nome}</span><span class="badge bg-{getStatusBadgeColor(matricula.situacao)}">{matricula.situacao}</span></div>' for turma, matricula in turmas]) if turmas else '<div class="list-group-item">Nenhuma turma encontrada</div>'}
    </div>
    
    <hr>
    
    <h6>Últimos Atendimentos ({len(atendimentos)})</h6>
    <div class="list-group">
        {''.join([f'<div class="list-group-item"><small>{atendimento.data_checkin.strftime("%d/%m/%Y")} - {atendimento.pet.nome} ({atendimento.turma.curso.nome})</small></div>' for atendimento in atendimentos]) if atendimentos else '<div class="list-group-item">Nenhum atendimento encontrado</div>'}
    </div>
    """
    
    return perfil_html

def getStatusBadgeColor(status):
    colors = {
        'Matriculado': 'primary',
        'Aprovado': 'success',
        'Reprovado': 'danger',
        'Desistente': 'warning'
    }
    return colors.get(status, 'secondary')

# =====================================================
# API DE MATRÍCULAS
# =====================================================

@api.route('/matricula', methods=['POST'])
@login_required_api
def api_criar_matricula():
    data = request.get_json()
    
    # Verificar se já existe matrícula
    matricula_existente = AlunoTurma.query.filter_by(
        aluno_id=data['aluno_id'],
        turma_id=data['turma_id']
    ).first()
    
    if matricula_existente:
        return jsonify({'success': False, 'message': 'Aluno já matriculado nesta turma'})
    
    try:
        matricula = AlunoTurma(
            aluno_id=data['aluno_id'],
            turma_id=data['turma_id'],
            situacao=data.get('situacao', 'Matriculado')
        )
        
        db.session.add(matricula)
        db.session.commit()
        
        return jsonify({'success': True, 'matricula_id': matricula.id})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})

@api.route('/matricula/<int:matricula_id>', methods=['PUT'])
@login_required_api
def api_update_matricula(matricula_id):
    matricula = AlunoTurma.query.get_or_404(matricula_id)
    data = request.get_json()
    
    try:
        matricula.situacao = data.get('situacao', matricula.situacao)
        db.session.commit()
        
        return jsonify({'success': True})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})

@api.route('/matricula/<int:matricula_id>', methods=['DELETE'])
@login_required_api
def api_delete_matricula(matricula_id):
    matricula = AlunoTurma.query.get_or_404(matricula_id)
    
    try:
        db.session.delete(matricula)
        db.session.commit()
        
        return jsonify({'success': True})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})

# =====================================================
# API DE ANAMNESE
# =====================================================

@api.route('/anamnese/verificar/<int:pet_id>', methods=['GET'])
@login_required_api
def api_verificar_anamnese(pet_id):
    anamnese = Anamnese.query.filter_by(pet_id=pet_id, ativa=True).first()
    
    return jsonify({
        'tem_anamnese': anamnese is not None,
        'anamnese_id': anamnese.id if anamnese else None,
        'data_criacao': anamnese.created_at.isoformat() if anamnese else None
    })