"""
Скрипт инициализации проекта для первого запуска
"""
import os
import sys
import subprocess

def check_python_version():
    """Проверка версии Python"""
    if sys.version_info < (3, 8):
        print("❌ Требуется Python 3.8 или выше")
        print(f"   Текущая версия: {sys.version}")
        return False
    print(f"✓ Python версия: {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    return True

def create_venv():
    """Создание виртуального окружения"""
    print("\n📦 Создание виртуального окружения...")
    if os.path.exists('venv'):
        print("✓ Виртуальное окружение уже существует")
        return True
    
    try:
        subprocess.run([sys.executable, '-m', 'venv', 'venv'], check=True)
        print("✓ Виртуальное окружение создано")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка создания виртуального окружения: {e}")
        return False

def install_dependencies():
    """Установка зависимостей"""
    print("\n📚 Установка зависимостей...")
    
    # Определяем путь к pip в виртуальном окружении
    if os.name == 'nt':  # Windows
        pip_path = os.path.join('venv', 'Scripts', 'pip.exe')
    else:  # Unix/Linux/Mac
        pip_path = os.path.join('venv', 'bin', 'pip')
    
    if not os.path.exists(pip_path):
        print(f"❌ pip не найден: {pip_path}")
        return False
    
    try:
        subprocess.run([pip_path, 'install', '--upgrade', 'pip'], check=True)
        subprocess.run([pip_path, 'install', '-r', 'requirements.txt'], check=True)
        print("✓ Зависимости установлены")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка установки зависимостей: {e}")
        return False

def create_env_file():
    """Создание .env файла из .env.example"""
    print("\n⚙️  Создание конфигурации...")
    
    if os.path.exists('.env'):
        print("✓ Файл .env уже существует")
        return True
    
    if os.path.exists('.env.example'):
        try:
            with open('.env.example', 'r', encoding='utf-8') as src:
                content = src.read()
            with open('.env', 'w', encoding='utf-8') as dst:
                dst.write(content)
            print("✓ Файл .env создан из .env.example")
            print("  ⚠️  Не забудьте изменить SECRET_KEY в .env для продакшена!")
            return True
        except Exception as e:
            print(f"❌ Ошибка создания .env: {e}")
            return False
    else:
        print("⚠️  Файл .env.example не найден, пропуск...")
        return True

def create_directories():
    """Создание необходимых директорий"""
    print("\n📁 Создание директорий...")
    
    dirs = [
        'app/data',
        'app/storage',
        'app/storage/codes',
        'app/storage/uploads'
    ]
    
    for dir_path in dirs:
        os.makedirs(dir_path, exist_ok=True)
    
    print("✓ Директории созданы")
    return True

def initialize_database():
    """Инициализация базы данных"""
    print("\n💾 Инициализация базы данных...")
    
    # Определяем путь к python в виртуальном окружении
    if os.name == 'nt':  # Windows
        python_path = os.path.join('venv', 'Scripts', 'python.exe')
    else:  # Unix/Linux/Mac
        python_path = os.path.join('venv', 'bin', 'python')
    
    try:
        # Запускаем приложение для инициализации БД
        result = subprocess.run(
            [python_path, '-c', 'from app import create_app; app = create_app(); print("БД инициализирована")'],
            check=True,
            capture_output=True,
            text=True
        )
        print("✓ База данных инициализирована")
        print("  ℹ️  Создан пользователь по умолчанию: admin / admin")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка инициализации базы данных: {e}")
        if e.output:
            print(f"   Вывод: {e.output}")
        return False

def print_next_steps():
    """Вывод следующих шагов"""
    print("\n" + "="*60)
    print("✅ Установка завершена!")
    print("="*60)
    print("\nСледующие шаги:")
    
    if os.name == 'nt':  # Windows
        print("\n1. Активировать виртуальное окружение:")
        print("   venv\\Scripts\\activate")
    else:  # Unix/Linux/Mac
        print("\n1. Активировать виртуальное окружение:")
        print("   source venv/bin/activate")
    
    print("\n2. Запустить сервер:")
    print("   python run.py")
    
    print("\n3. Открыть в браузере:")
    print("   http://127.0.0.1:5000")
    
    print("\n4. Войти с учетными данными по умолчанию:")
    print("   Логин: admin")
    print("   Пароль: admin")
    print("   ⚠️  Не забудьте изменить пароль!")
    
    print("\n" + "="*60)

def main():
    """Главная функция"""
    print("="*60)
    print("   Инициализация QR/Barcode Data System")
    print("="*60)
    
    # Проверка Python
    if not check_python_version():
        sys.exit(1)
    
    # Создание виртуального окружения
    if not create_venv():
        sys.exit(1)
    
    # Установка зависимостей
    if not install_dependencies():
        sys.exit(1)
    
    # Создание .env файла
    if not create_env_file():
        sys.exit(1)
    
    # Создание директорий
    if not create_directories():
        sys.exit(1)
    
    # Инициализация базы данных
    if not initialize_database():
        print("⚠️  База данных будет инициализирована при первом запуске")
    
    # Вывод следующих шагов
    print_next_steps()

if __name__ == '__main__':
    main()
