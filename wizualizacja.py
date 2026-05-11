import pygame
import random
import os
import sys
from functools import cmp_to_key

# Importujemy logikę z naszego modułu geometrycznego
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from src.patrol_ksiecia import orientacja, odleglosc_kwadrat
from src.przydzial_krasnoludkow import zbuduj_i_rozwiaz_siec

pygame.init()
WIDTH, HEIGHT = 1440, 900
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Wizualizacja Algorytmów - Krasnoludki 2026")

# Kolory
WHITE = (250, 250, 250)
BLACK = (30, 30, 30)
RED = (220, 50, 50)
GREEN = (50, 200, 50)
BLUE = (50, 100, 250)
GRAY = (150, 150, 150)
LIGHT_BLUE = (173, 216, 230)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)

font = pygame.font.SysFont("arial", 22)
title_font = pygame.font.SysFont("arial", 32, bold=True)

def generate_points(n):
    padding = 80
    return [(random.randint(padding, WIDTH - padding), random.randint(padding, HEIGHT - padding)) for _ in range(n)]

def math_coords(p):
    """
    Konwertuje współrzędne ekranu (gdzie Y rośnie w dół) na układ kartezjański 
    (gdzie Y rośnie w górę), aby nasza matematyczna funkcja 'orientacja' działała tak samo.
    """
    return (p[0], -p[1])

def graham_scan_generator(punkty):
    # W Pygame oś Y rośnie w dół, więc "najniższy" wizualnie punkt ma największą wartość Y.
    p0 = max(punkty, key=lambda p: (p[1], -p[0]))
    yield [p0], "Krok 1: Znaleziono punkt startowy p0 (najniższy na ekranie)"
    
    def compare_polar(p, q):
        # Przekazujemy odwrócone (matematyczne) Y, by sortowanie zachowało układ CCW
        o = orientacja(math_coords(p0), math_coords(p), math_coords(q))
        if o > 0: return -1
        elif o < 0: return 1
        else:
            d_p = odleglosc_kwadrat(p0, p)
            d_q = odleglosc_kwadrat(p0, q)
            return -1 if d_p < d_q else (1 if d_p > d_q else 0)

    posortowane = sorted([p for p in punkty if p != p0], key=cmp_to_key(compare_polar))
    yield [p0] + posortowane, "Krok 2: Posortowano punkty kątowo względem p0"
    
    unikalne_katy = []
    for p in posortowane:
        while len(unikalne_katy) > 0 and orientacja(math_coords(p0), math_coords(unikalne_katy[-1]), math_coords(p)) == 0:
            unikalne_katy.pop()
        unikalne_katy.append(p)
        
    if len(unikalne_katy) < 2:
        yield [p0] + unikalne_katy, "Zakończono: Za mało punktów do zbudowania figury."
        return
        
    stos = [p0, unikalne_katy[0], unikalne_katy[1]]
    yield list(stos), "Krok 3: Dodano pierwsze 3 punkty do otoczki (Stos)"
    
    for i in range(2, len(unikalne_katy)):
        p_i = unikalne_katy[i]
        
        while len(stos) > 1 and orientacja(math_coords(stos[-2]), math_coords(stos[-1]), math_coords(p_i)) <= 0:
            yield list(stos) + [p_i], f"Wykryto skręt w prawo na punkcie! Usuwam poprzedni wierzchołek ze stosu..."
            stos.pop()
            
        stos.append(p_i)
        yield list(stos), f"Skręt w lewo prawidłowy. Dodano punkt do otoczki."
        
    # Na sam koniec dodajemy p0 na koniec, aby rysowanie zamkniętej pętli w Pygame było ładne
    yield list(stos) + [p0], "Krok 4: Algorytm zakończony! Otrzymano optymalną Trasę Patrolu Księcia."

def generate_krasnoludki_kopalnie(num_k, num_m):
    padding = 80
    krasnoludki = [(f"K{i}", random.randint(padding, WIDTH - padding), random.randint(padding, HEIGHT - padding), ["ALL"]) for i in range(1, num_k + 1)]
    kopalnie = [(f"M{i}", random.randint(padding, WIDTH - padding), random.randint(padding, HEIGHT - padding), random.randint(1, 4)) for i in range(1, num_m + 1)]
    return krasnoludki, kopalnie

def mcmf_generator(krasnoludki, kopalnie):
    # S (Źródło) i T (Ujście) pozycje na ekranie
    source_pos = (50, HEIGHT // 2)
    sink_pos = (WIDTH - 50, HEIGHT // 2)
    
    yield {"step": "init", "przydzialy": []}, "Krok 1: Wyznaczono Źródło (S) i Ujście (T)"
    
    yield {"step": "source_edges", "przydzialy": []}, "Krok 2: Krawędzie ze Źródła do Krasnoludków (Przepustowość: 1)"
    
    yield {"step": "mine_edges", "przydzialy": []}, "Krok 3: Krawędzie z Kopalni do Ujścia (Przepustowość: Pojemność)"
    
    yield {"step": "bipartite", "przydzialy": []}, "Krok 4: Potencjalne drogi do pracy (Koszt to odległość)"
    
    # Obliczamy właściwy przepływ
    flow, cost, przydzialy = zbuduj_i_rozwiaz_siec(krasnoludki, kopalnie)
    
    current_przydzialy = []
    for p in przydzialy:
        current_przydzialy.append(p)
        yield {"step": "flow", "przydzialy": list(current_przydzialy)}, f"Przepycham przepływ: {p[0]} -> {p[1]} (Koszt/Dystans: {p[2]})"
        
    yield {"step": "done", "przydzialy": current_przydzialy}, f"Zakończono! Znalazło pracę: {flow} krasnali, Koszt całkowity: {cost}"

def main():
    clock = pygame.time.Clock()
    mode = "MENU"
    
    # Domyślne wartości
    num_k = 15
    num_m = 5
    
    shared_krasnoludki, shared_kopalnie = generate_krasnoludki_kopalnie(num_k, num_m)
    points = []
    krasnoludki = []
    kopalnie = []
    
    gen = None
    history = []
    history_idx = 0
    is_auto = False
    
    running = True
    finished = False
    
    last_update = pygame.time.get_ticks()
    update_delay = 500

    try:
        bg_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "tlo_startowe.png")
        bg_image = pygame.image.load(bg_path)
        bg_image = pygame.transform.smoothscale(bg_image, (WIDTH, HEIGHT))
    except Exception as e:
        print(f"Błąd ładowania tła: {e}")
        bg_image = None

    # Obszary przycisków na grafice dopasowane proporcjonalnie do rozmiaru okna
    btn_graham_rect = pygame.Rect(int(WIDTH * 0.05), int(HEIGHT * 0.81), int(WIDTH * 0.28), int(HEIGHT * 0.15))
    btn_mcmf_rect = pygame.Rect(int(WIDTH * 0.36), int(HEIGHT * 0.81), int(WIDTH * 0.28), int(HEIGHT * 0.15))
    
    while running:
        screen.fill(WHITE)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if mode == "MENU" and event.button == 1:
                    if btn_graham_rect.collidepoint(event.pos):
                        mode = "GRAHAM"
                        points = [(mx, my) for mid, mx, my, cap in shared_kopalnie]
                        history = list(graham_scan_generator(points))
                        if not history:
                            history = [([], "")]
                        history_idx = 0
                        is_auto = False
                        finished = False
                    elif btn_mcmf_rect.collidepoint(event.pos):
                        mode = "MCMF"
                        krasnoludki = shared_krasnoludki
                        kopalnie = shared_kopalnie
                        history = list(mcmf_generator(krasnoludki, kopalnie))
                        if not history:
                            history = [({"step": "init", "przydzialy": []}, "")]
                        history_idx = 0
                        is_auto = False
                        finished = False
            elif event.type == pygame.KEYDOWN:
                if mode == "MENU":
                    # Zmiana ilości Krasnoludków (Strzałki GÓRA/DÓŁ)
                    if event.key == pygame.K_UP: num_k = min(50, num_k + 1)
                    elif event.key == pygame.K_DOWN: num_k = max(1, num_k - 1)
                    # Zmiana ilości Kopalni (W/S)
                    elif event.key == pygame.K_w: num_m = min(20, num_m + 1)
                    elif event.key == pygame.K_s: num_m = max(1, num_m - 1)
                    
                    if event.key in (pygame.K_r, pygame.K_UP, pygame.K_DOWN, pygame.K_w, pygame.K_s):
                        shared_krasnoludki, shared_kopalnie = generate_krasnoludki_kopalnie(num_k, num_m)
                        
                    elif event.key == pygame.K_1:
                        mode = "GRAHAM"
                        points = [(mx, my) for mid, mx, my, cap in shared_kopalnie]
                        history = list(graham_scan_generator(points))
                        if not history:
                            history = [([], "")]
                        history_idx = 0
                        is_auto = False
                        finished = False
                        
                    elif event.key == pygame.K_2:
                        mode = "MCMF"
                        krasnoludki = shared_krasnoludki
                        kopalnie = shared_kopalnie
                        history = list(mcmf_generator(krasnoludki, kopalnie))
                        if not history:
                            history = [({"step": "init", "przydzialy": []}, "")]
                        history_idx = 0
                        is_auto = False
                        finished = False
                else:
                    if event.key == pygame.K_ESCAPE:
                        mode = "MENU"
                        is_auto = False
                    elif event.key == pygame.K_SPACE:
                        if mode == "GRAHAM":
                            history = list(graham_scan_generator(points))
                        elif mode == "MCMF":
                            history = list(mcmf_generator(krasnoludki, kopalnie))
                        if not history:
                            history = [([], "")]
                        history_idx = 0
                        is_auto = False
                        finished = False
                    elif event.key == pygame.K_r:
                        shared_krasnoludki, shared_kopalnie = generate_krasnoludki_kopalnie(num_k, num_m)
                        if mode == "GRAHAM":
                            points = [(mx, my) for mid, mx, my, cap in shared_kopalnie]
                            history = list(graham_scan_generator(points))
                        elif mode == "MCMF":
                            krasnoludki = shared_krasnoludki
                            kopalnie = shared_kopalnie
                            history = list(mcmf_generator(krasnoludki, kopalnie))
                        if not history:
                            history = [([], "")]
                        history_idx = 0
                        is_auto = False
                        finished = False
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

        if is_auto and not finished:
            now = pygame.time.get_ticks()
            if now - last_update > update_delay:
                if history_idx < len(history) - 1:
                    history_idx += 1
                else:
                    finished = True
                    is_auto = False
                last_update = now
                
        if mode == "MENU":
            if bg_image:
                screen.blit(bg_image, (0, 0))
            else:
                title = title_font.render("Wizualizacja Algorytmów - Krasnoludki 2026", True, BLACK)
                screen.blit(title, (WIDTH//2 - title.get_width()//2, 80))
            
            # Wskaźniki ilości wypisywane na kamiennej tablicy z tła
            DARK_TEXT = (40, 30, 20)
            base_y = int(HEIGHT * 0.25)
            
            font_dla_tabliczki = pygame.font.SysFont("arial", 16, bold = True)

            kras_txt = font_dla_tabliczki.render(f"Krasnoludki: {num_k} (Strzałka GÓRA/DÓŁ)", True, DARK_TEXT)
            screen.blit(kras_txt, (WIDTH//2 - kras_txt.get_width()//2, base_y))
            
            kop_txt = font_dla_tabliczki.render(f"Kopalnie: {num_m} (W/S)", True, DARK_TEXT)
            screen.blit(kop_txt, (WIDTH//2 - kop_txt.get_width()//2, base_y + 35))
            
            opt_r = font_dla_tabliczki.render("R - Przelosuj pozycje i pojemności", True, DARK_TEXT)
            screen.blit(opt_r, (WIDTH//2 - opt_r.get_width()//2, base_y + 75))
            
            if not bg_image:
                opt1 = font.render("1 - Patrol Księcia wokół kopalni (Algorytm Grahama)", True, BLACK)
                screen.blit(opt1, (WIDTH//2 - opt1.get_width()//2, 300))
                
                opt2 = font.render("2 - Przydział Krasnoludków do kopalni (MCMF)", True, BLACK)
                screen.blit(opt2, (WIDTH//2 - opt2.get_width()//2, 350))
                
                info = font.render("Wciśnij 1 lub 2 aby rozpocząć", True, GRAY)
                screen.blit(info, (WIDTH//2 - info.get_width()//2, 480))
            
        elif mode == "GRAHAM":
            if history:
                current_data, message = history[history_idx]
            else:
                current_data, message = [], ""
                
            # Rysujemy kopalnie jako kwadraty, żeby było widać, że to te same obiekty co w MCMF
            for p in points:
                pygame.draw.rect(screen, ORANGE, (p[0]-15, p[1]-15, 30, 30))
                
            if len(current_data) > 0:
                p0 = current_data[0]
                pygame.draw.circle(screen, GREEN, p0, 8)
                
                if "Posortowano" in message:
                    for idx, p in enumerate(current_data[1:]):
                        pygame.draw.line(screen, LIGHT_BLUE, p0, p, 1)
                        txt = font.render(str(idx+1), True, BLUE)
                        screen.blit(txt, (p[0]+15, p[1]-15))
                else:
                    if len(current_data) > 1:
                        pygame.draw.lines(screen, BLUE, False, current_data, 3)
                        
                    for p in current_data:
                        pygame.draw.circle(screen, RED, p, 6)
                    
                    if len(current_data) > 1 and "skręt w prawo" in message:
                        pygame.draw.line(screen, RED, current_data[-2], current_data[-1], 3)
                        pygame.draw.circle(screen, BLACK, current_data[-1], 8, 2)
                        
            title = title_font.render("Patrol Księcia (Algorytm Grahama)", True, BLACK)
            screen.blit(title, (20, 20))
            if history:
                msg_surface = font.render(f"Krok: {history_idx + 1} / {len(history)}", True, BLACK)
                screen.blit(msg_surface, (20, 60))
            info = font.render("R = Przelosuj | A = Auto (Wł/Wył) | LEWO/PRAWO = Krok | SPACJA = Od nowa | ESC = Menu", True, GRAY)
            screen.blit(info, (20, HEIGHT - 40))
        elif mode == "MCMF":
            if history:
                current_state, message = history[history_idx]
            else:
                current_state, message = {"step": "init", "przydzialy": []}, ""

            step = current_state["step"]
            przydzialy = current_state["przydzialy"]

            # Kolory
            FAINT_GRAY  = (210, 210, 210)
            SOFT_ORANGE = (240, 160, 50)
            DARK_SLATE  = (70, 90, 110)
            STRONG_GREEN = (30, 180, 60)
            LABEL_COL   = (60, 60, 200)
            LABEL_FLOW  = (200, 60, 60)

            n = len(krasnoludki)
            m = len(kopalnie)

            # --- Pozycje kolumnowe ---
            col_s_x = int(WIDTH * 0.09)
            col_k_x = int(WIDTH * 0.32)
            col_m_x = int(WIDTH * 0.68)
            col_t_x = int(WIDTH * 0.91)

            source_pos = (col_s_x, HEIGHT // 2)
            sink_pos   = (col_t_x, HEIGHT // 2)

            def node_y(idx, total):
                if total <= 1:
                    return HEIGHT // 2
                margin = int(HEIGHT * 0.14)
                return margin + idx * (HEIGHT - 2 * margin) // (total - 1)

            k_pos = {k_id: (col_k_x, node_y(i, n))
                     for i, (k_id, *_) in enumerate(krasnoludki)}
            m_pos = {m_id: (col_m_x, node_y(j, m))
                     for j, (m_id, *_) in enumerate(kopalnie)}

            # --- Pomocnik: strzałka z etykietą ---
            def draw_arrow(start, end, color, width=2, label="", lcolor=LABEL_COL):
                dx = end[0] - start[0]
                dy = end[1] - start[1]
                dist = max(1, (dx*dx + dy*dy) ** 0.5)
                ux, uy = dx / dist, dy / dist
                px, py = -uy, ux
                # Skróć linię o promień węzła docelowego (16px)
                tip   = (int(end[0] - ux * 16), int(end[1] - uy * 16))
                start2= (int(start[0] + ux * 16), int(start[1] + uy * 16))
                pygame.draw.line(screen, color, start2, tip, width)
                # Grot
                ar = 10
                b  = (tip[0] - int(ux * ar), tip[1] - int(uy * ar))
                p1 = (b[0] + int(px * ar * 0.5), b[1] + int(py * ar * 0.5))
                p2 = (b[0] - int(px * ar * 0.5), b[1] - int(py * ar * 0.5))
                pygame.draw.polygon(screen, color, [tip, p1, p2])
                # Etykieta nad środkiem
                if label:
                    mx2 = (start[0] + end[0]) // 2
                    my2 = (start[1] + end[1]) // 2
                    # Odsunięcie prostopadłe (żeby nie nakrywało linii)
                    off = 14
                    lbl = font.render(label, True, lcolor)
                    screen.blit(lbl, (mx2 - lbl.get_width()//2 + int(px*off),
                                      my2 - lbl.get_height() - 4 + int(py*off)))

            # === Krok 1: S -> Krasnoludki ===
            if step in ["source_edges", "mine_edges", "bipartite", "flow", "done"]:
                for k_id, kx, ky, prefs in krasnoludki:
                    draw_arrow(source_pos, k_pos[k_id], FAINT_GRAY, 1, "cap:1")

            # === Krok 2: Kopalnie -> T ===
            if step in ["mine_edges", "bipartite", "flow", "done"]:
                for m_id, mx, my, cap in kopalnie:
                    draw_arrow(m_pos[m_id], sink_pos, SOFT_ORANGE, 2, f"cap:{cap}")

            # === Krok 3: Krasnoludki -> Kopalnie (bipartite) ===
            if step in ["bipartite", "flow", "done"]:
                for k_id, kx, ky, prefs in krasnoludki:
                    for m_id, mx, my, cap in kopalnie:
                        dist = int(((kx - mx)**2 + (ky - my)**2) ** 0.5)
                        draw_arrow(k_pos[k_id], m_pos[m_id], FAINT_GRAY, 1)

            # === Aktywne przydziały (wynik MCMF) ===
            for k_id, m_id, cost in przydzialy:
                if k_id in k_pos and m_id in m_pos:
                    draw_arrow(k_pos[k_id], m_pos[m_id], STRONG_GREEN, 3,
                               f"w:{cost}", lcolor=LABEL_FLOW)

            # === Węzły (rysowane NA WIERZCHU krawędzi) ===
            # Źródło S
            pygame.draw.circle(screen, GREEN, source_pos, 22)
            ts = title_font.render("S", True, WHITE)
            screen.blit(ts, (source_pos[0] - ts.get_width()//2, source_pos[1] - ts.get_height()//2))

            # Ujście T
            pygame.draw.circle(screen, RED, sink_pos, 22)
            tt = title_font.render("T", True, WHITE)
            screen.blit(tt, (sink_pos[0] - tt.get_width()//2, sink_pos[1] - tt.get_height()//2))

            # Krasnoludki
            for k_id, kx, ky, prefs in krasnoludki:
                pos = k_pos[k_id]
                pygame.draw.circle(screen, DARK_SLATE, pos, 16)
                tk = font.render(k_id, True, WHITE)
                screen.blit(tk, (pos[0] - tk.get_width()//2, pos[1] - tk.get_height()//2))

            # Kopalnie
            for m_id, mx, my, cap in kopalnie:
                pos = m_pos[m_id]
                pygame.draw.rect(screen, SOFT_ORANGE, (pos[0]-16, pos[1]-16, 32, 32))
                pygame.draw.rect(screen, BLACK, (pos[0]-16, pos[1]-16, 32, 32), 2)
                tm = font.render(m_id, True, BLACK)
                screen.blit(tm, (pos[0] - tm.get_width()//2, pos[1] - tm.get_height()//2))

            # === UI ===
            title = title_font.render("Przydział Krasnoludków (MCMF)", True, BLACK)
            screen.blit(title, (20, 20))
            if history:
                msg_surface = font.render(f"Krok {history_idx + 1}/{len(history)}: {message}", True, DARK_SLATE)
                screen.blit(msg_surface, (20, 60))
            info = font.render("R = Przelosuj | A = Auto (Wł/Wył) | LEWO/PRAWO = Krok | SPACJA = Od nowa | ESC = Menu", True, GRAY)
            screen.blit(info, (20, HEIGHT - 40))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
