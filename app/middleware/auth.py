from fastapi import Request, HTTPException, Depends
from app.services.auth_service import decode_jwt_token
from app.services.user_service import get_user_by_id

async def get_current_user(request: Request):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")
    
    token = auth_header.split(" ")[1]
    
    try:
        payload = decode_jwt_token(token)
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    except Exception as e:
        # decode_jwt_token already raises HTTPException if JWTError, but just in case
        raise HTTPException(status_code=401, detail="Could not validate credentials")
    
    user = await get_user_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
        
    return user
