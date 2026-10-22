# Конечный автомат состояний заявки (FSM)

## 1. Схема жизненного цикла заявки

```mermaid
stateDiagram-v2
    [*] --> DRAFT: Создание заявки предпринимателем
    DRAFT --> SUBMITTED: Отправка заявки заемщиком
    
    SUBMITTED --> VALIDATING: Первичная валидация реквизитов
    VALIDATING --> ENRICHING: Запрос данных ФНС / ЕГРЮЛ / БКИ
    VALIDATING --> REJECTED: Ошибки верификации данных
    
    ENRICHING --> SCORING: Расчет скорингового балла (0-100)
    ENRICHING --> REJECTED: Выявление критических стоп-факторов
    
    SCORING --> OFFER_READY: Авто-одобрение (Score >= 75)
    SCORING --> OFFER_READY: Встречное предложение (Высокая сумма)
    SCORING --> MANUAL_REVIEW: На рассмотрение (Score 45-74 или факторы риска)
    SCORING --> REJECTED: Отказ (Score < 45 или стоп-факторы)
    
    MANUAL_REVIEW --> OFFER_READY: Одобрение или встречные условия андеррайтера
    MANUAL_REVIEW --> ADDITIONAL_INFO_REQUIRED: Запрос пояснений или документов
    MANUAL_REVIEW --> REJECTED: Отказ андеррайтера
    
    ADDITIONAL_INFO_REQUIRED --> MANUAL_REVIEW: Предоставление сведений заемщиком
    ADDITIONAL_INFO_REQUIRED --> REJECTED: Непредоставление сведений / Отказ
    
    OFFER_READY --> ACCEPTED: Заемщик акцептовал предложение
    OFFER_READY --> REJECTED: Заемщик отклонил предложение
    
    ACCEPTED --> COMPLETED: Договор заключен, средства зачислены
    COMPLETED --> [*]
    REJECTED --> [*]
```

---

## 2. Матрица допустимых переходов состояний

| Исходное состояние | Допустимые целевые состояния | Инициатор перехода | Условие перехода |
| :--- | :--- | :--- | :--- |
| `DRAFT` | `SUBMITTED` | Заемщик | Заполнение обязательных полей заявки |
| `SUBMITTED` | `VALIDATING` | Конвейер | Успешная постановка в очередь обработки |
| `VALIDATING` | `ENRICHING`, `REJECTED` | Конвейер | Проверка соответствия лимитам продукта |
| `ENRICHING` | `SCORING`, `REJECTED` | Конвейер | Получение ответов от сервисов ФНС и БКИ |
| `SCORING` | `OFFER_READY`, `MANUAL_REVIEW`, `REJECTED` | Конвейер | Вычисление риска по скоринговой модели |
| `MANUAL_REVIEW` | `OFFER_READY`, `ADDITIONAL_INFO_REQUIRED`, `REJECTED` | Андеррайтер | Экспертное решение сотрудника банка |
| `ADDITIONAL_INFO_REQUIRED`| `MANUAL_REVIEW`, `REJECTED` | Заемщик / Андеррайтер | Предоставление клиентом запрошенных данных |
| `OFFER_READY` | `ACCEPTED`, `REJECTED` | Заемщик | Принятие или отказ от условий финансирования |
| `ACCEPTED` | `COMPLETED` | Конвейер | Подписание договора простой ЭП и выдача |

---

## 3. Гарантии целостности и аудит FSM

1. **Запрет недопустимых переходов:** Метод `ApplicationPipelineService.change_status` валидирует текущий статус по словарю `ALLOWED_TRANSITIONS`. Попытка прямого перехода, например, из `DRAFT` в `COMPLETED`, вызывает исключение `ValidationError`.
2. **Атомарность (ACID):** Все изменения статуса, создание записей истории и аудит-логов выполняются внутри транзакции `@transaction.atomic`.
3. **Неизменяемый журнал (`StatusHistory`):** Каждый переход автоматически записывает:
   - Исходный и новый статус (`from_status`, `to_status`);
   - Инициатора действия (`changed_by`);
   - Текстовое основание (`reason`);
   - Метаданные скоринга или параметров решения (`metadata`).
