"""Falsification experiments: the agent writes, runs and judges its own simulations.

See ``lab.SimulationLab`` for the flow (protocol -> script -> run -> audit ->
evidence) and ``runner.ScriptRunner`` for the execution guard rails.
"""

from .lab import SimulationLab
from .protocol import ExperimentProtocol

__all__ = ["SimulationLab", "ExperimentProtocol"]
