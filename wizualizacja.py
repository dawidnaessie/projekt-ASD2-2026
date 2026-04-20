import pygame
import random
import os
import sys
from functools import cmp_to_key

# Importujemy logikę z naszego modułu geometrycznego
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from src.patrol_ksiecia import orientacja, odleglosc_kwadrat

pygame.init()
WIDTH, HEIGHT = 1000, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Wizualizacja Algorytmu Grahama - Krasnoludki 2026")

# Kolory
WHITE = (250, 250, 250)
BLACK = (30, 30, 30)
RED = (220, 50, 50)
GREEN = (50, 200, 50)
BLUE = (50, 100, 250)
GRAY = (150, 150, 150)
LIGHT_BLUE = (173, 216, 230)

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

def main():
    clock = pygame.time.Clock()
    points = generate_points(25)
    
    gen = graham_scan_generator(points)
    current_hull = []
    message = "Naciśnij SPACJĘ, aby wygenerować nową mapę i uruchomić algorytm"
    
    running = True
    animating = False
    finished = False
    
    last_update = pygame.time.get_ticks()
    update_delay = 500 # ms - opóźnienie pomiędzy krokami algorytmu
    
    while running:
        screen.fill(WHITE)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    points = generate_points(25)
                    gen = graham_scan_generator(points)
                    current_hull = []
                    message = "Inicjalizacja środowiska..."
                    animating = True
                    finished = False
                elif event.key == pygame.K_RIGHT and not finished and animating:
                    # Przyspieszenie o 1 krok z ręki
                    try:
                        current_hull, message = next(gen)
                    except StopIteration:
                        finished = True
                        animating = False

        if animating and not finished:
            now = pygame.time.get_ticks()
            if now - last_update > update_delay:
                try:
                    current_hull, message = next(gen)
                except StopIteration:
                    finished = True
                    animating = False
                last_update = now
                
        # 1. Rysuj wszystkie niepołączone jeszcze punkty
        for p in points:
            pygame.draw.circle(screen, GRAY, p, 5)
            
        # 2. Rysuj to co się dzieje obecnie
        if len(current_hull) > 0:
            p0 = current_hull[0]
            pygame.draw.circle(screen, GREEN, p0, 8) # Wyróżnij p0
            
            if "Posortowano" in message:
                # Pokazujemy powiązania kątowe do p0
                for idx, p in enumerate(current_hull[1:]):
                    pygame.draw.line(screen, LIGHT_BLUE, p0, p, 1)
                    txt = font.render(str(idx+1), True, BLUE)
                    screen.blit(txt, (p[0]+10, p[1]-10))
            else:
                # Normalne rysowanie aktualnego stanu stosu
                if len(current_hull) > 1:
                    pygame.draw.lines(screen, BLUE, False, current_hull, 3)
                    
                for p in current_hull:
                    pygame.draw.circle(screen, RED, p, 6)
                
                # Zaznacz najnowszy sprawdzany punkt, jeśli wystąpił skręt w prawo
                if len(current_hull) > 1 and "skręt w prawo" in message:
                    pygame.draw.line(screen, RED, current_hull[-2], current_hull[-1], 3)
                    pygame.draw.circle(screen, BLACK, current_hull[-1], 8, 2)
                    
        # 3. Informacje tekstowe (UI)
        title = title_font.render("Wizualizacja Algorytmu Grahama", True, BLACK)
        screen.blit(title, (20, 20))
        
        msg_surface = font.render(message, True, BLACK)
        screen.blit(msg_surface, (20, 60))
        
        info = font.render("SPACJA = Nowe punkty | STRZAŁKA W PRAWO = Kolejny krok", True, GRAY)
        screen.blit(info, (20, HEIGHT - 40))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
