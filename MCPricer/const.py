
from enum import Enum


class SecurityType(Enum):
    EuropeanOption = 'opt'
    AmericanOption = 'am_opt'


class IndexType(Enum):
    Equity = 'equity'
    FX = 'fx'
    RateOption = 'rate'


class Denominated(Enum):
    USD = 'usd'
    EUR = 'eur'
    GBP = 'gbp'
