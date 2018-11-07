"""
`gate` module implements quantum gate operations.
This module is internally used.
"""

import math
import random
from abc import ABC, abstractmethod
import numpy as np

class Gate(ABC):
    """Abstract quantum gate class."""
    lowername = None

    def __init__(self, targets, **kwargs):
        if self.lowername is None:
            raise ValueError(f"{self.__class__.__name__}.lowername is not defined.")
        self.kwargs = kwargs
        self.targets = targets

    def fallback(self):
        """Returns alternative gates to make equivalent circuit."""
        raise NotImplementedError(f"The fallback of {self.__class__.__name__} gate is not defined.")

class OneQubitGate(Gate):
    """Abstract quantum gate class for 1 qubit gate."""
    def target_iter(self, n_qubits):
        return slicing(self.targets, n_qubits)

class TwoQubitGate(Gate):
    """Abstract quantum gate class for 2 qubits gate."""
    def control_target_iter(self, n_qubits):
        return qubit_pairs(self.targets, n_qubits)

class IGate(OneQubitGate):
    """Identity Gate"""
    lowername = "i"
    def fallback(self):
        return []

class XGate(OneQubitGate):
    """Pauli's X Gate"""
    lowername = "x"

class YGate(OneQubitGate):
    """Pauli's Y Gate"""
    lowername = "y"

class ZGate(OneQubitGate):
    """Pauli's Z Gate"""
    lowername = "z"

class HGate(OneQubitGate):
    """Hadamard Gate"""
    lowername = "h"

class CZGate(TwoQubitGate):
    """Control-Z gate"""
    lowername = "cz"

class CXGate(TwoQubitGate):
    """Control-X (CNOT) Gate"""
    lowername = "cx"

class RXGate(OneQubitGate):
    """Rotate-X gate"""
    lowername = "rx"
    def __init__(self, targets, theta, **kwargs):
        super().__init__(targets, **kwargs)
        self.theta = theta

class RYGate(OneQubitGate):
    """Rotate-Y gate"""
    lowername = "ry"
    def __init__(self, targets, theta, **kwargs):
        super().__init__(targets, **kwargs)
        self.theta = theta

class RZGate(OneQubitGate):
    """Rotate-Z gate"""
    lowername = "rz"
    def __init__(self, targets, theta, **kwargs):
        super().__init__(targets, **kwargs)
        self.theta = theta

class TGate(OneQubitGate):
    """T ($\\pi/8$) gate"""
    lowername = "t"

class SGate(OneQubitGate):
    """S gate"""
    lowername = "s"

class Measurement(OneQubitGate):
    """Measurement gate"""
    lowername = "measure"

def slicing_singlevalue(arg, length):
    """Internally used."""
    if isinstance(arg, slice):
        start, stop, step = arg.indices(length)
        i = start
        if step > 0:
            while i < stop:
                yield i
                i += step
        else:
            while i > stop:
                yield i
                i += step
    else:
        try:
            i = arg.__index__()
        except AttributeError:
            raise TypeError("indices must be integers or slices, not " + arg.__class__.__name__)
        if i < 0:
            i += length
        yield i

def slicing(args, length):
    """Internally used."""
    if isinstance(args, tuple):
        for arg in args:
            yield from slicing_singlevalue(arg, length)
    else:
        yield from slicing_singlevalue(args, length)

def qubit_pairs(args, length):
    """Internally used."""
    if not isinstance(args, tuple):
        raise ValueError("Control and target qubits pair(s) are required.")
    if len(args) != 2:
        raise ValueError("Control and target qubits pair(s) are required.")
    controls = list(slicing(args[0], length))
    targets = list(slicing(args[1], length))
    if len(controls) != len(targets):
        raise ValueError("The number of control qubits and target qubits are must be same.")
    for c, z in zip(controls, targets):
        if c == z:
            raise ValueError("Control qubit and target qubit are must be different.")
    return zip(controls, targets)

def get_maximum_index(indices):
    """Internally used."""
    def _maximum_idx_single(idx):
        if isinstance(idx, slice):
            start = -1
            stop = 0
            if idx.start is not None:
                start = idx.start.__index__()
            if idx.stop is not None:
                stop = idx.stop.__index__()
            return max(start, stop - 1)
        else:
            return idx.__index__()
    if isinstance(indices, tuple):
        return max(_maximum_idx_single(i) for i in indices)
    else:
        return _maximum_idx_single(indices)

def find_n_qubits(gates):
    return max((get_maximum_index(g.targets) for g in gates), default=-1) + 1
