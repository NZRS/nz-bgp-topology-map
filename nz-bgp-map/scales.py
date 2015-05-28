class Scale:
    m = 0.0
    b = 0.0
    p = 0.0
    d = []
    r = []

    def __init__(self, domain, _range, power):
        self.m = (_range[-1] - _range[0]) / (pow(domain[-1], power) - pow(domain[0], power))
        self.b = _range[0] - self.m*pow(domain[0], power)
        self.p = power
        self.d = domain
        self.r = _range

    def get_value(self, v):
        if v <= self.d[0]:
            return self.r[0]
        elif v >= self.d[-1]:
            return self.r[-1]
        else:
            return self.m*pow(v, self.p) + self.b

