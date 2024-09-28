# experimental
from dataclasses import dataclass
from decimal import Decimal
from typing import Self


@dataclass
class Money:
    amount_cents: int = 0
    currency_symbol: str = "XAF"

    @classmethod
    def mint(cls, amount: Decimal | float, currency_symbol: str = "XAF") -> Self:
        return cls(int(amount * 100), currency_symbol)

    def __str__(self):
        amount = self.amount_cents / 100
        return f"{self.currency_symbol} {amount:,.2f}".replace(',', ' ')

    def __add__(self, other: Self) -> Self:
        if isinstance(other, Money):
            return Money(self.amount_cents + other.amount_cents, self.currency_symbol)

    def __sub__(self, other: Self) -> Self:
        if isinstance(other, Money):
            return Money(self.amount_cents - other.amount_cents, self.currency_symbol)