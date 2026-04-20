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
WIDTH, HEIGHT = 1000, 700
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
    krasnoludki = [(f"K{i}", random.randint(padding, WIDTH - padding), random.randint(padding, HEIGHT - padding)) for i in range(1, num_k + 1)]
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
    current_state = {"step": "init", "przydzialy": []}
    message = ""
    
    running = True
    animating = False
    finished = False
    
    last_update = pygame.time.get_ticks()
    update_delay = 500
    
    while running:
        screen.fill(WHITE)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
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
                        gen = graham_scan_generator(points)
                        # Dla Grahama używamy starych zmiennych
                        current_data = [] 
                        message = "Inicjalizacja środowiska..."
                        animating = True
                        finished = False
                        
                    elif event.key == pygame.K_2:
                        mode = "MCMF"
                        krasnoludki = shared_krasnoludki
                        kopalnie = shared_kopalnie
                        gen = mcmf_generator(krasnoludki, kopalnie)
                        current_state = {"step": "init", "przydzialy": []}
                        message = "Inicjalizacja środowiska..."
                        animating = True
                        finished = False
                else:
                    if event.key == pygame.K_ESCAPE:
                        mode = "MENU"
                        animating = False
                    elif event.key == pygame.K_SPACE:
                        if mode == "GRAHAM":
                            gen = graham_scan_generator(points)
                            current_data = []
                        elif mode == "MCMF":
                            gen = mcmf_generator(krasnoludki, kopalnie)
                            current_state = {"step": "init", "przydzialy": []}
                        message = "Inicjalizacja środowiska..."
                        animating = True
                        finished = False
                    elif event.key == pygame.K_RIGHT and not finished and animating:
                        try:
                            if mode == "GRAHAM":
                                current_data, message = next(gen)
                            else:
                                current_state, message = next(gen)
                        except StopIteration:
                            finished = True
                            animating = False

        if animating and not finished:
            now = pygame.time.get_ticks()
            if now - last_update > update_delay:
                try:
                    if mode == "GRAHAM":
                        current_data, message = next(gen)
                    else:
                        current_state, message = next(gen)
                except StopIteration:
                    finished = True
                    animating = False
                last_update = now
                
        if mode == "MENU":
            title = title_font.render("Wizualizacja Algorytmów - Krasnoludki 2026", True, BLACK)
            screen.blit(title, (WIDTH//2 - title.get_width()//2, 80))
            
            # Wskaźniki ilości
            kras_txt = font.render(f"Krasnoludki: {num_k} (Strzałka GÓRA/DÓŁ aby zmienić)", True, PURPLE)
            screen.blit(kras_txt, (WIDTH//2 - kras_txt.get_width()//2, 150))
            
            kop_txt = font.render(f"Kopalnie: {num_m} (W/S aby zmienić)", True, ORANGE)
            screen.blit(kop_txt, (WIDTH//2 - kop_txt.get_width()//2, 190))
            
            opt_r = font.render("R - Przelosuj pozycje i pojemności", True, BLUE)
            screen.blit(opt_r, (WIDTH//2 - opt_r.get_width()//2, 230))
            
            opt1 = font.render("1 - Patrol Księcia wokół kopalni (Algorytm Grahama)", True, BLACK)
            screen.blit(opt1, (WIDTH//2 - opt1.get_width()//2, 300))
            
            opt2 = font.render("2 - Przydział Krasnoludków do kopalni (MCMF)", True, BLACK)
            screen.blit(opt2, (WIDTH//2 - opt2.get_width()//2, 350))
            
            info = font.render("Wciśnij 1 lub 2 aby rozpocząć", True, GRAY)
            screen.blit(info, (WIDTH//2 - info.get_width()//2, 480))
            
        elif mode == "GRAHAM":
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
            msg_surface = font.render(message, True, BLACK)
            screen.blit(msg_surface, (20, 60))
            info = font.render("SPACJA = Powtórz animację | PRAWO = Krok | ESC = Menu", True, GRAY)
            screen.blit(info, (20, HEIGHT - 40))
        elif mode == "MCMF":
            source_pos = (50, HEIGHT // 2)
            sink_pos = (WIDTH - 50, HEIGHT // 2)
            step = current_state["step"]
            przydzialy = current_state["przydzialy"]

            # Nowe, stonowane kolory specjalnie dla tego trybu
            FAINT_GRAY = (230, 230, 230)
            SOFT_ORANGE = (240, 160, 50)
            DARK_SLATE = (70, 90, 110)
            STRONG_GREEN = (30, 180, 60)
            TEXT_GRAY = (120, 120, 120)

            # 1. Rysowanie Źródła i Ujścia
            pygame.draw.circle(screen, GREEN, source_pos, 20)
            txt_s = title_font.render("S", True, WHITE)
            screen.blit(txt_s, (source_pos[0]-8, source_pos[1]-15))
            
            pygame.draw.circle(screen, RED, sink_pos, 20)
            txt_t = title_font.render("T", True, WHITE)
            screen.blit(txt_t, (sink_pos[0]-8, sink_pos[1]-15))

            # 2. Rysowanie sieci (Zależne od kroku algorytmu)
            if step in ["source_edges", "mine_edges", "bipartite", "flow", "done"]:
                # Blade linie od Źródła (S)
                for k_id, kx, ky in krasnoludki:
                    pygame.draw.line(screen, FAINT_GRAY, source_pos, (kx, ky), 1)
                    
            if step in ["mine_edges", "bipartite", "flow", "done"]:
                # Linie do Ujścia (T) - ujednolicona, cieńsza grubość
                for k_id, mx, my, cap in kopalnie:
                    pygame.draw.line(screen, SOFT_ORANGE, (mx, my), sink_pos, 2) 
                    
                    # Napis "Cap" narysowany dyskretnym szarym kolorem bliżej kopalni (1/3 drogi)
                    txt_cap = font.render(f"Cap: {cap}", True, TEXT_GRAY)
                    cx = mx + (sink_pos[0] - mx) // 3
                    cy = my + (sink_pos[1] - my) // 3
                    screen.blit(txt_cap, (cx, cy))

            if step in ["bipartite"]:
                # Bardzo blada pajęczyna potencjalnych dróg
                for k_id, kx, ky in krasnoludki:
                    for mid, mx, my, cap in kopalnie:
                        pygame.draw.line(screen, FAINT_GRAY, (kx, ky), (mx, my), 1)

            # Rysowanie kopalń (Nieco mniejsze kwadraty)
            for k_id, mx, my, cap in kopalnie:
                pygame.draw.rect(screen, SOFT_ORANGE, (mx-12, my-12, 24, 24))
                cap_txt = font.render(f"{k_id}", True, BLACK)
                screen.blit(cap_txt, (mx-10, my-32))
                
            # Rysowanie krasnoludków (Eleganckie, ciemno-stalowe mniejsze kropki)
            for k_id, kx, ky in krasnoludki:
                pygame.draw.circle(screen, DARK_SLATE, (kx, ky), 6)
                txt = font.render(k_id, True, BLACK)
                screen.blit(txt, (kx-8, ky-26))
                
            # Aktywne przydziały (Wynik MCMF - gruby, mocny zielony kolor)
            if przydzialy:
                for k_id, m_id, cost in przydzialy:
                    kx, ky = next((x, y) for kid, x, y in krasnoludki if kid == k_id)
                    mx, my, _ = next((x, y, cap) for mid, x, y, cap in kopalnie if mid == m_id)
                    pygame.draw.line(screen, STRONG_GREEN, (kx, ky), (mx, my), 3)

            title = title_font.render("Przydział Krasnoludków (MCMF)", True, BLACK)
            screen.blit(title, (20, 20))
            msg_surface = font.render(message, True, BLACK)
            screen.blit(msg_surface, (20, 60))
            info = font.render("SPACJA = Powtórz animację | PRAWO = Krok | ESC = Menu", True, GRAY)
            screen.blit(info, (20, HEIGHT - 40))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
