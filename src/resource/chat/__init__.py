import socket
from threading import Thread
from fastapi import APIRouter, HTTPException
from src.utils.services import app, Send, esperar
from src.utils.validators import Validator


router = APIRouter(
    prefix="/chat",
    tags=["chat"],
    responses={
        404: {
            "description": "Not found"
        }
    },
)

@router.post('/')
async def post(username: str, msg: str, host: str = '127.0.0.1'):
    data = {
        "username": username,
        "msg": msg
    }
    print(data)
    s = socket.socket()
    try:
        s.connect(('localhost', 5000))
        s.sendall(str.encode(f'{username}: {msg}'))

        return f'{username}: {msg}'
    except Exception as error:
        data = {
            "error": {
                "code": 500,
                "message": str(error)
            }
        }, 500
        return data
    finally:
        s.close()