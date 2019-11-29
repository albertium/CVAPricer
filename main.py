
from MCPricer import Date, RDate
import MCPricer.security as sec


if __name__ == '__main__':
    print(Date('2019-01-01') > Date('2019-01-02'))
    print(Date('2019-01-01') + RDate('1m'))
    print(Date('2019-01-01') + RDate('2d'))
    print(Date('2019-01-01') + RDate('4w'))

