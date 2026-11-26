from fastapi import APIRouter

router = APIRouter()


@router.post("/register")
async def register():
    return {
        "success": True,
        "message": "Test Only Registration Successful",
    }
