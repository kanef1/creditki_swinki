# Модель данных и ER-диаграмма

## 1. Реляционная структура базы данных (ERD)

```mermaid
erDiagram
    User ||--o{ CompanyMembership : has
    Company ||--o{ CompanyMembership : members
    Company ||--o{ FinancialData : reports
    Company ||--o{ Application : submits
    User ||--o{ Application : applies
    CreditProduct ||--o{ Application : governs
    Application ||--o{ StatusHistory : tracks
    Application ||--o{ VerificationResult : undergoes
    Application ||--o{ ScoringResult : calculates
    Application ||--o| CreditDecision : receives
    Application ||--o{ Document : attaches
    User ||--o{ Notification : receives
    User ||--o{ AuditLog : initiates

    User {
        int id PK
        string username UK
        string email
        string role "ENTREPRENEUR | BANK_OFFICER"
        string phone
        string position
    }

    Company {
        int id PK
        string inn UK
        string ogrn
        string name
        string legal_form "LLC | IP | JSC"
        date registration_date
        string ceo_name
        string okved
        text legal_address
        string tax_system
        boolean is_active
    }

    FinancialData {
        int id PK
        int company_id FK
        int year
        int quarter
        decimal annual_revenue
        decimal net_profit
        decimal total_debt
        decimal monthly_credit_payments
    }

    CreditProduct {
        int id PK
        string code UK
        string name
        decimal min_amount
        decimal max_amount
        int min_term_months
        int max_term_months
        decimal base_rate
        json required_documents
        boolean is_active
    }

    Application {
        int id PK
        string application_number UK
        int applicant_id FK
        int company_id FK
        int product_id FK
        decimal requested_amount
        int term_months
        string purpose
        string status "DRAFT .. COMPLETED"
        datetime submitted_at
        datetime completed_at
    }

    StatusHistory {
        int id PK
        int application_id FK
        string from_status
        string to_status
        int changed_by_id FK
        text reason
        json metadata
        datetime created_at
    }

    VerificationResult {
        int id PK
        int application_id FK
        string source "FNS | BKI | EGRUL | SPARK"
        string status "PASSED | WARNING | FAILED"
        boolean risk_flag_raised
        boolean stop_factor_raised
        text summary
        json details
    }

    ScoringResult {
        int id PK
        int application_id FK
        int score "0..100"
        string risk_level "LOW | MEDIUM | HIGH | CRITICAL"
        string recommendation "AUTO_APPROVE | COUNTER_OFFER | MANUAL_REVIEW | REJECT"
        json factors
        json stop_factors
        text explanation
    }

    CreditDecision {
        int id PK
        int application_id FK, UK
        string decision_type "APPROVED | COUNTER_OFFER | MANUAL_REVIEW_REQUIRED | REJECTED"
        boolean is_automated
        int decided_by_id FK
        decimal approved_amount
        int approved_term_months
        decimal approved_rate
        decimal monthly_payment
        text rationale
        json rejection_reasons
        string client_response "PENDING | ACCEPTED | DECLINED"
    }
```

---

## 2. Описание ключевых сущностей

| Сущность | Назначение | Ключевые поля |
| :--- | :--- | :--- |
| `User` | Учетные записи предпринимателей и сотрудников банка | `role`, `phone`, `position`, `email` |
| `Company` | Юридические лица и ИП заемщиков | `inn` (Уникальный индекс), `ogrn`, `legal_form`, `okved` |
| `FinancialData` | Финансовая отчетность предприятия (выручка, прибыль, долги) | `annual_revenue`, `net_profit`, `total_debt`, `monthly_credit_payments` |
| `CreditProduct` | Банковские кредитные программы с лимитами и базовой ставкой | `min_amount`, `max_amount`, `min_term_months`, `max_term_months`, `base_rate` |
| `Application` | Кредитная заявка (объект кредитного конвейера) | `application_number`, `status`, `requested_amount`, `term_months` |
| `StatusHistory` | Неизменяемый журнал движения заявки по статусам FSM | `from_status`, `to_status`, `changed_by`, `reason`, `created_at` |
| `VerificationResult` | Результаты внешних проверок государственных реестров | `source` (ФНС, БКИ, ЕГРЮЛ), `status`, `stop_factor_raised`, `details` |
| `ScoringResult` | Расчет кредитного риска (0-100) и классификация заемщика | `score`, `risk_level`, `factors`, `stop_factors`, `explanation` |
| `CreditDecision` | Итоговое кредитное решение (автоматическое или экспертное) | `decision_type`, `approved_amount`, `approved_rate`, `rationale`, `client_response` |
| `Document` | Загруженные файлы (бух. отчетность, выписки, паспорта) | `file`, `doc_type`, `is_verified`, `file_size_bytes` |
| `AuditLog` | Журнал аудита для комплаенс и информационной безопасности | `action`, `actor`, `resource_type`, `resource_id`, `timestamp` |
