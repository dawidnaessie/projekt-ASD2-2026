"""
scenes/graham.py — Wizualizacja algorytmu Graham Scan (Patrol Księcia).
"""
import pygame
from functools import cmp_to_key
from wizualizacja import theme
from wizualizacja.effects import draw_glow_line, draw_glow_circle, draw_title_bar

# Importy logiki algorytmu
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from src.patrol_ksiecia import orientacja, odleglosc_kwadrat


def math_coords(p):
    """Konwertuje ekranowe Y (w dół) na kartezjańskie Y (w górę)."""
    return (p[0], -p[1])


def graham_scan_generator(punkty):
    """Generator kroków algorytmu Grahama do wizualizacji krok-po-kroku."""
    p0 = max(punkty, key=lambda p: (p[1], -p[0]))
    yield [p0], "Znaleziono punkt startowy p0 (najniższy na ekranie)"

    def compare_polar(p, q):
        o = orientacja(math_coords(p0), math_coords(p), math_coords(q))
        if o > 0: return -1
        elif o < 0: return 1
        else:
            d_p = odleglosc_kwadrat(p0, p)
            d_q = odleglosc_kwadrat(p0, q)
            return -1 if d_p < d_q else (1 if d_p > d_q else 0)

    posortowane = sorted([p for p in punkty if p != p0], key=cmp_to_key(compare_polar))
    yield [p0] + posortowane, "Posortowano punkty kątowo względem p0"

    unikalne_katy = []
    for p in posortowane:
        while len(unikalne_katy) > 0 and orientacja(math_coords(p0), math_coords(unikalne_katy[-1]), math_coords(p)) == 0:
            unikalne_katy.pop()
        unikalne_katy.append(p)

    if len(unikalne_katy) < 2:
        yield [p0] + unikalne_katy, "Za mało punktów do zbudowania figury."
        return

    stos = [p0, unikalne_katy[0], unikalne_katy[1]]
    yield list(stos), "Dodano pierwsze 3 punkty do otoczki (Stos)"

    for i in range(2, len(unikalne_katy)):
        p_i = unikalne_katy[i]
        while len(stos) > 1 and orientacja(math_coords(stos[-2]), math_coords(stos[-1]), math_coords(p_i)) <= 0:
            yield list(stos) + [p_i], f"Wykryto skręt w prawo! Usuwam punkt ze stosu..."
            stos.pop()
        stos.append(p_i)
        yield list(stos), f"Skręt w lewo prawidłowy. Dodano punkt do otoczki."

    yield list(stos) + [p0], "Algorytm zakończony! Trasa Patrolu Księcia wyznaczona."


class GrahamScene:
    """Wizualizacja Graham Scan z tematycznym tłem pergaminowej mapy."""

    def __init__(self, fonts, images):
        self.fonts = fonts
        self.images = images

    def draw(self, surface, points, history, history_idx):
        """Rysuje aktualny stan algorytmu Grahama."""
        # Tło — pergaminowa mapa
        bg = self.images.get("bg_graham")
        if bg:
            surface.blit(bg, (0, 0))
        else:
            surface.fill(theme.BG_DARK)

        if not history:
            return

        current_data, message = history[history_idx]

        # Rysujemy kopalnie (wszystkie punkty)
        mine_img = self.images.get("kopalnia_sm")
        for p in points:
            if mine_img:
                surface.blit(mine_img, (p[0] - 30, p[1] - 30))
            else:
                pygame.draw.rect(surface, theme.AMBER, (p[0] - 12, p[1] - 12, 24, 24))

        if len(current_data) > 0:
            p0 = current_data[0]

            # Punkt startowy p0 — flaga
            flaga = self.images.get("flaga_p0")
            if flaga:
                surface.blit(flaga, (p0[0] - 20, p0[1] - 40))
            draw_glow_circle(surface, theme.EMERALD, p0, 8)

            if "Posortowano" in message:
                # Linie od p0 do posortowanych punktów
                for idx, p in enumerate(current_data[1:]):
                    pygame.draw.line(surface, theme.FAINT_GRAY, p0, p, 1)
                    txt = self.fonts["small"].render(str(idx + 1), True, theme.CRYSTAL_BLUE)
                    surface.blit(txt, (p[0] + 25, p[1] - 25))
            else:
                # Linie otoczki z glow
                if len(current_data) > 1:
                    for i in range(len(current_data) - 1):
                        draw_glow_line(surface, theme.CRYSTAL_BLUE,
                                       current_data[i], current_data[i + 1], 3, 10)

                # Punkty na otoczce
                for p in current_data:
                    draw_glow_circle(surface, theme.AMBER, p, 6)

                # Podświetlenie przy skręcie w prawo
                if len(current_data) > 1 and "skręt w prawo" in message:
                    draw_glow_line(surface, theme.BLOOD_RED,
                                   current_data[-2], current_data[-1], 3, 12)
                    pygame.draw.circle(surface, theme.BLOOD_RED, current_data[-1], 8, 2)

        # Nagłówek
        step_text = f"Krok {history_idx + 1}/{len(history)}: {message}"
        draw_title_bar(surface, "⚔ Patrol Księcia — Algorytm Grahama", step_text, self.fonts)
