from fastapi import APIRouter, HTTPException, Depends
from app.domain.auth.auth_schema import UserSignupRequest, UserLoginRequest, AuthResponse
from app.domain.auth.auth_service import AuthService
from app.www.jwt_auth_middleware import get_current_user

router = APIRouter()
auth_service = AuthService()

@router.post("/signup", response_model=AuthResponse)
async def signup(user_data: UserSignupRequest):
    try:
        result = await auth_service.signup(user_data)
        if result["success"]:
            return AuthResponse(
                success=True,
                message=result["message"]
            )
        else:
            raise HTTPException(status_code=400, detail=result["message"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"회원가입 처리 실패: {str(e)}")

@router.post("/login", response_model=AuthResponse)
async def login(login_data: UserLoginRequest):
    try:
        result = await auth_service.login(login_data)
        if result["success"]:
            return AuthResponse(
                success=True,
                message=result["message"],
                data=result["data"]
            )
        else:
            raise HTTPException(status_code=401, detail=result["message"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"로그인 처리 실패: {str(e)}")

@router.get("/me")
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    return {"success": True, "user": current_user}
