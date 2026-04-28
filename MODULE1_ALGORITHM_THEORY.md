# Teoria Algorytmu: Successive Shortest Path (Busacker-Gowen)

> **Nota architektoniczna:** Poniższy dokument przedstawia klasyczny pseudokod algorytmu *Successive Shortest Path* (znanego również jako algorytm Busackera-Gowena) oparty na autorytatywnej literaturze przedmiotu. W dokumencie wyraźnie wskazano (krok 8), w którym miejscu nasza implementacja w języku Python została celowo i matematycznie zoptymalizowana względem klasycznego podejścia, poprzez całkowite wyeliminowanie obliczania potencjałów wierzchołków.

**Źródło literaturowe:** Ahuja R.K., Magnanti T.L., Orlin J.B., *"Network Flows: Theory, Algorithms, and Applications"*, Rozdział 9.7 (Figure 9.9).

---

## ⚙️ Oryginalny Pseudokod Algorytmu

### INICJALIZACJA:
1. Przepływ początkowy `x := 0`
2. Potencjały wierzchołków `π := 0`
3. Zdefiniuj **`E`** jako zbiór wierzchołków z nadmiarem *(w naszym projekcie: Źródło S)*
4. Zdefiniuj **`D`** jako zbiór wierzchołków z deficytem *(w naszym projekcie: Ujście T)*

### GŁÓWNA PĘTLA:
**Dopóki** zbiór `E` nie jest pusty *(czyli dopóki mamy nieprzydzielonych krasnali)*:
**Początek**
&nbsp;&nbsp;&nbsp;&nbsp;**5.** Wybierz wierzchołek `k ∈ E` (Źródło) oraz `l ∈ D` (Ujście).
&nbsp;&nbsp;&nbsp;&nbsp;**6.** Znajdź najkrótsze odległości `d(j)` ze Źródła do wszystkich innych węzłów w sieci rezydualnej, używając zredukowanych kosztów.
&nbsp;&nbsp;&nbsp;&nbsp;**7.** Niech `P` oznacza najkrótszą ścieżkę od `k` do `l`.

> 🚨 **KLUCZOWA RÓŻNICA W NASZEJ IMPLEMENTACJI:**
> &nbsp;&nbsp;&nbsp;&nbsp;**8.** Zaktualizuj potencjały: `π := π - d`
> 
> *Komentarz inżynierski:* Oryginalny algorytm zakłada wykorzystanie algorytmu Dijkstry (krok 6), który wymaga nieujemnych wag, dlatego Ahuja dodaje utrzymywanie tzw. potencjałów wierzchołków (π) w kroku 8. W naszej implementacji zastąpiono algorytm Dijkstry silnikiem **SPFA (Shortest Path Faster Algorithm)**, który natywnie obsługuje ujemne krawędzie powrotne. Ponieważ udowodniono matematycznie (patrz plik PDF z dowodem), że topologia naszego grafu wyklucza powstawanie ujemnych cykli, **krok 8 został całkowicie usunięty z kodu**, co oszczędza pamięć i redukuje złożoność czasową.*

&nbsp;&nbsp;&nbsp;&nbsp;**9.** Oblicz `δ` = maksimum przepływu, jakie można wepchnąć w ścieżkę `P` 
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;*(nasze szukanie "wąskiego gardła" / w kodzie zmienna `push`).*
&nbsp;&nbsp;&nbsp;&nbsp;**10.** Przepchnij `δ` jednostek przepływu wzdłuż ścieżki `P`.
&nbsp;&nbsp;&nbsp;&nbsp;**11.** Zaktualizuj przepływy (`x`), sieć rezydualną, zbiory `E` i `D` oraz zredukowane koszty *(nasza aktualizacja krawędzi w przód i krawędzi powrotnych o przeciwnym znaku)*.
**Koniec**