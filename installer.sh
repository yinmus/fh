#!/usr/bin/env bash

echo "Выберите пользователя для установки:"

mapfile -t users < <(ls /home/)
for i in "${!users[@]}"; do
    printf "%d. %s\n" "$((i + 1))" "${users[$i]}"
done

read -rp "Введите номер пользователя: " user_choice

if ! [[ "$user_choice" =~ ^[0-9]+$ ]] || ((user_choice < 1 || user_choice > ${#users[@]})); then
    echo "Некорректный выбор."
    exit 1
fi

USERNAME="${users[$((user_choice - 1))]}"
INSTALL_DIR="/home/$USERNAME/.fh"
SCRIPT_NAME="fhs.py"
BIN_PATH="/usr/local/bin/fh"

echo "Этот скрипт установит $SCRIPT_NAME в $INSTALL_DIR."
read -rp "Продолжить? [Y/n] " confirm

if [[ -z "$confirm" || "$confirm" =~ ^[Yy]$ ]]; then
    mkdir -p "$INSTALL_DIR"
    cp "$SCRIPT_NAME" "$INSTALL_DIR"

echo '#!/usr/bin/env bash
SCRIPT_PATH="'$INSTALL_DIR'/'$SCRIPT_NAME'"

python3 "$SCRIPT_PATH" "$@"' | sudo tee "$BIN_PATH" >/dev/null || { echo "Ошибка записи в $BIN_PATH"; exit 1; }

    sudo chmod +x "$BIN_PATH"
    echo "Установка завершена. Используйте команду 'fh'."
else
    echo "Установка отменена."
fi
