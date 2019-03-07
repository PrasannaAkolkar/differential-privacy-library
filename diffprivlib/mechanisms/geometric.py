from numbers import Integral

from numpy.random import random
from numpy import exp, floor, log, isclose

from . import DPMechanism, TruncationAndFoldingMachine


class Geometric(DPMechanism):
    def __init__(self):
        super().__init__()
        self._sensitivity = None
        self._scale = None

    def __repr__(self):
        output = super().__repr__()
        output += ".set_sensitivity(" + str(self._sensitivity) + ")" if self._sensitivity is not None else ""

        return output

    def set_sensitivity(self, sensitivity):
        """

        :param sensitivity:
        :type sensitivity `float`
        :return:
        """
        if not isinstance(sensitivity, Integral):
            raise TypeError("Sensitivity must be an integer")

        if sensitivity <= 0:
            raise ValueError("Sensitivity must be strictly positive")

        self._sensitivity = sensitivity
        return self

    def check_inputs(self, value=None):
        super().check_inputs(value)

        if (value is not None) and not isinstance(value, Integral):
            raise TypeError("Value to be randomised must be an integer")

        if self._sensitivity is None:
            raise ValueError("Sensitivity must be set")

    def set_epsilon_delta(self, epsilon, delta):
        if not delta == 0:
            raise ValueError("Delta must be zero")

        return super().set_epsilon_delta(epsilon, delta)

    def randomise(self, value):
        self.check_inputs(value)

        if self._scale is None:
            self._scale = - self._epsilon / self._sensitivity

        # Need to account for overlap of 0-value between distributions of different sign
        u = random() - 0.5
        u *= 1 + exp(self._scale)
        sgn = -1 if u < 0 else 1

        # Use formula for geometric distribution, with ratio of exp(-epsilon/sensitivity)
        return int(round(value + sgn * floor(log(sgn * u) / self._scale)))


class GeometricTruncated(Geometric, TruncationAndFoldingMachine):
    def __init__(self):
        super().__init__()
        TruncationAndFoldingMachine.__init__(self)

    def __repr__(self):
        output = super().__repr__()
        output += TruncationAndFoldingMachine.__repr__(self)

        return output

    def set_bounds(self, lower, upper):
        if not isinstance(lower, Integral) or not isinstance(upper, Integral):
            raise TypeError("Bounds must be integers")

        return super().set_bounds(lower, upper)

    def randomise(self, value):
        TruncationAndFoldingMachine.check_inputs(self, value)

        noisy_value = super().randomise(value)
        return int(round(self._truncate(noisy_value)))


class GeometricFolded(Geometric, TruncationAndFoldingMachine):
    def __init__(self):
        super().__init__()
        TruncationAndFoldingMachine.__init__(self)

    def __repr__(self):
        output = super().__repr__()
        output += TruncationAndFoldingMachine.__repr__(self)

        return output

    def set_bounds(self, lower, upper):
        if not isclose(2 * lower, round(2 * lower)) or not isclose(2 * upper, round(2 * upper)):
            raise ValueError("Bounds must be integer or half-integer floats")

        return super().set_bounds(lower, upper)

    def _fold(self, value):
        return super()._fold(int(round(value)))

    def randomise(self, value):
        TruncationAndFoldingMachine.check_inputs(self, value)

        noisy_value = super().randomise(value)
        return int(round(self._fold(noisy_value)))
