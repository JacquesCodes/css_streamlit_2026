# -*- coding: utf-8 -*-
"""
Created on Tue Jan 27 17:38:34 2026

@author: BBarsch
"""

import subprocess

# file = "app.py"
# file = "app_plots.py"
# file = "app_profiler.py"
file = "app_profiler_menus.py"


subprocess.Popen(
    ["streamlit", "run", file], shell=True
)