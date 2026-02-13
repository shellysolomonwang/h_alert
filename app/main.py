from dotenv import load_dotenv
import asyncio
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.orm import Session

from .database import Base, SessionLocal, engine
from .hermes import get_available_bags
from .models import Subscription
from .monitor import monitor_loop

load_dotenv()

Base.metadata.create_all(bind=engine)
templates = Jinja2Templates(directory="app/templates")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    stop_event = asyncio.Event()
    task = asyncio.create_task(monitor_loop(stop_event))
    app.state.stop_event = stop_event
    app.state.monitor_task = task
    yield
    stop_event.set()
    await task


app = FastAPI(title="Hermès Bag Alert", lifespan=lifespan)


@app.get("/", response_class=HTMLResponse)
def index(request: Request, db: Session = Depends(get_db)):
    subscriptions = db.execute(select(Subscription).where(Subscription.active.is_(True))).scalars().all()
    bag_names = sorted(get_available_bags().keys())
    return templates.TemplateResponse(
        request,
        "index.html",
        {
            "subscriptions": subscriptions,
            "bag_names": bag_names,
            "message": request.query_params.get("message", ""),
        },
    )


@app.post("/subscribe")
def subscribe(email: str = Form(...), bag_name: str = Form(...), db: Session = Depends(get_db)):
    exists = db.execute(
        select(Subscription).where(
            Subscription.email == email,
            Subscription.bag_name == bag_name,
            Subscription.active.is_(True),
        )
    ).scalar_one_or_none()
    if not exists:
        db.add(Subscription(email=email, bag_name=bag_name))
        db.commit()

    return RedirectResponse(url="/?message=Subscription+saved", status_code=303)


@app.post("/unsubscribe/{subscription_id}")
def unsubscribe(subscription_id: int, db: Session = Depends(get_db)):
    sub = db.get(Subscription, subscription_id)
    if sub:
        sub.active = False
        db.commit()
    return RedirectResponse(url="/?message=Unsubscribed", status_code=303)
