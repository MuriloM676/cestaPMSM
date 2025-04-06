from flask import Flask, request, redirect, render_template, session, url_for
import sqlite3

app = Flask(__name__)
app.secret_key = 'chave_secreta'  # Necessário para sessões

# Função para conectar ao banco
def get_db():
    conn = sqlite3.connect('cestas.db')
    conn.row_factory = sqlite3.Row  # Para retornar resultados como dicionários
    return conn

# Criar tabelas (executar apenas uma vez)
def init_db():
    conn = get_db()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username VARCHAR(50) UNIQUE,
            password VARCHAR(255),
            email VARCHAR(100)
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS beneficiarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome VARCHAR(100),
            telefone VARCHAR(20),
            endereco TEXT,
            cesta_retirada BOOLEAN DEFAULT 0,
            data_cadastro DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    # Usuário padrão
    conn.execute('INSERT OR IGNORE INTO usuarios (username, password, email) VALUES (?, ?, ?)',
                 ('admin', '1234', 'admin@example.com'))
    conn.commit()
    conn.close()

# Rota inicial
@app.route('/')
def index():
    return redirect('/login')

# Tela de login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db()
        user = conn.execute('SELECT * FROM usuarios WHERE username = ? AND password = ?',
                           (username, password)).fetchone()
        conn.close()
        if user:
            session['logged_in'] = True
            return redirect('/dashboard')
        return 'Usuário ou senha inválidos'
    return render_template('login.html')

# Dashboard com filtros
@app.route('/dashboard', methods=['GET'])
def dashboard():
    if not session.get('logged_in'):
        return redirect('/login')
    
    # Parâmetros de filtro
    nome_filtro = request.args.get('nome', '').strip()
    status_filtro = request.args.get('status', 'todos')  # 'todos', 'retirada', 'nao_retirada'

    conn = get_db()
    query = 'SELECT * FROM beneficiarios WHERE 1=1'
    params = []

    # Filtro por nome
    if nome_filtro:
        query += ' AND nome LIKE ?'
        params.append(f'%{nome_filtro}%')

    # Filtro por status da cesta
    if status_filtro == 'retirada':
        query += ' AND cesta_retirada = 1'
    elif status_filtro == 'nao_retirada':
        query += ' AND cesta_retirada = 0'

    beneficiarios = conn.execute(query, params).fetchall()
    conn.close()
    
    return render_template('dashboard.html', beneficiarios=beneficiarios, 
                          nome_filtro=nome_filtro, status_filtro=status_filtro)

# Cadastro de beneficiário
@app.route('/cadastrar', methods=['POST'])
def cadastrar():
    if not session.get('logged_in'):
        return redirect('/login')
    nome = request.form['nome']
    telefone = request.form['telefone']
    endereco = request.form['endereco']
    conn = get_db()
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
    conn.execute('UPDATE beneficiarios SET cesta_retirada = 1 WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect('/dashboard')

# Logout
@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect('/login')

if __name__ == '__main__':
    init_db()  # Cria o banco na primeira execução
    app.run(debug=True)