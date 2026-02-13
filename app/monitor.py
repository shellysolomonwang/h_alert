import asyncio
import logging
import os
from datetime import datetime, timedelta, timezone

from sqlalchemy import and_, select

from .database import SessionLocal
from .emailer import send_alert_email
from .hermes import get_available_bags
from .models import AlertLog, Subscription

CHECK_INTERVAL_SECONDS = int(os.getenv("CHECK_INTERVAL_SECONDS", "30"))
DEDUP_MINUTES = int(os.getenv("DEDUP_MINUTES", "120"))
logger = logging.getLogger(__name__)


def _normalize(name: str) -> str:
    return " ".join(name.split()).strip().lower()


async def check_and_notify_once() -> int:
    available = get_available_bags()
    if not available:
        return 0

    sent = 0
    with SessionLocal() as db:
        subscriptions = db.execute(select(Subscription).where(Subscription.active.is_(True))).scalars().all()

        for sub in subscriptions:
            wanted = _normalize(sub.bag_name)
            if not available.get(wanted, False):
                continue

            cutoff = datetime.now(timezone.utc) - timedelta(minutes=DEDUP_MINUTES)
            already_sent = db.execute(
                select(AlertLog).where(
                    and_(
                        AlertLog.email == sub.email,
                        AlertLog.bag_name == sub.bag_name,
                        AlertLog.sent_at >= cutoff,
                    )
                )
            ).scalar_one_or_none()
            if already_sent:
                continue

            try:
                await send_alert_email(sub.email, sub.bag_name)
            except Exception as exc:  # noqa: BLE001
                logger.exception("Unable to send email for %s (%s): %s", sub.email, sub.bag_name, exc)
                continue

            db.add(AlertLog(email=sub.email, bag_name=sub.bag_name))
            db.commit()
            sent += 1

    return sent


async def monitor_loop(stop_event: asyncio.Event) -> None:
    while not stop_event.is_set():
        try:
            await check_and_notify_once()
        except Exception as exc:  # noqa: BLE001
            logger.exception("monitor loop failure: %s", exc)

        try:
            await asyncio.wait_for(stop_event.wait(), timeout=CHECK_INTERVAL_SECONDS)
        except asyncio.TimeoutError:
            continue
