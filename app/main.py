import time
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.exc import OperationalError

from app.db import engine, Base
from app.api import router as api_router

# Templates directory
templates = Jinja2Templates(directory="app/templates")


def create_app() -> FastAPI:
    app = FastAPI(
        title="Luggage Agentic MVP",
        version="0.1.0"
    )

    # 🔹 Serve static files (images, css, js)
    app.mount(
        "/static",
        StaticFiles(directory="app/static"),
        name="static"
    )

    # 🔹 Ensure DB is ready before app starts
    @app.on_event("startup")
    def on_startup():
        for _ in range(30):
            try:
                Base.metadata.create_all(bind=engine)
                return
            except OperationalError:
                time.sleep(1)
        Base.metadata.create_all(bind=engine)

    # 🔹 Home page (booking form)
    @app.get("/", response_class=HTMLResponse)
    def home(request: Request):
        return templates.TemplateResponse(
            "index.html",
            {"request": request}
        )

    # 🔹 Phase-2 Order Status Page
    @app.get("/order/{order_id}", response_class=HTMLResponse)
    def order_status_page(request: Request, order_id: str):
        return templates.TemplateResponse(
            "order_status.html",
            {
                "request": request,
                "order_id": order_id
            }
        )

    # 🔹 API routes
    app.include_router(api_router, prefix="/api")

    return app


app = create_app()
