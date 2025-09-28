import os
from flask import Flask
from .extensions import init_db_teardown, ensure_dirs
from .models.users import init_users_schema, ensure_admin_seed
from .models.history import init_history_schema

def create_app():
    app = Flask(__name__)
    from flask import send_from_directory, current_app

    @app.route('/favicon.ico')
    def favicon():
        return send_from_directory(current_app.static_folder, 'favicon.ico', mimetype='image/vnd.microsoft.icon')
    app.config["SECRET_KEY"] = "dev-secret"

    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(base_dir, "data")
    storage_dir = os.path.join(base_dir, "storage")
    codes_dir = os.path.join(storage_dir, "codes")
    uploads_dir = os.path.join(storage_dir, "uploads")

    app.config["DATABASE_PATH"] = os.path.join(data_dir, "app.db")
    app.config["STORAGE_CODES_DIR"] = codes_dir
    app.config["STORAGE_UPLOADS_DIR"] = uploads_dir
    app.config["MAX_CONTENT_LENGTH"] = 20 * 1024 * 1024

    ensure_dirs([data_dir, storage_dir, codes_dir, uploads_dir])
    init_db_teardown(app)
    init_users_schema(app)
    init_history_schema(app)

    if os.getenv("AUTO_SEED_ADMIN", "1") == "1":
        ensure_admin_seed(app)

    from .routes.main import bp as main_bp
    from .routes.auth import bp as auth_bp
    from .routes.admin import bp as admin_bp
    from .routes.forms import bp as forms_bp
    from .routes.scan import bp as scan_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(forms_bp, url_prefix="/forms")
    app.register_blueprint(scan_bp, url_prefix="/scan")

    return app