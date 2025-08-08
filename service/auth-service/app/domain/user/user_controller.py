"""
User Controller
"""
from fastapi import APIRouter

router = APIRouter(prefix="/user", tags=["User"])

@router.get("/")
async def get_user():
    return {"message": "User endpoint"}
