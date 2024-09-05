# main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import httpx
from uuid import UUID
from typing import Optional
from datetime import date
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)

app = FastAPI()

# 요청 바디를 위한 데이터 모델 정의
class LoginRequest(BaseModel):
    accountId: str
    password: str

# 외부 API로부터 받아오는 데이터 모델 정의
class UserResponse(BaseModel):
    id: UUID
    account_id: str
    password: str
    name: str
    grade: int
    class_num: int
    num: int
    user_role: str
    club_name: Optional[str] = None
    profileImageUrl: Optional[str] = None
    birthDay: date

# 외부 서비스에 로그인 요청을 보내는 함수
async def login_to_service(accountId: str, password: str):
    url = "https://prod-server.xquare.app/dsm-login/user/user-data"
    payload = {
        "accountId": accountId,
        "password": password
    }

    logging.info(f"Sending request to {url} with payload: {payload}")

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, json=payload)
            response.raise_for_status()

            logging.info(f"Received response: {response.text}")

            user_data = response.json()
            
            # 응답 데이터 검증
            validated_data = UserResponse(**user_data)
            return validated_data
        
        except httpx.HTTPStatusError as e:
            error_detail = e.response.json() if e.response.content else str(e)
            logging.error(f"HTTP error occurred: {error_detail}")
            raise HTTPException(status_code=e.response.status_code, detail=f"로그인 실패: {error_detail}")
        
        except httpx.RequestError as e:
            logging.error(f"Request error occurred: {e}")
            raise HTTPException(status_code=500, detail=f"Request error occurred: {str(e)}")
        
        except Exception as e:
            logging.error(f"Unexpected error occurred: {e}")
            raise HTTPException(status_code=500, detail=f"Unexpected error occurred: {str(e)}")

# FastAPI 엔드포인트 설정
@app.post("/login", response_model=UserResponse)
async def login(login_request: LoginRequest):
    result = await login_to_service(login_request.accountId, login_request.password)
    return result
