from fastapi import APIRouter

router = APIRouter()


@router.post("/login")
async def login():
    return {
        "success": True,
        "message": "Test Only Login Successful",
    }
