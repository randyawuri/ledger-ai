# API Overview

## Base URL:
/api/v1

# Authentication
## Register:
POST /api/v1/auth/register

Request:
{
  "email": "randy@example.com",
  "password": "********",
  "first_name": "Randy",
  "last_name": "Awuri"
}
Respone:
{
  "access_token": "...",
  "refresh_token": "...",
  "user": {}
}

# Login
POST /api/v1/auth/login

# Refresh Token
POST /api/v1/auth/refresh

# Current User
GET /api/v1/users/me

# Accounts
## List Accounts
GET /api/v1/accounts

# Create Account
POST /api/v1/accounts

# Get Account
GET /api/v1/accounts/{id}

# Update Account
PATCH /api/v1/accounts/{id}

# Delete Account
DELETE /api/v1/accounts/{id}

# Transactions
## List Transcations
GET /api/v1/transactions

# Supported query parameters:
?page=1

&page_size=25

&category=food

&account=uuid

&start_date=2026-07-01

&end_date=2026-07-31

&type=expense

&merchant=kfc

# Create Transaction
POST /api/v1/transactions

# Get Transaction
GET /api/v1/transactions/{id}

# Update Transaction
PATCH /api/v1/transactions/{id}

# Delete Transaction
DELETE /api/v1/transactions/{id}

# Categories
GET /categories
POST /categories
PATCH /categories/{id}
DELETE /categories/{id}

# Budgets
GET /budgets
POST /budgets
PATCH /budgets/{id}
DELETE /budgets/{id}

# Goals
GET /goals
POST /goals
PATCH /goals/{id}
DELETE /goals/{id}

# CSV Import
## Upload Statement
POST /imports/upload

# Multipart request
statement.csv

### Response
{
  "job_id": "...",
  "status": "processing"
}

### Import Status
GET /imports/{job_id}

### Import History
GET /imports

# Analtics
## Dashboard Summary
GET /analytics/dashboard

Returns:
{
  "income": 520000,
  "expenses": 311000,
  "cash_flow": 209000,
  "savings_rate": 40.2
}

## Spending by Category
GET /analytics/categories

## Monthly Trend
GET /analytics/monthly

## Merchant Analysis
GET /analytics/merchants

## Cashflow
GET /analytics/cashflow

# AI
## Generate Insights
GET /ai/insights

Example response:
{
  "title": "Restaurant Spending",
  "summary": "Restaurant spending increased by 28% this month."
}

## Categorize Transaction
POST /ai/categorize

## Chat Assistant
POST /ai/chat

Request
{
  "message": "Why did I spend more this month?"
}

Standard Response Format
{
  "success": true,
  "data": {},
  "meta": {}
}
Errors:
{
  "success": false,
  "error": {
    "code": "TRANSACTION_NOT_FOUND",
    "message": "Transaction not found."
  }
}

Pagination
{
  "data": [],
  "pagination": {
    "page": 1,
    "page_size": 25,
    "total_items": 643,
    "total_pages": 26
  }
}

### Authentication:
Authorization: Bearer <access_token>

# API Principles
Resource-oriented URLs (/transactions, not /getTransactions)
Correct HTTP verbs (GET, POST, PATCH, DELETE)
Idempotent GET, PUT, and DELETE
Versioned API (/api/v1)
Consistent error responses
Pagination for collection endpoints
Filtering via query parameters
Validation on every request
