from datetime import datetime, timedelta
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app = FastAPI()

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


class Send:
    def __init__(self):
        self.__msg = ''
        self.new = True
        self.con = None

    def put(self, msg):
        self.__msg = msg
        if self.con != None:
            # envia um mensagem atravez de uma conexão socket
            self.con.send(str.encode(self.__msg))

    def get(self):
        return self.__msg

    def loop(self):
        return self.new


# função esperar - Thread
def esperar(tcp, send, host='localhost', port=5000):
    destino = (host, port)
    # conecta ao servidor
    tcp.connect(destino)

    while send.loop():
        # atribui a conexão ao manipulador
        send.con = tcp
        while send.loop():
            # aceita uma mensagem
            msg = tcp.recv(1024)
            if not msg: break
            print(str(msg, 'utf-8'))