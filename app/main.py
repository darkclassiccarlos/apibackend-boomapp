from fastapi import FastAPI
from src.routes import users,auth,admin
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware import Middleware


middleware = [
    Middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
]


app = FastAPI(
    title="API Boom WS admin",
    description="Esta API de administración del WS de Boom APIs con FastAPI",
    version = "1.0",
    openapi_url="/openapi.json", 
    docs_url="/docs",
    middleware=middleware
)

app.include_router(users.router)
app.include_router(auth.router)
app.include_router(admin.router)

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, port=8000, host='0.0.0.0')
