
from datetime import datetime
from dateutil.relativedelta import relativedelta


class Date:
    def __init__(self, expr: str):
        self.expr = expr
        self.date = datetime.strptime(expr, '%Y-%m-%d')

    def __add__(self, other):
        self.date = self.date + other.delta
        self.expr = datetime.strftime(self.date, '%Y-%m-%d')
        return self

    def __sub__(self, other):
        return (self.date - other.date).days / 360

    def __repr__(self):
        return self.expr

    def __hash__(self):
        # need to override if overriding __eq__
        return hash(self.expr)

    def __eq__(self, other):
        # this can deal with both Date == str and str == Date
        if isinstance(other, str):
            return self.expr == other
        return self.expr == other.expr

    def __gt__(self, other):
        return self.date > other.date

    def __ge__(self, other):
        return self.date >= other.date

    def __lt__(self, other):
        return self.date < other.date

    def __le__(self, other):
        return self.date <= other.date


class RDate:
    def __init__(self, expr: str):
        self.unit = expr[-1]
        self.interval = int(expr[:-1])

        if self.unit == 'd':
            self.delta = relativedelta(days=self.interval)
        elif self.unit == 'w':
            self.delta = relativedelta(weeks=self.interval)
        elif self.unit == 'm':
            self.delta = relativedelta(months=self.interval)
        else:
            raise ValueError(f'Unrecognized unit {self.unit}')
