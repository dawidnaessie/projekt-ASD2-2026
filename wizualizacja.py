"""
wizualizacja.py — Punkt wejścia (redirect do nowej modularnej struktury).

Uruchomienie:
    python wizualizacja.py

Nowa struktura kodu znajduje się w katalogu wizualizacja/
"""
import sys
import os

# Dodajemy katalog projektu do ścieżki
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from wizualizacja.app import main

if __name__ == "__main__":
    main()
