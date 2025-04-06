from flask import Flask, request, render_template, redirect, session, url_for
import sqlite3

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta_aqui'  # Substitua por uma chave secreta segura

# Função para conectar ao banco de dados
def get_db():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

# Inicializar o banco de dados
def init_db():
    conn = get_db()
    conn.execute('''CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL,
        role TEXT NOT NULL DEFAULT 'user'
    )''')
    conn.execute('''CREATE TABLE IF NOT EXISTS beneficiarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        telefone TEXT NOT NULL UNIQUE,
        endereco TEXT NOT NULL,
        cesta_retirada INTEGER DEFAULT 0
    )''')
    conn.execute('''CREATE TABLE IF NOT EXISTS historico_retiradas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        beneficiario_id INTEGER NOT NULL,
        data_retirada TEXT NOT NULL,
        FOREIGN KEY (beneficiario_id) REFERENCES beneficiarios(id)
    )''')
    
    # Criar usuário administrador padrão (se não existir)
    admin_exists = conn.execute('SELECT * FROM usuarios WHERE username = ?', ('admin',)).fetchone()
    if not admin_exists:
        conn.execute('INSERT INTO usuarios (username, password, role) VALUES (?, ?, ?)', ('admin', 'admin123', 'admin'))
    
    # Criar usuário comum padrão (se não existir)
    user_exists = conn.execute('SELECT * FROM usuarios WHERE username = ?', ('user',)).fetchone()
    if not user_exists:
        conn.execute('INSERT INTO usuarios (username, password, role) VALUES (?, ?, ?)', ('user', 'user123', 'user'))
    
    conn.commit()
    conn.close()

# Inicializar o banco de dados ao iniciar o app
init_db()

# Rota para a página inicial (redireciona para login)
@app.route('/')
def index():
    return redirect('/login')

# Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db()
        user = conn.execute('SELECT * FROM usuarios WHERE username = ? AND password = ?', (username, password)).fetchone()
        conn.close()
        if user:
            session['logged_in'] = True
            session['username'] = user['username']
            session['role'] = user['role']
            return redirect('/dashboard')
        else:
            return render_template('login.html', error='Usuário ou senha inválidos.')
    return render_template('login.html', error=None)

# Logout
@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('username', None)
    session.pop('role', None)
    return redirect('/login')

# Dashboard com filtros e paginação
@app.route('/dashboard', methods=['GET'])
def dashboard():
    if not session.get('logged_in'):
        return redirect('/login')
    
    # Parâmetros de filtro
    nome_filtro = request.args.get('nome', '').strip()
    telefone_filtro = request.args.get('telefone', '').strip()
    status_filtro = request.args.get('status', 'todos')
    
    # Parâmetros de paginação
    page = int(request.args.get('page', 1))
    per_page = 10
    offset = (page - 1) * per_page

    conn = get_db()
    
    # Contar o total de beneficiários
    count_query = 'SELECT COUNT(*) FROM beneficiarios WHERE 1=1'
    count_params = []
    if nome_filtro:
        count_query += ' AND nome LIKE ?'
        count_params.append(f'%{nome_filtro}%')
    if telefone_filtro:
        count_query += ' AND telefone LIKE ?'
        count_params.append(f'%{telefone_filtro}%')
    if status_filtro == 'retirada':
        count_query += ' AND cesta_retirada = 1'
    elif status_filtro == 'nao_retirada':
        count_query += ' AND cesta_retirada = 0'
    
    total = conn.execute(count_query, count_params).fetchone()[0]
    total_pages = (total + per_page - 1) // per_page

    # Buscar beneficiários com paginação
    query = 'SELECT * FROM beneficiarios WHERE 1=1'
    params = []
    if nome_filtro:
        query += ' AND nome LIKE ?'
        params.append(f'%{nome_filtro}%')
    if telefone_filtro:
        query += ' AND telefone LIKE ?'
        params.append(f'%{telefone_filtro}%')
    if status_filtro == 'retirada':
        query += ' AND cesta_retirada = 1'
    elif status_filtro == 'nao_retirada':
        query += ' AND cesta_retirada = 0'
    
    query += ' LIMIT ? OFFSET ?'
    params.extend([per_page, offset])

    beneficiarios = conn.execute(query, params).fetchall()
    conn.close()
    
    return render_template('dashboard.html', beneficiarios=beneficiarios, 
                          nome_filtro=nome_filtro, telefone_filtro=telefone_filtro, 
                          status_filtro=status_filtro, error_message=request.args.get('error_message', ''),
                          page=page, total_pages=total_pages, per_page=per_page)

# Cadastro de beneficiário
@app.route('/cadastrar', methods=['POST'])
def cadastrar():
    if not session.get('logged_in'):
        return redirect('/login')
    
    # Verificar se o usuário é administrador
    if session.get('role') != 'admin':
        conn = get_db()
        beneficiarios = conn.execute('SELECT * FROM beneficiarios').fetchall()
        conn.close()
        return render_template('dashboard.html', beneficiarios=beneficiarios,
                             nome_filtro='', telefone_filtro='', status_filtro='todos',
                             error_message='Apenas administradores podem cadastrar beneficiários.')
    
    nome = request.form['nome']
    telefone = request.form['telefone']
    endereco = request.form['endereco']
    
    conn = get_db()
    
    # Verificar se o telefone já existe
    existing = conn.execute('SELECT * FROM beneficiarios WHERE telefone = ?', (telefone,)).fetchone()
    if existing:
        beneficiarios = conn.execute('SELECT * FROM beneficiarios').fetchall()
        conn.close()
        return render_template('dashboard.html', 
                             beneficiarios=beneficiarios,
                             nome_filtro='', telefone_filtro='', status_filtro='todos',
                             error_message='Erro: Este telefone já está cadastrado.')
    
    # Se não existe, prosseguir com o cadastro
    conn.execute('INSERT INTO beneficiarios (nome, telefone, endereco) VALUES (?, ?, ?)',
                 (nome, telefone, endereco))
    conn.commit()
    conn.close()
    return redirect('/dashboard')

# Marcar cesta como retirada
@app.route('/marcar_retirada/<int:id>', methods=['POST'])
def marcar_retirada(id):
    if not session.get('logged_in'):
        return redirect('/login')
    
    conn = get_db()
    # Atualizar o status da cesta
    conn.execute('UPDATE beneficiarios SET cesta_retirada = 1 WHERE id = ?', (id,))
    
    # Registrar no histórico
    from datetime import datetime
    data_retirada = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    conn.execute('INSERT INTO historico_retiradas (beneficiario_id, data_retirada) VALUES (?, ?)', (id, data_retirada))
    
    conn.commit()
    conn.close()
    return redirect('/dashboard')

# Histórico de retiradas
@app.route('/historico', methods=['GET'])
def historico():
    if not session.get('logged_in'):
        return redirect('/login')
    
    conn = get_db()
    historico = conn.execute('''
        SELECT h.id, h.beneficiario_id, h.data_retirada, b.nome 
        FROM historico_retiradas h 
        JOIN beneficiarios b ON h.beneficiario_id = b.id 
        ORDER BY h.data_retirada DESC
    ''').fetchall()
    conn.close()
    
    return render_template('historico.html', historico=historico)

if __name__ == '__main__':
    app.run(debug=True)