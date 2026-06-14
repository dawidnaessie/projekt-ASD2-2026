"""
scenes/dekametrowcy.py — Wizualizacja Drzewa Przedziałowego (Segment Tree RMQ).
"""
import pygame
import math
from wizualizacja import theme
from wizualizacja.effects import draw_glow_line, draw_glow_circle, draw_title_bar

# Import logiki algorytmu
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from src.dekametrowcy import uruchom_modul as dekametrowcy_rmq, _wczytaj_glosnosci, SegmentTreeRMQ


def dekametrowcy_generator(glosnosci, zapytania):
    """Generator krokow wizualizacji Segment Tree RMQ."""
    n = len(glosnosci)
    yield {"phase": "data", "ql": -1, "qr": -1, "max_idx": -1, "active": []}, \
          "Tablica glosnosci dekametrowcow"
    yield {"phase": "tree", "ql": -1, "qr": -1, "max_idx": -1, "active": []}, \
          "Budowanie Drzewa Przedzialowego (Segment Tree)"

    wyniki = dekametrowcy_rmq(glosnosci, zapytania)
    for (ql, qr), (bs, be, max_val) in zip(zapytania, wyniki):
        active = list(range(bs, be + 1))
        max_idx = -1
        for idx in range(bs, be + 1):
            if idx < len(glosnosci) and glosnosci[idx] == max_val:
                max_idx = idx
                break
        yield {"phase": "query", "ql": bs, "qr": be, "max_idx": max_idx, "active": active}, \
              f"Zapytanie [{bs}..{be}]: maks. glosnosc = {max_val} dB"

    yield {"phase": "done", "ql": -1, "qr": -1, "max_idx": -1, "active": []}, \
          "Zakonczono wszystkie zapytania RMQ!"


class DekametrowcyScene:
    """Wizualizacja Segment Tree z pełnym drzewem binarnym i kryształowymi słupkami."""

    def __init__(self, fonts, images):
        self.fonts = fonts
        self.images = images
        self.font_cache = {}

    def get_font_of_size(self, size, bold=True):
        if (size, bold) not in self.font_cache:
            f = pygame.font.Font(None, size)
            f.set_bold(bold)
            self.font_cache[(size, bold)] = f
        return self.font_cache[(size, bold)]

    def _draw_segment_tree(self, surface, rmq, n, ql, qr, active_nodes=None):
        """Rysuje pełne drzewo Segment Tree w górnej części ekranu."""
        if n == 0:
            return

        # Obliczamy głębokość drzewa
        depth = max(1, math.ceil(math.log2(n)) + 1)

        # Obszar rysowania drzewa
        tree_top = 95
        tree_bottom = theme.HEIGHT // 2 - 20
        tree_left = 100
        tree_right = theme.WIDTH - 100
        level_h = (tree_bottom - tree_top) / depth

        # Rekurencyjne rysowanie węzłów
        def draw_node(v, l, r, cx, cy, span):
            if v >= len(rmq.drzewo) or l > r:
                return

            val = rmq.drzewo[v]
            if val == float('-inf'):
                return

            # Sprawdzamy czy węzeł jest aktywny (w zakresie zapytania)
            is_active = (ql >= 0 and qr >= 0 and not (r < ql or qr < l))
            is_full_match = (ql >= 0 and qr >= 0 and ql <= l and r <= qr)

            # Rysuj krawędzie do dzieci
            if l < r:
                mid = (l + r) // 2
                child_span = span / 2
                left_cx = cx - child_span
                right_cx = cx + child_span
                child_cy = cy + level_h

                if 2 * v < len(rmq.drzewo):
                    edge_color = theme.CRYSTAL_CYAN if is_active else (50, 50, 70)
                    pygame.draw.line(surface, edge_color, (int(cx), int(cy)),
                                    (int(left_cx), int(child_cy)), 1)
                    draw_node(2 * v, l, mid, left_cx, child_cy, child_span)
                if 2 * v + 1 < len(rmq.drzewo):
                    edge_color = theme.CRYSTAL_CYAN if is_active else (50, 50, 70)
                    pygame.draw.line(surface, edge_color, (int(cx), int(cy)),
                                    (int(right_cx), int(child_cy)), 1)
                    draw_node(2 * v + 1, mid + 1, r, right_cx, child_cy, child_span)

            # Rysuj węzeł
            radius = 24
            cx_i, cy_i = int(cx), int(cy)

            if is_full_match:
                draw_glow_circle(surface, theme.AMBER, (cx_i, cy_i), radius)
            elif is_active:
                draw_glow_circle(surface, theme.CRYSTAL_CYAN, (cx_i, cy_i), radius - 2)
            else:
                pygame.draw.circle(surface, (50, 50, 70), (cx_i, cy_i), radius)
                pygame.draw.circle(surface, theme.STONE_GRAY, (cx_i, cy_i), radius, 1)

            # Wartość w węźle
            val_str = str(int(val))
            node_font_size = 20
            node_font = self.get_font_of_size(node_font_size, bold=True)
            text_color = theme.BG_DARKER if (is_full_match or is_active) else theme.PARCHMENT
            val_surf = node_font.render(val_str, True, text_color)
            surface.blit(val_surf, (cx_i - val_surf.get_width() // 2,
                                    cy_i - val_surf.get_height() // 2))

        # Punkt startowy drzewa
        center_x = (tree_left + tree_right) / 2
        initial_span = (tree_right - tree_left) / 4
        draw_node(1, 0, n - 1, center_x, tree_top + 20, initial_span)

    def draw(self, surface, glosnosci, history, history_idx):
        """Rysuje aktualny stan wizualizacji Dekametrowców."""
        # Tło — kryształowa jaskinia
        bg = self.images.get("bg_dekametrowcy")
        if bg:
            surface.blit(bg, (0, 0))
        else:
            surface.fill(theme.BG_DARK)

        if not history or not glosnosci:
            return

        current_state, message = history[history_idx]
        phase = current_state["phase"]
        ql = current_state["ql"]
        qr = current_state["qr"]
        max_idx = current_state["max_idx"]
        active = current_state["active"]

        n_bars = len(glosnosci)
        if n_bars == 0:
            return

        # === Drzewo Segment Tree (górna połowa) ===
        if phase in ("tree", "query", "done") and glosnosci:
            rmq = SegmentTreeRMQ(glosnosci)
            self._draw_segment_tree(surface, rmq, n_bars, ql, qr)

        # === Słupki (dolna połowa) ===
        margin_x = 100
        margin_top_bars = theme.HEIGHT // 2 + 10
        margin_bot = theme.HEIGHT - 120  # Miejsce na panel UI
        bar_area_w = theme.WIDTH - 2 * margin_x
        bar_w = max(20, bar_area_w // n_bars - 6)
        spacing = (bar_area_w - bar_w * n_bars) // (n_bars + 1)
        max_h = margin_bot - margin_top_bars - 30
        max_val_all = max(glosnosci) if glosnosci else 1

        for i, val in enumerate(glosnosci):
            bx = margin_x + spacing + i * (bar_w + spacing)
            bh = int(val / max_val_all * max_h)
            by = margin_bot - bh

            # Kolor słupka
            if i == max_idx and phase in ("query", "done"):
                # Najgłośniejszy — czerwony z glow
                col_top = theme.BLOOD_RED
                col_bot = (140, 30, 40)
            elif i in active and phase == "query":
                # Aktywny zakres — złoty
                col_top = theme.GOLD
                col_bot = (140, 110, 30)
            else:
                # Normalny — kryształowy gradient
                col_top = theme.CRYSTAL_BLUE
                col_bot = (40, 80, 140)

            # Gradient słupka (rysujemy linia po linii)
            for row in range(bh):
                t = row / max(1, bh)
                r = int(col_top[0] * (1 - t) + col_bot[0] * t)
                g = int(col_top[1] * (1 - t) + col_bot[1] * t)
                b = int(col_top[2] * (1 - t) + col_bot[2] * t)
                pygame.draw.line(surface, (r, g, b), (bx, by + row), (bx + bar_w, by + row))

            # Ramka słupka
            pygame.draw.rect(surface, theme.STONE_GRAY, (bx, by, bar_w, bh), 1, border_radius=2)

            # Wartość nad słupkiem
            val_txt = self.fonts["small"].render(str(val), True, theme.PARCHMENT)
            surface.blit(val_txt, (bx + bar_w // 2 - val_txt.get_width() // 2, by - 20))

            # Indeks pod słupkiem
            idx_txt = self.fonts["small"].render(f"D{i + 1}", True, theme.STEEL)
            surface.blit(idx_txt, (bx + bar_w // 2 - idx_txt.get_width() // 2, margin_bot + 4))

        # Podświetlenie przedziału zapytania
        if phase == "query" and ql >= 0 and qr >= 0:
            bx_l = margin_x + spacing + ql * (bar_w + spacing) - 4
            bx_r = margin_x + spacing + qr * (bar_w + spacing) + bar_w + 4
            # Glow ramka
            glow_h = margin_bot - margin_top_bars + 30
            glow_surf = pygame.Surface((bx_r - bx_l, glow_h), pygame.SRCALPHA)
            glow_surf.fill((255, 200, 50, 20))
            surface.blit(glow_surf, (bx_l, margin_top_bars))
            pygame.draw.rect(surface, theme.GOLD,
                           (bx_l, margin_top_bars, bx_r - bx_l, glow_h),
                           2, border_radius=6)

        # Naglowek
        step_text = f"Krok {history_idx + 1}/{len(history)}: {message}"
        draw_title_bar(surface, "Dekametrowcy — Segment Tree RMQ", step_text, self.fonts)
