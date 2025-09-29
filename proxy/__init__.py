#!/usr/bin/env python3
"""
Proxy-Package Export: Lädt die passende TorProxy-Implementierung je OS.
Vermeidet Namenskonflikte mit externen Paketen namens 'proxy'.
"""

from .tor_proxy import TorProxy  # dynamischer Loader in tor_proxy.py

__all__ = ["TorProxy"]


