"""
app.py — Główna pętla aplikacji Pygame. Router trybów, obsługa zdarzeń.
"""
import pygame
import random
import os
import sys

# Dodajemy ścieżkę projektu do sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from wizualizacja import theme
from wizualizacja.ui import ControlPanel
from wizualizacja.scenes.menu import MenuScene
from wizualizacja.scenes.graham import GrahamScene, graham_scan_generator
from wizualizacja.scenes.mcmf import MCMFScene, mcmf_generator
from wizualizacja.scenes.dekametrowcy import DekametrowcyScene, dekametrowcy_generator
from src.dekametrowcy import _wczytaj_glosnosci


def generate_point_in_map(padding_x=45, padding_y=45):
    """Generuje losowy punkt wewnątrz pergaminowej mapy (trapezu)."""
    # Wierzchołki pergaminowej mapy:
    # A = (264, 345) [lewy górny], B = (1197, 345) [prawy górny]
    # C = (1375, 761) [prawy dolny], D = (73, 754) [lewy dolny]
    y = random.randint(345 + padding_y, 754 - padding_y)
    t = (y - 345) / (754 - 345)
    # Liniowa interpolacja lewej i prawej krawędzi dla danej wysokości Y
    left_x = int(264 + t * (73 - 264))
    right_x = int(1197 + t * (1375 - 1197))
    x = random.randint(left_x + padding_x, right_x - padding_x)
    return x, y


def generate_krasnoludki_kopalnie(num_k, num_m):
    """Generuje losowe krasnoludki i kopalnie na całym ekranie."""
    padding = 80
    W, H = theme.WIDTH, theme.HEIGHT
    krasnoludki = [
        (f"K{i}", random.randint(padding, W - padding),
         random.randint(padding, H - padding), ["ALL"])
        for i in range(1, num_k + 1)
    ]
    kopalnie = [
        (f"M{i}", random.randint(padding, W - padding),
         random.randint(padding, H - padding), random.randint(1, 4))
        for i in range(1, num_m + 1)
    ]
    return krasnoludki, kopalnie


def main():
    """Główna pętla wizualizacji."""
    pygame.init()

    screen = pygame.display.set_mode((theme.WIDTH, theme.HEIGHT))
    pygame.display.set_caption("Wizualizacja Algorytmow — Krasnoludki 2026")

    # Ładowanie zasobów
    fonts = theme.load_fonts()
    images = theme.load_images()

    # Ikona aplikacji
    if images.get("app_icon"):
        pygame.display.set_icon(images["app_icon"])

    # Inicjalizacja scen
    menu_scene = MenuScene(fonts, images)
    graham_scene = GrahamScene(fonts, images)
    mcmf_scene = MCMFScene(fonts, images)
    dek_scene = DekametrowcyScene(fonts, images)
    control_panel = ControlPanel(fonts, images)

    # Stan aplikacji
    clock = pygame.time.Clock()
    mode = "MENU"

    num_k = 15
    num_m = 5
    shared_krasnoludki, shared_kopalnie = generate_krasnoludki_kopalnie(num_k, num_m)

    points = []
    krasnoludki = []
    kopalnie = []
    dek_glosnosci = []
    dek_zapytania = []

    history = []
    history_idx = 0
    is_auto = False
    finished = False

    last_update = pygame.time.get_ticks()
    update_delay = 500
    last_regen_time = 0

    def setup_graham():
        nonlocal points, history, history_idx, is_auto, finished
        new_points = []
        min_dist = 75  # Minimum distance to prevent mines from overlapping
        for _ in range(num_m):
            for _ in range(100):
                candidate = generate_point_in_map()
                too_close = False
                for p in new_points:
                    dx = candidate[0] - p[0]
                    dy = candidate[1] - p[1]
                    if (dx * dx + dy * dy) < (min_dist * min_dist):
                        too_close = True
                        break
                if not too_close:
                    new_points.append(candidate)
                    break
            else:
                new_points.append(generate_point_in_map())
        points = new_points
        history = list(graham_scan_generator(points))
        if not history:
            history = [([], "")]
        history_idx = 0
        is_auto = False
        finished = False

    def setup_mcmf():
        nonlocal krasnoludki, kopalnie, history, history_idx, is_auto, finished
        krasnoludki = shared_krasnoludki
        kopalnie = shared_kopalnie
        history = list(mcmf_generator(krasnoludki, kopalnie))
        if not history:
            history = [({"step": "init", "przydzialy": []}, "")]
        history_idx = 0
        is_auto = False
        finished = False

    def setup_dek():
        nonlocal dek_glosnosci, dek_zapytania, history, history_idx, is_auto, finished
        dek_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                'data', 'dekametrowcy.txt')
        dek_glosnosci = _wczytaj_glosnosci(dek_path)
        n_dek = len(dek_glosnosci)
        dek_zapytania = [(0, n_dek // 3), (n_dek // 3, 2 * n_dek // 3), (2 * n_dek // 3, n_dek - 1)]
        history = list(dekametrowcy_generator(dek_glosnosci, dek_zapytania))
        history_idx = 0
        is_auto = False
        finished = False

    def regenerate_data():
        nonlocal shared_krasnoludki, shared_kopalnie, last_regen_time
        shared_krasnoludki, shared_kopalnie = generate_krasnoludki_kopalnie(num_k, num_m)
        last_regen_time = pygame.time.get_ticks()

    # === GŁÓWNA PĘTLA ===
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if mode == "MENU":
                    result = menu_scene.handle_click(event.pos)
                    if result == "GRAHAM":
                        mode = "GRAHAM"
                        setup_graham()
                    elif result == "MCMF":
                        mode = "MCMF"
                        setup_mcmf()
                    elif result == "DEKAMETROWCY":
                        mode = "DEKAMETROWCY"
                        setup_dek()
                else:
                    # Panel sterowania
                    btn = control_panel.handle_click(event.pos)
                    if btn == "menu":
                        mode = "MENU"
                        is_auto = False
                    elif btn == "first":
                        is_auto = False
                        history_idx = 0
                    elif btn == "prev":
                        is_auto = False
                        if history_idx > 0:
                            history_idx -= 1
                    elif btn == "auto":
                        is_auto = not is_auto
                    elif btn == "next":
                        is_auto = False
                        if history_idx < len(history) - 1:
                            history_idx += 1
                        else:
                            finished = True
                    elif btn == "last":
                        is_auto = False
                        history_idx = len(history) - 1
                        finished = True
                    elif btn == "reset":
                        regenerate_data()
                        if mode == "GRAHAM":
                            setup_graham()
                        elif mode == "MCMF":
                            setup_mcmf()
                        elif mode == "DEKAMETROWCY":
                            setup_dek()

            elif event.type == pygame.KEYDOWN:
                if mode == "MENU":
                    if event.key == pygame.K_e:
                        num_k = min(50, num_k + 1)
                    elif event.key == pygame.K_d:
                        num_k = max(1, num_k - 1)
                    elif event.key == pygame.K_w:
                        num_m = min(20, num_m + 1)
                    elif event.key == pygame.K_s:
                        num_m = max(1, num_m - 1)
                    elif event.key == pygame.K_r:
                        num_k = random.randint(5, 40)
                        num_m = random.randint(3, 15)

                    if event.key in (pygame.K_r, pygame.K_e, pygame.K_d, pygame.K_w, pygame.K_s):
                        regenerate_data()

                    if event.key == pygame.K_1:
                        mode = "GRAHAM"
                        setup_graham()
                    elif event.key == pygame.K_2:
                        mode = "MCMF"
                        setup_mcmf()
                    elif event.key == pygame.K_3:
                        mode = "DEKAMETROWCY"
                        setup_dek()
                else:
                    if event.key == pygame.K_ESCAPE:
                        mode = "MENU"
                        is_auto = False
                    elif event.key == pygame.K_r:
                        regenerate_data()
                        if mode == "GRAHAM":
                            setup_graham()
                        elif mode == "MCMF":
                            setup_mcmf()
                    elif event.key == pygame.K_a:
                        is_auto = not is_auto
                    elif event.key == pygame.K_LEFT:
                        is_auto = False
                        if history_idx > 0:
                            history_idx -= 1
                    elif event.key == pygame.K_RIGHT:
                        is_auto = False
                        if history_idx < len(history) - 1:
                            history_idx += 1
                        else:
                            finished = True

        # Auto-play
        if is_auto and not finished:
            now = pygame.time.get_ticks()
            if now - last_update > update_delay:
                if history_idx < len(history) - 1:
                    history_idx += 1
                else:
                    finished = True
                    is_auto = False
                last_update = now

        # === RYSOWANIE ===
        screen.fill(theme.BG_DARK)

        if mode == "MENU":
            menu_scene.draw(screen, num_k, num_m)

        elif mode == "GRAHAM":
            graham_scene.draw(screen, points, history, history_idx)
            control_panel.draw(screen, history_idx, len(history), is_auto)

        elif mode == "MCMF":
            mcmf_scene.draw(screen, krasnoludki, kopalnie, history, history_idx)
            control_panel.draw(screen, history_idx, len(history), is_auto)

        elif mode == "DEKAMETROWCY":
            dek_scene.draw(screen, dek_glosnosci, history, history_idx)
            control_panel.draw(screen, history_idx, len(history), is_auto)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
