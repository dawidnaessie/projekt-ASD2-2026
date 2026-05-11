import os
from typing import List, Tuple

class SegmentTreeRMQ:
    """
    Nieliniowa struktura danych (Drzewo Przedziałowe) służąca do błyskawicznego
    odpowiadania na zapytania o maksimum na zadanym przedziale (Range Maximum Query).
    Implementacja rekurencyjna zgodna z paradygmatem wykładowym.
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
        self.drzewo: List[float] = [float('-inf')] * (4 * self.n)
        
        if self.n > 0:
            # Wywołanie procedury BUILD(root, 1, n, f) od korzenia (v=1)
            self._build(1, 0, self.n - 1)

    def _build(self, v: int, l: int, r: int) -> None:
        """
        Rekurencyjnie buduje poddrzewo o korzeniu v dla przedziału [l, r]
        
        Złożoność czasowa: O(n)
        """
        # 1) jeśli (l == r), to tree[v] = A[l]
        if l == r:
            self.drzewo[v] = self.dane[l]
        else:
            # a) mid = floor((l + r) / 2)
            mid = (l + r) // 2
            # b) BUILD(v.left, l, mid, f)
            self._build(2 * v, l, mid)
            # c) BUILD(v.right, mid + 1, r, f)
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
        if r < ql or qr < l:
            return float('-inf')
            
        # 2) jeśli (ql <= l oraz r <= qr), to zwróć tree[v]
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
        
        Złożoność czasowa: O(log n) - odwiedzamy logarytmiczną liczbę węzłów[cite: 228].
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
    sciezka_dane = os.path.join(os.path.dirname(__file__), '..', 'data', 'dekametrowcy.txt')
    try:
        glosnosci_test = _wczytaj_glosnosci(sciezka_dane)
        print("=== TEST MODUŁU OBRONNEGO ===")
        print(f"Wczytano {len(glosnosci_test)} dekametrowców na granicy.")
        
        # Przykładowe ataki testowe
        ataki_testowe = [(0, 2), (2, 5), (5, 9)]
        
        raport = uruchom_modul(glosnosci_test, ataki_testowe)
        
        print("\nOdpowiedzi systemu na ataki:")
        for start, koniec, max_val in raport:
            print(f" -> Atak na odcinek [{start}-{koniec}]: Najgłośniejszy rozkaz to {max_val} dB")
            
    except FileNotFoundError:
        print(f"Błąd! Nie znaleziono pliku wejściowego: {os.path.abspath(sciezka_dane)}")