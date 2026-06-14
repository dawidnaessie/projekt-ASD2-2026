"""
scenes/mcmf.py — Wizualizacja algorytmu Min-Cost Max-Flow (Przydział Krasnoludków).
"""
import pygame
from wizualizacja import theme
from wizualizacja.effects import draw_arrow, draw_glow_circle, draw_title_bar

# Import logiki algorytmu
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from src.przydzial_krasnoludkow import zbuduj_i_rozwiaz_siec


def mcmf_generator(krasnoludki, kopalnie):
    """Generator krokow wizualizacji Min-Cost Max-Flow."""
    yield {"step": "init", "przydzialy": []}, "Wyznaczono Zrodlo (S) i Ujscie (T)"
    yield {"step": "source_edges", "przydzialy": []}, "Krawedzie ze Zrodla do Krasnoludkow (Przepustowosc: 1)"
    yield {"step": "mine_edges", "przydzialy": []}, "Krawedzie z Kopalni do Ujscia (Przepustowosc: Pojemnosc)"
    yield {"step": "bipartite", "przydzialy": []}, "Potencjalne drogi do pracy (Koszt = odleglosc)"

    flow, cost, przydzialy = zbuduj_i_rozwiaz_siec(krasnoludki, kopalnie)

    current_przydzialy = []
    for p in przydzialy:
        current_przydzialy.append(p)
        yield {"step": "flow", "przydzialy": list(current_przydzialy)}, \
              f"Przeplyw: {p[0]} -> {p[1]} (Koszt: {p[2]})"

    yield {"step": "done", "przydzialy": current_przydzialy}, \
          f"Zakonczono! Przydzielono: {flow} krasnali, Koszt: {cost}"


class MCMFScene:
    """Wizualizacja MCMF z tematycznymi sprite'ami krasnali i kopalni."""

    def __init__(self, fonts, images):
        self.fonts = fonts
        self.images = images
        self.font_cache = {}

    def get_font_of_size(self, size, bold=True):
        if (size, bold) not in self.font_cache:
            # Uzywamy domyslnego fontu Pygame (None), ktory gwarantuje poprawne skalowanie rozmiaru
            f = pygame.font.Font(None, size)
            f.set_bold(bold)
            self.font_cache[(size, bold)] = f
        return self.font_cache[(size, bold)]

    def draw(self, surface, krasnoludki, kopalnie, history, history_idx):
        """Rysuje aktualny stan algorytmu MCMF."""
        # Tło — ciemna kopalnia
        bg = self.images.get("bg_mcmf")
        if bg:
            surface.blit(bg, (0, 0))
        else:
            surface.fill(theme.BG_DARK)

        if not history:
            return

        current_state, message = history[history_idx]
        step = current_state["step"]
        przydzialy = current_state["przydzialy"]

        n = len(krasnoludki)
        m = len(kopalnie)

        # Dynamiczne skalowanie rozmiarów
        # Krasnoludki (n): od 65px (n <= 10) do 18px (n >= 50)
        dwarf_size = max(18, min(65, int(65 - (n - 10) * (47 / 40)))) if n > 10 else 65
        dwarf_rad = dwarf_size // 2
        dwarf_font_size = max(8, min(18, int(8 + (dwarf_size - 18) * (10 / 47))))
        dwarf_font = self.get_font_of_size(dwarf_font_size, bold=True)

        # Kopalnie (m): od 65px (m <= 5) do 24px (m >= 20)
        mine_size = max(24, min(65, int(65 - (m - 5) * (41 / 15)))) if m > 5 else 65
        mine_rad = mine_size // 2
        mine_font_size = max(9, min(18, int(9 + (mine_size - 24) * (9 / 41))))
        mine_font = self.get_font_of_size(mine_font_size, bold=True)

        # Pozycje kolumnowe
        col_s_x = int(theme.WIDTH * 0.09)
        col_k_x = int(theme.WIDTH * 0.30)
        col_m_x = int(theme.WIDTH * 0.70)
        col_t_x = int(theme.WIDTH * 0.91)

        source_pos = (col_s_x, theme.HEIGHT // 2)
        sink_pos = (col_t_x, theme.HEIGHT // 2)

        # Dynamiczne wyliczenie marginesów tak, aby zmieścić się dokładnie w przedziale Y: [95, 820]
        k_margin_top = 95 + dwarf_rad
        k_margin_bot = 820 - dwarf_rad

        m_margin_top = 95 + mine_rad
        m_margin_bot = 820 - mine_rad

        def k_node_y(idx, total):
            if total <= 1:
                return (k_margin_top + k_margin_bot) // 2
            return k_margin_top + idx * (k_margin_bot - k_margin_top) // (total - 1)

        def m_node_y(idx, total):
            if total <= 1:
                return (m_margin_top + m_margin_bot) // 2
            return m_margin_top + idx * (m_margin_bot - m_margin_top) // (total - 1)

        k_pos = {k_id: (col_k_x, k_node_y(i, n))
                 for i, (k_id, *_) in enumerate(krasnoludki)}
        m_pos = {m_id: (col_m_x, m_node_y(j, m))
                 for j, (m_id, *_) in enumerate(kopalnie)}

        # === Krawędzie S -> Krasnoludki ===
        if step in ["source_edges", "mine_edges", "bipartite", "flow", "done"]:
            for k_id, kx, ky, prefs in krasnoludki:
                draw_arrow(surface, source_pos, k_pos[k_id], theme.FAINT_GRAY,
                          1, "1", theme.STEEL, start_rad=55, end_rad=dwarf_rad, fonts=self.fonts)

        # === Krawędzie Kopalnie -> T ===
        if step in ["mine_edges", "bipartite", "flow", "done"]:
            for m_id, mx, my, cap in kopalnie:
                draw_arrow(surface, m_pos[m_id], sink_pos, theme.FAINT_GRAY,
                          1, f"{cap}", theme.STEEL, start_rad=mine_rad, end_rad=55, fonts=self.fonts)

        # === Krawędzie K -> M (bipartite) ===
        if step in ["bipartite", "flow", "done"]:
            for k_id, kx, ky, prefs in krasnoludki:
                for m_id, mx, my, cap in kopalnie:
                    draw_arrow(surface, k_pos[k_id], m_pos[m_id], (50, 45, 65),
                               1, "", start_rad=dwarf_rad, end_rad=mine_rad, fonts=self.fonts)

        # === Aktywne przydziały (wynik MCMF) ===
        for k_id, m_id, cost in przydzialy:
            if k_id in k_pos and m_id in m_pos:
                draw_arrow(surface, k_pos[k_id], m_pos[m_id], theme.EMERALD,
                          3, f"{cost}", theme.GOLD, start_rad=dwarf_rad, end_rad=mine_rad,
                          fonts=self.fonts, glow=True)

        # === Węzły na wierzchu ===
        
        # Źródło S — tron (rozmiar 110x110, przesunięcie 55)
        tron = self.images.get("tron")
        if tron:
            surface.blit(tron, (source_pos[0] - 55, source_pos[1] - 55))
        else:
            draw_glow_circle(surface, theme.EMERALD_DARK, source_pos, 22)
        ts = self.fonts["subtitle"].render("S", True, theme.EMERALD)
        surface.blit(ts, (source_pos[0] - ts.get_width() // 2, source_pos[1] + 60))

        # Ujście T — wózek z owsianką (rozmiar 110x110, przesunięcie 55)
        wozek = self.images.get("wozek")
        if wozek:
            surface.blit(wozek, (sink_pos[0] - 55, sink_pos[1] - 55))
        else:
            draw_glow_circle(surface, theme.BLOOD_RED, sink_pos, 22)
        tt = self.fonts["subtitle"].render("T", True, theme.SOFT_RED)
        surface.blit(tt, (sink_pos[0] - tt.get_width() // 2, sink_pos[1] + 60))

        # Krasnoludki — sprite'y (skalowane)
        krasnal_img = self.images.get("krasnal")
        if krasnal_img:
            krasnal_scaled = pygame.transform.smoothscale(krasnal_img, (dwarf_size, dwarf_size))
        else:
            krasnal_scaled = None

        for k_id, kx, ky, prefs in krasnoludki:
            pos = k_pos[k_id]
            if krasnal_scaled:
                surface.blit(krasnal_scaled, (pos[0] - dwarf_rad, pos[1] - dwarf_rad))
            else:
                draw_glow_circle(surface, theme.NODE_DWARF, pos, dwarf_rad)

        # Kopalnie — sprite'y kopalni (skalowane)
        mine_img = self.images.get("kopalnia_lg")
        if mine_img:
            mine_scaled = pygame.transform.smoothscale(mine_img, (mine_size, mine_size))
        else:
            mine_scaled = None

        for m_id, mx, my, cap in kopalnie:
            pos = m_pos[m_id]
            if mine_scaled:
                surface.blit(mine_scaled, (pos[0] - mine_rad, pos[1] - mine_rad))
            else:
                pygame.draw.rect(surface, theme.AMBER, (pos[0] - mine_rad, pos[1] - mine_rad, mine_size, mine_size))

        # Rysowanie podpisów (w osobnym kroku, po lewej dla krasnali, po prawej dla kopalń)
        for k_id, kx, ky, prefs in krasnoludki:
            pos = k_pos[k_id]
            tk = dwarf_font.render(k_id, True, theme.PARCHMENT)
            surface.blit(tk, (pos[0] - dwarf_rad - tk.get_width() - 8, pos[1] - tk.get_height() // 2))

        for m_id, mx, my, cap in kopalnie:
            pos = m_pos[m_id]
            tm = mine_font.render(f"{m_id} [{cap}]", True, theme.PARCHMENT)
            surface.blit(tm, (pos[0] + mine_rad + 8, pos[1] - tm.get_height() // 2))

        # Naglowek
        step_text = f"Krok {history_idx + 1}/{len(history)}: {message}"
        draw_title_bar(surface, "Przydzial Krasnoludkow — Min-Cost Max-Flow", step_text, self.fonts)
