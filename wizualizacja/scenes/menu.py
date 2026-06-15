"""
scenes/menu.py — Ekran menu głównego.
"""
import pygame
from wizualizacja import theme


class MenuScene:
    """Ekran startowy z tłem kopalni i trzema przyciskami algorytmów."""

    def __init__(self, fonts, images):
        self.fonts = fonts
        self.images = images

        # Obszary przycisków dopasowane do grafiki tła (x1, y1, szerokość, wysokość)
        self.btn_graham = pygame.Rect(131, 740, 342, 120)
        self.btn_mcmf   = pygame.Rect(551, 740, 342, 120)
        self.btn_dek    = pygame.Rect(970, 740, 342, 120)

    def draw(self, surface, num_k, num_m, num_dek=0, show_feedback=False):
        """Rysuje ekran menu."""
        # Tło
        bg = self.images.get("bg_menu")
        if bg:
            surface.blit(bg, (0, 0))
        else:
            surface.fill(theme.BG_DARK)
            title_font = self.fonts.get("title")
            title = title_font.render("Wizualizacja Algorytmow — Krasnoludki 2026", True, theme.GOLD)
            surface.blit(title, (theme.WIDTH // 2 - title.get_width() // 2, 80))

        # Wskaźniki na kamiennej tablicy
        base_y = int(theme.HEIGHT * 0.25) + 7
        tab_font = self.fonts.get("menu_tab")
        step = 22

        kras_txt = tab_font.render(f"KRASNOLUDKI: {num_k} (E/D)", True, theme.DARK_TEXT)
        surface.blit(kras_txt, (theme.WIDTH // 2 - kras_txt.get_width() // 2, base_y))

        kop_txt = tab_font.render(f"KOPALNIE: {num_m} (W/S)", True, theme.DARK_TEXT)
        surface.blit(kop_txt, (theme.WIDTH // 2 - kop_txt.get_width() // 2, base_y + step))

        dek_txt = tab_font.render(f"DEKAMETROWCY: {num_dek} (Q/A)", True, theme.DARK_TEXT)
        surface.blit(dek_txt, (theme.WIDTH // 2 - dek_txt.get_width() // 2, base_y + step * 2))

        opt_r = tab_font.render("R — PRZELOSUJ", True, theme.DARK_TEXT)
        surface.blit(opt_r, (theme.WIDTH // 2 - opt_r.get_width() // 2, base_y + step * 3))

        # Hover na przyciskach — subtelne podświetlenie
        mouse = pygame.mouse.get_pos()
        for btn_rect in [self.btn_graham, self.btn_mcmf, self.btn_dek]:
            if btn_rect.collidepoint(mouse):
                hover_surf = pygame.Surface((btn_rect.width, btn_rect.height), pygame.SRCALPHA)
                hover_surf.fill((255, 200, 50, 35))
                surface.blit(hover_surf, btn_rect.topleft)

        # Fallback — jeśli brak tła, rysuj tekstowe przyciski
        if not bg:
            btn_font = self.fonts.get("subtitle")
            labels = [
                (self.btn_graham, "1 — Patrol Ksiecia (Graham)"),
                (self.btn_mcmf,   "2 — Przydzial Krasnoludkow (MCMF)"),
                (self.btn_dek,    "3 — Dekametrowcy (Segment Tree)"),
            ]
            for rect, label in labels:
                pygame.draw.rect(surface, theme.STONE_GRAY, rect, 2, border_radius=8)
                txt = btn_font.render(label, True, theme.PARCHMENT)
                surface.blit(txt, (rect.centerx - txt.get_width() // 2,
                                   rect.centery - txt.get_height() // 2))

    def handle_click(self, pos):
        """Zwraca tryb algorytmu na podstawie kliknięcia lub None."""
        if self.btn_graham.collidepoint(pos):
            return "GRAHAM"
        elif self.btn_mcmf.collidepoint(pos):
            return "MCMF"
        elif self.btn_dek.collidepoint(pos):
            return "DEKAMETROWCY"
        return None
