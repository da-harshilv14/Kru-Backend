"""
Unit tests for DashboardConfig.ready.
"""

import sys
import types
import pytest
import importlib
import builtins
from django.apps import apps

from dashboard.apps import DashboardConfig


@pytest.fixture(autouse=True)
def cleanup_dashboard_signals_import():
    """Ensure clean import state before/after each test."""
    sys.modules.pop("dashboard.signals", None)
    yield
    sys.modules.pop("dashboard.signals", None)


@pytest.fixture
def dashboard_config():
    """Return the real DashboardConfig instance."""
    return apps.get_app_config("dashboard")


class TestDashboardConfigReady:

    @pytest.mark.happy_path
    def test_ready_imports_signals_successfully(self, dashboard_config):
        dashboard_config.ready()
        assert "dashboard.signals" in sys.modules

    @pytest.mark.happy_path
    def test_ready_is_idempotent(self, dashboard_config):
        dashboard_config.ready()
        dashboard_config.ready()
        dashboard_config.ready()
        assert "dashboard.signals" in sys.modules

    @pytest.mark.edge_case
    def test_ready_uses_existing_signals_module(self, dashboard_config, monkeypatch):
        dummy = types.ModuleType("dashboard.signals")
        monkeypatch.setitem(sys.modules, "dashboard.signals", dummy)

        dashboard_config.ready()

        assert sys.modules["dashboard.signals"] is dummy

    @pytest.mark.edge_case
    def test_ready_propagates_import_error(self, dashboard_config, monkeypatch):
        """Simulate failure of direct Python import (import dashboard.signals)."""

        def fake_import(name, globals=None, locals=None, fromlist=None, level=0):
            if name == "dashboard.signals":
                raise ImportError("Simulated import error")
            return real_import(name, globals, locals, fromlist, level)

        real_import = builtins.__import__
        monkeypatch.setattr(builtins, "__import__", fake_import)

        with pytest.raises(ImportError, match="Simulated import error"):
            dashboard_config.ready()
