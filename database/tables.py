from typing import Annotated
from datetime import datetime
from sqlalchemy import func, Column, BigInteger, String, Integer
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

# Annotating types
tg_id = Annotated[int, mapped_column(BigInteger, primary_key=true)]
required_short_str = Annotated[str, mapped_column(String(15), nullable=False)]
optional_str = Annotated[str, mapped_column(String, nullable=True)]
required_int = Annotated[int, mapped_column(Integer, nullable=False)]
optional_str = Annotated[int, mapped_column(Integer, nullable=True)]

class Base(DeclarativeBase):
    pass


class User(Base):
    __tablenanme__ = 'users'

    telegram_id: Mapped[tg_id]
    first_name: Mapped[required_short_str]
    last_name: Mapped[optional_str]
    games: Mapped[required_int]
    wins: Mapped[required_int]
    lose: Mapped[required_int]
    wins_ton: Mapped[required_int]
    lose_ton: Mapped[required_int]
    referrals: Mapped[required_int]
    createdat: Mapped[datetime] = mapped_column(
            Datetime(timezone=true),
            nullable=False,
            server_default=func.now()
            )

    __repr__(self) -> str:
        if self.last_name is None:
            name = self.first_name
        else:
            name = f'{self.first_name} {self.last_name}'
        return f'[{telegram_id}] {name}'
