import os
import heapq
from collections import Counter
from typing import List, Tuple, Dict, Optional

class WezelHuffmana:
    """
    Reprezentuje pojedynczy węzeł w drzewie Huffmana.
    """
    def __init__(self, znak: Optional[str], czestosc: int):
        self.znak = znak
        self.czestosc = czestosc
        self.lewy: Optional['WezelHuffmana'] = None
        self.prawy: Optional['WezelHuffmana'] = None

    def __lt__(self, other: 'WezelHuffmana') -> bool:
        """
        Porównywanie węzłów na podstawie częstości występowania.
        Niezbędne do prawidłowego działania kolejki priorytetowej (kopca).
        """
        return self.czestosc < other.czestosc


class KompresorHuffmana:
    """
    Klasa realizująca algorytm kompresji i dekompresji Huffmana.
    Pozwala zaoszczędzić "elektroniczny papier" w księgach królestwa.
    """
    def __init__(self):
        self.korzen: Optional[WezelHuffmana] = None
        self.kody: Dict[str, str] = {}

    def _zbuduj_drzewo(self, tekst: str) -> None:
        """
        Buduje drzewo Huffmana na podstawie częstości wystąpień znaków w tekście.
        
        Złożoność czasowa: O(k log k), gdzie k to liczba unikalnych znaków (rozmiar alfabetu).
        Złożoność pamięciowa: O(k) na przechowanie kopca i drzewa.
        """
        czestosci = Counter(tekst)
        kopiec = [WezelHuffmana(znak, czestosc) for znak, czestosc in czestosci.items()]
        heapq.heapify(kopiec)

        while len(kopiec) > 1:
            lewy = heapq.heappop(kopiec)
            prawy = heapq.heappop(kopiec)
            
            # Tworzymy węzeł wewnętrzny (bez znaku), którego częstość to suma dzieci
            wewnetrzny = WezelHuffmana(None, lewy.czestosc + prawy.czestosc)
            wewnetrzny.lewy = lewy
            wewnetrzny.prawy = prawy
            
            heapq.heappush(kopiec, wewnetrzny)

        if kopiec:
            self.korzen = kopiec[0]

    def _generuj_kody(self, wezel: Optional[WezelHuffmana], aktualny_kod: str = "") -> None:
        """
        Przechodzi przez drzewo i generuje słownik kodów dla każdego znaku.
        Złożoność czasowa: O(k)
        """
        if wezel is None:
            return
            
        if wezel.znak is not None:
            self.kody[wezel.znak] = aktualny_kod
            return
            
        self._generuj_kody(wezel.lewy, aktualny_kod + "0")
        self._generuj_kody(wezel.prawy, aktualny_kod + "1")

    def kompresuj(self, tekst: str) -> str:
        """
        Kompresuje tekst wejściowy algorytmem Huffmana.
        Złożoność czasowa: O(n + k log k), gdzie n to długość tekstu, k - unikalne znaki.
        Złożoność pamięciowa: O(n) na skompresowany ciąg binarny.
        """
        if not tekst:
            return ""
            
        self._zbuduj_drzewo(tekst)
        self._generuj_kody(self.korzen)
        
        # Jeśli jest tylko jeden unikalny znak w tekście, przypiszmy mu "0"
        if len(self.kody) == 1:
            znak = list(self.kody.keys())[0]
            self.kody[znak] = "0"
            
        skompresowany = "".join(self.kody[znak] for znak in tekst)
        return skompresowany

    def dekompresuj(self, skompresowany_tekst: str) -> str:
        """
        Odtwarza oryginalny tekst na podstawie drzewa Huffmana.
        Złożoność czasowa: O(n), gdzie n to długość zdekodowanego tekstu.
        """
        if not skompresowany_tekst or self.korzen is None:
            return ""
            
        zdekodowany_tekst = []
        aktualny_wezel = self.korzen
        
        # Obsługa przypadku brzegowego: tylko 1 unikalny znak w całym drzewie
        if aktualny_wezel.lewy is None and aktualny_wezel.prawy is None:
            return aktualny_wezel.znak * len(skompresowany_tekst)

        for bit in skompresowany_tekst:
            if bit == '0':
                aktualny_wezel = aktualny_wezel.lewy
            else:
                aktualny_wezel = aktualny_wezel.prawy
                
            if aktualny_wezel.znak is not None:
                zdekodowany_tekst.append(aktualny_wezel.znak)
                aktualny_wezel = self.korzen
                
        return "".join(zdekodowany_tekst)


def szukaj_kmp(tekst: str, wzorzec: str) -> List[int]:
    """
    Wyszukuje wszystkie wystąpienia wzorca w tekście przy użyciu algorytmu Knuth-Morris-Pratt (KMP).
    Złożoność czasowa: O(n + m), gdzie n to długość tekstu, m to długość wzorca.
    Złożoność pamięciowa: O(m) na tablicę LPS.
    
    Argumenty:
    tekst (str): Dekompresowany tekst, w którym szukamy informacji.
    wzorzec (str): Słowo kluczowe do znalezienia.
    
    Zwraca:
    List[int]: Lista początkowych indeksów, pod którymi znaleziono wzorzec.
    """
    n = len(tekst)
    m = len(wzorzec)
    
    if m == 0 or m > n:
        return []

    # 1. Budowa tablicy LPS (Longest Proper Prefix which is also Suffix)
    lps = [0] * m
    dlugosc = 0
    i = 1
    
    while i < m:
        if wzorzec[i] == wzorzec[dlugosc]:
            dlugosc += 1
            lps[i] = dlugosc
            i += 1
        else:
            if dlugosc != 0:
                dlugosc = lps[dlugosc - 1]
            else:
                lps[i] = 0
                i += 1

    # 2. Wyszukiwanie wzorca
    indeksy_wystapien = []
    i = 0  # indeks dla tekst
    j = 0  # indeks dla wzorzec
    
    while i < n:
        if wzorzec[j] == tekst[i]:
            i += 1
            j += 1
            
        if j == m:
            indeksy_wystapien.append(i - j)
            j = lps[j - 1]
        elif i < n and wzorzec[j] != tekst[i]:
            if j != 0:
                j = lps[j - 1]
            else:
                i += 1
                
    return indeksy_wystapien


def uruchom_modul(tekst_do_zapisu: str, poszukiwany_wzorzec: str) -> Tuple[str, float, List[int]]:
    """
    Główna funkcja orkiestrująca Moduł Archiwalny.
    Kompresuje tekst, dekompresuje go, a następnie wyszukuje zadaną frazę.
    Złożoność czasowa: O(n + m + k log k)
    Złożoność pamięciowa: O(n + m + k)
    
    Zwraca:
    Tuple[str, float, List[int]]: (Skompresowany tekst, współczynnik kompresji, lista wystąpień wzorca).
    """
    # Etap 1: Kompresja (Oszczędzanie papieru)
    kompresor = KompresorHuffmana()
    skompresowany = kompresor.kompresuj(tekst_do_zapisu)
    
    # Obliczenie współczynnika kompresji (założenie: 1 znak = 8 bitów przed kompresją)
    rozmiar_przed = len(tekst_do_zapisu) * 8
    rozmiar_po = len(skompresowany)
    wspolczynnik = rozmiar_po / rozmiar_przed if rozmiar_przed > 0 else 0
    
    # Etap 2: Dekompresja i Wyszukiwanie (Odtwarzanie i znajdowanie informacji)
    odtworzony_tekst = kompresor.dekompresuj(skompresowany)
    wystapienia = szukaj_kmp(odtworzony_tekst, poszukiwany_wzorzec)
    
    return skompresowany, wspolczynnik, wystapienia


def _wczytaj_ksiege(sciezka: str) -> str:
    """Funkcja pomocnicza do wczytywania wiedzy z pliku (jeśli taki istnieje)."""
    try:
        with open(sciezka, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        # Tekst awaryjny, gdyby pliku testowego nie było
        return ("Królewna Śnieżka nadzoruje gotowanie owsianki. Krasnoludki kochają pracę. "
                "Często krasnoludki szmuglują jabłka, choć królewna tego zabroniła. "
                "Owsianki potrzeba coraz więcej, gdy krasnoludki pracują daleko.")


if __name__ == "__main__":
    sciezka_dane = os.path.join(os.path.dirname(__file__), '..', 'data', 'ksiega_wiedzy.txt')
    
    wiedza = _wczytaj_ksiege(sciezka_dane)
    szukana_fraza = "krasnoludki"
    
    print("=== TEST MODUŁU ARCHIWALNEGO (HUFFMAN + KMP) ===")
    print(f"Długość oryginalnego tekstu w księdze: {len(wiedza)} znaków.\n")
    
    skompresowany_bin, wspolczynnik_kompresji, pozycje = uruchom_modul(wiedza, szukana_fraza)
    
    print(f"Tekst skompresowany (fragment): {skompresowany_bin[:50]}...")
    print(f"Współczynnik kompresji (bity po / bity przed): {wspolczynnik_kompresji:.2%}")
    print(f"Zaoszczędzono: {100 - (wspolczynnik_kompresji * 100):.2f}% 'elektronicznego papieru'!\n")
    
    print(f"Wyniki wyszukiwania KMP dla słowa kluczowego '{szukana_fraza}':")
    if pozycje:
        print(f" -> Znaleziono w {len(pozycje)} miejscach. Indeksy początkowe: {pozycje}")
    else:
        print(" -> Nie znaleziono wzorca w zapisanej księdze.")