# 🚀 Руководство по развертыванию

## Перенос проекта на новый ПК/сервер через GitHub

### 1. Подготовка к переносу (исходная машина)

#### 1.1. Убедитесь что .gitignore настроен правильно
```bash
# Проверьте что следующие файлы/папки игнорируются:
# - venv/
# - app/data/
# - app/storage/
# - .env
# - *.db
```

#### 1.2. Закоммитьте изменения
```bash
git add .
git commit -m "Update: готов к развертыванию"
git push origin main
```

⚠️ **Важно:** База данных и файлы в storage/ НЕ должны попадать в репозиторий!

---

### 2. Клонирование на новую машину

#### Windows:
```bash
# 1. Установите Git (если еще не установлен)
# Скачайте с https://git-scm.com/download/win

# 2. Клонируйте репозиторий
git clone <url-вашего-репозитория>
cd project_root

# 3. Запустите автоматическую установку
python setup.py

# 4. Активируйте виртуальное окружение
venv\Scripts\activate

# 5. Запустите приложение
python run.py
```

#### Linux/Mac:
```bash
# 1. Убедитесь что Git установлен
sudo apt install git -y  # Debian/Ubuntu
# или
brew install git  # macOS

# 2. Клонируйте репозиторий
git clone <url-вашего-репозитория>
cd project_root

# 3. Запустите автоматическую установку
python3 setup.py

# 4. Активируйте виртуальное окружение
source venv/bin/activate

# 5. Запустите приложение
python run.py
```

---

### 3. Ручная установка (если setup.py не работает)

```bash
# 1. Создать виртуальное окружение
python -m venv venv

# 2. Активировать
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 3. Обновить pip
python -m pip install --upgrade pip

# 4. Установить зависимости
pip install -r requirements.txt

# 5. Создать .env файл
# Windows:
copy .env.example .env
# Linux/Mac:
cp .env.example .env

# 6. Создать необходимые директории
mkdir -p app/data app/storage/codes app/storage/uploads

# 7. Запустить приложение (БД создастся автоматически)
python run.py
```

---

### 4. Перенос данных (опционально)

Если вам нужно перенести существующие данные:

#### 4.1. На исходной машине - экспортируйте базу данных
```bash
# Windows:
mkdir backup
copy app\data\app.db backup\app.db
copy app\storage backup\storage /E

# Linux/Mac:
mkdir backup
cp app/data/app.db backup/app.db
cp -r app/storage backup/storage
```

#### 4.2. Перенесите файлы backup/ на новую машину
```bash
# Используйте любой метод:
# - USB флешка
# - scp (для серверов)
# - облачное хранилище
# - email (если размер небольшой)

# Пример через scp:
scp -r backup/ user@new-server:/path/to/project_root/
```

#### 4.3. На новой машине - импортируйте данные
```bash
# Windows:
copy backup\app.db app\data\app.db
xcopy backup\storage app\storage /E /I

# Linux/Mac:
cp backup/app.db app/data/app.db
cp -r backup/storage/* app/storage/
```

---

### 5. Развертывание на production сервере

#### 5.1. Подготовка сервера (Ubuntu/Debian)

```bash
# Обновить систему
sudo apt update && sudo apt upgrade -y

# Установить необходимые пакеты
sudo apt install python3 python3-pip python3-venv git nginx -y

# Создать пользователя для приложения
sudo useradd -m -s /bin/bash qrapp
sudo su - qrapp
```

#### 5.2. Установка приложения

```bash
# Клонировать репозиторий
git clone <url-вашего-репозитория> ~/qr-system
cd ~/qr-system/project_root

# Установить
python3 setup.py
source venv/bin/activate

# Настроить .env для production
nano .env
```

Настройки для production в .env:
```ini
FLASK_ENV=production
SECRET_KEY=<сгенерировать-длинный-случайный-ключ-32-символа>
AUTO_SEED_ADMIN=0
PORT=5000
```

Генерация безопасного SECRET_KEY:
```python
python -c "import secrets; print(secrets.token_hex(32))"
```

#### 5.3. Установка и настройка Gunicorn

```bash
# Установить Gunicorn
pip install gunicorn

# Протестировать запуск
gunicorn -w 4 -b 127.0.0.1:5000 "app:create_app()"
```

#### 5.4. Создание systemd сервиса

```bash
# Выйти из пользователя qrapp
exit

# Создать файл сервиса
sudo nano /etc/systemd/system/qr-system.service
```

Содержимое файла:
```ini
[Unit]
Description=QR/Barcode Data System
After=network.target

[Service]
User=qrapp
Group=qrapp
WorkingDirectory=/home/qrapp/qr-system/project_root
Environment="PATH=/home/qrapp/qr-system/project_root/venv/bin"
ExecStart=/home/qrapp/qr-system/project_root/venv/bin/gunicorn \
    -w 4 \
    -b 127.0.0.1:5000 \
    --access-logfile /home/qrapp/qr-system/logs/access.log \
    --error-logfile /home/qrapp/qr-system/logs/error.log \
    "app:create_app()"
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# Создать директорию для логов
sudo -u qrapp mkdir -p /home/qrapp/qr-system/logs

# Запустить сервис
sudo systemctl enable qr-system
sudo systemctl start qr-system
sudo systemctl status qr-system
```

#### 5.5. Настройка Nginx

```bash
sudo nano /etc/nginx/sites-available/qr-system
```

Содержимое файла:
```nginx
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;

    # Логи
    access_log /var/log/nginx/qr-system-access.log;
    error_log /var/log/nginx/qr-system-error.log;

    # Основное приложение
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Таймауты
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Статические файлы
    location /static {
        alias /home/qrapp/qr-system/project_root/app/static;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Максимальный размер загружаемых файлов
    client_max_body_size 20M;
}
```

```bash
# Активировать конфигурацию
sudo ln -s /etc/nginx/sites-available/qr-system /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

#### 5.6. Настройка SSL (HTTPS) с Let's Encrypt

```bash
# Установить Certbot
sudo apt install certbot python3-certbot-nginx -y

# Получить SSL сертификат
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# Автообновление сертификата
sudo systemctl enable certbot.timer
```

#### 5.7. Настройка Firewall

```bash
# Установить UFW
sudo apt install ufw -y

# Разрешить необходимые порты
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'

# Включить firewall
sudo ufw enable
sudo ufw status
```

---

### 6. Обновление приложения на production

```bash
# Перейти в директорию проекта
cd ~/qr-system/project_root

# Получить обновления
git pull origin main

# Активировать venv
source venv/bin/activate

# Обновить зависимости
pip install -r requirements.txt --upgrade

# Перезапустить сервис
sudo systemctl restart qr-system

# Проверить статус
sudo systemctl status qr-system
```

---

### 7. Резервное копирование

#### 7.1. Создание бэкапа

```bash
#!/bin/bash
# backup.sh

BACKUP_DIR="/home/qrapp/backups"
PROJECT_DIR="/home/qrapp/qr-system/project_root"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_NAME="qr-system-backup-$DATE"

mkdir -p "$BACKUP_DIR/$BACKUP_NAME"

# Копировать базу данных
cp "$PROJECT_DIR/app/data/app.db" "$BACKUP_DIR/$BACKUP_NAME/"

# Копировать storage
cp -r "$PROJECT_DIR/app/storage" "$BACKUP_DIR/$BACKUP_NAME/"

# Копировать .env
cp "$PROJECT_DIR/.env" "$BACKUP_DIR/$BACKUP_NAME/"

# Создать архив
cd "$BACKUP_DIR"
tar -czf "$BACKUP_NAME.tar.gz" "$BACKUP_NAME"
rm -rf "$BACKUP_NAME"

# Удалить старые бэкапы (старше 30 дней)
find "$BACKUP_DIR" -name "*.tar.gz" -mtime +30 -delete

echo "Backup created: $BACKUP_DIR/$BACKUP_NAME.tar.gz"
```

#### 7.2. Автоматизация бэкапов через cron

```bash
# Сделать скрипт исполняемым
chmod +x /home/qrapp/backup.sh

# Добавить в cron (запуск каждый день в 2:00)
crontab -e

# Добавить строку:
0 2 * * * /home/qrapp/backup.sh >> /home/qrapp/backup.log 2>&1
```

#### 7.3. Восстановление из бэкапа

```bash
#!/bin/bash
# restore.sh

BACKUP_FILE="$1"
PROJECT_DIR="/home/qrapp/qr-system/project_root"

if [ -z "$BACKUP_FILE" ]; then
    echo "Usage: ./restore.sh /path/to/backup.tar.gz"
    exit 1
fi

# Остановить сервис
sudo systemctl stop qr-system

# Распаковать бэкап
tar -xzf "$BACKUP_FILE" -C /tmp/

BACKUP_DIR=$(basename "$BACKUP_FILE" .tar.gz)

# Восстановить файлы
cp /tmp/$BACKUP_DIR/app.db "$PROJECT_DIR/app/data/"
cp -r /tmp/$BACKUP_DIR/storage/* "$PROJECT_DIR/app/storage/"
cp /tmp/$BACKUP_DIR/.env "$PROJECT_DIR/"

# Очистить временные файлы
rm -rf /tmp/$BACKUP_DIR

# Запустить сервис
sudo systemctl start qr-system

echo "Restore completed"
```

---

### 8. Мониторинг и логи

#### 8.1. Просмотр логов приложения
```bash
# Логи сервиса
sudo journalctl -u qr-system -f

# Логи Gunicorn
tail -f /home/qrapp/qr-system/logs/error.log
tail -f /home/qrapp/qr-system/logs/access.log

# Логи Nginx
sudo tail -f /var/log/nginx/qr-system-error.log
sudo tail -f /var/log/nginx/qr-system-access.log
```

#### 8.2. Проверка статуса
```bash
# Статус сервиса
sudo systemctl status qr-system

# Проверка процессов
ps aux | grep gunicorn

# Проверка портов
sudo netstat -tulpn | grep :5000
```

---

### 9. Решение типичных проблем

#### База данных не найдена
```bash
# Создать директории
mkdir -p app/data app/storage/codes app/storage/uploads

# Инициализировать БД
python -c "from app import create_app; create_app()"
```

#### Ошибка прав доступа
```bash
# Дать права пользователю qrapp
sudo chown -R qrapp:qrapp /home/qrapp/qr-system
sudo chmod -R 755 /home/qrapp/qr-system
```

#### Сервис не запускается
```bash
# Проверить логи
sudo journalctl -u qr-system -n 50

# Проверить конфигурацию
sudo systemctl daemon-reload
sudo systemctl restart qr-system
```

#### Nginx показывает 502 Bad Gateway
```bash
# Проверить что gunicorn запущен
sudo systemctl status qr-system

# Проверить порты
sudo netstat -tulpn | grep :5000

# Проверить логи nginx
sudo tail -f /var/log/nginx/qr-system-error.log
```

---

### 10. Контрольный чеклист

#### Перед переносом:
- [ ] Все изменения закоммичены в Git
- [ ] .gitignore правильно настроен
- [ ] База данных НЕ в репозитории
- [ ] Секретные ключи НЕ в репозитории
- [ ] requirements.txt актуален
- [ ] README.md содержит актуальные инструкции

#### После переноса:
- [ ] Приложение клонировано
- [ ] Виртуальное окружение создано
- [ ] Зависимости установлены
- [ ] .env файл настроен
- [ ] База данных инициализирована
- [ ] Приложение запускается
- [ ] Можно войти в систему
- [ ] Все функции работают

#### Production дополнительно:
- [ ] SECRET_KEY изменен на безопасный
- [ ] FLASK_ENV=production
- [ ] Gunicorn установлен и настроен
- [ ] systemd сервис создан и запущен
- [ ] Nginx настроен
- [ ] SSL сертификат установлен
- [ ] Firewall настроен
- [ ] Бэкапы настроены
- [ ] Мониторинг работает

---

## 📞 Поддержка

При возникновении проблем:
1. Проверьте логи
2. Убедитесь что все зависимости установлены
3. Проверьте права доступа к файлам
4. Проверьте конфигурацию .env
