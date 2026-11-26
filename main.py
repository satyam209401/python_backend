import App.app
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import v1

app = FastAPI(
    title="Python Backend API",
    version="1.0.0",
    redirect_slashes=False,
    lifespan=App.app.lifespan,
)

cors_origins = [o.strip() for o in env("CORS_ORIGINS", "*").split(",") if o.strip()]
cors_headers = [h.strip() for h in env("CORS_HEADERS", "*").split(",") if h.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins if cors_origins else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=cors_headers if cors_headers else ["*"],
)

App.app.init(app)

app.include_router(v1.router, prefix="/v1")



@app.get("/")
async def home():
    return res.s("Python Backend Running")

