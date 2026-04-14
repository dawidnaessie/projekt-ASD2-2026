# Podział zadań w zespole (Grupa A)
## Zgodnie z wymaganiami projektowymi, każda osoba odpowiada za dedykowany moduł algorytmiczny:

### **Osoba A:** Moduł logistyczny (`src/przydzial_krasnoludkow.py`).
 - Implementacja algorytmu **Min-Cost Max-Flow** do optymalnego przydziału krasnoludków.
 - Złożoność: $O(F \cdot E \cdot V)$.

### **Osoba B:** Moduł geometryczny (`src/patrol_ksiecia.py`).
 - Implementacja otoczki wypukłej algorytmem **Grahama** (Graham Scan).
 - Złożoność: $O(n \log n)$.

### **Osoba C:** Moduł obronny (`src/dekametrowcy.py`).
 - Implementacja struktury **Drzewa Przedziałowego** dla Range Maximum Query.
 - Złożoność zapytania: $O(\log n)$.

### **Osoba D:** Moduł archiwalny (`src/elektroniczne_ksiegi.py`).
 - Implementacja kompresji **Huffmana** oraz wyszukiwania wzorców algorytmem **KMP**.
 - Złożoność: Huffman $O(k \log k)$, KMP $O(n + m)$
