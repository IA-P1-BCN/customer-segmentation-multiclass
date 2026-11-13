"""Central project configuration (US-03, issue #15).

``RANDOM_STATE`` is the single source of truth for every stochastic step of
the project (data splits, cross-validation, resampling and models), so that
any run can be repeated exactly (AGENTS.md section 5).

Usage:

    from src.config import RANDOM_STATE

Never hardcode ``42`` elsewhere; import this constant instead.
"""

RANDOM_STATE = 42
