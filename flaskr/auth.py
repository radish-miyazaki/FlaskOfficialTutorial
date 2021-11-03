import functools

from flask import (
    Blueprint, g, request, session, jsonify
)
from werkzeug.security import check_password_hash, generate_password_hash
from flaskr.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')


# ログイン必須のデコレータを作成
def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        # 認証情報がない場合はjsonを返す。
        if g.user is None:
            res = {
                "status": 401,
                "message": "Unauthorized."
            }

            return jsonify(res)

        # 認証情報がある場合のみdecorateしている関数を呼び出す
        return wrapped_view


@bp.route('/register', methods=["POST"])
def register():
    postedData = request.get_json()
    username = postedData['username']
    password = postedData['password']

    db = get_db()
    error = None

    if not username:
        error = "Username is required."
    elif not password:
        error = "Password is required."
    elif db.execute(
        'SELECT id FROM user WHERE username = ?', (username,)
    ).fetchone() is not None:
        error = f"User {username} is already registered."

    if error:
        res = {
            "status": 400,
            "message": error
        }
    else:
        db.execute(
            'INSERT INTO user (username, password) VALUES (?, ?)',
            (username, generate_password_hash(password))
        )
        db.commit()
        res = {
            "status": 200,
            "message": "You're successfully registered."
        }

    return jsonify(res)


@bp.route('/login', methods=["POST"])
def login():
    postedData = request.get_json()
    username = postedData['username']
    password = postedData['password']

    db = get_db()
    error = None

    user = db.execute(
        'SELECT * FROM user WHERE username = ?', (username,)
    ).fetchone()

    if user is None:
        error = 'Incorrect username'
    elif not check_password_hash(user['password'], password):
        error = 'Incorrect password'

    if error:
        res = {
            "status": 400,
            "message": error
        }
    else:
        # Cookieの値をリセットし、userのidを認証情報として格納
        session.clear()
        session['user_id'] = user['id']

        res = {
            "status": 200,
            "message": "You're successfully signed in."
        }

    return jsonify(res)


@bp.route('/logout', methods=['POST'])
def logout():
    session.clear()

    res = {
        "status": 204,
        "message": "You're successfully signed out."
    }

    return jsonify(res)