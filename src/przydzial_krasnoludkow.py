import math
from typing import List, Tuple, Optional

class Edge:
    """
    Reprezentuje skierowaną krawędź w sieci przepływowej.
    """
    def __init__(self, to: int, cap: int, cost: int, rev_idx: int):
        self.to = to            # Do jakiego wierzchołka (ID)
        self.cap = cap          # Przepustowość krawędzi (maksymalny przepływ)
        self.cost = cost        # Koszt przesłania jednostki przepływu
        self.flow = 0           # Aktualny przepływ w krawędzi
        self.rev_idx = rev_idx  # Indeks krawędzi powrotnej w liście sąsiedztwa wierzchołka docelowego

class MinCostMaxFlow:
    """
    Implementacja algorytmu Min-Cost Max-Flow wykorzystująca algorytm SPFA
    (Shortest Path Faster Algorithm) do wyszukiwania najtańszych ścieżek powiększających.
    """
    def __init__(self, vertices_count: int):
        self.V = vertices_count
        self.graph: List[List[Edge]] = [[] for _ in range(self.V)]

    def add_edge(self, u: int, v: int, cap: int, cost: int) -> None:
        """
        Dodaje krawędź skierowaną do sieci przepływowej oraz jej krawędź rezydualną.
        
        Złożoność czasowa: O(1)
        Złożoność pamięciowa: O(1)
        """
        # Krawędź w przód
        self.graph[u].append(Edge(v, cap, cost, len(self.graph[v])))
        # Krawędź powrotna (rezydualna) - przepustowość 0, ujemny koszt
        self.graph[v].append(Edge(u, 0, -cost, len(self.graph[u]) - 1))

    def solve(self, source: int, sink: int) -> Tuple[int, int]:
        """
        Rozwiązuje problem minimalnego kosztu maksymalnego przepływu.
        
        Złożoność czasowa: O(F * V * E), gdzie F to maksymalny przepływ, V - wierzchołki, E - krawędzie
        Złożoność pamięciowa: O(V + E)
        
        Argumenty:
        source (int): Indeks wierzchołka źródła (S).
        sink (int): Indeks wierzchołka ujścia (T).
        
        Zwraca:
        Tuple[int, int]: Zwraca krotkę (całkowity_przepływ, całkowity_koszt).
        """
        total_flow = 0
        total_cost = 0

        while True:
            # Algorytm SPFA do znalezienia najtańszej ścieżki
            dist = [float('inf')] * self.V
            parent_edge = [-1] * self.V
            parent_node = [-1] * self.V
            in_queue = [False] * self.V

            queue = [source]
            dist[source] = 0
            in_queue[source] = True

            while queue:
                u = queue.pop(0)
                in_queue[u] = False

                for idx, edge in enumerate(self.graph[u]):
                    # Jeśli jest wolna przepustowość i znaleziona ścieżka jest tańsza
                    if edge.cap - edge.flow > 0 and dist[edge.to] > dist[u] + edge.cost:
                        dist[edge.to] = dist[u] + edge.cost
                        parent_node[edge.to] = u
                        parent_edge[edge.to] = idx
                        if not in_queue[edge.to]:
                            queue.append(edge.to)
                            in_queue[edge.to] = True

            # Jeśli nie ma już drogi od Źródła do Ujścia, przerywamy pętlę
            if dist[sink] == float('inf'):
                break

            # Szukamy "wąskiego gardła", czyli ile maksymalnie możemy przepchnąć tą ścieżką
            push = float('inf')
            curr = sink
            while curr != source:
                p = parent_node[curr]
                idx = parent_edge[curr]
                push = min(push, self.graph[p][idx].cap - self.graph[p][idx].flow)
                curr = p

            push = int(push)  # Konwersja do int dla spójności z typami danych

            # Aktualizujemy przepływy (w przód i rezydualne) oraz dodajemy koszty
            total_flow += push
            curr = sink
            while curr != source:
                p = parent_node[curr]
                idx = parent_edge[curr]
                rev_idx = self.graph[p][idx].rev_idx
                
                self.graph[p][idx].flow += push
                self.graph[curr][rev_idx].flow -= push
                total_cost += push * self.graph[p][idx].cost
                curr = p

        return int(total_flow), int(total_cost)

def zbuduj_i_rozwiaz_siec(dane_krasnoludki: List[Tuple[str, int, int]], 
                          dane_kopalnie: List[Tuple[str, int, int, int]]) -> Tuple[int, int, List[Tuple[str, str, int]]]:
    """
    Funkcja budująca 4-etapowy model asymetryczny i uruchamiająca MCMF.
    Przetwarza surowe dane wejściowe na strukturę sieci przepływowej.
    
    Złożoność czasowa: O(N * M + F * V * E), gdzie N to liczba krasnali, M to liczba kopalni
    Złożoność pamięciowa: O(N * M) dla grafu pełnego dwudzielnego
    
    Argumenty:
    dane_krasnoludki (List[Tuple[str, int, int]]): Dane krasnoludków w formacie (id, x, y).
    dane_kopalnie (List[Tuple[str, int, int, int]]): Dane kopalni w formacie (id, x, y, pojemność).
    
    Zwraca:
    Tuple[int, int, List[Tuple[str, str, int]]]: (maksymalny_przepływ, minimalny_koszt, lista_przydziałów).
    """
    n = len(dane_krasnoludki)
    m = len(dane_kopalnie)
    
    # Mapowanie wierzchołków:
    # 0: Źródło (S)
    # 1 do n: Krasnoludki
    # n+1 do n+m: Kopalnie
    # n+m+1: Ujście (T)
    source = 0
    sink = n + m + 1
    mcmf = MinCostMaxFlow(vertices_count=sink + 1)

    # 1. Źródło -> Krasnoludki (Pojemność 1, Koszt 0)
    for i in range(1, n + 1):
        mcmf.add_edge(source, i, cap=1, cost=0)

    # 2. Krasnoludki -> Kopalnie (Pojemność 1, Koszt = Odległość)
    for i, (k_id, kx, ky) in enumerate(dane_krasnoludki, start=1):
        for j, (m_id, mx, my, m_cap) in enumerate(dane_kopalnie, start=n + 1):
            # Obliczanie odległości euklidesowej (zaokrąglonej do int dla jednorodności wag)
            dystans = int(math.hypot(kx - mx, ky - my))
            mcmf.add_edge(i, j, cap=1, cost=dystans)

    # 3. Kopalnie -> Ujście (Pojemność = wydajność, Koszt 0)
    for j, (m_id, mx, my, m_cap) in enumerate(dane_kopalnie, start=n + 1):
        mcmf.add_edge(j, sink, cap=m_cap, cost=0)

    # 4. Rozwiązanie MCMF
    flow, cost = mcmf.solve(source, sink)
    
    # Odzyskiwanie wyników (kto poszedł do jakiej kopalni)
    przydzialy = []
    for i, (k_id, _, _) in enumerate(dane_krasnoludki, start=1):
        for edge in mcmf.graph[i]:
            if edge.flow > 0: # Jeśli krasnal poszedł tą krawędzią (przepływ > 0)
                idx_kopalni = edge.to - n - 1
                if 0 <= idx_kopalni < m:
                    przydzialy.append((k_id, dane_kopalnie[idx_kopalni][0], edge.cost))

    return flow, cost, przydzialy