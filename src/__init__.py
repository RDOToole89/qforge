"""QForge - A general-purpose quantum experiment framework built on Qiskit."""

try:
    from ._version import version as __version__
except ImportError:
    __version__ = "0.0.0.dev"
