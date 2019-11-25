
from datetime import datetime


class Date:
    def __init__(self, expr: str):
        self.expr = expr
        self.date = datetime.strptime(expr, '%Y-%m-%d')

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
