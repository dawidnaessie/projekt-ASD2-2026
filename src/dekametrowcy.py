import os
from typing import List, Tuple

class SegmentTreeRMQ:
    """
    Nieliniowa struktura danych (Drzewo Przedziałowe) służąca do błyskawicznego
    odpowiadania na zapytania o maksimum na zadanym przedziale (Range Maximum Query).
    Implementacja rekurencyjna zgodna z wykładem.
    """

    
    def __init__(self, dane: List[int]) -> None:
        """
        Buduje drzewo przedziałowe na podstawie początkowej tablicy głośności.
        
        Złożoność czasowa: O(n) - budowa rekurencyjna
        Złożoność pamięciowa: O(n) - drzewo wymaga 4*n elementów w wersji rekurencyjnej.
        
        Argumenty:
        dane (List[int]): Tablica z poziomami głośności dekametrowców.
        """
        self.n: int = len(dane)
        self.dane: List[int] = dane
        # Rozmiar 4n zapewnia bezpieczeństwo indeksowania dzieci w dół drzewa.
        self.drzewo: List[float] = [float('-inf')] * (4 * self.n) #4n, zeby uniknac przekroczenia bo mamy 2v i 2v+1 wiec najgorszy przypadek musimy miec 4n
        # brutal force 
        if self.n > 0:
            # Wywołanie procedury BUILD(root, 1, n, f) od korzenia (v=1)
            self._build(1, 0, self.n - 1)

    def _build(self, v: int, l: int, r: int) -> None:
        """
        Rekurencyjnie buduje poddrzewo o korzeniu v dla przedziału [l, r]
        
        Złożoność czasowa: O(n)
        """
        # 1) jeśli (l == r), to tree[v] = A[l]
        if l == r: # jesli to, to jestesmy na samym dnie drzewa w lisciu
            self.drzewo[v] = self.dane[l]
        else:
            # a) mid = floor((l + r) / 2)
            mid = (l + r) // 2
            # b) BUILD(v.left, l, mid, f) lewe dziecko
            self._build(2 * v, l, mid)
            # c) BUILD(v.right, mid + 1, r, f) prawe dziecko
            self._build(2 * v + 1, mid + 1, r)
            # d) tree[v] = f(tree[v.left], tree[v.right])
            self.drzewo[v] = max(self.drzewo[2 * v], self.drzewo[2 * v + 1])

    def _query(self, v: int, l: int, r: int, ql: int, qr: int) -> float:
        """
        Wyszukuje wartość funkcji f dla zadanego przedziału [ql, qr]
        
        Złożoność czasowa: O(log n)
        """
        # 1) jeśli (r < ql lub qr < l), to zwróć e (element neutralny)
        # Dla f=max, element neutralny e = -nieskończoność
        #jesli prawy koniec wezla jest mniejszy niz lewy koniec zapytania i na odwrot
        if r < ql or qr < l:
            return float('-inf')
            
        # 2) jeśli (ql <= l oraz r <= qr), to zwróć tree[v]
        # jesli lewy koniec zapytania jest mniejszy lub rowny lewemu koncowi wezla i na odwrot
        if ql <= l and r <= qr:
            return self.drzewo[v]
            
        # Wykonaj rekurencyjne zejście w dół drzewa
        mid = (l + r) // 2
        # b) x = QUERY(v.left, l, mid, ql, qr, f)
        x = self._query(2 * v, l, mid, ql, qr)
        # c) y = QUERY(v.right, mid + 1, r, ql, qr, f)
        y = self._query(2 * v + 1, mid + 1, r, ql, qr)
        # d) zwróć f(x, y)
        return max(x, y)

    def query(self, lewy: int, prawy: int) -> int:
        """
        Wyszukuje maksymalną głośność w przedziale [lewy, prawy] włącznie.
        
        Złożoność czasowa: O(log n) - odwiedzamy logarytmiczną liczbę węzłów
        Złożoność pamięciowa: O(log n) - stos wywołań rekurencyjnych.
        
        Argumenty:
        lewy (int): Początkowy indeks przedziału (od 0).
        prawy (int): Końcowy indeks przedziału (włącznie).
        
        Zwraca:
        int: Najwyższa wartość w zadanym przedziale.
        """
        if self.n == 0:
            return 0
            
        # Wywołanie QUERY(root, 1, n, ql, qr, f)
        wynik = self._query(1, 0, self.n - 1, lewy, prawy)
        return int(wynik)


def brute_force(dane: List[int], lewy: int, prawy: int) -> int:
    """
    Rozwiązanie naiwne (Brute Force) dla problemu Range Maximum Query.
    Przeszukuje tablicę element po elemencie w pętli for.
    
    Złożoność czasowa: O(n) dla jednego zapytania.
    Złożoność pamięciowa: O(1) - nie używa dodatkowej pamięci.
    """
    if not dane:
        return 0
        
    # Zabezpieczenie przed wyjściem poza indeksy tablicy
    lewy = max(0, min(lewy, len(dane) - 1))
    prawy = max(0, min(prawy, len(dane) - 1))
    
    maksimum: float = float('-inf')
    
    # Przejście po każdym elemencie po kolei
    for i in range(lewy, prawy + 1):
        if dane[i] > maksimum:
            maksimum = dane[i]
            
    return int(maksimum)

def uruchom_modul(dane_glosnosci: List[int], zapytania: List[Tuple[int, int]]) -> List[Tuple[int, int, int]]:
    """
    Główna funkcja orkiestrująca Moduł Obronny.
    
    Złożoność czasowa: O(n + q * log n) gdzie n to liczba krasnoludków, a q to liczba zapytań.
    Złożoność pamięciowa: O(n) dla drzewa oraz O(q) na wynik.
    
    Argumenty:
    dane_glosnosci (List[int]): Lista poziomów głośności krasnoludków.
    zapytania (List[Tuple[int, int]]): Lista krotek z przedziałami ataków (start, koniec).
    
    Zwraca:
    List[Tuple[int, int, int]]: Lista wyników w formacie (start, koniec, max_glosnosc).
    """
    if not dane_glosnosci:
        return []

    dowodztwo = SegmentTreeRMQ(dane_glosnosci)
    wyniki: List[Tuple[int, int, int]] = []
    
    for start, koniec in zapytania:
        # Zabezpieczenie przed wyjściem poza tablicę
        #jak mamy np podany index 100 a mamy 10 krasnoludkow to max dac 9
        #to samo z min jakby podali -10 to min dac 0 
        bezpieczny_start = max(0, min(start, len(dane_glosnosci) - 1))
        bezpieczny_koniec = max(0, min(koniec, len(dane_glosnosci) - 1))
        
        najglosniejszy = dowodztwo.query(bezpieczny_start, bezpieczny_koniec)
        wyniki.append((bezpieczny_start, bezpieczny_koniec, najglosniejszy))
        
    return wyniki


def _wczytaj_glosnosci(sciezka: str) -> List[int]:
    """Funkcja pomocnicza do wczytywania głośności dekametrowców z pliku."""
    glosnosci = []
    with open(sciezka, 'r', encoding='utf-8') as f:
        for linia in f:
            dane = linia.strip().split()
            if len(dane) >= 2:  # Oczekujemy formatu np. "Krasnal_1 80"
                glosnosci.append(int(dane[1]))
            elif len(dane) == 1: # Lub po prostu samej liczby "80"
                glosnosci.append(int(dane[0]))
    return glosnosci


if __name__ == "__main__":
    import random
    import time

    print("==================================================")
    print(" START TESTU BAZOWEGO Z PLIKU ")
    print("==================================================")
    sciezka_dane = os.path.join(os.path.dirname(__file__), '..', 'data', 'dekametrowcy.txt')
    try:
        glosnosci_test = _wczytaj_glosnosci(sciezka_dane)
        print(f"Wczytano {len(glosnosci_test)} dekametrowców na granicy z pliku.")
        
        ataki_testowe = [(0, 2), (2, 5), (5, 9)]
        raport = uruchom_modul(glosnosci_test, ataki_testowe)
        
        print("Odpowiedzi systemu na ataki (Drzewo Przedziałowe):")
        for start, koniec, max_val in raport:
            print(f" -> Atak na odcinek [{start}-{koniec}]: Najgłośniejszy rozkaz to {max_val} dB")
            
    except FileNotFoundError:
        print(f"Błąd! Nie znaleziono pliku wejściowego: {os.path.abspath(sciezka_dane)}")


    print("\n==================================================")
    print(" AUTOMATYCZNE TESTY RÓŻNICOWE (BRUTE FORCE VS TREE) ")
    print("==================================================")
    
    ROZMIAR_TESTU = 10000
    LICZBA_ZAPYTAŃ = 5000
    
    print(f"Generowanie losowej linii obrony: {ROZMIAR_TESTU} krasnoludków...")
    losowe_glosnosci = [random.randint(10, 120) for _ in range(ROZMIAR_TESTU)]
    
    losowe_ataki = []
    for _ in range(LICZBA_ZAPYTAŃ):
        l = random.randint(0, ROZMIAR_TESTU - 1)
        r = random.randint(l, ROZMIAR_TESTU - 1)
        losowe_ataki.append((l, r))
        
    print(f"Wygenerowano {LICZBA_ZAPYTAŃ} losowych zapytań.\n")

    # TEST POPRAWNOŚCI
    print("--- KROK 1: Sprawdzanie poprawności wyników ---")
    dowodztwo_tree = SegmentTreeRMQ(losowe_glosnosci)
    
    bledy = 0
    for start, koniec in losowe_ataki:
        wynik_drzewa = dowodztwo_tree.query(start, koniec)
        wynik_brute = brute_force(losowe_glosnosci, start, koniec)
        
        if wynik_drzewa != wynik_brute:
            bledy += 1
            
    if bledy == 0:
        print(f"SUKCES! W {LICZBA_ZAPYTAŃ} przypadkach Drzewo Przedziałowe dało wynik w 100% zgodny z Brute Force.")
    else:
        print(f"PORAŻKA! Znaleziono rozbieżności w {bledy} przypadkach.")

    # TEST WYDAJNOŚCI
    print("\n--- KROK 2: Test wydajności (Pojedynek prędkości) ---")
    
    # Czas dla Brute Force
    start_time_bf = time.perf_counter()
    for start, koniec in losowe_ataki:
        brute_force(losowe_glosnosci, start, koniec)
    czas_bf = time.perf_counter() - start_time_bf
    print(f"Czas dla pętli Brute Force (O(n)): {czas_bf:.4f} sekund")

    # Czas dla Drzewa Przedziałowego
    start_time_tree = time.perf_counter()
    for start, koniec in losowe_ataki:
        dowodztwo_tree.query(start, koniec)
    czas_tree = time.perf_counter() - start_time_tree
    print(f"Czas dla Drzewa Przedziałowego (O(log n)): {czas_tree:.4f} sekund")

    if czas_tree < czas_bf:
        przyspieszenie = czas_bf / czas_tree if czas_tree > 0 else float('inf')
        print(f"\n[WERDYKT]: Drzewo Przedziałowe okazało się {przyspieszenie:.1f}x szybsze!")