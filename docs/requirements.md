# Границы MVP и матрица

Источник: мастер-промпт пользователя и полный PDF кейса из 16 страниц, предоставленный 22 октября 2026. Таблица ниже относится к дополнительным требованиям пользователя; постраничная матрица организаторов находится в `pdf-compliance.md`. Прочитан весь PDF. Наличие кода не равно подтверждённому запуску: результаты проверок отдельно приведены в `verification.md`.

| Требование текста | Реализация | Проверка |
|---|---|---|
| Две роли, изоляция компаний | Django Auth, membership, фильтрация queryset | API permissions tests |
| Продукты, калькулятор, мастер, черновики | REST products/applications, React формы | TypeScript, API tests |
| Проверки ФНС/БКИ | детерминированные синтетические адаптеры | четыре сценария |
| Скоринг отдельно от решений | scoring/engine.py, decisions/engine.py | unit tests |
| FSM, история, повторные запросы | atomic + select_for_update, история, уникальный ключ создания | API tests |
| Ручное решение и дополнительные сведения | bank decision, resubmit | API tests |
| PostgreSQL, Decimal, миграции | Django models, PostgreSQL 16 | PostgreSQL CI |
| Документы, уведомления, аудит | защищённые REST endpoints | API tests |
| React/TS, RHF/Zod, shadcn, Tailwind | frontend | build, component tests |
| Docker, nginx, gunicorn | compose.yaml, Dockerfiles | compose smoke test |
| OpenAPI, Postman, описание модели | schema endpoint, docs | schema generation |
| Обязательные требования PDF | pdf-compliance.md | Сверено; GitHub, Docker smoke и browser QA остаются открытыми |

MVP — синтетический кредитный процесс без выдачи денег и юридически значимой подписи. Допущения: синхронный конвейер, сотрудники имеют доступ ко всей демо-очереди, деньги в рублях, годовая выручка. Принятие предложения завершает демо-процесс.

Последовательность: модели и контракты → транзакционные сервисы → API и тесты → интерфейсы → Docker и документация → интеграционная проверка.
