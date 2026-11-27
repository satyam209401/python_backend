from fastapi import APIRouter, Request

router = APIRouter()


@router.post("")
@limiter.limit("5/minute") 
@body.limit("100KB")  
async def register(request: Request):
    
    return res.s("only test api")

