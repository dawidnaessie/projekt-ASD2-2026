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
    """Generator kroków wizualizacji Min-Cost Max-Flow."""
    yield {"step": "init", "przydzialy": []}, "Wyznaczono Źródło (S) i Ujście (T)"
    yield {"step": "source_edges", "przydzialy": []}, "Krawędzie ze Źródła do Krasnoludków (Przepustowość: 1)"
    yield {"step": "mine_edges", "przydzialy": []}, "Krawędzie z Kopalni do Ujścia (Przepustowość: Pojemność)"
    yield {"step": "bipartite", "przydzialy": []}, "Potencjalne drogi do pracy (Koszt = odległość)"

    flow, cost, przydzialy = zbuduj_i_rozwiaz_siec(krasnoludki, kopalnie)

    current_przydzialy = []
    for p in przydzialy:
        current_przydzialy.append(p)
        yield {"step": "flow", "przydzialy": list(current_przydzialy)}, \
              f"Przepływ: {p[0]} → {p[1]} (Koszt: {p[2]})"

    yield {"step": "done", "przydzialy": current_przydzialy}, \
          f"Zakończono! Przydzielono: {flow} krasnali, Koszt: {cost}"


class MCMFScene:
    """Wizualizacja MCMF z tematycznymi sprite'ami krasnali i kopalni."""

    def __init__(self, fonts, images):
        self.fonts = fonts
        self.images = images

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

        # Pozycje kolumnowe
        col_s_x = int(theme.WIDTH * 0.09)
        col_k_x = int(theme.WIDTH * 0.30)
        col_m_x = int(theme.WIDTH * 0.70)
        col_t_x = int(theme.WIDTH * 0.91)

        source_pos = (col_s_x, theme.HEIGHT // 2)
        sink_pos = (col_t_x, theme.HEIGHT // 2)

        # Marginesy uwzględniające panel UI (80px na dole) i title bar (90px na górze)
        margin_top = 100
        margin_bot = 100

        def node_y(idx, total):
            if total <= 1:
                return theme.HEIGHT // 2
            return margin_top + idx * (theme.HEIGHT - margin_top - margin_bot) // (total - 1)

        k_pos = {k_id: (col_k_x, node_y(i, n))
                 for i, (k_id, *_) in enumerate(krasnoludki)}
        m_pos = {m_id: (col_m_x, node_y(j, m))
                 for j, (m_id, *_) in enumerate(kopalnie)}

        # === Krawędzie S -> Krasnoludki ===
        if step in ["source_edges", "mine_edges", "bipartite", "flow", "done"]:
            for k_id, kx, ky, prefs in krasnoludki:
                draw_arrow(surface, source_pos, k_pos[k_id], theme.FAINT_GRAY,
                          1, "1", theme.STEEL, start_rad=28, end_rad=21, fonts=self.fonts)

        # === Krawędzie Kopalnie -> T ===
        if step in ["mine_edges", "bipartite", "flow", "done"]:
            for m_id, mx, my, cap in kopalnie:
                draw_arrow(surface, m_pos[m_id], sink_pos, theme.FAINT_GRAY,
                          1, f"{cap}", theme.STEEL, start_rad=40, end_rad=28, fonts=self.fonts)

        # === Krawędzie K -> M (bipartite) ===
        if step in ["bipartite", "flow", "done"]:
            for k_id, kx, ky, prefs in krasnoludki:
                for m_id, mx, my, cap in kopalnie:
                    draw_arrow(surface, k_pos[k_id], m_pos[m_id], (50, 45, 65),
                              1, "", start_rad=21, end_rad=40, fonts=self.fonts)

        # === Aktywne przydziały (wynik MCMF) ===
        for k_id, m_id, cost in przydzialy:
            if k_id in k_pos and m_id in m_pos:
                draw_arrow(surface, k_pos[k_id], m_pos[m_id], theme.EMERALD,
                          3, f"{cost}", theme.GOLD, start_rad=21, end_rad=40,
                          fonts=self.fonts, glow=True)

        # === Węzły na wierzchu ===
        
        # Źródło S — tron
        tron = self.images.get("tron")
        if tron:
            surface.blit(tron, (source_pos[0] - 28, source_pos[1] - 28))
        else:
            draw_glow_circle(surface, theme.EMERALD_DARK, source_pos, 22)
        ts = self.fonts["subtitle"].render("S", True, theme.EMERALD)
        surface.blit(ts, (source_pos[0] - ts.get_width() // 2, source_pos[1] + 30))

        # Ujście T — wózek z owsianką
        wozek = self.images.get("wozek")
        if wozek:
            surface.blit(wozek, (sink_pos[0] - 28, sink_pos[1] - 28))
        else:
            draw_glow_circle(surface, theme.BLOOD_RED, sink_pos, 22)
        tt = self.fonts["subtitle"].render("T", True, theme.SOFT_RED)
        surface.blit(tt, (sink_pos[0] - tt.get_width() // 2, sink_pos[1] + 30))

        # Krasnoludki — sprite'y
        krasnal_img = self.images.get("krasnal")
        for k_id, kx, ky, prefs in krasnoludki:
            pos = k_pos[k_id]
            if krasnal_img:
                surface.blit(krasnal_img, (pos[0] - 21, pos[1] - 21))
            else:
                draw_glow_circle(surface, theme.NODE_DWARF, pos, 16)
            tk = self.fonts["small"].render(k_id, True, theme.PARCHMENT)
            surface.blit(tk, (pos[0] - tk.get_width() // 2, pos[1] + 23))

        # Kopalnie — sprite'y kopalni
        mine_img = self.images.get("kopalnia_lg")
        for m_id, mx, my, cap in kopalnie:
            pos = m_pos[m_id]
            if mine_img:
                surface.blit(mine_img, (pos[0] - 40, pos[1] - 40))
            else:
                pygame.draw.rect(surface, theme.AMBER, (pos[0] - 16, pos[1] - 16, 32, 32))
            tm = self.fonts["small"].render(f"{m_id} [{cap}]", True, theme.PARCHMENT)
            surface.blit(tm, (pos[0] - tm.get_width() // 2, pos[1] + 42))

        # Nagłówek
        step_text = f"Krok {history_idx + 1}/{len(history)}: {message}"
        draw_title_bar(surface, "⛏ Przydział Krasnoludków — Min-Cost Max-Flow", step_text, self.fonts)
