#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
VENV_DIR="$PROJECT_DIR/venv"
SERVICE_NAME="speech-shortener"
SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}.service"

info()  { echo -e "\033[1;32m[INFO]\033[0m $*"; }
warn()  { echo -e "\033[1;33m[WARN]\033[0m $*"; }
error() { echo -e "\033[1;31m[ERROR]\033[0m $*"; }

# ── 0. Root check ────────────────────────────────────────────────────────────
if [[ $EUID -ne 0 ]]; then
    error "Этот скрипт нужно запускать с правами root (sudo ./deploy.sh)"
    exit 1
fi

# ── 1. Системные зависимости ─────────────────────────────────────────────────
info "Проверка системных зависимостей..."

apt-get update -qq

for pkg in python3 python3-pip python3-venv ffmpeg; do
    if ! dpkg -s "$pkg" &>/dev/null; then
        info "Устанавливаю $pkg..."
        apt-get install -y -qq "$pkg"
    else
        info "$pkg уже установлен"
    fi
done

# Создание сервисного пользователя
SERVICE_USER="speechbot"
if ! id -u "$SERVICE_USER" &>/dev/null; then
    useradd -r -s /usr/sbin/nologin "$SERVICE_USER"
    info "Пользователь $SERVICE_USER создан"
else
    info "Пользователь $SERVICE_USER уже существует"
fi

# ── 2. Python venv и зависимости ─────────────────────────────────────────────
info "Настройка Python окружения..."

if [[ ! -d "$VENV_DIR" ]]; then
    python3 -m venv "$VENV_DIR"
    info "Виртуальное окружение создано"
else
    info "Виртуальное окружение уже существует"
fi

"$VENV_DIR/bin/pip" install --upgrade pip -q
"$VENV_DIR/bin/pip" install -r "$PROJECT_DIR/requirements.txt" -q
info "Python-зависимости установлены"

# ── 3. Файл .env ─────────────────────────────────────────────────────────────
if [[ ! -f "$PROJECT_DIR/.env" ]]; then
    cp "$PROJECT_DIR/.env.example" "$PROJECT_DIR/.env"
    warn "Создан файл .env из .env.example"
    warn "Заполните его перед запуском:"
    warn "  nano $PROJECT_DIR/.env"
    warn "Затем запустите скрипт повторно."
    exit 0
fi

# Проверка что токены заполнены
set -a
source "$PROJECT_DIR/.env"
set +a

if [[ -z "${TELEGRAM_BOT_TOKEN:-}" ]]; then
    error "TELEGRAM_BOT_TOKEN не задан в .env"
    exit 1
fi

if [[ -z "${GROQ_API_KEY:-}" ]]; then
    error "GROQ_API_KEY не задан в .env"
    exit 1
fi

info "Конфигурация .env проверена"

# ── 4. Systemd сервис ────────────────────────────────────────────────────────
info "Настройка systemd сервиса..."

cat > "$SERVICE_FILE" <<EOF
[Unit]
Description=Speech Shortener Telegram Bot
After=network.target

[Service]
Type=simple
User=$SERVICE_USER
WorkingDirectory=$PROJECT_DIR
ExecStart=$VENV_DIR/bin/python -m bot.main
EnvironmentFile=$PROJECT_DIR/.env
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
info "Сервис создан: $SERVICE_FILE"

# ── 5. Запуск сервиса ────────────────────────────────────────────────────────
chown -R "$SERVICE_USER":"$SERVICE_USER" "$PROJECT_DIR"
systemctl enable "$SERVICE_NAME"
systemctl restart "$SERVICE_NAME"
info "Сервис включён и запущен"

# ── 6. Статус ─────────────────────────────────────────────────────────────────
echo ""
systemctl status "$SERVICE_NAME" --no-pager || true
echo ""
info "Деплой завершён!"
info "Управление: systemctl {start|stop|restart|status} $SERVICE_NAME"
info "Логи: journalctl -u $SERVICE_NAME -f"
