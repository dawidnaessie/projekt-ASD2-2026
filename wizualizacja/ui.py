"""
ui.py — Komponenty interfejsu użytkownika: panel sterowania, przyciski.
"""
import pygame
from wizualizacja import theme
from wizualizacja.effects import draw_progress_bar


class ControlPanel:
    """
    Kamienny panel sterowania na dole ekranu z przyciskami nawigacji,
    paskiem postępu i informacjami.
    """
    HEIGHT = 80
    
    def __init__(self, fonts, images):
        self.fonts = fonts
        self.images = images
        self.y = theme.HEIGHT - self.HEIGHT
        self.buttons = self._create_buttons()
    
    def _create_buttons(self):
        """Tworzy prostokąty przycisków w panelu."""
        cx = theme.WIDTH // 2
        btn_w, btn_h = 40, 30
        by = self.y + 18
        
        return {
            "first":    pygame.Rect(cx - 125, by, btn_w, btn_h),
            "prev":     pygame.Rect(cx - 75, by, btn_w, btn_h),
            "auto":     pygame.Rect(cx - 25, by, 50, btn_h),
            "next":     pygame.Rect(cx + 35, by, btn_w, btn_h),
            "last":     pygame.Rect(cx + 85, by, btn_w, btn_h),
        }
    
    def draw(self, surface, history_idx, history_len, is_auto):
        """Rysuje cały panel sterowania."""
        # Tło panelu (kamienny pasek)
        if self.images.get("pasek_ui"):
            surface.blit(self.images["pasek_ui"], (0, self.y - 6))
        else:
            bar = pygame.Surface((theme.WIDTH, self.HEIGHT), pygame.SRCALPHA)
            bar.fill((30, 25, 40, 220))
            surface.blit(bar, (0, self.y))
        
        # Pasek postępu (na górze panelu)
        if history_len > 0:
            progress = (history_idx + 1) / history_len
            draw_progress_bar(surface, 220, self.y + 4, theme.WIDTH - 440, 8, progress, self.fonts)
        
        # Przyciski
        btn_labels = {
            "first": "|<",
            "prev":  "<",
            "auto":  "||" if is_auto else ">",
            "next":  ">",
            "last":  ">|",
        }
        
        btn_font = self.fonts.get("ui_btn", pygame.font.SysFont("arial", 16, bold=True))
        
        for name, rect in self.buttons.items():
            # Tło przycisku
            hover = rect.collidepoint(pygame.mouse.get_pos())
            bg_color = (80, 70, 100) if hover else (50, 45, 65)
            border_color = theme.GOLD if hover else theme.STONE_GRAY
            
            pygame.draw.rect(surface, bg_color, rect, border_radius=6)
            pygame.draw.rect(surface, border_color, rect, 1, border_radius=6)
            
            # Tekst
            label = btn_labels.get(name, "")
            color = theme.GOLD if name == "auto" and is_auto else theme.PARCHMENT
            txt = btn_font.render(label, True, color)
            surface.blit(txt, (rect.centerx - txt.get_width() // 2,
                              rect.centery - txt.get_height() // 2))
        
        # Skróty klawiszowe (rozmiar 14 regular w Georgia)
        shortcut_font = pygame.font.SysFont("georgia", 14)
        shortcuts = shortcut_font.render(
            "<- -> Krok  |  A Auto  |  R Reset  |  ESC Menu", True, theme.FAINT_GRAY
        )
        surface.blit(shortcuts, (theme.WIDTH // 2 - shortcuts.get_width() // 2, self.y + 54))
    
    def handle_click(self, pos):
        """Sprawdza czy kliknięto w przycisk. Zwraca nazwę przycisku lub None."""
        for name, rect in self.buttons.items():
            if rect.collidepoint(pos):
                return name
        return None
