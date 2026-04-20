import os
import math
from typing import List, Tuple

def orientacja(p: Tuple[int, int], q: Tuple[int, int], r: Tuple[int, int]) -> int:
    """
    Oblicza iloczyn wektorowy dla trzech punktów (p, q, r), aby określić ich orientację.
    
    Złożoność czasowa: O(1)
    Złożoność pamięciowa: O(1)
    
    Argumenty:
    p, q, r (Tuple[int, int]): Współrzędne punktów 2D.
    
    Zwraca:
    int: Wartość dodatnia (skręt w lewo/CCW), ujemna (skręt w prawo/CW) lub 0 (współliniowe).
    """
    return (q[0] - p[0]) * (r[1] - p[1]) - (q[1] - p[1]) * (r[0] - p[0])

def odleglosc_kwadrat(p: Tuple[int, int], q: Tuple[int, int]) -> int:
    """
    Oblicza kwadrat odległości euklidesowej między punktami.
    
    Złożoność czasowa: O(1)
    Złożoność pamięciowa: O(1)
    
    Argumenty:
    p, q (Tuple[int, int]): Współrzędne punktów 2D.
    
    Zwraca:
    int: Kwadrat odległości.
    """
    return (p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2

def graham_scan(punkty: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
    """
    Implementacja algorytmu Grahama (Graham Scan) do wyznaczania otoczki wypukłej.
    Znajduje najkrótszą zamkniętą trasę (otoczkę wypukłą) okalającą podany zbiór punktów.
    
    Złożoność czasowa: O(n log n) - dominuje sortowanie kątowe
    Złożoność pamięciowa: O(n) - przechowywanie wierzchołków otoczki na stosie
    
    Argumenty:
    punkty (List[Tuple[int, int]]): Lista krotek reprezentujących współrzędne (x, y).
    
    Zwraca:
    List[Tuple[int, int]]: Lista wierzchołków otoczki wypukłej w kolejności CCW.
    """
    if len(punkty) < 3:
        return punkty
        
    # Punkt początkowy: najniższy Y, w razie remisów najmniejszy X
    p0 = min(punkty, key=lambda p: (p[1], p[0]))
    
    def polar_order(p: Tuple[int, int]) -> Tuple[float, int]:
        return (math.atan2(p[1] - p0[1], p[0] - p0[0]), odleglosc_kwadrat(p0, p))
        
    # Sortowanie pozostałych punktów względem kąta i odległości
    posortowane = sorted([p for p in punkty if p != p0], key=polar_order)
    
    # Oczyszczanie ze współliniowych - zostawiamy tylko najdalszy punkt dla każdego kąta
    unikalne_katy = []
    for p in posortowane:
        while len(unikalne_katy) > 0 and orientacja(p0, unikalne_katy[-1], p) == 0:
            unikalne_katy.pop()
        unikalne_katy.append(p)
        
    if len(unikalne_katy) < 2:
        return [p0] + unikalne_katy
        
    # Inicjalizacja stosu trzema pierwszymi punktami
    stos = [p0, unikalne_katy[0], unikalne_katy[1]]
    
    # Przechodzenie przez pozostałe punkty
    for i in range(2, len(unikalne_katy)):
        p_i = unikalne_katy[i]
        # Dopóki nie wykonujemy skrętu w lewo, usuwaj ostatni punkt ze stosu
        while len(stos) > 1 and orientacja(stos[-2], stos[-1], p_i) <= 0:
            stos.pop()
        stos.append(p_i)
        
    return stos

def uruchom_modul(dane_kopalni: List[Tuple[str, int, int, int]]) -> List[Tuple[int, int]]:
    """
    Główna funkcja uruchamiająca Moduł Geometryczny.
    Przetwarza surowe dane kopalni na współrzędne i wyznacza trasę patrolu.
    
    Złożoność czasowa: O(n log n)
    Złożoność pamięciowa: O(n)
    
    Argumenty:
    dane_kopalni (List[Tuple[str, int, int, int]]): Lista kopalni w formacie (nazwa, x, y, pojemność).
    
    Zwraca:
    List[Tuple[int, int]]: Lista współrzędnych otoczki wypukłej.
    """
    punkty = [(kopalnia[1], kopalnia[2]) for kopalnia in dane_kopalni]
    return graham_scan(punkty)

def _wczytaj_testowe(sciezka: str) -> List[Tuple[str, int, int, int]]:
    """Funkcja pomocnicza do wczytania danych, kiedy moduł uruchamiany jest bezpośrednio."""
    kopalnie = []
    with open(sciezka, 'r', encoding='utf-8') as f:
        for linia in f:
            dane = linia.strip().split()
            if len(dane) == 4:
                kopalnie.append((dane[0], int(dane[1]), int(dane[2]), int(dane[3])))
    return kopalnie

if __name__ == "__main__":
    sciezka_dane = os.path.join(os.path.dirname(__file__), '..', 'data', 'kopalnie.txt')
    try:
        kopalnie_test = _wczytaj_testowe(sciezka_dane)
        print("=== TEST MODUŁU GEOMETRYCZNEGO ===")
        print(f"Wczytano punktów (kopalni): {len(kopalnie_test)}")
        
        trasa = uruchom_modul(kopalnie_test)
        
        print("\nTrasa Patrolu Księcia (kolejność wierzchołków otoczki wypukłej):")
        for pkt in trasa:
            print(f" -> {pkt}")
            
    except FileNotFoundError:
        print(f"Błąd! Nie znaleziono pliku wejściowego: {os.path.abspath(sciezka_dane)}")
