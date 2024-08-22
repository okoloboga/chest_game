from typing import Annotated
from datetime import datetime
from fluent_compiler.utils import re
from sqlalchemy import func, BigInteger, DateTime, String, Integer, Float
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

# Annotating types
tg_id = Annotated[int, mapped_column(BigInteger, primary_key=True)]
tr_hash = Annotated[str, mapped_column(String, primary_key=True)]
name = Annotated[str, mapped_column(String, primary_key=True)]
required_short_str = Annotated[str, mapped_column(String(15), nullable=False)]
optional_short_str = Annotated[str, mapped_column(String(15), nullable=True)]
required_str = Annotated[str, mapped_column(String, nullable=False)]
required_int = Annotated[int, mapped_column(Integer, nullable=False)]
required_float = Annotated[float, mapped_column(Float, nullable=False)]


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'users'

    telegram_id: Mapped[tg_id]
    first_name: Mapped[required_short_str]
    last_name: Mapped[optional_short_str]
    games: Mapped[required_int]
    wins: Mapped[required_int]
    lose: Mapped[required_int]
    wins_ton: Mapped[required_float]
    lose_ton: Mapped[required_float]
    referrals: Mapped[required_int]
    parent: Mapped[required_str]
    ton: Mapped[required_float]
    promo: Mapped[required_int]
    used_promo: Mapped[required_str]
    
    created_at: Mapped[datetime] = mapped_column(
            DateTime(timezone=True),
            nullable=False,
            server_default=func.now()
            )

    def __repr__(self) -> str:
        if self.last_name is None:
            name = self.first_name
        else:
            name = f'{self.first_name} {self.last_name}'
        return f'[{self.telegram_id}] {name}'
    

class TransactionHashes(Base):
    __tablename__ = 'hashes'
    
    transaction_hash: Mapped[tr_hash]
    transaction_value: Mapped[required_int]
    created_at: Mapped[datetime] = mapped_column(
                DateTime(timezone=True),
                nullable=False,
                server_default=func.now()
                )

    def __repr__(self) -> str:
        return f'[{self.transaction_hash}] = {self.transaction_value}'


class Variables(Base):
    __tablename__ = 'variables'

    name: Mapped[name]
    value: Mapped[required_str] 

