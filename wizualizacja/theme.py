"""
theme.py — Paleta kolorów, fonty i ładowanie assetów graficznych.
Centralny punkt konfiguracji wizualnej całego projektu.
"""
import os
import pygame

# ============================================================
# WYMIARY OKNA
# ============================================================
WIDTH, HEIGHT = 1440, 900

# ============================================================
# PALETA KOLORÓW — FANTASY KOPALNIANA
# ============================================================

# Tła
BG_DARK       = (25, 20, 35)      # Ciemny ametyst — główne tło algorytmów
BG_DARKER     = (15, 12, 22)      # Jeszcze ciemniejsze — dolna część gradientu

# Kryształy / lodowe akcenty
CRYSTAL_BLUE  = (80, 180, 255)    # Lodowy błękit — linie, krawędzie
CRYSTAL_CYAN  = (60, 220, 220)    # Cyjan — drzewo segment tree

# Ogień / ciepłe
AMBER         = (255, 140, 50)    # Bursztynowy — punkty aktywne, ogień latarni
GOLD          = (200, 160, 50)    # Złoty — akcenty, runy, etykiety ważne

# Natura / sukces
EMERALD       = (50, 255, 180)    # Szmaragdowy — otoczka, flow, sukces
EMERALD_DARK  = (30, 180, 60)     # Ciemniejszy szmaragd

# Tekst
PARCHMENT     = (220, 210, 190)   # Pergaminowy — tekst główny na ciemnym tle
STEEL         = (140, 160, 180)   # Stalowy — tekst drugorzędny
DARK_TEXT      = (40, 30, 20)     # Ciemny brąz — tekst na jasnym tle (menu)

# Negatywne / alerty
BLOOD_RED     = (200, 50, 60)     # Krew — usunięcie, błąd
SOFT_RED      = (220, 80, 80)     # Miękki czerwony — podświetlenie

# Neutralne
FAINT_GRAY    = (80, 80, 100)     # Przyciemniony szary — nieaktywne krawędzie
STONE_GRAY    = (100, 95, 110)    # Kamień — obramowania

# Specjalne
GLOW_BLUE     = (80, 180, 255, 60)   # Glow niebieski (z alpha)
GLOW_GREEN    = (50, 255, 180, 60)   # Glow zielony (z alpha)
GLOW_AMBER    = (255, 140, 50, 60)   # Glow bursztynowy (z alpha)

# Kolory węzłów MCMF
NODE_DWARF    = (70, 90, 130)     # Stalowy błękit — krasnoludki
NODE_SOURCE   = EMERALD_DARK      # Źródło
NODE_SINK     = BLOOD_RED         # Ujście

# ============================================================
# ŚCIEŻKI ASSETÓW
# ============================================================
_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_ASSETS   = os.path.join(_BASE_DIR, "assets")
_FONTS    = os.path.join(_ASSETS, "fonts")

# ============================================================
# ŁADOWANIE FONTÓW
# ============================================================
def _load_font(name, size, bold=False):
    """Próbuje załadować font z pliku TTF, fallback na systemowe."""
    path = os.path.join(_FONTS, name)
    try:
        if os.path.exists(path):
            f = pygame.font.Font(path, size)
            # Weryfikacja — próba renderowania
            f.render("X", True, (255, 255, 255))
            return f
    except Exception:
        pass
    # Fallback: Copperplate (fantazyjny, dostępny na macOS) -> Georgia -> Arial
    for fallback in ["copperplate", "georgia", "arial"]:
        try:
            f = pygame.font.SysFont(fallback, size, bold=bold)
            f.render("X", True, (255, 255, 255))
            return f
        except Exception:
            continue
    return pygame.font.SysFont(None, size, bold=bold)

def load_fonts():
    """Zwraca słownik z fontami używanymi w aplikacji."""
    return {
        "title":    _load_font("MedievalSharp-Regular.ttf", 36, bold=True),
        "subtitle": _load_font("MedievalSharp-Regular.ttf", 26),
        "body":     pygame.font.SysFont("georgia", 20),
        "small":    pygame.font.SysFont("georgia", 22, bold = True),
        "mono":     pygame.font.SysFont("couriernew", 18),
        "menu_tab": _load_font("MedievalSharp-Regular.ttf", 19, bold=False),
        "ui_btn":   pygame.font.SysFont("georgia", 16, bold=True),
    }

# ============================================================
# ŁADOWANIE OBRAZÓW
# ============================================================
def _safe_load(filename, size=None):
    """Ładuje obraz z assets/, skaluje jeśli podano rozmiar. Zwraca None przy błędzie."""
    path = os.path.join(_ASSETS, filename)
    try:
        img = pygame.image.load(path).convert_alpha()
        if filename == "pasek_ui.png":
            # Crop to the actual wooden beam (vertical range [150, 350] inside 500x500 canvas)
            img = img.subsurface((0, 150, img.get_width(), 200))
        if size:
            img = pygame.transform.smoothscale(img, size)
        return img
    except Exception as e:
        print(f"[theme] Nie można załadować {filename}: {e}")
        return None

def load_images():
    """Zwraca słownik ze wszystkimi obrazami/sprite'ami."""
    return {
        # Tła (NIE usuwamy czerni — to część scenerii)
        "bg_menu":         _safe_load("tlo_startowe.png", (WIDTH, HEIGHT)),
        "bg_graham":       _safe_load("tlo_graham.png", (WIDTH, HEIGHT)),
        "bg_mcmf":         _safe_load("tlo_mcmf.png", (WIDTH, HEIGHT)),
        "bg_dekametrowcy": _safe_load("tlo_dekametrowcy.png", (WIDTH, HEIGHT)),

        # Sprite'y obiektów (Mają już przezroczyste tło w plikach PNG)
        "kopalnia_sm":     _safe_load("kopalnia.png", (70, 70)),
        "kopalnia_lg":     _safe_load("kopalnia.png", (65, 65)),
        "krasnal":         _safe_load("krasnal_sprite.png", (65, 65)),
        "tron":            _safe_load("tron_sprite.png", (110, 110)),
        "wozek":           _safe_load("wozek_sprite.png", (110, 110)),
        "flaga_p0":        _safe_load("flaga_p0.png", (50, 50)),

        # UI (NIE usuwamy — ciemne tło paska jest zamierzone)
        "pasek_ui":        _safe_load("pasek_ui.png", (WIDTH, 86)),

        # Ikona aplikacji
        "app_icon":        _safe_load("app_icon.png"),
    }

