import os
import sys

# Permet à Python de trouver main.py et agents.py situés à la racine
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app
