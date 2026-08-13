# Domain Model

User
│
├── Accounts
│      │
│      └── Transactions
│               │
│               ├── Category
│               ├── Merchant
│               └── Import Job
│
├── Budgets
│
├── Goals
│
└── AI Insights

# Tables

## users
| Column        | Type      |
| ------------- | --------- |
| id            | UUID      |
| email         | VARCHAR   |
| password_hash | TEXT      |
| first_name    | VARCHAR   |
| last_name     | VARCHAR   |
| currency      | VARCHAR   |
| timezone      | VARCHAR   |
| created_at    | TIMESTAMP |
| updated_at    | TIMESTAMP |

## accounts
| Column          | Type      |
| --------------- | --------- |
| id              | UUID      |
| user_id         | UUID      |
| name            | VARCHAR   |
| institution     | VARCHAR   |
| account_type    | ENUM      |
| currency        | VARCHAR   |
| opening_balance | DECIMAL   |
| current_balance | DECIMAL   |
| created_at      | TIMESTAMP |

### relationship
User

1

↓

Many

Accounts

## transactions
| Column           | Type          |
| ---------------- | ------------- |
| id               | UUID          |
| account_id       | UUID          |
| category_id      | UUID          |
| merchant_id      | UUID          |
| amount           | DECIMAL(18,2) |
| transaction_type | ENUM          |
| transaction_date | DATE          |
| description      | TEXT          |
| reference        | VARCHAR       |
| source           | ENUM          |
| is_recurring     | BOOLEAN       |
| created_at       | TIMESTAMP     |

## categories
| Column  | Type                                |
| ------- | ----------------------------------- |
| id      | UUID                                |
| user_id | UUID (nullable for system defaults) |
| name    | VARCHAR                             |
| type    | ENUM                                |
| icon    | VARCHAR                             |
| color   | VARCHAR                             |

## merchants
| Column          | Type    |
| --------------- | ------- |
| id              | UUID    |
| name            | VARCHAR |
| normalized_name | VARCHAR |
| category_id     | UUID    |

## import_jobs
| Column                 | Type      |
| ---------------------- | --------- |
| id                     | UUID      |
| user_id                | UUID      |
| filename               | VARCHAR   |
| status                 | ENUM      |
| imported_transactions  | INTEGER   |
| duplicate_transactions | INTEGER   |
| started_at             | TIMESTAMP |
| finished_at            | TIMESTAMP |

## budgets
| Column      | Type    |
| ----------- | ------- |
| id          | UUID    |
| user_id     | UUID    |
| category_id | UUID    |
| amount      | DECIMAL |
| month       | DATE    |

## goals
| Column         | Type    |
| -------------- | ------- |
| id             | UUID    |
| user_id        | UUID    |
| target_amount  | DECIMAL |
| current_amount | DECIMAL |
| target_date    | DATE    |

## ai_insights
| Column     | Type      |
| ---------- | --------- |
| id         | UUID      |
| user_id    | UUID      |
| title      | TEXT      |
| insight    | TEXT      |
| confidence | FLOAT     |
| created_at | TIMESTAMP |


# Relationships
User
 │
 ├────── Accounts
 │           │
 │           └──── Transactions
 │                     │
 │          ┌──────────┴──────────┐
 │          │                     │
 │      Category             Merchant
 │
 ├──── Budgets
 │
 ├──── Goals
 │
 └──── AI Insights

 
# Enums
## account_type
CHECKING

SAVINGS

CASH

WALLET

CREDIT

## transation_type
INCOME

EXPENSE

TRANSFER

## import_status
UPLOADING

PROCESSING

COMPLETED

FAILED

## source
MANUAL

CSV

API

SMS

