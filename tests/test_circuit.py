import circuit
import numpy as np
import sys
from collections import Counter

EPS = 1e-16

def vec_distsq(a, b):
    diff = a - b
    return diff.T.conjugate() @ diff

def is_vec_same(a, b, eps=EPS):
    return vec_distsq(a, b) < eps

def test_hgate1():
    assert is_vec_same(circuit.Circuit().h[1].h[0].run(), np.array([0.5, 0.5, 0.5, 0.5]))

def test_hgate2():
    assert is_vec_same(circuit.Circuit().x[0].h[0].run(), np.array([1/np.sqrt(2), -1/np.sqrt(2)]))

def test_cx():
    assert is_vec_same(
            circuit.Circuit().h[0].h[1].cx[1,0].h[0].h[1].run(),
            circuit.Circuit().cx[0,1].run()
    )

def test_rz():
    assert is_vec_same(circuit.Circuit().h[0].rz(np.pi)[0].run(), circuit.Circuit().x[0].h[0].run())

def test_measurement1():
    c = circuit.Circuit().m[0]
    for _ in range(10000):
        c.run()
    cnt = Counter(c.run_history)
    assert cnt.most_common(1) == [((0,), 10000)]

def test_measurement2():
    c = circuit.Circuit().x[0].m[0]
    for _ in range(10000):
        c.run()
    cnt = Counter(c.run_history)
    assert cnt.most_common(1) == [((1,), 10000)]

def test_measurement_multiqubit1():
    c = circuit.Circuit().x[0].m[1]
    for _ in range(10000):
        c.run()
    cnt = Counter(c.run_history)
    # 0-th qubit is also 0 because it is not measured.
    assert cnt.most_common(1) == [((0,0), 10000)]

def test_measurement_multiqubit2():
    c = circuit.Circuit().x[0].m[1].m[0]
    for _ in range(10000):
        c.run()
    cnt = Counter(c.run_history)
    assert cnt.most_common(1) == [((1,0), 10000)]

def test_measurement_hadamard1():
    n = 10000
    c = circuit.Circuit().h[0].m[0]
    for _ in range(n):
        c.run()
    cnt = Counter(c.run_history)
    a, b = cnt.most_common(2)
    assert a[1] + b[1] == n
    # variance of binomial distribution (n -> ∞) is np(1-p)
    # therefore, 2σ = 2 * sqrt(np(1-p))
    two_sigma = 2 * np.sqrt(n * 0.5 * 0.5)
    assert abs(a[1] - n/2) < two_sigma
