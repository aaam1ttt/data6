import os

class Config:
    """Базовая конфигурация"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # База данных
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DATA_DIR = os.path.join(BASE_DIR, 'app', 'data')
    DATABASE_PATH = os.environ.get('DATABASE_PATH') or os.path.join(DATA_DIR, 'app.db')
    
    # Хранилище
    STORAGE_DIR = os.path.join(BASE_DIR, 'app', 'storage')
    STORAGE_CODES_DIR = os.path.join(STORAGE_DIR, 'codes')
    STORAGE_UPLOADS_DIR = os.path.join(STORAGE_DIR, 'uploads')
    
    # Загрузки
    MAX_CONTENT_LENGTH = 20 * 1024 * 1024  # 20MB
    
    # Автоматическое создание админа
    AUTO_SEED_ADMIN = os.environ.get('AUTO_SEED_ADMIN', '1') == '1'


class DevelopmentConfig(Config):
    """Конфигурация для разработки"""
    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    """Конфигурация для продакшена"""
    DEBUG = False
    TESTING = False
    SECRET_KEY = os.environ.get('SECRET_KEY')  # Обязательно должен быть установлен


class TestingConfig(Config):
    """Конфигурация для тестирования"""
    TESTING = True
    DEBUG = True
    DATABASE_PATH = ':memory:'


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
