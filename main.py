from fastapi import FastAPI, Request
import App.app

docs_enabled = str(env("DOCS", "true")).strip().lower() in ("true", "1", "yes")

app = FastAPI(
    lifespan=App.app.lifespan,
    docs_url="/docs" if docs_enabled else None,
    redoc_url="/redoc" if docs_enabled else None,
    openapi_url="/openapi.json" if docs_enabled else None,
)

App.app.init(app)

# Main API Entry Gate:
# Yahan se aap custom check, SQL query, ya koi bhi validation laga sakte hain:

@entry(app)
async def gate(request: Request):
    ip = user_info.ip(request)
    browser = user_info.browser(request)
    os_name = user_info.os(request)
    data = await req.b(request)
    auth_header = await req.h(request)

    maintenance = False
    if maintenance:
        return res.e("API is currently unavailable", 422)
    return True


@app.get("/")
async def home():

    return res.s("Python Backend Running")


if __name__ == "__main__":
    App.app.run()
