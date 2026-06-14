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
        btn_w, btn_h = 50, 36
        gap = 10
        by = self.y + 22
        
        return {
            "first":    pygame.Rect(cx - 150, by, btn_w, btn_h),
            "prev":     pygame.Rect(cx - 90, by, btn_w, btn_h),
            "auto":     pygame.Rect(cx - 30, by, 60, btn_h),
            "next":     pygame.Rect(cx + 40, by, btn_w, btn_h),
            "last":     pygame.Rect(cx + 100, by, btn_w, btn_h),
            "menu":     pygame.Rect(20, by, 80, btn_h),
            "reset":    pygame.Rect(110, by, 80, btn_h),
        }
    
    def draw(self, surface, history_idx, history_len, is_auto):
        """Rysuje cały panel sterowania."""
        # Tło panelu (kamienny pasek)
        if self.images.get("pasek_ui"):
            surface.blit(self.images["pasek_ui"], (0, self.y))
        else:
            bar = pygame.Surface((theme.WIDTH, self.HEIGHT), pygame.SRCALPHA)
            bar.fill((30, 25, 40, 220))
            surface.blit(bar, (0, self.y))
        
        # Pasek postępu (na górze panelu)
        if history_len > 0:
            progress = (history_idx + 1) / history_len
            draw_progress_bar(surface, 220, self.y + 6, theme.WIDTH - 440, 10, progress, self.fonts)
        
        # Przyciski
        btn_labels = {
            "first": "⏮",
            "prev":  "◀",
            "auto":  "⏸" if is_auto else "▶",
            "next":  "▶",
            "last":  "⏭",
            "menu":  "Menu",
            "reset": "Reset",
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
        
        # Info krok
        if history_len > 0:
            info_font = self.fonts.get("small", pygame.font.SysFont("arial", 16))
            step_txt = info_font.render(
                f"Krok {history_idx + 1} / {history_len}", True, theme.STEEL
            )
            surface.blit(step_txt, (theme.WIDTH - 180, self.y + 30))
        
        # Skróty klawiszowe
        shortcut_font = self.fonts.get("small", pygame.font.SysFont("arial", 14))
        shortcuts = shortcut_font.render(
            "← → Krok  |  A Auto  |  R Reset  |  ESC Menu", True, theme.FAINT_GRAY
        )
        surface.blit(shortcuts, (theme.WIDTH // 2 - shortcuts.get_width() // 2, self.y + 62))
    
    def handle_click(self, pos):
        """Sprawdza czy kliknięto w przycisk. Zwraca nazwę przycisku lub None."""
        for name, rect in self.buttons.items():
            if rect.collidepoint(pos):
                return name
        return None
