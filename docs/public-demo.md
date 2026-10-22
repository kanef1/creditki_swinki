# Временная публичная демонстрация

Запуск в PowerShell из корня проекта:

```powershell
.\scripts\start-public.ps1
```

Нужны работающий Docker Desktop и Windows OpenSSH. Скрипт создаёт отдельный Compose-проект `credit-public`: Django, frontend и PostgreSQL, затем подключает бесплатный SSH-туннель localhost.run. Обычный локальный проект не изменяется. Секреты создаются случайно и сохраняются только в игнорируемом `.runtime/public.env`; адрес — в `.runtime/public-url.txt`. После изменения исходников сначала выполнить `docker compose --env-file .runtime/public.env -p credit-public -f compose.public.yaml build`.

Ссылка HTTPS временная: работает при включённом компьютере и запущенном SSH-туннеле. Бесплатный сервис периодически меняет домен; повторный запуск скрипта получает актуальный адрес и обновляет разрешённые Host и CSRF origin. Wildcard origins не используются. Cookies публичной версии имеют Secure. Поддерживается приватный гостевой контекст с четырьмя компаниями на посетителя; общие demo/bank аккаунты не создаются. В публичном режиме заблокированы login, банковские решения и страницы схемы API. Данные и документы этой демонстрации находятся в отдельных Docker volumes.

Проверки внешней ссылки:

```powershell
$env:APP_URL = Get-Content .runtime/public-url.txt
node scripts/check-jury.cjs
node scripts/check-module.cjs
```

Остановить внешний доступ, сохранив данные:

```powershell
.\scripts\stop-public.ps1
```

Остановить всю публичную демо-среду: дополнительно выполнить `docker compose --env-file .runtime/public.env -p credit-public -f compose.public.yaml stop`. Не использовать `down -v`, если данные нужны. Это демонстрационная публикация, а не постоянный хостинг: [localhost.run Free Tier](https://localhost.run/docs/forever-free/) ограничивает скорость и регулярно меняет hostname. Проверенная альтернатива Cloudflare Quick Tunnel в текущей сети возвращала 530 и обрывала соединение; её контейнер остановлен, профиль `tunnel` оставлен в Compose как необязательный вариант.
