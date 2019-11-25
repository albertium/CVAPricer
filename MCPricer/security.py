
from typing import Dict
from .const import SecurityType
from .date import Date
from . import cashflow as cf


class Index:
    """
    This represents price of equity and FX or value of rates
    To be differentiated with asset, which is traded on the market and thus holds market value directly.
    For example the value of rates (an index) is a derived quantity from market value of bonds and swaps (assets)
    """
    def __init__(self, index_type, name):
        self.index_type = index_type
        self.name = name


class Security:
    def __init__(self, security_type, cashflows: Dict[Date, cf.Cashflow]):
        self.security_type = security_type
        # schedule is the dates of event that are known as of today
        # to be differentiate with event_dates which can be added by the pricer to improve accuracy
        self.cashflows = cashflows
        self.schedule = sorted(self.cashflows.keys())

    def __str__(self):
        text = ''
        text += f'{self.security_type.name}\n'
        for date, cashflow in zip(self.schedule, self.cashflows):
            text += f'{date}: {cashflow}'
        return text

    def __repr__(self):
        return self.security_type.name


class EuropeanOption(Security):
    def __init__(self, asset: str, expiry: Date, strike: float):
        self.asset = asset
        self.expiry = expiry
        self.strike = strike
        cashflows = {expiry: cf.Max(cf.Equity(asset) - strike, 0)}
        super(EuropeanOption, self).__init__(SecurityType.EuropeanOption, cashflows=cashflows)
