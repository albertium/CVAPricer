
import abc
from typing import Union, Dict, Tuple
import numpy as np
from .simulation import Engine
from .date import Date


# ========== Base Cashflow ==========

class Cashflow(abc.ABC):
    """
    Provide basic cache functionality for cashflow
    We don't provide override for >, <, >= ,<= because we use fuzzy logic and need to customize epsilon
    """
    def __init__(self):
        self.cache = {}  # type: Dict[Tuple[Engine, Date], np.ndarray]
        self.empty = np.empty(0)

    @abc.abstractmethod
    def _evaluate(self, engine: Engine, date: Date) -> np.ndarray:
        pass

    def evaluate(self, engine: Engine, date: Date) -> np.ndarray:
        if (engine, date) in self.cache:
            return self.cache[(engine, date)]
        value = self._evaluate(engine, date)
        self.cache[(engine, date)] = value
        return value

    def __add__(self, rhs):
        if isinstance(rhs, (int, float)):
            rhs = Constant(rhs)
        return Addition(self, rhs)

    def __sub__(self, rhs):
        if isinstance(rhs, (int, float)):
            rhs = Constant(rhs)
        return Subtraction(self, rhs)

    def __mul__(self, rhs):
        if isinstance(rhs, (int, float)):
            rhs = Constant(rhs)
        return Multiplication(self, rhs)

    def __neg__(self):
        return Negation(self)


# ========== Atom Cashflow ==========

class Negation(Cashflow):
    def __init__(self, cashflow: Cashflow):
        super(Negation, self).__init__()
        self.cashflow = cashflow

    def _evaluate(self, engine, date) -> np.ndarray:
        return -self.cashflow.evaluate(engine, date)


class Addition(Cashflow):
    def __init__(self, lhs: Cashflow, rhs: Cashflow):
        super(Addition, self).__init__()
        self.lhs = lhs
        self.rhs = rhs

    def _evaluate(self, engine, date) -> np.ndarray:
        return self.lhs.evaluate(engine, date) + self.rhs.evaluate(engine, date)

    def __repr__(self):
        return f'{self.lhs} + {self.rhs}'


class Subtraction(Cashflow):
    def __init__(self, lhs: Cashflow, rhs: Cashflow):
        super(Subtraction, self).__init__()
        self.lhs = lhs
        self.rhs = rhs

    def _evaluate(self, engine, date) -> np.ndarray:
        return self.lhs.evaluate(engine, date) - self.rhs.evaluate(engine, date)

    def __repr__(self):
        return f'{self.lhs} - {self.rhs}'


class Multiplication(Cashflow):
    def __init__(self ,lhs: Cashflow, rhs: Cashflow):
        super(Multiplication, self).__init__()
        self.lhs = lhs
        self.rhs = rhs

    def _evaluate(self, engine: Engine, date: Date) -> np.ndarray:
        return self.lhs.evaluate(engine, date) * self.rhs.evaluate(engine, date)

    def __repr__(self):
        return f'{self.lhs} * {self.rhs}'


# ========== Storage Cashflow ==========

class Constant(Cashflow):
    def __init__(self, value: float):
        super(Constant, self).__init__()
        self.value = np.array(value)

    def _evaluate(self, engine, date) -> np.ndarray:
        return self.value

    def __repr__(self):
        return str(self.value)


class Vector(Cashflow):
    def __init__(self, value: Union[list, np.ndarray]):
        super(Vector, self).__init__()

        if not isinstance(value, np.ndarray):
            value = np.array(value)  # check first so that not to recreate a numpy array
        self.value = value

    def _evaluate(self, engine: Engine, date) -> np.ndarray:
        return self.value

    def __repr__(self):
        return f'Vec({self.value[0]}, {self.value[1]}, ...)'


class Cache(Cashflow):
    """
    Example usage:
    var = Cache(1)
    var.assign(Max(S > 100, var.value, 0))

    Using var and var.value to go around the recursive cashflow specification
    """
    def __init__(self, initial_value: Union[float, list, np.ndarray]):
        super(Cache, self).__init__()
        if isinstance(initial_value, (float, int)):
            initial_value = [initial_value]
        self.state = Vector(initial_value)
        self.cashflow = None

    def _evaluate(self, engine: Engine, date) -> np.ndarray:
        self.state.value = self.cashflow.evaluate(engine, date)
        return self.state.value

    def assign(self, cashflow: Cashflow):
        self.cashflow = cashflow


# ========== Index Cashflow ==========

class Equity(Cashflow):
    def __init__(self, name):
        super(Equity, self).__init__()
        self.name = name

    def _evaluate(self, engine, date) -> np.ndarray:
        engine.get_equity(date, self.name)

    def __repr__(self):
        return f'Eq[{self.name}]'


# ========== Operator Cashflow ==========

class Indicator(Cashflow):
    def __init__(self, condition: Cashflow, epsilon=1e-5):
        super(Indicator, self).__init__()
        self.condition = condition
        self.epsilon = epsilon
        self.half_eps = epsilon / 2

    def _evaluate(self, engine, date) -> np.ndarray:
        cond = self.condition.evaluate(engine, date)
        scaled = cond / self.epsilon
        return (scaled + 0.5) * (cond > -self.half_eps) - (scaled - 0.5) * (cond > self.half_eps)


class Max(Cashflow):
    """
    No need for fuzzy logic here. Max is smooth enough. Fuzzy logic is for sudden jump like binary function
    """
    def __init__(self, lhs: Cashflow, rhs: Cashflow):
        super(Max, self).__init__()
        self.lhs = lhs
        self.rhs = rhs

    def _evaluate(self, engine, date) -> np.ndarray:
        return np.maximum(self.lhs.evaluate(engine, date), self.rhs.evaluate(engine, date))

    def __repr__(self):
        return f'max({self.lhs}, {self.rhs})'
