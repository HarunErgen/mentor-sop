from datetime import datetime, timezone, timedelta
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import User
from app.core.config import TOKEN_RESET_DAYS

async def check_and_reset_tokens(user: User, db: AsyncSession) -> User:
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    
    if user.last_reset_date is None or (now - user.last_reset_date) >= timedelta(days=TOKEN_RESET_DAYS):
        user.tokens_used = 0
        user.last_reset_date = now
        
        await db.execute(
            update(User)
            .where(User.id == user.id)
            .values(tokens_used=0, last_reset_date=now)
        )
        await db.commit()
    
    return user

def has_enough_tokens(user: User, estimated_tokens: int = 0) -> bool:
    return (user.tokens_used + estimated_tokens) < user.token_limit
