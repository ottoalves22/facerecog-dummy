from fastapi import HTTPException
from jose import JWTError, jwt
import utils.configs as configs


def validate_token(token: str):
        try:
            payload = jwt.decode(token, configs.secret_key, algorithms=['HS256'])
            username = payload.get("sub")
            return payload
        except JWTError as e:
            credentials_exception = HTTPException(
            status_code=401,
            detail="As credenciais não puderam ser validadas",
            headers={"WWW-Authenticate": "Bearer"},
            )
            raise credentials_exception