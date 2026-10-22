.DEFAULT_GOAL := help

# Colors for terminal output
COLOR_RESET   := \033[0m
COLOR_CYAN    := \033[36m
COLOR_GREEN   := \033[32m
COLOR_YELLOW  := \033[33m
COLOR_BOLD    := \033[1m

.PHONY: help run up down stop restart build logs logs-backend logs-frontend ps status test test-local seed migrate makemigrations shell clean

help: ## Показать справку по доступным командам
	@echo ""
	@echo "$(COLOR_BOLD)Умный кредитный кабинет предпринимателя (Альфа-Банк Хакатон)$(COLOR_RESET)"
	@echo "$(COLOR_CYAN)Использование:$(COLOR_RESET) make [команда]"
	@echo ""
	@echo "$(COLOR_BOLD)Основные команды:$(COLOR_RESET)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(COLOR_GREEN)%-18s$(COLOR_RESET) %s\n", $$1, $$2}'
	@echo ""
	@echo "$(COLOR_YELLOW)Сервисы после запуска:$(COLOR_RESET)"
	@echo "  • Frontend:       http://localhost:3000"
	@echo "  • Backend API:    http://localhost:8000/api/v1/"
	@echo "  • Swagger UI:     http://localhost:8000/api/v1/docs/"
	@echo "  • ReDoc:          http://localhost:8000/api/v1/redoc/"
	@echo "  • Django Admin:   http://localhost:8000/admin/"
	@echo ""

run: ## Собрать образы и запустить весь проект в фоновом режиме (Docker Compose)
	@echo "$(COLOR_CYAN)Сборка и запуск сервисов проекта...$(COLOR_RESET)"
	docker compose up --build -d
	@echo ""
	@echo "$(COLOR_GREEN)✓ Проект успешно запущен!$(COLOR_RESET)"
	@echo "  • Frontend:    http://localhost:3000"
	@echo "  • Swagger UI:  http://localhost:8000/api/v1/docs/"
	@echo "  • Backend API: http://localhost:8000/api/v1/"
	@echo ""
	@echo "$(COLOR_YELLOW)Для просмотра логов используйте:$(COLOR_RESET) make logs"

up: ## Запустить контейнеры без пересборки в фоновом режиме
	docker compose up -d

down: ## Остановить и удалить все контейнеры проекта
	@echo "$(COLOR_YELLOW)Остановка сервисов...$(COLOR_RESET)"
	docker compose down

stop: down ## Псевдоним для make down

restart: ## Перезапустить все сервисы
	@echo "$(COLOR_YELLOW)Перезапуск сервисов...$(COLOR_RESET)"
	docker compose restart

build: ## Собрать docker-образы backend и frontend
	docker compose build

logs: ## Просмотр логов всех сервисов в реальном времени
	docker compose logs -f

logs-backend: ## Просмотр логов бэкенда в реальном времени
	docker compose logs -f backend

logs-frontend: ## Просмотр логов фронтенда в реальном времени
	docker compose logs -f frontend

ps: ## Проверить статус запущенных контейнеров
	docker compose ps

status: ps ## Псевдоним для make ps

test: ## Запустить автоматические тесты backend (pytest) в Docker
	@echo "$(COLOR_CYAN)Запуск тестов backend (pytest)...$(COLOR_RESET)"
	@if [ "$$(docker compose ps -q backend 2>/dev/null)" != "" ]; then \
		docker compose exec backend pytest -v; \
	elif command -v docker >/dev/null 2>&1 && docker compose version >/dev/null 2>&1; then \
		docker compose run --rm backend pytest -v; \
	else \
		cd backend && (if [ -d .venv ]; then .venv/bin/pytest -v; else pytest -v; fi); \
	fi

test-local: ## Запустить тесты backend локально через виртуальное окружение
	@echo "$(COLOR_CYAN)Запуск тестов через локальный pytest...$(COLOR_RESET)"
	@cd backend && (if [ -d .venv ]; then .venv/bin/pytest -v; else pytest -v; fi)

seed: ## Заново заполнить базу демонстрационными данными (Сценарии A, B, C, D)
	@echo "$(COLOR_CYAN)Сброс и наполнение демо-данных...$(COLOR_RESET)"
	docker compose exec backend python manage.py seed_demo_data

migrate: ## Применить миграции базы данных Django
	docker compose exec backend python manage.py migrate

makemigrations: ## Сгенерировать новые миграции Django
	docker compose exec backend python manage.py makemigrations

shell: ## Открыть интерактивную консоль Django в контейнере
	docker compose exec backend python manage.py shell

clean: ## Остановить проект и удалить Docker-тома (полная очистка данных)
	@echo "$(COLOR_YELLOW)Остановка и удаление контейнеров, сетей и томов...$(COLOR_RESET)"
	docker compose down -v --remove-orphans
	@echo "$(COLOR_GREEN)✓ Очистка завершена.$(COLOR_RESET)"
