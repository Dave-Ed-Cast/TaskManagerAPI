import os, logging
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from contextlib import asynccontextmanager
from app.database.database import init_db
from app.routes import users, tasks

logger = logging.getLogger("uvicorn")
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    logger.info("Database initialized")
    yield
    logger.info("Shutting down...")

app = FastAPI(title="Task Manager API", lifespan=lifespan)

# Mount static files
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Set up Jinja2 templates
templates = Jinja2Templates(directory=TEMPLATES_DIR)


# Include API routers
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(tasks.router, prefix="/tasks", tags=["Tasks"])

# Serve login page
@app.get("/", response_class=HTMLResponse)
@app.get("/login.html", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

# Serve signup page
@app.get("/signup", response_class=HTMLResponse)
@app.get("/signup.html", response_class=HTMLResponse)
def signup_page(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request})

# Serve user page
@app.get("/user", response_class=HTMLResponse)
def user_page(request: Request):
    # Example of passing dynamic data:
    user_info = {"username": "Davide", "tasks": ["Task 1", "Task 2"]}
    return templates.TemplateResponse("user.html", {"request": request, "user": user_info})
