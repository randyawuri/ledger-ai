from app.tasks.celery import celery

from app.db.session import SessionLocal

from app.automation.service import AutomationService


@celery.task
def process_transaction(transaction_id):

    db = SessionLocal()

    try:

        from app.transactions.domain.models import Transaction

        transaction = (
            db.query(Transaction)
            .filter(
                Transaction.id == transaction_id
            )
            .first()
        )

        if transaction:

            AutomationService(
                db
            ).process_transaction(transaction)

    finally:

        db.close()