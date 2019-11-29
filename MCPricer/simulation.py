
import numpy as np
import abc
from typing import Iterable
from .date import Date
from .const import Denominated


class Engine(abc.ABC):
    def __init__(self, model_name, dates: np.ndarray, num_paths=10000, equities=None, rates=None, fxs=None):
        self.model_name = model_name
        indices = np.arange(dates.shape[0])
        self.date_map = {date: idx for date, idx in zip(dates, indices)}
        self.num_paths = num_paths
        self.states = {}  # for storing simulated risk factors

        # supported risk factors
        self.equities = {eq: 1 for eq in equities} if equities is not None else {}
        self.rates = {rate: 1 for rate in rates} if rates is not None else {}
        self.fxs = {fx: 1 for fx in fxs} if fxs is not None else {}

    @abc.abstractmethod
    def simulate(self, dates: np.ndarray):
        pass

    def get_equity(self, name, date: Date) -> np.ndarray:
        raise ValueError(f'Equity is not supported in {self.model_name}')

    def get_rate(self, name, date: Date):
        raise ValueError(f'Rate is not supported in {self.model_name}')

    def get_fx(self, name, date: Date):
        raise ValueError(f'FX is not supported in {self.model_name}')

    def get_numeraire(self, fixing_date: Date, target_date: Date):
        raise ValueError(f'Discounting is not supported in {self.model_name}')

    def __hash__(self):
        return hash(self.model_name)

    def __eq__(self, other):
        return self.model_name == other.model_name


class DummyEngine(Engine):
    def simulate(self, dates: np.ndarray):
        pass


class BlackScholes(Engine):
    def __init__(self, dates: np.ndarray, denominated, name, spot, r, q, sigma):
        super(BlackScholes, self).__init__('Black Scholes', dates, equities=[name])
        self.denominated = denominated
        self.name = name
        self.spot = spot
        self.r = r
        self.q = q
        self.sigma = sigma

    def simulate(self, dates: np.ndarray, num_paths=10000):
        delta_t = dates[1:] - dates[:-1]
        normal = np.random.normal(0, 1, (dates.shape[0], num_paths))
        mu = ((self.r - self.q) * delta_t).reshape((-1, 1))
        sig = (self.sigma * np.sqrt(delta_t)).reshape((-1, 1))
        prices = self.spot * np.exp(np.cumsum(mu + sig * normal, axis=0))
        self.states[self.name] = np.vstack([self.spot * np.ones(num_paths), prices])

    def get_equity(self, name, date: Date):
        return self.states[self.date_map[date]]

    def get_numeraire(self, fixing_date: Date, target_date: Date):
        return np.exp(self.r * (target_date - fixing_date))
