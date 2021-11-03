# 続き：https://msiz07-flask-docs-ja.readthedocs.io/ja/latest/tutorial/blog.html
import os
from flask import Flask


def create_app(test_config=None):
    # Flaskインスタンスを生成
    # instance_relative_config: 設定ファイルがインスタンスフォルダから相対的に示されていることをappに伝える。
    app = Flask(__name__, instance_relative_config=True)

    # appが使用する標準設定をセットする。
    # SECRET_KEY: データを安全に保つためにFlaskによって利用。Deployのときはランダム値にすべき。
    app.config.from_mapping(SECRET_KEY='dev', DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'))

    if test_config is None:
        # config.pyがあれば、そこから値を取り出して設定を上書きする。
        app.config.from_pyfile('config.py', silent=True)
    else:
        # 無い場合は上記の設定のままいく。
        app.config.from_mapping(test_config)

    try:
        # app.instance_pathが確実に存在するようにする。
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # データベースの初期化処理
    from . import db
    db.init_app(app)

    # Blueprintの登録
    from . import auth
    app.register_blueprint(auth.bp)

    @app.route('/hello')
    def hello():
        return 'Hello World!'

    return app
