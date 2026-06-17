from flask import Flask, request, render_template_string, redirect, url_for, send_from_directory
import hashlib
import os
import base64
from datetime import datetime
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'секретный_ключ_для_платформы_2024'

# Переходим в папку с файлом
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Принудительно создаем папки
for folder in ['static', 'static/avatars', 'static/default_avatars']:
    if not os.path.exists(folder):
        os.makedirs(folder)
        print(f"Создана папка: {folder}")

app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'avatars')

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Функция для создания простой аватарки (цветной квадрат с буквой)
def create_avatar_image(name, surname):
    try:
        from PIL import Image, ImageDraw, ImageFont
        colors = ['#3b82f6', '#ef4444', '#10b981', '#f59e0b', '#8b5cf6', '#ec4899', '#06b6d4', '#84cc16']
        color = colors[hash(name + surname) % len(colors)]
        
        img = Image.new('RGB', (200, 200), color=color)
        draw = ImageDraw.Draw(img)
        
        letter = name[0].upper() if name else 'U'
        
        try:
            font = ImageFont.truetype("arial.ttf", 80)
        except:
            font = ImageFont.load_default()
        
        bbox = draw.textbbox((0, 0), letter, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        x = (200 - text_width) // 2
        y = (200 - text_height) // 2
        
        draw.text((x, y), letter, fill='white', font=font)
        
        filename = f"{datetime.now().timestamp()}_{name}_{surname}.png"
        filepath = os.path.join('static', 'default_avatars', filename)
        img.save(filepath)
        return f'/static/default_avatars/{filename}'
    except:
        return 'U'

# ========== БАЗА ДАННЫХ ==========
пользователи = {}
текущий_пользователь = None
следующий_id_юзера = 1
следующий_id_задания = 1
следующий_id_ответа = 1

ЗАДАНИЯ = {"test": [], "homework": [], "project": []}
ответы_учеников = []

# ========== HTML ШАБЛОН ==========
ОСНОВНОЙ_ШАБЛОН = '''
<!DOCTYPE html>
<html>
<head>
    <title>StudyHub - Учебная платформа</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Inter', sans-serif; background: #0a0a0f; min-height: 100vh; color: #e5e7eb; }
        .layout { display: flex; min-height: 100vh; }
        
        .sidebar { width: 260px; background: #111114; border-right: 1px solid #2a2a2f; padding: 24px 16px; position: fixed; height: 100vh; overflow-y: auto; }
        .sidebar .logo { margin-bottom: 32px; padding: 0 12px; }
        .sidebar .logo h2 { font-size: 20px; font-weight: 600; background: linear-gradient(135deg, #3b82f6, #60a5fa); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
        .sidebar h3 { color: #6b7280; font-size: 11px; font-weight: 600; letter-spacing: 1px; margin: 20px 0 10px 12px; text-transform: uppercase; }
        .sidebar a { display: flex; align-items: center; gap: 12px; padding: 10px 12px; color: #9ca3af; text-decoration: none; border-radius: 8px; margin-bottom: 4px; transition: all 0.2s; font-size: 14px; }
        .sidebar a:hover { background: #1f1f23; color: #f3f4f6; }
        .sidebar a.active { background: #1e3a5f; color: #60a5fa; }
        
        .user-info-sidebar { text-align: center; padding: 16px 12px; border-bottom: 1px solid #2a2a2f; margin-bottom: 20px; cursor: pointer; border-radius: 12px; transition: all 0.2s; }
        .user-info-sidebar:hover { background: #1f1f23; }
        .avatar-large { width: 80px; height: 80px; border-radius: 50%; margin: 0 auto 12px; background: linear-gradient(135deg, #1e3a5f, #3b82f6); display: flex; align-items: center; justify-content: center; font-size: 36px; overflow: hidden; }
        .avatar-large img { width: 100%; height: 100%; border-radius: 50%; object-fit: cover; }
        .user-name { font-weight: 600; font-size: 14px; margin-bottom: 4px; }
        .user-role { font-size: 11px; color: #6b7280; }
        
        .main { margin-left: 260px; flex: 1; padding: 24px 32px; }
        .header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 32px; }
        .header h1 { font-size: 24px; font-weight: 600; color: #f3f4f6; }
        .user-menu { display: flex; align-items: center; gap: 16px; cursor: pointer; padding: 8px 12px; border-radius: 40px; transition: all 0.2s; }
        .user-menu:hover { background: #1f1f23; }
        .avatar-small { width: 40px; height: 40px; border-radius: 50%; background: linear-gradient(135deg, #1e3a5f, #3b82f6); display: flex; align-items: center; justify-content: center; font-size: 20px; overflow: hidden; }
        .avatar-small img { width: 100%; height: 100%; object-fit: cover; }
        
        .card { background: #111114; border: 1px solid #2a2a2f; border-radius: 12px; padding: 24px; margin-bottom: 24px; }
        .card h2 { font-size: 18px; font-weight: 600; margin-bottom: 20px; color: #f3f4f6; border-bottom: 1px solid #2a2a2f; padding-bottom: 12px; }
        .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 20px; }
        .task-card { background: #0f0f12; border: 1px solid #2a2a2f; border-radius: 12px; padding: 20px; transition: all 0.2s; }
        .task-card:hover { border-color: #3b82f6; transform: translateY(-2px); }
        
        .btn { padding: 8px 16px; border: none; border-radius: 8px; cursor: pointer; font-size: 14px; font-weight: 500; transition: all 0.2s; text-decoration: none; display: inline-flex; align-items: center; gap: 8px; }
        .btn-primary { background: #1e3a5f; color: #60a5fa; border: 1px solid #3b82f6; }
        .btn-primary:hover { background: #1e4a7a; color: #93c5fd; }
        .btn-success { background: #064e3b; color: #34d399; border: 1px solid #059669; }
        .btn-danger { background: #7f1d1d; color: #f87171; border: 1px solid #dc2626; }
        .btn-outline { background: transparent; color: #9ca3af; border: 1px solid #374151; }
        .btn-outline:hover { background: #1f1f23; color: #f3f4f6; }
        .btn-sm { padding: 6px 12px; font-size: 12px; }
        
        input, select, textarea { background: #0f0f12; border: 1px solid #2a2a2f; border-radius: 8px; padding: 10px 12px; width: 100%; color: #e5e7eb; font-size: 14px; }
        input:focus, select:focus, textarea:focus { outline: none; border-color: #3b82f6; }
        .form-group { margin-bottom: 20px; }
        label { display: block; margin-bottom: 8px; font-size: 14px; font-weight: 500; color: #9ca3af; }
        
        .profile-row { display: flex; gap: 20px; margin-bottom: 16px; padding: 12px 0; border-bottom: 1px solid #2a2a2f; }
        .profile-label { width: 140px; font-weight: 500; color: #6b7280; }
        .profile-value { flex: 1; color: #e5e7eb; }
        .badge { padding: 4px 10px; border-radius: 20px; font-size: 11px; font-weight: 500; display: inline-block; }
        .badge-grade { background: #1e3a5f; color: #60a5fa; }
        .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 16px; margin-bottom: 24px; }
        .stat-card { background: #0f0f12; border: 1px solid #2a2a2f; border-radius: 12px; padding: 20px; text-align: center; }
        .stat-number { font-size: 32px; font-weight: 700; color: #60a5fa; margin-bottom: 8px; }
        
        /* ИСПРАВЛЕННАЯ ТАБЛИЦА - дата не уезжает вниз */
        table { width: 100%; border-collapse: collapse; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #2a2a2f; vertical-align: top; }
        th { color: #9ca3af; font-weight: 500; font-size: 13px; }
        td { color: #e5e7eb; font-size: 14px; }
        td:last-child { white-space: nowrap; }
        
        .role-selector { display: flex; gap: 20px; justify-content: center; margin: 24px 0; }
        .role-card { text-align: center; padding: 32px; border: 1px solid #2a2a2f; border-radius: 12px; cursor: pointer; transition: all 0.2s; width: 200px; background: #0f0f12; }
        .role-card.selected { border-color: #3b82f6; background: #1e3a5f; }
        .role-icon { font-size: 48px; margin-bottom: 16px; }
        
        .modal { display: none; position: fixed; z-index: 1000; left: 0; top: 0; width: 100%; height: 100%; background-color: rgba(0,0,0,0.7); backdrop-filter: blur(5px); }
        .modal-content { background: #111114; margin: 10% auto; padding: 0; border-radius: 16px; width: 350px; border: 1px solid #2a2a2f; overflow: hidden; animation: modalFade 0.3s; }
        @keyframes modalFade { from { opacity: 0; transform: translateY(-50px); } to { opacity: 1; transform: translateY(0); } }
        .modal-header { background: linear-gradient(135deg, #1e3a5f, #3b82f6); padding: 20px; text-align: center; }
        .modal-avatar { width: 80px; height: 80px; border-radius: 50%; margin: 0 auto 12px; background: white; display: flex; align-items: center; justify-content: center; overflow: hidden; }
        .modal-avatar img { width: 100%; height: 100%; object-fit: cover; }
        .modal-name { font-size: 18px; font-weight: 600; margin-bottom: 5px; }
        .modal-email { font-size: 12px; color: #9ca3af; }
        .modal-body { padding: 20px; text-align: center; }
        .modal-body .btn { display: block; margin: 10px 0; }
        .close { float: right; font-size: 28px; font-weight: bold; cursor: pointer; background: none; border: none; color: white; }
        .close:hover { color: #f87171; }
        
        @media (max-width: 768px) { .sidebar { width: 72px; } .main { margin-left: 72px; padding: 20px; } }
    </style>
</head>
<body>
<div class="layout">
    {% if user %}
    <div class="sidebar">
        <div class="logo"><h2>StudyHub</h2></div>
        <div class="user-info-sidebar" onclick="openModal()">
            <div class="avatar-large">
                {% if user.avatar and user.avatar.startswith('/static/') %}
                    <img src="{{ user.avatar }}" alt="avatar">
                {% else %}
                    {{ user.avatar or 'U' }}
                {% endif %}
            </div>
            <div class="user-name">{{ user.name }} {{ user.surname }}</div>
            <div class="user-role">{% if user.role == "teacher" %}Преподаватель{% else %}Студент{% endif %}</div>
        </div>
        
        <h3>ОСНОВНОЕ</h3>
        <a href="/profile" class="{% if active_page == 'profile' %}active{% endif %}">Мой профиль</a>
        
        {% if user.role == "student" %}
        <h3>ЗАДАНИЯ</h3>
        <a href="/tasks/test" class="{% if active_page == 'test' %}active{% endif %}">Тесты</a>
        <a href="/tasks/homework" class="{% if active_page == 'homework' %}active{% endif %}">Домашние задания</a>
        <a href="/tasks/project" class="{% if active_page == 'project' %}active{% endif %}">Проекты</a>
        <h3>СТАТИСТИКА</h3>
        <a href="/my_grades" class="{% if active_page == 'my_grades' %}active{% endif %}">Мои оценки</a>
        {% endif %}
        
        {% if user.role == "teacher" %}
        <h3>УПРАВЛЕНИЕ</h3>
        <a href="/create_task/test" class="{% if active_page == 'create_test' %}active{% endif %}">Создать тест</a>
        <a href="/create_task/homework" class="{% if active_page == 'create_homework' %}active{% endif %}">Создать ДЗ</a>
        <a href="/create_task/project" class="{% if active_page == 'create_project' %}active{% endif %}">Создать проект</a>
        <h3>ПРОВЕРКА</h3>
        <a href="/check_tasks" class="{% if active_page == 'check_tasks' %}active{% endif %}">Проверить работы</a>
        <h3>СТУДЕНТЫ</h3>
        <a href="/students_list" class="{% if active_page == 'students_list' %}active{% endif %}">Список студентов</a>
        {% endif %}
    </div>
    
    <div class="main">
        <div class="header">
            <h1>{{ page_title }}</h1>
            <div class="user-menu" onclick="openModal()">
                <span>{{ user.name }}</span>
                <div class="avatar-small">
                    {% if user.avatar and user.avatar.startswith('/static/') %}
                        <img src="{{ user.avatar }}" alt="avatar">
                    {% else %}
                        {{ user.avatar or 'U' }}
                    {% endif %}
                </div>
            </div>
        </div>
        {{ content|safe }}
    </div>
    
    <div id="userModal" class="modal">
        <div class="modal-content">
            <div class="modal-header">
                <button class="close" onclick="closeModal()">&times;</button>
                <div class="modal-avatar">
                    {% if user.avatar and user.avatar.startswith('/static/') %}
                        <img src="{{ user.avatar }}" alt="avatar">
                    {% else %}
                        <span style="font-size:48px;">{{ user.avatar or 'U' }}</span>
                    {% endif %}
                </div>
                <div class="modal-name">{{ user.name }} {{ user.surname }}</div>
                <div class="modal-email">{{ user.email }}</div>
            </div>
            <div class="modal-body">
                <p>{% if user.role == "teacher" %}Преподаватель{% else %}Студент{% endif %}</p>
                <p>Зарегистрирован: {{ user.created_at }}</p>
                <hr style="border-color: #2a2a2f; margin: 15px 0;">
                <a href="/profile" class="btn btn-primary" style="width: 100%;">Мой профиль</a>
                <a href="/logout" class="btn btn-danger" style="width: 100%;">Выйти</a>
            </div>
        </div>
    </div>
    
    <script>
        function openModal() { document.getElementById('userModal').style.display = 'block'; }
        function closeModal() { document.getElementById('userModal').style.display = 'none'; }
        window.onclick = function(event) { if (event.target == document.getElementById('userModal')) closeModal(); }
    </script>
    {% else %}
    <div style="width: 100%; padding: 40px;">{{ content|safe }}</div>
    {% endif %}
</div>
</body>
</html>
'''

def render_page(content, title="StudyHub", active_page=""):
    return render_template_string(ОСНОВНОЙ_ШАБЛОН, content=content, page_title=title, active_page=active_page, user=текущий_пользователь)

# ========== СТАТИКА ==========
@app.route('/static/avatars/<path:filename>')
def serve_avatar(filename):
    return send_from_directory('static/avatars', filename)

@app.route('/static/default_avatars/<path:filename>')
def serve_default_avatar(filename):
    return send_from_directory('static/default_avatars', filename)

# ========== АВТОРИЗАЦИЯ ==========
@app.route('/')
def index():
    return redirect(url_for('profile')) if текущий_пользователь else redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    global текущий_пользователь
    if request.method == 'POST':
        email = request.form.get('email')
        password = hashlib.md5(request.form.get('password').encode()).hexdigest()
        for user in пользователи.values():
            if user['email'] == email and user['password'] == password:
                текущий_пользователь = user
                return redirect(url_for('profile'))
        content = '<div class="card" style="max-width: 420px; margin: 80px auto;"><h2>Вход</h2><div style="background:#7f1d1d;padding:12px;border-radius:8px;margin-bottom:20px;">Неверный email или пароль</div><form method="post"><div class="form-group"><label>Email</label><input type="email" name="email" required></div><div class="form-group"><label>Пароль</label><input type="password" name="password" required></div><button type="submit" class="btn btn-primary">Войти</button><a href="/register" class="btn btn-outline">Регистрация</a></form><div style="margin-top:20px;"><p style="font-size:12px;color:#6b7280;text-align:center;">Тестовые аккаунты: teacher@edu.ru / 123 | student@edu.ru / 123</p></div></div>'
        return render_page(content, "Вход")
    content = '<div class="card" style="max-width: 420px; margin: 80px auto;"><h2>Вход</h2><form method="post"><div class="form-group"><label>Email</label><input type="email" name="email" required></div><div class="form-group"><label>Пароль</label><input type="password" name="password" required></div><button type="submit" class="btn btn-primary">Войти</button><a href="/register" class="btn btn-outline">Регистрация</a></form><div style="margin-top:20px;"><p style="font-size:12px;color:#6b7280;text-align:center;">Тестовые аккаунты: teacher@edu.ru / 123 | student@edu.ru / 123</p></div></div>'
    return render_page(content, "Вход")

@app.route('/register', methods=['GET', 'POST'])
def register():
    global следующий_id_юзера
    if request.method == 'POST':
        role = request.form.get('role')
        name = request.form.get('name')
        surname = request.form.get('surname')
        email = request.form.get('email')
        password = hashlib.md5(request.form.get('password').encode()).hexdigest()
        
        # Создаем аватарку автоматически
        avatar = create_avatar_image(name, surname)
        
        if role == 'student':
            course = request.form.get('course', '')
            specialty = request.form.get('specialty', '')
        else:
            course = specialty = ''
        
        пользователи[следующий_id_юзера] = {
            'id': следующий_id_юзера, 'role': role, 'name': name, 'surname': surname,
            'email': email, 'password': password, 'avatar': avatar,
            'course': course, 'specialty': specialty,
            'created_at': datetime.now().strftime("%d.%m.%Y")
        }
        следующий_id_юзера += 1
        return redirect(url_for('login'))
    
    content = '''
    <div class="card" style="max-width: 550px; margin: 50px auto;">
        <h2>Регистрация</h2>
        <form method="post">
            <div class="role-selector">
                <div class="role-card" onclick="selectRole('student')"><div class="role-icon">С</div><h3>Студент</h3></div>
                <div class="role-card" onclick="selectRole('teacher')"><div class="role-icon">П</div><h3>Преподаватель</h3></div>
            </div>
            <input type="hidden" name="role" id="role" value="student">
            
            <div class="form-group"><label>Имя</label><input type="text" name="name" required></div>
            <div class="form-group"><label>Фамилия</label><input type="text" name="surname" required></div>
            
            <div id="studentFields">
                <div class="form-group"><label>Курс</label><input type="text" name="course" placeholder="1-4"></div>
                <div class="form-group"><label>Специальность</label><input type="text" name="specialty" placeholder="ИС-01"></div>
            </div>
            
            <div class="form-group"><label>Email</label><input type="email" name="email" required></div>
            <div class="form-group"><label>Пароль</label><input type="password" name="password" required></div>
            
            <button type="submit" class="btn btn-success">Зарегистрироваться</button>
            <a href="/login" class="btn btn-outline">Уже есть аккаунт?</a>
        </form>
    </div>
    <script>
        document.getElementById('role').value = 'student';
        document.querySelectorAll('.role-card')[0].classList.add('selected');
        function selectRole(r) {
            document.getElementById('role').value = r;
            document.querySelectorAll('.role-card').forEach(c => c.classList.remove('selected'));
            event.currentTarget.classList.add('selected');
            document.getElementById('studentFields').style.display = r === 'student' ? 'block' : 'none';
        }
    </script>
    '''
    return render_page(content, "Регистрация")

@app.route('/logout')
def logout():
    global текущий_пользователь
    текущий_пользователь = None
    return redirect(url_for('login'))

# ========== ПРОФИЛЬ ==========
@app.route('/profile')
def profile():
    if not текущий_пользователь:
        return redirect(url_for('login'))
    u = текущий_пользователь
    avatar = f'<img src="{u["avatar"]}" style="width:100%;height:100%;border-radius:50%;object-fit:cover;">' if u.get('avatar', '').startswith('/static/') else u.get('avatar', 'U')
    content = f'''
    <div class="card">
        <h2>Мой профиль</h2>
        <div style="display:flex;gap:32px;flex-wrap:wrap;">
            <div style="text-align:center;"><div class="avatar-large" style="width:120px;height:120px;">{avatar}</div><a href="/profile/edit" class="btn btn-outline btn-sm" style="margin-top:16px;">Редактировать</a></div>
            <div style="flex:1;">
                <div class="profile-row"><div class="profile-label">Имя</div><div class="profile-value">{u["name"]}</div></div>
                <div class="profile-row"><div class="profile-label">Фамилия</div><div class="profile-value">{u["surname"]}</div></div>
                <div class="profile-row"><div class="profile-label">Email</div><div class="profile-value">{u["email"]}</div></div>
                {f'<div class="profile-row"><div class="profile-label">Курс</div><div class="profile-value">{u["course"]}</div></div>' if u["role"]=="student" else ''}
                {f'<div class="profile-row"><div class="profile-label">Специальность</div><div class="profile-value">{u["specialty"]}</div></div>' if u["role"]=="student" else ''}
                <div class="profile-row"><div class="profile-label">Роль</div><div class="profile-value"><span class="badge badge-grade">{"Преподаватель" if u["role"]=="teacher" else "Студент"}</span></div></div>
                <div class="profile-row"><div class="profile-label">Дата регистрации</div><div class="profile-value">{u.get("created_at","-")}</div></div>
            </div>
        </div>
    </div>
    '''
    return render_page(content, "Мой профиль", "profile")

@app.route('/profile/edit', methods=['GET', 'POST'])
def edit_profile():
    global текущий_пользователь
    if not текущий_пользователь:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        if 'avatar_file' in request.files:
            file = request.files['avatar_file']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(f"{datetime.now().timestamp()}_{file.filename}")
                filepath = os.path.join('static', 'avatars', filename)
                file.save(filepath)
                текущий_пользователь['avatar'] = f'/static/avatars/{filename}'
                print(f"Фото сохранено: {filepath}")
        
        if 'name' in request.form:
            текущий_пользователь['name'] = request.form.get('name')
            текущий_пользователь['surname'] = request.form.get('surname')
        
        return redirect(url_for('profile'))
    
    current_avatar = текущий_пользователь.get('avatar', 'U')
    is_image = current_avatar.startswith('/static/')
    
    content = f'''
    <div class="card">
        <h2>Редактировать профиль</h2>
        <form method="post" enctype="multipart/form-data">
            <div style="text-align:center;margin-bottom:20px;">
                <div class="avatar-large" style="width:100px;height:100px;">
                    {'<img src="'+current_avatar+'" style="width:100%;height:100%;border-radius:50%;object-fit:cover;">' if is_image else '<span style="font-size:48px;">'+current_avatar+'</span>'}
                </div>
            </div>
            
            <div class="form-group"><label>Имя</label><input type="text" name="name" value="{текущий_пользователь['name']}" required></div>
            <div class="form-group"><label>Фамилия</label><input type="text" name="surname" value="{текущий_пользователь['surname']}" required></div>
            
            <div class="form-group">
                <label>Загрузить свою фотографию:</label>
                <input type="file" name="avatar_file" accept="image/*">
                <p style="font-size:12px; color:#6b7280; margin-top:8px;">Поддерживаются форматы: PNG, JPG, JPEG, GIF, WEBP</p>
            </div>
            
            <button type="submit" class="btn btn-success">Сохранить</button>
            <a href="/profile" class="btn btn-outline">Отмена</a>
        </form>
    </div>
    '''
    return render_page(content, "Редактировать профиль", "profile")

# ========== ЗАДАНИЯ ==========
def show_tasks(task_type, title):
    if not текущий_пользователь or текущий_пользователь['role'] != 'student':
        return redirect(url_for('profile'))
    tasks = ЗАДАНИЯ.get(task_type, [])
    html = ''
    for t in tasks:
        submitted = any(a['task_id'] == t['id'] and a['student_id'] == текущий_пользователь['id'] for a in ответы_учеников)
        status = 'Сдано' if submitted else 'Не сдано'
        html += f'<div class="task-card"><h3>{t["title"]}</h3><p style="color:#9ca3af;">{t["description"][:100]}</p><div style="display:flex;justify-content:space-between;margin-top:12px;"><span class="badge {"badge-submitted" if submitted else "badge-pending"}">{status}</span><a href="/submit_task/{t["id"]}" class="btn btn-primary btn-sm">Сдать</a></div></div>'
    content = f'<div class="card"><h2>{title}</h2><div class="grid">{html or "<p>Нет заданий</p>"}</div></div>'
    return render_page(content, title, task_type)

@app.route('/tasks/test')
def test_tasks():
    return show_tasks('test', 'Тесты')

@app.route('/tasks/homework')
def homework_tasks():
    return show_tasks('homework', 'Домашние задания')

@app.route('/tasks/project')
def project_tasks():
    return show_tasks('project', 'Проекты')

@app.route('/submit_task/<int:task_id>', methods=['GET', 'POST'])
def submit_task(task_id):
    global следующий_id_ответа
    if not текущий_пользователь or текущий_пользователь['role'] != 'student':
        return redirect(url_for('profile'))
    task = None
    task_type = None
    for tt, tasks in ЗАДАНИЯ.items():
        for t in tasks:
            if t['id'] == task_id:
                task, task_type = t, tt
                break
    if request.method == 'POST':
        ответы_учеников.append({'id': следующий_id_ответа, 'task_id': task_id, 'student_id': текущий_пользователь['id'], 'answer': request.form.get('answer'), 'submitted_at': datetime.now().strftime("%d.%m.%Y %H:%M"), 'grade': None, 'feedback': None})
        следующий_id_ответа += 1
        return redirect(url_for(f'{task_type}_tasks'))
    content = f'<div class="card"><h2>Сдать: {task["title"]}</h2><div style="background:#0f0f12;padding:16px;border-radius:12px;margin-bottom:20px;">{task["description"]}</div><form method="post"><textarea name="answer" rows="6" required></textarea><button type="submit" class="btn btn-success">Отправить</button><a href="/tasks/{task_type}" class="btn btn-outline">Назад</a></form></div>'
    return render_page(content, f"Сдать: {task['title']}")

def create_task_form(task_type, title):
    global следующий_id_задания
    if not текущий_пользователь or текущий_пользователь['role'] != 'teacher':
        return redirect(url_for('profile'))
    if request.method == 'POST':
        ЗАДАНИЯ[task_type].append({'id': следующий_id_задания, 'type': task_type, 'title': request.form.get('title'), 'description': request.form.get('description'), 'deadline': request.form.get('deadline'), 'created_by': f"{текущий_пользователь['name']} {текущий_пользователь['surname']}", 'created_at': datetime.now().strftime("%d.%m.%Y")})
        следующий_id_задания += 1
        return redirect(url_for('profile'))
    content = f'<div class="card"><h2>Создать {title}</h2><form method="post"><div class="form-group"><label>Название</label><input type="text" name="title" required></div><div class="form-group"><label>Описание</label><textarea name="description" rows="5" required></textarea></div><div class="form-group"><label>Дедлайн</label><input type="date" name="deadline"></div><button type="submit" class="btn btn-success">Создать</button><a href="/profile" class="btn btn-outline">Назад</a></form></div>'
    return render_page(content, f"Создать {title}")

@app.route('/create_task/test', methods=['GET', 'POST'])
def create_test():
    return create_task_form('test', 'тест')

@app.route('/create_task/homework', methods=['GET', 'POST'])
def create_homework():
    return create_task_form('homework', 'ДЗ')

@app.route('/create_task/project', methods=['GET', 'POST'])
def create_project():
    return create_task_form('project', 'проект')

@app.route('/check_tasks')
def check_tasks():
    if not текущий_пользователь or текущий_пользователь['role'] != 'teacher':
        return redirect(url_for('profile'))
    html = ''
    for a in ответы_учеников:
        task = None
        for t in ЗАДАНИЯ.values():
            for tt in t:
                if tt['id'] == a['task_id']:
                    task = tt
                    break
        s = пользователи.get(a['student_id'], {})
        html += f'<div class="task-card"><h3>{task["title"] if task else "?"}</h3><p>{s.get("name", "?")} {s.get("surname", "")}</p><p>{a["answer"][:80]}</p><a href="/grade_task/{a["id"]}" class="btn btn-primary btn-sm">Оценить</a></div>'
    content = f'<div class="card"><h2>Проверка работ</h2><div class="grid">{html or "<p>Нет работ</p>"}</div></div>'
    return render_page(content, "Проверка работ", "check_tasks")

@app.route('/grade_task/<int:answer_id>', methods=['GET', 'POST'])
def grade_task(answer_id):
    if not текущий_пользователь or текущий_пользователь['role'] != 'teacher':
        return redirect(url_for('profile'))
    a = next((x for x in ответы_учеников if x['id'] == answer_id), None)
    if request.method == 'POST':
        a['grade'] = int(request.form.get('grade'))
        a['feedback'] = request.form.get('feedback')
        return redirect(url_for('check_tasks'))
    content = f'<div class="card"><h2>Оценить работу</h2><div style="background:#0f0f12;padding:16px;border-radius:12px;margin-bottom:20px;">{a["answer"]}</div><form method="post"><div class="form-group"><label>Оценка (2-5)</label><input type="number" name="grade" min="2" max="5" required></div><div class="form-group"><label>Отзыв</label><textarea name="feedback" rows="3"></textarea></div><button type="submit" class="btn btn-success">Сохранить</button><a href="/check_tasks" class="btn btn-outline">Назад</a></form></div>'
    return render_page(content, "Оценка работы")

@app.route('/my_grades')
def my_grades():
    if not текущий_пользователь or текущий_пользователь['role'] != 'student':
        return redirect(url_for('profile'))
    my = [a for a in ответы_учеников if a['student_id'] == текущий_пользователь['id']]
    rows = ''
    total, cnt = 0, 0
    for a in my:
        task = None
        for t in ЗАДАНИЯ.values():
            for tt in t:
                if tt['id'] == a['task_id']:
                    task = tt
                    break
        if a['grade']:
            total += a['grade']
            cnt += 1
        rows += f'<tr><td style="vertical-align:top;">{task["title"] if task else "?"}</td><td style="vertical-align:top;">{a["grade"] if a["grade"] else "-"}</td><td style="vertical-align:top;">{a["feedback"] or "-"}</td><td style="vertical-align:top; white-space:nowrap;">{a["submitted_at"]}</td></tr>'
    avg = round(total/cnt, 2) if cnt else 0
    content = f'''
    <div class="card">
        <h2>Мои оценки</h2>
        <div class="stats">
            <div class="stat-card"><div class="stat-number">{avg}</div><div class="stat-label">Средний балл</div></div>
            <div class="stat-card"><div class="stat-number">{len(my)}</div><div class="stat-label">Сдано работ</div></div>
        </div>
        <table>
            <thead><tr><th>Задание</th><th>Оценка</th><th>Отзыв</th><th>Дата</th></tr></thead>
            <tbody>{rows or '<tr><td colspan="4">Нет заданий</td></tr>'}</tbody>
        </table>
    </div>
    '''
    return render_page(content, "Мои оценки", "my_grades")

@app.route('/students_list')
def students_list():
    if not текущий_пользователь or текущий_пользователь['role'] != 'teacher':
        return redirect(url_for('profile'))
    students = [u for u in пользователи.values() if u['role'] == 'student']
    rows = ''
    for s in students:
        my = [a for a in ответы_учеников if a['student_id'] == s['id'] and a['grade']]
        avg = round(sum(a['grade'] for a in my)/len(my), 2) if my else 0
        rows += f'<tr><td style="vertical-align:top;">{s["name"]} {s["surname"]}</td><td style="vertical-align:top;">{s["email"]}</td><td style="vertical-align:top;">{s.get("course", "-")}</td><td style="vertical-align:top;">{avg}</td><td style="vertical-align:top;"><a href="/student_grades/{s["id"]}" class="btn btn-primary btn-sm">Детали</a></td></tr>'
    content = f'''
    <div class="card">
        <h2>Список студентов</h2>
        <table>
            <thead><tr><th>ФИО</th><th>Email</th><th>Курс</th><th>Средний балл</th><th>Действия</th></tr></thead>
            <tbody>{rows or '<tr><td colspan="5">Нет студентов</td></tr>'}</tbody>
        </table>
    </div>
    '''
    return render_page(content, "Список студентов", "students_list")

@app.route('/student_grades/<int:student_id>')
def student_grades(student_id):
    if not текущий_пользователь or текущий_пользователь['role'] != 'teacher':
        return redirect(url_for('profile'))
    s = пользователи.get(student_id)
    if not s:
        return "Студент не найден"
    my = [a for a in ответы_учеников if a['student_id'] == student_id]
    rows = ''
    for a in my:
        task = None
        for t in ЗАДАНИЯ.values():
            for tt in t:
                if tt['id'] == a['task_id']:
                    task = tt
                    break
        rows += f'<tr><td style="vertical-align:top;">{task["title"] if task else "?"}</td><td style="vertical-align:top;">{a["grade"] if a["grade"] else "-"}</td><td style="vertical-align:top;">{a["feedback"] or "-"}</td><td style="vertical-align:top; white-space:nowrap;">{a["submitted_at"]}</td></tr>'
    content = f'''
    <div class="card">
        <h2>Успеваемость: {s["name"]} {s["surname"]}</h2>
        <table>
            <thead><tr><th>Задание</th><th>Оценка</th><th>Отзыв</th><th>Дата</th></tr></thead>
            <tbody>{rows or '<tr><td colspan="4">Нет заданий</td></tr>'}</tbody>
        </table>
        <br><a href="/students_list" class="btn btn-outline">Назад</a>
    </div>
    '''
    return render_page(content, f"Успеваемость: {s['name']}")

# ========== ТЕСТОВЫЕ АККАУНТЫ ==========
def create_test_accounts():
    global следующий_id_юзера
    if not any(u['email'] == 'teacher@edu.ru' for u in пользователи.values()):
        пользователи[следующий_id_юзера] = {
            'id': следующий_id_юзера, 'role': 'teacher', 'name': 'Анна', 'surname': 'Сергеевна',
            'email': 'teacher@edu.ru', 'password': hashlib.md5('123'.encode()).hexdigest(),
            'avatar': create_avatar_image('Анна', 'Сергеевна'),
            'course': '', 'specialty': '', 'created_at': datetime.now().strftime("%d.%m.%Y")
        }
        следующий_id_юзера += 1
        print("Создан тестовый преподаватель: teacher@edu.ru / 123")
    if not any(u['email'] == 'student@edu.ru' for u in пользователи.values()):
        пользователи[следующий_id_юзера] = {
            'id': следующий_id_юзера, 'role': 'student', 'name': 'Иван', 'surname': 'Петров',
            'email': 'student@edu.ru', 'password': hashlib.md5('123'.encode()).hexdigest(),
            'avatar': create_avatar_image('Иван', 'Петров'),
            'course': '3', 'specialty': 'Информационные системы',
            'created_at': datetime.now().strftime("%d.%m.%Y")
        }
        следующий_id_юзера += 1
        print("Создан тестовый студент: student@edu.ru / 123")

# ========== ЗАПУСК ==========
if __name__ == '__main__':
    create_test_accounts()
    print("\n" + "=" * 60)
    print("STUDYHUB - Учебная платформа")
    print("=" * 60)
    print("Сервер: http://127.0.0.1:5000")
    print("Тестовые аккаунты: teacher@edu.ru / 123 | student@edu.ru / 123")
    print("Аватарки создаются автоматически при регистрации")
    print("=" * 60 + "\n")
    app.run(debug=True, host='127.0.0.1', port=5000)