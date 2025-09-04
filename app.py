#!/usr/bin/env python
# coding: utf-8

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import sqlite3
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta_aqui_altere_em_producao'

# Configuração do Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Classe User para o Flask-Login
class User(UserMixin):
    def __init__(self, id, username, role):
        self.id = id
        self.username = username
        self.role = role

# Configuração do banco de dados
def init_db():
    conn = sqlite3.connect('estoque_construcao.db')
    cursor = conn.cursor()
    
    # Criar tabela de usuários
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL DEFAULT 'user',
        nome TEXT NOT NULL,
        email TEXT,
        data_cadastro TEXT NOT NULL
    )
    ''')
    
    # Criar tabela de produtos
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS produtos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        codigo INTEGER UNIQUE NOT NULL,
        descricao TEXT NOT NULL,
        categoria TEXT NOT NULL,
        quantidade INTEGER NOT NULL,
        preco_unitario REAL NOT NULL,
        fornecedor TEXT NOT NULL,
        estoque_minimo INTEGER NOT NULL,
        data_validade TEXT,
        lote TEXT,
        data_cadastro TEXT NOT NULL
    )
    ''')
    
    # Criar tabela de movimentações
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS movimentacoes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        produto_id INTEGER NOT NULL,
        tipo TEXT NOT NULL,
        quantidade INTEGER NOT NULL,
        data TEXT NOT NULL,
        observacao TEXT,
        usuario_id INTEGER,
        FOREIGN KEY (produto_id) REFERENCES produtos (id),
        FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
    )
    ''')
    
    # Inserir usuário admin padrão se não existir
    cursor.execute("SELECT COUNT(*) FROM usuarios WHERE username = 'admin'")
    if cursor.fetchone()[0] == 0:
        password_hash = generate_password_hash('admin123')
        cursor.execute('''
        INSERT INTO usuarios (username, password_hash, role, nome, email, data_cadastro)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', ('admin', password_hash, 'admin', 'Administrador', 'admin@empresa.com', datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
    
    # Inserir alguns dados de exemplo de produtos
    cursor.execute("SELECT COUNT(*) FROM produtos")
    if cursor.fetchone()[0] == 0:
        produtos_exemplo = [
            (1001, 'Cimento CP II 50kg', 'CIMENTO', 500, 28.90, 'Votorantim', 100, '2024-12-31', 'LOTE001'),
            (1002, 'Areia Média m³', 'AGREGADOS', 200, 85.00, 'Pedreira São José', 50, None, None),
            (1003, 'Tijolo Baiano 1000un', 'CERÂMICOS', 150, 450.00, 'Cerâmica Santa Rita', 30, None, None),
            (1004, 'Vergalhão CA-50 6mm', 'FERRO_E_ACO', 80, 25.00, 'Gerdau', 20, None, None),
            (1005, 'Tinta Acrílica Branco Gelo 18L', 'TINTAS', 40, 189.90, 'Suvinil', 10, '2025-06-30', 'LOTE005')
        ]
        
        for produto in produtos_exemplo:
            cursor.execute('''
            INSERT INTO produtos (codigo, descricao, categoria, quantidade, preco_unitario, fornecedor, estoque_minimo, data_validade, lote, data_cadastro)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', produto + (datetime.now().strftime('%Y-%m-%d %H:%M:%S'),))
    
    conn.commit()
    conn.close()

# Função para conectar ao banco de dados
def get_db_connection():
    conn = sqlite3.connect('estoque_construcao.db')
    conn.row_factory = sqlite3.Row
    return conn

# Callback para carregar o usuário
@login_manager.user_loader
def load_user(user_id):
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM usuarios WHERE id = ?', (user_id,)).fetchone()
    conn.close()
    
    if user:
        return User(user['id'], user['username'], user['role'])
    return None

# Rotas de autenticação
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM usuarios WHERE username = ?', (username,)).fetchone()
        conn.close()
        
        if user and check_password_hash(user['password_hash'], password):
            user_obj = User(user['id'], user['username'], user['role'])
            login_user(user_obj)
            
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            return redirect(url_for('index'))
        else:
            flash('Usuário ou senha incorretos!', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Você foi desconectado com sucesso!', 'info')
    return redirect(url_for('login'))

@app.route('/alterar-senha', methods=['GET', 'POST'])
@login_required
def alterar_senha():
    if request.method == 'POST':
        senha_atual = request.form['senha_atual']
        nova_senha = request.form['nova_senha']
        confirmar_senha = request.form['confirmar_senha']
        
        if nova_senha != confirmar_senha:
            flash('As novas senhas não coincidem!', 'danger')
            return render_template('alterar_senha.html')
        
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM usuarios WHERE id = ?', (current_user.id,)).fetchone()
        
        if user and check_password_hash(user['password_hash'], senha_atual):
            new_password_hash = generate_password_hash(nova_senha)
            conn.execute('UPDATE usuarios SET password_hash = ? WHERE id = ?', (new_password_hash, current_user.id))
            conn.commit()
            conn.close()
            
            flash('Senha alterada com sucesso!', 'success')
            return redirect(url_for('index'))
        else:
            conn.close()
            flash('Senha atual incorreta!', 'danger')
    
    return render_template('alterar_senha.html')

# Rotas protegidas da aplicação
@app.route('/')
@login_required
def index():
    conn = get_db_connection()
    produtos = conn.execute('SELECT * FROM produtos ORDER BY descricao').fetchall()
    
    # Calcular valor total do estoque
    valor_total = conn.execute('SELECT SUM(quantidade * preco_unitario) FROM produtos').fetchone()[0] or 0
    
    # Verificar produtos com estoque baixo
    produtos_baixo_estoque = conn.execute(
        'SELECT * FROM produtos WHERE quantidade <= estoque_minimo ORDER BY quantidade ASC'
    ).fetchall()
    
    conn.close()
    
    return render_template('index.html', 
                         produtos=produtos, 
                         valor_total=valor_total,
                         produtos_baixo_estoque=produtos_baixo_estoque)

@app.route('/adicionar', methods=['GET', 'POST'])
@login_required
def adicionar_produto():
    if request.method == 'POST':
        codigo = request.form['codigo']
        descricao = request.form['descricao']
        categoria = request.form['categoria']
        quantidade = request.form['quantidade']
        preco_unitario = request.form['preco_unitario']
        fornecedor = request.form['fornecedor']
        estoque_minimo = request.form['estoque_minimo']
        data_validade = request.form['data_validade'] or None
        lote = request.form['lote'] or None
        
        try:
            conn = get_db_connection()
            conn.execute('''
            INSERT INTO produtos (codigo, descricao, categoria, quantidade, preco_unitario, fornecedor, estoque_minimo, data_validade, lote, data_cadastro)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (codigo, descricao, categoria, quantidade, preco_unitario, fornecedor, estoque_minimo, data_validade, lote, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
            
            # Registrar a movimentação de entrada
            produto_id = conn.execute('SELECT id FROM produtos WHERE codigo = ?', (codigo,)).fetchone()['id']
            conn.execute('''
            INSERT INTO movimentacoes (produto_id, tipo, quantidade, data, observacao, usuario_id)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', (produto_id, 'ENTRADA', quantidade, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'Cadastro inicial', current_user.id))
            
            conn.commit()
            conn.close()
            
            flash('Produto adicionado com sucesso!', 'success')
            return redirect(url_for('index'))
        except sqlite3.IntegrityError:
            flash('Erro: Código do produto já existe!', 'danger')
        except Exception as e:
            flash(f'Erro ao adicionar produto: {str(e)}', 'danger')
    
    categorias = ['CIMENTO', 'AGREGADOS', 'CERÂMICOS', 'FERRO_E_ACO', 'MADEIRAS', 
                 'TINTAS', 'HIDRAULICA', 'ELETRICA', 'FERRAMENTAS', 'OUTROS']
    
    return render_template('adicionar_produto.html', categorias=categorias)

@app.route('/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_produto(id):
    conn = get_db_connection()
    produto = conn.execute('SELECT * FROM produtos WHERE id = ?', (id,)).fetchone()
    
    if request.method == 'POST':
        codigo = request.form['codigo']
        descricao = request.form['descricao']
        categoria = request.form['categoria']
        preco_unitario = request.form['preco_unitario']
        fornecedor = request.form['fornecedor']
        estoque_minimo = request.form['estoque_minimo']
        data_validade = request.form['data_validade'] or None
        lote = request.form['lote'] or None
        
        try:
            conn.execute('''
            UPDATE produtos 
            SET codigo = ?, descricao = ?, categoria = ?, preco_unitario = ?, fornecedor = ?, estoque_minimo = ?, data_validade = ?, lote = ?
            WHERE id = ?
            ''', (codigo, descricao, categoria, preco_unitario, fornecedor, estoque_minimo, data_validade, lote, id))
            
            conn.commit()
            conn.close()
            
            flash('Produto atualizado com sucesso!', 'success')
            return redirect(url_for('index'))
        except sqlite3.IntegrityError:
            flash('Erro: Código do produto já existe!', 'danger')
        except Exception as e:
            flash(f'Erro ao atualizar produto: {str(e)}', 'danger')
    
    categorias = ['CIMENTO', 'AGREGADOS', 'CERÂMICOS', 'FERRO_E_ACO', 'MADEIRAS', 
                 'TINTAS', 'HIDRAULICA', 'ELETRICA', 'FERRAMENTAS', 'OUTROS']
    
    conn.close()
    return render_template('editar_produto.html', produto=produto, categorias=categorias)

@app.route('/excluir/<int:id>')
@login_required
def excluir_produto(id):
    try:
        conn = get_db_connection()
        conn.execute('DELETE FROM produtos WHERE id = ?', (id,))
        conn.execute('DELETE FROM movimentacoes WHERE produto_id = ?', (id,))
        conn.commit()
        conn.close()
        
        flash('Produto excluído com sucesso!', 'success')
    except Exception as e:
        flash(f'Erro ao excluir produto: {str(e)}', 'danger')
    
    return redirect(url_for('index'))

@app.route('/entrada/<int:id>', methods=['GET', 'POST'])
@login_required
def entrada_estoque(id):
    conn = get_db_connection()
    produto = conn.execute('SELECT * FROM produtos WHERE id = ?', (id,)).fetchone()
    
    if request.method == 'POST':
        quantidade = int(request.form['quantidade'])
        observacao = request.form['observacao'] or 'Entrada de estoque'
        
        try:
            # Atualizar quantidade em estoque
            conn.execute('UPDATE produtos SET quantidade = quantidade + ? WHERE id = ?', (quantidade, id))
            
            # Registrar a movimentação
            conn.execute('''
            INSERT INTO movimentacoes (produto_id, tipo, quantidade, data, observacao, usuario_id)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', (id, 'ENTRADA', quantidade, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), observacao, current_user.id))
            
            conn.commit()
            conn.close()
            
            flash('Entrada de estoque registrada com sucesso!', 'success')
            return redirect(url_for('index'))
        except Exception as e:
            flash(f'Erro ao registrar entrada: {str(e)}', 'danger')
    
    conn.close()
    return render_template('entrada_estoque.html', produto=produto)

@app.route('/saida/<int:id>', methods=['GET', 'POST'])
@login_required
def saida_estoque(id):
    conn = get_db_connection()
    produto = conn.execute('SELECT * FROM produtos WHERE id = ?', (id,)).fetchone()
    
    if request.method == 'POST':
        quantidade = int(request.form['quantidade'])
        observacao = request.form['observacao'] or 'Saída de estoque'
        
        try:
            # Verificar se há estoque suficiente
            if produto['quantidade'] < quantidade:
                flash('Erro: Quantidade solicitada maior que o estoque disponível!', 'danger')
                return render_template('saida_estoque.html', produto=produto)
            
            # Atualizar quantidade em estoque
            conn.execute('UPDATE produtos SET quantidade = quantidade - ? WHERE id = ?', (quantidade, id))
            
            # Registrar a movimentação
            conn.execute('''
            INSERT INTO movimentacoes (produto_id, tipo, quantidade, data, observacao, usuario_id)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', (id, 'SAIDA', quantidade, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), observacao, current_user.id))
            
            conn.commit()
            conn.close()
            
            flash('Saída de estoque registrada com sucesso!', 'success')
            return redirect(url_for('index'))
        except Exception as e:
            flash(f'Erro ao registrar saída: {str(e)}', 'danger')
    
    conn.close()
    return render_template('saida_estoque.html', produto=produto)

@app.route('/movimentacoes')
@login_required
def movimentacoes():
    conn = get_db_connection()
    movimentacoes = conn.execute('''
    SELECT m.*, p.descricao as produto_descricao, u.username as usuario
    FROM movimentacoes m 
    JOIN produtos p ON m.produto_id = p.id 
    LEFT JOIN usuarios u ON m.usuario_id = u.id
    ORDER BY m.data DESC
    ''').fetchall()
    
    conn.close()
    return render_template('movimentacoes.html', movimentacoes=movimentacoes)

@app.route('/api/produtos')
@login_required
def api_produtos():
    conn = get_db_connection()
    produtos = conn.execute('SELECT * FROM produtos ORDER BY descricao').fetchall()
    conn.close()
    
    produtos_list = [dict(produto) for produto in produtos]
    return jsonify(produtos_list)

@app.route('/api/produtos/<int:id>')
@login_required
def api_produto(id):
    conn = get_db_connection()
    produto = conn.execute('SELECT * FROM produtos WHERE id = ?', (id,)).fetchone()
    conn.close()
    
    if produto:
        return jsonify(dict(produto))
    else:
        return jsonify({'error': 'Produto não encontrado'}), 404

if __name__ == '__main__':
    init_db()
    app.run(debug=True)