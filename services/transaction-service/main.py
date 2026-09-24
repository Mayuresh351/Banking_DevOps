import os

import psycopg2
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

load_dotenv()

app = FastAPI(title="Transaction Service")


class Transaction(BaseModel):
    user_id: int
    amount: float


def get_connection():
    return psycopg2.connect(
        host=os.getenv("DATABASE_HOST"),
        port=os.getenv("DATABASE_PORT"),
        database=os.getenv("DATABASE_NAME"),
        user=os.getenv("DATABASE_USER"),
        password=os.getenv("DATABASE_PASSWORD"),
    )


@app.get("/healthz")
def health_check():
    return {"status": "healthy"}


@app.post("/transactions/deposit")
def deposit(transaction: Transaction):
    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(
            """
            UPDATE users_account_info
            SET balance = balance + %s
            WHERE id = %s
            RETURNING id, balance;
            """,
            (transaction.amount, transaction.user_id),
        )

        user = cursor.fetchone()

        if user is None:
            raise HTTPException(status_code=404, detail="User not found")

        cursor.execute(
            """
            INSERT INTO transactions_info (user_id, type, amount)
            VALUES (%s, 'deposit', %s)
            RETURNING id;
            """,
            (transaction.user_id, transaction.amount),
        )

        transaction_id = cursor.fetchone()[0]
        connection.commit()

        return {
            "transaction_id": transaction_id,
            "user_id": user[0],
            "type": "deposit",
            "amount": transaction.amount,
            "balance": float(user[1]),
        }

    except Exception:
        connection.rollback()
        raise

    finally:
        cursor.close()
        connection.close()


@app.post("/transactions/withdraw")
def withdraw(transaction: Transaction):
    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(
            """
            UPDATE users_account_info
            SET balance = balance - %s
            WHERE id = %s
              AND balance >= %s
            RETURNING id, balance;
            """,
            (transaction.amount, transaction.user_id, transaction.amount),
        )

        user = cursor.fetchone()

        if user is None:
            raise HTTPException(
                status_code=400,
                detail="User not found or insufficient balance",
            )

        cursor.execute(
            """
            INSERT INTO transactions_info (user_id, type, amount)
            VALUES (%s, 'withdraw', %s)
            RETURNING id;
            """,
            (transaction.user_id, transaction.amount),
        )

        transaction_id = cursor.fetchone()[0]
        connection.commit()

        return {
            "transaction_id": transaction_id,
            "user_id": user[0],
            "type": "withdraw",
            "amount": transaction.amount,
            "balance": float(user[1]),
        }

    except Exception:
        connection.rollback()
        raise

    finally:
        cursor.close()
        connection.close()
