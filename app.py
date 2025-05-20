from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)


# Инициализация базы данных
def init_db():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            full_name TEXT,
            bio TEXT
        )
    ''')
    conn.commit()
    conn.close()


init_db()

python_data = {
    "site_title": "Python - просто о сложном",
    "description": "Исчерпывающий гид по языку программирования Python",
    "sections": {
        "about": {
            "title": "Что такое Python?",
            "content": "Python - это высокоуровневый язык программирования общего назначения, который сочетает простоту изучения с мощными возможностями.",
            "image": "python-logo.png"
        },
        "why_learn": {
            "title": "Зачем учить Python?",
            "reasons": [
                {
                    "title": "Простота изучения",
                    "content": "Чистый и понятный синтаксис делает Python идеальным для начинающих."
                },
                {
                    "title": "Универсальность",
                    "content": "От веб-разработки до анализа данных и искусственного интеллекта."
                },
                {
                    "title": "Большое сообщество",
                    "content": "Огромное количество учебных материалов и готовых решений."
                }
            ]
        },
        "usage": {
            "title": "Где применяется Python?",
            "areas": [
                {
                    "name": "Веб-разработка",
                    "frameworks": ["Django", "Flask", "FastAPI"],
                    "description": "Создание сайтов и веб-приложений"
                },
                {
                    "name": "Наука о данных",
                    "frameworks": ["Pandas", "NumPy", "Matplotlib"],
                    "description": "Анализ данных и визуализация"
                },
                {
                    "name": "Машинное обучение",
                    "frameworks": ["TensorFlow", "PyTorch", "scikit-learn"],
                    "description": "ИИ и нейронные сети"
                }
            ]
        },
        "getting_started": {
            "title": "С чего начать?",
            "steps": [
                {
                    "title": "Установка Python",
                    "content": "Скачайте последнюю версию с официального сайта python.org"
                },
                {
                    "title": "Выбор IDE",
                    "content": "PyCharm, VS Code или Jupyter Notebook для начала"
                },
                {
                    "title": "Первые программы",
                    "content": "Начните с простых скриптов и постепенно усложняйте"
                }
            ]
        }
    },
    "resources": {
        "title": "Полезные ресурсы",
        "links": [
            {"name": "Официальная документация", "url": "https://docs.python.org/3/"},
            {"name": "Real Python Tutorials", "url": "https://realpython.com/"},
            {"name": "Python для начинающих", "url": "https://pythonru.com/uroki"}
        ]
    }
}


@app.route('/')
def home():
    return render_template('index.html', data=python_data, user=session.get('user'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        full_name = request.form.get('full_name', '')

        hashed_password = generate_password_hash(password)

        try:
            conn = sqlite3.connect('users.db')
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO users (username, email, password, full_name) VALUES (?, ?, ?, ?)',
                (username, email, hashed_password, full_name)
            )
            conn.commit()
            flash('Регистрация прошла успешно! Теперь вы можете войти.', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Пользователь с таким именем или email уже существует', 'error')
        finally:
            conn.close()

    return render_template('register.html', data=python_data)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        user = cursor.fetchone()
        conn.close()

        if user and check_password_hash(user[3], password):
            session['user'] = {
                'id': user[0],
                'username': user[1],
                'email': user[2],
                'full_name': user[4],
                'bio': user[5]
            }
            flash('Вы успешно вошли в систему!', 'success')
            return redirect(url_for('profile'))
        else:
            flash('Неверное имя пользователя или пароль', 'error')

    return render_template('login.html', data=python_data)


@app.route('/profile')
def profile():
    if 'user' not in session:
        flash('Пожалуйста, войдите в систему', 'error')
        return redirect(url_for('login'))

    return render_template('profile.html',
                           data=python_data,  # Добавьте data
                           user=session['user'])


@app.route('/logout')
def logout():
    session.pop('user', None)
    flash('Вы вышли из системы', 'info')
    return redirect(url_for('home'))


@app.route('/update_profile', methods=['GET', 'POST'])
def update_profile():
    if 'user' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        full_name = request.form['full_name']
        bio = request.form['bio']

        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute(
            'UPDATE users SET full_name = ?, bio = ? WHERE id = ?',
            (full_name, bio, session['user']['id'])
        )
        conn.commit()
        conn.close()

        session['user']['full_name'] = full_name
        session['user']['bio'] = bio
        flash('Профиль успешно обновлен!', 'success')
        return redirect(url_for('profile'))

    return render_template('update_profile.html',
                           data=python_data,  # Добавьте data
                           full_name=session['user'].get('full_name', ''),
                           bio=session['user'].get('bio', ''))


if __name__ == '__main__':
    app.run(debug=True)