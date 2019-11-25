
import abc
from typing import Union
from .simulation import Engine
from .const import Denominated


# ========== Atom Cashflow ==========
class Cashflow(abc.ABC):
    @abc.abstractmethod
    def evaluate(self, engine: Engine, date):
        pass

    def __add__(self, rhs):
        if isinstance(rhs, float):
            rhs = Constant(rhs)
        return Addition(self, rhs)

    def __sub__(self, rhs):
        if isinstance(rhs, float):
            rhs = Constant(rhs)
        return Subtraction(self, rhs)

    def __neg__(self):
        return Negation(self)


class Constant(Cashflow):
    def __init__(self, value: float):
        self.value = value

    def evaluate(self, engine, date):
        return self.value

    def __repr__(self):
        return str(self.value)


class Negation(Cashflow):
    def __init__(self, cashflow: Cashflow):
        self.cashflow = cashflow

    def evaluate(self, engine, date):
        return -self.cashflow.evaluate(engine, date)


class Addition(Cashflow):
    def __init__(self, lhs, rhs):
        self.lhs = lhs
        self.rhs = rhs

    def evaluate(self, engine, date):
        return self.lhs.evaluate(engine, date) + self.rhs.evaluate(engine, date)

    def __repr__(self):
        return f'{self.lhs} + {self.rhs}'


class Subtraction(Cashflow):
    def __init__(self, lhs, rhs):
        self.lhs = lhs
        self.rhs = rhs

    def evaluate(self, engine, date):
        return self.lhs.evaluate(engine, date) - self.rhs.evaluate(engine, date)

    def __repr__(self):
        return f'{self.lhs} - {self.rhs}'


# ========== Index Cashflow ==========

class Equity(Cashflow):
    def __init__(self, name):
        self.name = name

    def evaluate(self, engine, date):
        engine.get_equity(date, self.name)

    def __repr__(self):
        return f'Eq[{self.name}]'


class DF(Cashflow):
    def __init__(self, denominated: Denominated, tenor):
        self.denominated = denominated
        self.tenor = tenor

    def evaluate(self, engine, date):
        engine.get_numeraire(self.denominated, date, date, date + self.tenor)

    def __repr__(self):
        return f'Disc[{self.denominated.name}]'


# ========== Operator Cashflow ==========

class Indicator(Cashflow):
    def __init__(self, condition: Cashflow, epsilon=1e-5):
        self.condition = condition
        self.epsilon = epsilon
        self.half_eps = epsilon / 2

    def evaluate(self, engine, date):
        cond = self.condition.evaluate(engine, date)
        scaled = cond / self.epsilon
        return (scaled + 0.5) * (cond > -self.half_eps) - (scaled - 0.5) * (cond > self.half_eps)


class Max(Cashflow):
    def __init__(self, lhs: [float, Cashflow], rhs: Union[float, Cashflow]):
        self.lhs = lhs if isinstance(lhs, Cashflow) else Constant(lhs)  # type: Cashflow
        self.rhs = rhs if isinstance(rhs, Cashflow) else Constant(rhs)  # type: Cashflow
        self.ind = Indicator(lhs - rhs)

    def evaluate(self, engine, date):
        ind = self.ind.evaluate(engine, date)
        return ind * self.lhs.evaluate(engine, date) * (1 - ind) * self.rhs.evaluate(engine, date)

    def __repr__(self):
        return f'max({self.lhs}, {self.rhs})'
