
import unittest as ut
import numpy as np
from numpy.testing import assert_equal, assert_almost_equal

from MCPricer import cashflow as cf
from MCPricer.simulation import DummyEngine
from MCPricer import Date


class TestAtomicCashflow(ut.TestCase):
    def test_arithmetic(self):
        dates = np.array([Date('2019-01-01'), Date('2019-02-01'), Date('2019-03-01')])
        engine = DummyEngine('dummy', dates, 1000)
        x = cf.Constant(1)
        y = cf.Constant(3)

        # addition
        self.assertEqual(4, (x + y).evaluate(engine, dates[0]))
        self.assertEqual(6, (x + 5).evaluate(engine, dates[0]))

        # subtraction
        self.assertEqual(-2, (x - y).evaluate(engine, dates[0]))
        self.assertEqual(0, (x - 1).evaluate(engine, dates[0]))

        # multiplication
        self.assertEqual(3, (x * y).evaluate(engine, dates[0]))
        self.assertEqual(4, (x * 4).evaluate(engine, dates[0]))

        # negation
        val = -x.evaluate(engine, dates[0])
        self.assertEqual(-1, val)

    def test_caching(self):
        dates = np.array([Date('2019-01-01'), Date('2019-02-01'), Date('2019-03-01')])
        engine = DummyEngine('dummy', dates, 1000)
        x = cf.Constant(1)
        y = cf.Constant(2)

        self.assertEqual(0, len(x.cache))
        self.assertEqual(0, len(y.cache))

        x.evaluate(engine, dates[0])
        self.assertEqual(1, len(x.cache))

        # cached
        x.value = 10
        val = x.evaluate(engine, dates[0])
        self.assertEqual(1, val)

        # not cached
        y.value = 10
        val = y.evaluate(engine, dates[0])
        self.assertEqual(10, val)

    def test_vector(self):
        N = 10
        date = Date('2019-01-01')
        engine = DummyEngine('dummy', np.array([date]), N)
        x = cf.Vector(np.ones(N))
        y = cf.Constant(10)

        # arithmetic
        assert_equal(np.ones(N) * -9, (x - y).evaluate(engine, date))
        assert_equal(np.ones(N) * -1, -x.evaluate(engine, date))
        assert_equal(np.ones(N) * 10, (x * 10).evaluate(engine, date))

    def test_condition(self):
        N = 10
        date = Date('2019-01-01')
        engine = DummyEngine('dummy', np.array([date]), N)

        # test basic indicator
        ind = cf.Indicator(cf.Vector(np.arange(5)) - 2, 0.1)
        val = ind.evaluate(engine, date)
        assert_equal([0, 0, 0.5, 1, 1], val)

        ind = cf.Indicator(cf.Vector([1.95, 1.97, 2, 2.03, 2.05]) - 2, 0.1)
        val = ind.evaluate(engine, date)
        assert_almost_equal([0, 0.2, 0.5, 0.8, 1], val, decimal=10)

        # test max
        val = cf.Max(cf.Vector(np.arange(5)), cf.Constant(2)).evaluate(engine, date)
        assert_almost_equal([2, 2, 2, 3, 4], val)

        val = cf.Max(cf.Vector([3, 2, 1, 4, 5]), cf.Vector(np.arange(5))).evaluate(engine, date)
        assert_almost_equal([3, 2, 2, 4, 5], val)

        val = cf.Max(cf.Vector([1.95, 1.975, 2, 2.025, 2.05]), cf.Constant(2)).evaluate(engine, date)
        assert_almost_equal([2, 2, 2, 2.025, 2.05], val)

    def test_cache(self):
        N = 10
        dates = [Date('2019-01-01'), Date('2019-02-01'), Date('2019-03-01'), Date('2019-04-01'), Date('2019-05-01')]
        engine = DummyEngine('dummy', np.array(dates), N)

        class MockCashflow(cf.Cashflow):
            def __init__(self, map):
                super(MockCashflow, self).__init__()
                self.spot = map

            def _evaluate(self, eng, dt: Date) -> np.ndarray:
                return np.array(self.spot[dt])

        # single variable corner case
        index = MockCashflow({k: v for k, v in zip(dates, [101, 100, 100, 99, 101])})
        alive = cf.Cache(1)
        alive.assign(cf.Indicator(index - cf.Constant(100)) * alive.state)
        vals = [alive.evaluate(engine, d) for d in dates]
        assert_almost_equal([[1], [0.5], [0.25], [0], [0]], vals)

        # multivariate normal case
        index = MockCashflow({k: v for k, v in zip(dates, [[101, 100], [100, 100], [100, 100], [99, 100], [101, 99]])})
        alive = cf.Cache([1, 1])
        alive.assign(cf.Indicator(index - cf.Constant(100)) * alive.state)
        vals = [alive.evaluate(engine, d) for d in dates]
        assert_almost_equal([[1, 0.5], [0.5, 0.25], [0.25, 0.125], [0, 0.0625], [0, 0]], vals)
