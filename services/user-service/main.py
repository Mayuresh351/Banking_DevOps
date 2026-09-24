import os

import psycopg2
from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel

load_dotenv()

app = FastAPI(title="User Service")


class User(BaseModel):
    name: str
    email: str


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


@app.post("/users")
def create_user(user: User):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO users_account_info (name, email)
        VALUES (%s, %s)
        RETURNING id, name, email, balance, created_at;
        """,
        (user.name, user.email),
    )

    new_user = cursor.fetchone()

    connection.commit()

    cursor.close()
    connection.close()

    return {
        "id": new_user[0],
        "name": new_user[1],
        "email": new_user[2],
        "balance": float(new_user[3]),
        "created_at": new_user[4],
    }
    
    
    
@app.get("/users/{user_id}")
def get_user(user_id: int):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT id, name, email, balance, created_at
        FROM users_account_info
        WHERE id = %s;
        """,
        (user_id,),
    )

    user = cursor.fetchone()

    cursor.close()
    connection.close()

    if user is None:
        return {"error": "User not found"}

    return {
        "id": user[0],
        "name": user[1],
        "email": user[2],
        "balance": float(user[3]),
        "created_at": user[4],
    }
