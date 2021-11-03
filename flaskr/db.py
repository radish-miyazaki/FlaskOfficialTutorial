import sqlite3
import click
from flask import current_app, g
from flask.cli import with_appcontext


def init_app(app):
    # レスポンスを返した後のクリーンアップを行っているときにclose_dbを呼び出すようにappに伝える
    app.teardown_appcontext(close_db)
    # flaskコマンドを使って呼び出すことができる新しいコマンドを追加
    app.cli.add_command(init_db_command)


def init_db():
    db = get_db()

    # open_resource: パッケージから相対的な場所で指定されたファイルを開く。
    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))


# コマンドラインから使用できるコマンドを定義。
@click.command('init-db')
@with_appcontext
def init_db_command():
    # 既存のデータを削除し、新しいテーブルを作成する
    init_db()
    click.echo("Initialized the database.")


def get_db():
    # リクエストの期間中に複数の関数によってアクセスされるデータの中にdbが存在しない場合の処理。
    if 'db' not in g:
        # データベースとの接続を確立する。
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES,
        )
        # dictのように振る舞う行を返すように伝える。
        g.db.row_factory = sqlite3.Row
    return g.db


def close_db(e=None):
    db = g.pop('db', None)

    # dbが接続されていたら、閉じる
    if db is not None:
        db.close()
