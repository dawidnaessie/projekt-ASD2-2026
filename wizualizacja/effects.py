"""
effects.py — Efekty wizualne: glow, strzałki, particles.
"""
import pygame
import math
from wizualizacja import theme


def draw_glow_line(surface, color, start, end, width=3, glow_radius=8):
    """
    Rysuje linię ze świecącym efektem (glow).
    Najpierw gruba rozmyta linia (na osobnym surface z alpha),
    potem cienka ostra linia na wierzchu.
    """
    # Glow — gruba linia z alpha
    glow_surf = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
    glow_color = (*color[:3], 40)
    pygame.draw.line(glow_surf, glow_color, start, end, glow_radius)
    surface.blit(glow_surf, (0, 0))

    # Druga warstwa glow
    glow_surf2 = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
    glow_color2 = (*color[:3], 80)
    pygame.draw.line(glow_surf2, glow_color2, start, end, width + 2)
    surface.blit(glow_surf2, (0, 0))

    # Ostra linia na wierzchu
    pygame.draw.line(surface, color, start, end, width)


def draw_glow_circle(surface, color, center, radius, glow_radius=None):
    """
    Rysuje kółko ze świecącym efektem.
    """
    if glow_radius is None:
        glow_radius = radius + 6

    glow_surf = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
    glow_color = (*color[:3], 30)
    pygame.draw.circle(glow_surf, glow_color, center, glow_radius)
    surface.blit(glow_surf, (0, 0))

    glow_surf2 = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
    glow_color2 = (*color[:3], 60)
    pygame.draw.circle(glow_surf2, glow_color2, center, radius + 3)
    surface.blit(glow_surf2, (0, 0))

    pygame.draw.circle(surface, color, center, radius)


def draw_arrow(surface, start, end, color, width=2, label="",
               label_color=None, start_rad=16, end_rad=16, fonts=None, glow=False):
    """
    Rysuje strzałkę z grotem i opcjonalną etykietą.
    Wersja ulepszona z obsługą glow.
    """
    if label_color is None:
        label_color = theme.GOLD
    if fonts is None:
        fonts = {}

    dx = end[0] - start[0]
    dy = end[1] - start[1]
    dist = max(1, math.hypot(dx, dy))
    ux, uy = dx / dist, dy / dist
    px, py = -uy, ux

    # Skróć linię o promień węzłów
    tip = (int(end[0] - ux * end_rad), int(end[1] - uy * end_rad))
    start2 = (int(start[0] + ux * start_rad), int(start[1] + uy * start_rad))

    if glow:
        draw_glow_line(surface, color, start2, tip, width)
    else:
        pygame.draw.line(surface, color, start2, tip, width)

    # Grot strzałki
    ar = 10
    b = (tip[0] - int(ux * ar), tip[1] - int(uy * ar))
    p1 = (b[0] + int(px * ar * 0.5), b[1] + int(py * ar * 0.5))
    p2 = (b[0] - int(px * ar * 0.5), b[1] - int(py * ar * 0.5))
    pygame.draw.polygon(surface, color, [tip, p1, p2])

    # Etykieta nad środkiem
    if label:
        font = fonts.get("small", pygame.font.SysFont("arial", 16))
        mx2 = (start[0] + end[0]) // 2
        my2 = (start[1] + end[1]) // 2
        off = 14
        lbl = font.render(label, True, label_color)
        surface.blit(lbl, (mx2 - lbl.get_width() // 2 + int(px * off),
                           my2 - lbl.get_height() - 4 + int(py * off)))


def draw_progress_bar(surface, x, y, width, height, progress, fonts=None):
    """
    Rysuje kamienny pasek postępu.
    progress: float 0.0 - 1.0
    """
    # Tło paska
    bg_rect = pygame.Rect(x, y, width, height)
    pygame.draw.rect(surface, (40, 35, 50), bg_rect, border_radius=4)
    pygame.draw.rect(surface, theme.STONE_GRAY, bg_rect, 1, border_radius=4)

    # Wypełnienie
    if progress > 0:
        fill_w = max(2, int((width - 4) * progress))
        fill_rect = pygame.Rect(x + 2, y + 2, fill_w, height - 4)
        # Gradient: od bursztynu do szmaragdu
        r = int(theme.AMBER[0] + (theme.EMERALD[0] - theme.AMBER[0]) * progress)
        g = int(theme.AMBER[1] + (theme.EMERALD[1] - theme.AMBER[1]) * progress)
        b = int(theme.AMBER[2] + (theme.EMERALD[2] - theme.AMBER[2]) * progress)
        pygame.draw.rect(surface, (r, g, b), fill_rect, border_radius=3)


def draw_title_bar(surface, title, step_text, fonts, bg_image=None):
    """
    Rysuje nagłówek sceny z tytułem i opisem kroku.
    Ciemny półprzezroczysty pasek na górze ekranu.
    """
    # Półprzezroczysty pasek
    bar_surf = pygame.Surface((theme.WIDTH, 90), pygame.SRCALPHA)
    bar_surf.fill((15, 12, 22, 180))
    surface.blit(bar_surf, (0, 0))

    # Tytuł
    title_font = fonts.get("title", fonts.get("body"))
    title_surf = title_font.render(title, True, theme.GOLD)
    surface.blit(title_surf, (20, 12))

    # Opis kroku
    if step_text:
        body_font = fonts.get("body", fonts.get("small"))
        step_surf = body_font.render(step_text, True, theme.PARCHMENT)
        surface.blit(step_surf, (20, 54))
