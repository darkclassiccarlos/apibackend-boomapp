from fastapi import FastAPI

from src.routers import router

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
    title="API semilla",
    description="Esta API es una semilla para crear APIs con FastAPI",
    version = "1.0",
    openapi_url="/openapi.json", 
    docs_url="/docs",
    middleware=middleware
)

app.include_router(router)

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, port=8000, host='0.0.0.0')
