import os
from src.przydzial_krasnoludkow import zbuduj_i_rozwiaz_siec

def wczytaj_krasnoludki(sciezka):
    krasnoludki = []
    with open(sciezka, 'r', encoding='utf-8') as f:
        for linia in f:
            dane = linia.strip().split()
            if len(dane) == 3:
                krasnoludki.append((dane[0], int(dane[1]), int(dane[2])))
    return krasnoludki

def wczytaj_kopalnie(sciezka):
    kopalnie = []
    with open(sciezka, 'r', encoding='utf-8') as f:
        for linia in f:
            dane = linia.strip().split()
            if len(dane) == 4:
                kopalnie.append((dane[0], int(dane[1]), int(dane[2]), int(dane[3])))
    return kopalnie

def testuj_modul_logistyczny():
    print("="*50)
    print(" START TESTU: Moduł Logistyczny (Dawid Olszewski) ")
    print("="*50)
    
    sciezka_krasnale = os.path.join('data', 'krasnoludki.txt')
    sciezka_kopalnie = os.path.join('data', 'kopalnie.txt')
    
    try:
        krasnoludki = wczytaj_krasnoludki(sciezka_krasnale)
        kopalnie = wczytaj_kopalnie(sciezka_kopalnie)
        
        print(f"Wczytano {len(krasnoludki)} krasnoludków oraz {len(kopalnie)} kopalni.\n")
        
        przeplyw, calkowity_koszt, przydzialy = zbuduj_i_rozwiaz_siec(krasnoludki, kopalnie)
        
        print("--- WYNIKI ---")
        print(f"Ilość krasnoludków, którzy otrzymali pracę (Max Flow): {przeplyw}")
        print(f"Całkowity koszt owsianki (Min Cost): {calkowity_koszt}\n")
        print("--- SZCZEGÓŁOWY PRZYDZIAŁ ---")
        for krasnal, kopalnia, odleglosc in przydzialy:
            print(f"Krasnoludek {krasnal} idzie do Kopalni {kopalnia} (koszt: {odleglosc})")
            
    except FileNotFoundError as e:
        print(f"Błąd! Nie znaleziono pliku: {e}")

if __name__ == "__main__":
    testuj_modul_logistyczny()