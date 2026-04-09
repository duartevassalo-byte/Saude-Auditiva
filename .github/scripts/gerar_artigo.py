#!/usr/bin/env python3
"""
Gera um artigo via Claude API e adiciona ao artigos.json.
Corre automaticamente via GitHub Actions.
"""

import anthropic
import json
import os
import random
from datetime import datetime, timezone

# ── Configuração ──────────────────────────────────────────────
CATEGORIAS = [
    "Perda Auditiva",
    "Sinais de Alerta",
    "Prevenção",
    "Família",
    "Diagnóstico",
    "Aparelhos",
]