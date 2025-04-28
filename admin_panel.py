import os
import json
import requests
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.utils import secure_filename
from werkzeug.security import check_password_hash
from functools import wraps
from dotenv import load_dotenv

UPLOAD_FOLDER = 'static/menus'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
CONFIG_FILE = 'lojas_config.json'

load_dotenv()
ADMIN_USER = os.environ.get('ADMIN_USER', 'USUARIO_ADMIN_AQUI')  # Defina o usuário admin
ADMIN_PASS_HASH = os.environ.get('ADMIN_PASS_HASH')  # Defina o hash da senha admin
SECRET_KEY = os.environ.get('SECRET_KEY', 'SUA_SECRET_KEY_AQUI')  # Defina uma chave secreta forte

app = Flask(__name__)
app.secret_key = SECRET_KEY
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def load_config():
    if not os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump({'lojas': []}, f, ensure_ascii=False, indent=2)
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_config(data):
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = request.form['username']
        pwd = request.form['password']
        if user == ADMIN_USER and ADMIN_PASS_HASH and check_password_hash(ADMIN_PASS_HASH, pwd):
            session['logged_in'] = True
            return redirect(url_for('index'))
        flash('Usuário ou senha inválidos.', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    config = load_config()
    return render_template('index.html', lojas=config['lojas'])

@app.route('/add', methods=['GET', 'POST'])
@login_required
def add_loja():
    if request.method == 'POST':
        config = load_config()
        menu_img = None
        if 'menu_img' in request.files:
            file = request.files['menu_img']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                menu_img = f"menus/{filename}"
        nova_loja = {
            "id": str(len(config['lojas']) + 1),
            "nome": request.form['nome'],
            "zapi_instance": request.form['zapi_instance'],
            "zapi_url": request.form['zapi_url'],
            "grupo_aviso": request.form['grupo_aviso'],
            "connected_phone": request.form['connected_phone'],
            "tipo": request.form['tipo'],
            "horario": request.form['horario'],
            "endereco": request.form['endereco'],
            "menu": [item.strip() for item in request.form['menu'].split(',')],
            "menu_img": menu_img
        }
        config['lojas'].append(nova_loja)
        save_config(config)
        return redirect(url_for('index'))
    return render_template('add_loja.html')

@app.route('/edit/<id>', methods=['GET', 'POST'])
@login_required
def edit_loja(id):
    config = load_config()
    loja = next((l for l in config['lojas'] if l['id'] == id), None)
    if not loja:
        return "Loja não encontrada", 404
    if request.method == 'POST':
        loja['nome'] = request.form['nome']
        loja['zapi_instance'] = request.form['zapi_instance']
        loja['zapi_url'] = request.form['zapi_url']
        loja['grupo_aviso'] = request.form['grupo_aviso']
        loja['connected_phone'] = request.form['connected_phone']
        loja['tipo'] = request.form['tipo']
        loja['horario'] = request.form['horario']
        loja['endereco'] = request.form['endereco']
        loja['menu'] = [item.strip() for item in request.form['menu'].split(',')]
        if 'menu_img' in request.files:
            file = request.files['menu_img']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                loja['menu_img'] = f"menus/{filename}"
        save_config(config)
        return redirect(url_for('index'))
    return render_template('edit_loja.html', loja=loja)

@app.route('/delete/<id>', methods=['POST'])
@login_required
def delete_loja(id):
    config = load_config()
    lojas = config['lojas']
    nova_lista = [l for l in lojas if l['id'] != id]
    config['lojas'] = nova_lista
    save_config(config)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(port=5001, debug=True) 