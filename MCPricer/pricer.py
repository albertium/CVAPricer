
import numpy as np
from .security import Security
from .simulation import Engine


class Pricer:
    def __init__(self, security: Security, engine: Engine):
        self.security = security
        self.engine = engine

    def price(self):
        schedule = np.flip(self.security.schedule)  # backward induction
        self.engine.simulate(schedule)
        for date in schedule:
            cashflow = self.security.cashflows[date].evaluate(self.engine, date)
