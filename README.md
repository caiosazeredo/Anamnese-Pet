# 🐾 PetAnamnese - Sistema de Gestão de Atendimentos Pet

Sistema de gerenciamento de atendimentos para pets desenvolvido para os cursos do  . O sistema permite controle completo do fluxo desde o cadastro de tutores e pets até o check-out do atendimento com assinaturas digitais.

![Python](https://img.shields.io/badge/Python-3.8+-blue)
![Flask](https://img.shields.io/badge/Flask-2.3+-green)
![MySQL](https://img.shields.io/badge/MySQL-8.0+-orange)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-purple)

## 📋 Funcionalidades

### 👥 Gestão de Pessoas
- **Tutores**: Cadastro completo com validação de CPF
- **Alunos**: Registro de estudantes vinculados às turmas
- **Instrutores**: Gestão de professores responsáveis

### 🐕 Gestão de Pets
- Cadastro detalhado (espécie, raça, porte, pelagem, temperamento)
- Histórico completo de atendimentos
- Suporte para fotos
- Busca avançada por características

### 📋 Anamnese Digital
- Formulário completo baseado no template 
- Termo de ciência e responsabilidade
- Assinaturas digitais otimizadas para tablets
- Validações médicas (alergias, cirurgias, etc.)

### 🏥 Controle de Atendimentos
- **Check-in**: Registro de entrada com validação de anamnese
- **Acompanhamento**: Status em tempo real
- **Check-out**: Finalização com procedimentos realizados
- **Assinaturas**: Tutor + até 3 alunos participantes

### 📊 Relatórios Avançados
- Pets atendidos por turma/aula/curso
- Histórico de atendimentos por aluno
- Distribuição por raças, portes e espécies
- Exportação em PDF para documentação

### 🎯 Características Especiais
- **Interface otimizada para tablets**
- **Assinaturas digitais com canvas**
- **Busca inteligente de tutores**
- **Controle de intercorrências**
- **Histórico completo para fins legais**

## 🚀 Instalação e Configuração

### Pré-requisitos
- Python 3.8+
- MySQL 8.0+
- pip (gerenciador de pacotes Python)

### 1. Clone o Repositório
```bash
git clone https://github.com//petanamnese.git
cd petanamnese
```

### 2. Instale as Dependências
```bash
pip install -r requirements.txt
```

### 3. Configure o Banco de Dados
```bash
# Copie o arquivo de exemplo
cp .env.example .env

# Edite o .env com suas configurações
nano .env
```

**Configuração do banco (.env):**
```env
DATABASE_URL=mysql+pymysql://usuario:senha@host:porta/database
SECRET_KEY=sua-chave-secreta-super-segura
```

### 4. Execute o Script de Configuração
```bash
# Criar estrutura do banco e usuário admin
python run.py admin

# Testar conexão
python run.py test
```

### 5. Execute o Sistema
```bash
python run.py
```

O sistema estará disponível em: `http://localhost:5000`

**Login padrão:**
- Email: `admin@.br`
- Senha: `admin123`

## 🗄️ Estrutura do Banco de Dados

### Principais Tabelas
- **usuarios**: Controle de acesso ao sistema
- **tutores**: Responsáveis pelos pets
- **pets**: Animais cadastrados
- **alunos**: Estudantes dos cursos
- **turmas**: Classes de ensino
- **anamneses**: Fichas médicas dos pets
- **atendimentos**: Registros de check-in/check-out
- **aulas**: Controle de datas das aulas

### Relacionamentos
```
Tutor (1:N) Pet
Pet (1:N) Anamnese
Pet (1:N) Atendimento
Atendimento (N:M) Aluno
Turma (1:N) Atendimento
```

## 📱 Uso do Sistema

### 1. Fluxo Básico de Atendimento

#### **Passo 1: Cadastro do Tutor**
- Acessar "Gerenciar Tutores" → "Adicionar Tutor"
- Preencher dados completos com validação de CPF
- Sistema verifica duplicatas automaticamente

#### **Passo 2: Cadastro do Pet**
- Selecionar tutor cadastrado
- Preencher informações (espécie, raça, porte, pelagem)
- Opção de adicionar foto

#### **Passo 3: Anamnese**
- Preenchimento automático após cadastro do pet
- Formulário médico completo
- Termo de ciência obrigatório
- Assinatura digital do tutor

#### **Passo 4: Check-in**
- Buscar tutor/pet
- Validar anamnese ativa
- Vincular à turma/aula do dia
- Confirmar entrada

#### **Passo 5: Check-out**
- Selecionar procedimentos realizados
- Registrar observações do dia
- Marcar até 3 alunos participantes
- Colher assinaturas digitais (tutor + alunos)

### 2. Gestão de Alunos e Turmas

#### **Cadastro de Alunos**
```python
# Acessar "Gerenciar Alunos" → "Adicionar Aluno"
# Dados: nome, CPF, telefone, endereço
```

#### **Vinculação à Turmas**
```python
# Cada aluno pode estar em múltiplas turmas
# Controle de situação: Matriculado/Aprovado/Reprovado
```

### 3. Relatórios Disponíveis

#### **Pets por Turma/Aula**
- Filtro por período
- Agrupamento por curso
- Contadores automáticos

#### **Atendimentos por Aluno**
- Histórico completo
- Função no atendimento (Principal/Auxiliar)
- Exportação PDF

#### **Distribuição por Características**
- Raças mais atendidas
- Portes predominantes
- Espécies por curso

## 🛠️ Tecnologias Utilizadas

### Backend
- **Flask 2.3+**: Framework web Python
- **SQLAlchemy**: ORM para banco de dados
- **PyMySQL**: Driver MySQL
- **Werkzeug**: Utilitários web

### Frontend
- **Bootstrap 5.3**: Framework CSS responsivo
- **Font Awesome 6**: Ícones
- **jQuery 3.6**: Biblioteca JavaScript
- **Signature Pad**: Assinaturas digitais

### Banco de Dados
- **MySQL 8.0+**: Banco principal
- **Suporte Aiven Cloud**: Para produção

## 📊 Estrutura de Arquivos

```
petanamnese/
├── app.py                      # Aplicação principal
├── models.py                   # Modelos de dados
├── config.py                   # Configurações
├── run.py                      # Script de execução
├── requirements.txt            # Dependências
├── .env.example               # Exemplo de configuração
├── README.md                  # Esta documentação
│
├── templates/                 # Templates HTML
│   ├── base.html             # Template base
│   ├── login.html            # Tela de login
│   ├── dashboard.html        # Dashboard principal
│   ├── tutores/              # Templates de tutores
│   ├── pets/                 # Templates de pets
│   ├── anamnese/             # Templates de anamnese
│   ├── atendimentos/         # Templates de atendimentos
│   ├── relatorios/           # Templates de relatórios
│   └── alunos/               # Templates de alunos
│
├── static/                   # Arquivos estáticos
│   ├── css/
│   ├── js/
│   └── images/
│
├── scripts/                  # Scripts auxiliares
│   ├── backup_database.py    # Backup automático
│   ├── import_data.py        # Importação de dados
│   └── setup_production.py  # Configuração produção
│
└── uploads/                  # Uploads (fotos, etc.)
```

## 🔧 Configuração para Produção

### 1. Servidor Web
```bash
# Usar Gunicorn
pip install gunicorn
gunicorn -w 3 -b 127.0.0.1:5000 run:app
```

### 2. Banco de Dados
```bash
# Configure SSL e pool de conexões
DATABASE_URL=mysql+pymysql://user:pass@host:port/db?ssl_disabled=false
```

### 3. Nginx (Exemplo)
```nginx
server {
    listen 80;
    server_name petanamnese..br;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    location /static {
        alias /var/www/petanamnese/static;
        expires 1y;
    }
}
```

## 📱 Otimizações para Tablet

### Interface Touch-Friendly
- Botões com área mínima de 44px
- Inputs com fonte 16px (evita zoom no iOS)
- Feedback tátil e visual

### Assinaturas Digitais
- Canvas responsivo para diferentes orientações
- Resolução otimizada para alta qualidade
- Auto-resize em mudança de orientação

### Performance
- Auto-save de formulários longos
- Carregamento progressivo
- Cache inteligente

## 🔒 Segurança

### Autenticação
- Hash seguro de senhas (Werkzeug)
- Sessões com timeout configurável
- Proteção CSRF

### Validações
- CPF com algoritmo de validação
- Sanitização de inputs
- Proteção contra SQL Injection

### Backup
- Script automático de backup
- Retenção configurável
- Compressão de arquivos

## 📈 Monitoramento

### Logs do Sistema
```python
# Logs automáticos de:
- Logins/logouts
- Criação de registros
- Erros e exceções
- Ações críticas
```

### Métricas Disponíveis
- Atendimentos por dia/semana/mês
- Utilização por curso
- Performance do sistema

## 🤝 Contribuição

### Padrões de Código
- PEP 8 para Python
- Comentários em português
- Docstrings para funções importantes

### Estrutura de Commits
```
feat: adiciona nova funcionalidade
fix: corrige bug
docs: atualiza documentação
style: ajustes de formatação
refactor: reestruturação de código
test: adiciona testes
```

## 📞 Suporte

### Contatos
- **Email**: suporte.ti@.br
- **Telefone**: (21) 3883-7000
- **Documentação**: Esta README

### Troubleshooting Comum

#### Erro de Conexão MySQL
```bash
# Verificar se o servidor está rodando
systemctl status mysql

# Testar conexão
python run.py test
```

#### Problema com Assinaturas
```bash
# Verificar se Signature Pad está carregado
# Limpar cache do navegador
# Verificar orientação do tablet
```

#### Performance Lenta
```bash
# Verificar pool de conexões no .env
# Analisar logs de erro
# Otimizar queries do banco
```

## 📋 Roadmap

### Versão 2.0 (Próxima)
- [ ] Integração com Power Apps
- [ ] Sincronização SharePoint
- [ ] App mobile nativo
- [ ] Relatórios em tempo real

### Versão 1.5 (Em desenvolvimento)
- [ ] Dashboard avançado
- [ ] Notificações automáticas
- [ ] Exportação Excel
- [ ] Temas personalizáveis

## 📄 Licença

Este projeto é propriedade do   e destina-se exclusivamente ao uso interno da instituição para fins educacionais.

---

**🐾 PetAnamnese -  **  
*Sistema desenvolvido para otimizar o atendimento pet nos cursos técnicos*

*Versão 1.0 - Janeiro 2025*