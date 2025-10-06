# QR/Barcode Data System

Система генерации и сканирования QR-кодов и штрихкодов с поддержкой кириллицы.

## 🚀 Быстрый старт

### Требования
- Python 3.8 или выше
- pip (менеджер пакетов Python)

### Автоматическая установка

**Windows:**
```bash
python setup.py
venv\Scripts\activate
python run.py
```

**Linux/Mac:**
```bash
python3 setup.py
source venv/bin/activate
python run.py
```

### Ручная установка

1. **Клонировать репозиторий:**
```bash
git clone <url-репозитория>
cd project_root
```

2. **Создать виртуальное окружение:**
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

3. **Установить зависимости:**
```bash
pip install -r requirements.txt
```

4. **Создать файл конфигурации:**
```bash
# Windows
copy .env.example .env

# Linux/Mac
cp .env.example .env
```

5. **Запустить приложение:**
```bash
python run.py
```

6. **Открыть в браузере:**
```
http://127.0.0.1:5000
```

## 🔐 Учетные данные по умолчанию

- **Логин:** admin
- **Пароль:** admin

⚠️ **Важно:** Измените пароль администратора после первого входа!

## 📁 Структура проекта

```
project_root/
├── app/                    # Основное приложение
│   ├── core/              # Бизнес-логика
│   ├── models/            # Модели данных
│   ├── routes/            # Маршруты (endpoints)
│   ├── static/            # Статические файлы (CSS, JS, изображения)
│   ├── templates/         # HTML шаблоны
│   ├── utils/             # Утилиты
│   ├── data/              # База данных (создается автоматически)
│   └── storage/           # Хранилище файлов (создается автоматически)
├── config.py              # Конфигурация приложения
├── run.py                 # Точка входа для запуска
├── setup.py               # Скрипт автоматической установки
├── requirements.txt       # Python зависимости
├── .env.example          # Пример конфигурации
└── README.md             # Этот файл
```

## ⚙️ Конфигурация

### Переменные окружения (.env)

```ini
# Режим работы (development/production)
FLASK_ENV=development

# Секретный ключ (обязательно изменить для продакшена!)
SECRET_KEY=your-secret-key-here

# Путь к базе данных (опционально)
DATABASE_PATH=/path/to/database.db

# Автоматическое создание админа (1 или 0)
AUTO_SEED_ADMIN=1

# Порт сервера
PORT=5000
```

### Режимы работы

- **development** - Режим разработки (DEBUG=True)
- **production** - Режим продакшена (DEBUG=False)
- **testing** - Режим тестирования (БД в памяти)

## 🔧 Основные команды

### Запуск сервера разработки
```bash
python run.py
```

### Создание администратора вручную
```bash
python create_admin.py
```

### Диагностика проблем входа
```bash
python diagnose_login.py
```

### Проверка сборки
```bash
python -c "from app import create_app; app = create_app(); print('Build successful')"
```

## 📦 Зависимости

- **Flask** - веб-фреймворк
- **Pillow** - обработка изображений
- **qrcode** - генерация QR-кодов
- **pylibdmtx** - генерация DataMatrix
- **opencv-python** - обработка изображений и видео
- **pdf417gen** - генерация PDF417
- **python-barcode** - генерация штрихкодов
- **pyzbar** - чтение штрихкодов
- **pyzxing** - чтение различных форматов кодов
- **reportlab** - генерация PDF
- **openpyxl** - работа с Excel
- **aztec-code-generator** - генерация Aztec кодов

## 🌐 Развертывание на сервере

### 1. Подготовка сервера

```bash
# Обновить систему
sudo apt update && sudo apt upgrade -y

# Установить Python и необходимые пакеты
sudo apt install python3 python3-pip python3-venv git -y

# Клонировать репозиторий
git clone <url-репозитория>
cd project_root
```

### 2. Настройка приложения

```bash
# Запустить автоустановку
python3 setup.py

# Активировать виртуальное окружение
source venv/bin/activate

# Настроить .env для продакшена
nano .env
```

Важные настройки для продакшена:
```ini
FLASK_ENV=production
SECRET_KEY=<сгенерировать-длинный-случайный-ключ>
AUTO_SEED_ADMIN=0
```

### 3. Запуск с помощью Gunicorn (рекомендуется)

```bash
# Установить Gunicorn
pip install gunicorn

# Запустить
gunicorn -w 4 -b 0.0.0.0:5000 "app:create_app()"
```

### 4. Настройка systemd (автозапуск)

Создать файл `/etc/systemd/system/qr-system.service`:

```ini
[Unit]
Description=QR/Barcode Data System
After=network.target

[Service]
User=your-user
WorkingDirectory=/path/to/project_root
Environment="PATH=/path/to/project_root/venv/bin"
ExecStart=/path/to/project_root/venv/bin/gunicorn -w 4 -b 127.0.0.1:5000 "app:create_app()"
Restart=always

[Install]
WantedBy=multi-user.target
```

Запустить сервис:
```bash
sudo systemctl enable qr-system
sudo systemctl start qr-system
sudo systemctl status qr-system
```

### 5. Настройка Nginx (обратный прокси)

Создать файл `/etc/nginx/sites-available/qr-system`:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static {
        alias /path/to/project_root/app/static;
        expires 30d;
    }

    client_max_body_size 20M;
}
```

Активировать конфигурацию:
```bash
sudo ln -s /etc/nginx/sites-available/qr-system /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## 🔒 Безопасность

1. **Измените SECRET_KEY** - используйте длинный случайный ключ в продакшене
2. **Измените пароль администратора** - сразу после первого входа
3. **Настройте HTTPS** - используйте Let's Encrypt для SSL сертификата
4. **Ограничьте доступ** - настройте firewall и ограничьте доступ к базе данных
5. **Регулярные обновления** - обновляйте зависимости и систему

## 🐛 Решение проблем

### База данных не создается
```bash
# Создать директории вручную
mkdir -p app/data app/storage/codes app/storage/uploads

# Запустить инициализацию
python -c "from app import create_app; create_app()"
```

### Ошибки импорта модулей
```bash
# Убедиться что виртуальное окружение активно
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate

# Переустановить зависимости
pip install -r requirements.txt
```

### Ошибка "Permission denied"
```bash
# Linux/Mac - дать права на выполнение
chmod +x run.py setup.py

# Или запускать через python
python run.py
```

### Порт уже занят
```bash
# Изменить порт в .env
echo "PORT=5001" >> .env

# Или в run.py изменить строку
# app.run(host="127.0.0.1", port=5001, debug=True)
```

## 📝 Логи

Логи приложения сохраняются в:
- Стандартный вывод (консоль)
- Системные логи (при использовании systemd): `journalctl -u qr-system -f`

## 🔄 Обновление приложения

```bash
# Остановить сервер
# Ctrl+C или sudo systemctl stop qr-system

# Получить обновления
git pull origin main

# Активировать venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Обновить зависимости
pip install -r requirements.txt --upgrade

# Запустить сервер
python run.py
# или sudo systemctl start qr-system
```

## 📄 Лицензия

Проект для внутреннего использования.

## 🤝 Поддержка

При возникновении проблем:
1. Проверьте логи приложения
2. Запустите `diagnose_login.py` для диагностики
3. Проверьте, что все зависимости установлены
4. Убедитесь, что файлы .env и config.py настроены правильно

## 📚 Дополнительная документация

- [Транслитерация](README_TRANSLITERATION.md)
- [ГОСТ стандарты](README_GOST.md)
- [Временные зоны](TIMEZONE_UPDATE.md)
