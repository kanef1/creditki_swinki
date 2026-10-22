# Границы MVP и матрица

Источник: текст задания пользователя. PDF кейса не предоставлен; номера страниц и соответствие PDF не подтверждены. Не использовать эту таблицу как подтверждение требований организаторов.

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
| Обязательные требования PDF | Ожидается PDF | НЕ ПРОВЕРЕНО |

MVP — синтетический кредитный процесс без выдачи денег и юридически значимой подписи. Допущения: синхронный конвейер, сотрудники имеют доступ ко всей демо-очереди, деньги в рублях, годовая выручка. Принятие предложения завершает демо-процесс.

Последовательность: модели и контракты → транзакционные сервисы → API и тесты → интерфейсы → Docker и документация → интеграционная проверка.
