"""
Flask Application Factory
Creates and configures the Flask application
"""
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO
from flask_login import LoginManager
from flask_session import Session
import os
import logging
from logging.handlers import RotatingFileHandler

from app.config import config

# Initialize Flask extensions
db = SQLAlchemy()
socketio = SocketIO()
login_manager = LoginManager()
session = Session()


def create_app(config_name=None):
    """
    Application factory pattern
    
    Args:
        config_name: Configuration to use (development, production, testing)
    
    Returns:
        Flask application instance
    """
    # Determine configuration
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    # Create Flask app
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    
    # Initialize extensions
    db.init_app(app)
    socketio.init_app(
        app,
        async_mode=app.config['SOCKETIO_ASYNC_MODE'],
        cors_allowed_origins="*",
        logger=app.config['SOCKETIO_LOGGER'],
        engineio_logger=app.config['SOCKETIO_ENGINEIO_LOGGER']
    )
    login_manager.init_app(app)
    session.init_app(app)
    
    # Configure login manager
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    
    # Register user loader for Flask-Login
    from app.models.user import User
    
    @login_manager.user_loader
    def load_user(user_id):
        """Load user by ID for Flask-Login"""
        return User.query.get(int(user_id))
    
    # Setup logging
    setup_logging(app)
    
    # Register template filters
    register_template_filters(app)
    
    # Register blueprints
    register_blueprints(app)
    
    # Register error handlers
    register_error_handlers(app)
    
    # Register template context processors
    register_context_processors(app)
    
    # Register CLI commands
    register_cli_commands(app)
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    app.logger.info(f'{app.config["APP_NAME"]} v{app.config["APP_VERSION"]} started')
    
    return app


def setup_logging(app):
    """Configure application logging"""
    if not app.debug and not app.testing:
        if not os.path.exists('logs'):
            os.mkdir('logs')
        
        file_handler = RotatingFileHandler(
            str(app.config['LOG_FILE']),
            maxBytes=10240000,
            backupCount=10
        )
        file_handler.setFormatter(logging.Formatter(
            app.config['LOG_FORMAT']
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        
        app.logger.setLevel(logging.INFO)


def register_template_filters(app):
    """Register custom Jinja2 template filters"""
    from app.core import filters
    
    app.jinja_env.filters['format_datetime'] = filters.format_datetime
    app.jinja_env.filters['format_date'] = filters.format_date
    app.jinja_env.filters['format_time'] = filters.format_time
    app.jinja_env.filters['format_number'] = filters.format_number
    app.jinja_env.filters['format_percentage'] = filters.format_percentage
    app.jinja_env.filters['timeago'] = filters.timeago
    app.jinja_env.filters['default_zero'] = filters.default_zero
    app.jinja_env.filters['safe_float'] = filters.safe_float
    app.jinja_env.filters['clamp'] = filters.clamp


def register_blueprints(app):
    """Register all application blueprints"""
    from app.blueprints.home import home_bp
    from app.blueprints.auth import auth_bp
    from app.blueprints.demo1_carbon import demo1_bp
    from app.blueprints.demo2_grid import demo2_bp
    from app.blueprints.demo3_safety import demo3_bp
    from app.blueprints.demo4_mobility import demo4_bp
    from app.blueprints.demo5_copilot import demo5_bp
    
    app.register_blueprint(home_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(demo1_bp, url_prefix='/demo1')
    app.register_blueprint(demo2_bp, url_prefix='/demo2')
    app.register_blueprint(demo3_bp, url_prefix='/demo3')
    app.register_blueprint(demo4_bp, url_prefix='/demo4')
    app.register_blueprint(demo5_bp, url_prefix='/demo5')


def register_error_handlers(app):
    """Register error handlers"""
    
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('errors/500.html'), 500
    
    @app.errorhandler(403)
    def forbidden_error(error):
        return render_template('errors/403.html'), 403


def register_context_processors(app):
    """Register template context processors"""
    
    @app.context_processor
    def inject_config():
        """Inject configuration into templates"""
        return {
            'app_name': app.config['APP_NAME'],
            'app_version': app.config['APP_VERSION'],
            'demo_mode': app.config['DEMO_MODE']
        }


def register_cli_commands(app):
    """Register Flask CLI commands"""
    
    @app.cli.command()
    def init_db():
        """Initialize the database"""
        db.create_all()
        print('Database initialized!')
    
    @app.cli.command()
    def seed_db():
        """Seed database with sample data"""
        from app.core.seeder import seed_all_demos
        seed_all_demos()
        print('Database seeded with sample data!')
    
    @app.cli.command()
    def reset_db():
        """Reset the database (WARNING: Deletes all data)"""
        if input('Are you sure? This will delete all data (y/N): ').lower() == 'y':
            db.drop_all()
            db.create_all()
            print('Database reset complete!')
        else:
            print('Reset cancelled.')