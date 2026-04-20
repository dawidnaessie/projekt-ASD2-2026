import math

class Edge:
    def __init__(self, to, cap, cost, rev_idx):
        self.to = to          # Do jakiego wierzchołka
        self.cap = cap        # Przepustowość
        self.cost = cost      # Koszt
        self.flow = 0         # Aktualny przepływ
        self.rev_idx = rev_idx # Indeks krawędzi powrotnej (dla sieci residualnej)

class MinCostMaxFlow:
    def __init__(self, vertices_count):
        self.V = vertices_count
        self.graph = [[] for _ in range(self.V)]

    def add_edge(self, u, v, cap, cost):
        # Krawędź w przód
        self.graph[u].append(Edge(v, cap, cost, len(self.graph[v])))
        # Krawędź powrotna (rezydualna) - przepustowość 0, ujemny koszt
        self.graph[v].append(Edge(u, 0, -cost, len(self.graph[u]) - 1))

    def solve(self, source, sink):
        total_flow = 0
        total_cost = 0

        while True:
            # Używamy algorytmu SPFA (Bellman-Ford z kolejką) do znalezienia najtańszej ścieżki
            dist = [float('inf')] * self.V
            parent_edge = [-1] * self.V
            parent_node = [None] * self.V
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

            # Jeśli nie ma już drogi od Źródła do Ujścia, kończymy
            if dist[sink] == float('inf'):
                break

            # Szukamy, ile maksymalnie możemy przepchnąć tą ścieżką
            push = float('inf')
            curr = sink
            while curr != source:
                p = parent_node[curr]
                idx = parent_edge[curr]
                push = min(push, self.graph[p][idx].cap - self.graph[p][idx].flow)
                curr = p

            # Aktualizujemy przepływy i dodajemy koszty
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

        return total_flow, total_cost

def zbuduj_i_rozwiaz_siec(dane_krasnoludki, dane_kopalnie):
    """
    Funkcja budująca model 4-etapowy i uruchamiająca MCMF.
    """
    n = len(dane_krasnoludki)
    m = len(dane_kopalnie)
    
    # Wierzchołki:
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
            # Obliczanie odległości euklidesowej (zaokrąglonej do int dla czystości logiki grafu)
            dystans = int(math.hypot(kx - mx, ky - my))
            mcmf.add_edge(i, j, cap=1, cost=dystans)

    # 3. Kopalnie -> Ujście (Pojemność = wydajność, Koszt 0)
    for j, (m_id, mx, my, m_cap) in enumerate(dane_kopalnie, start=n + 1):
        mcmf.add_edge(j, sink, cap=m_cap, cost=0)

    # 4. Rozwiązanie MCMF
    flow, cost = mcmf.solve(source, sink)
    
    # Odzyskiwanie wyników (kto poszedł gdzie)
    przydzialy = []
    for i, (k_id, _, _) in enumerate(dane_krasnoludki, start=1):
        for edge in mcmf.graph[i]:
            if edge.flow > 0: # Jeśli krasnal poszedł tą krawędzią
                idx_kopalni = edge.to - n - 1
                if 0 <= idx_kopalni < m:
                    przydzialy.append((k_id, dane_kopalnie[idx_kopalni][0], edge.cost))

    return flow, cost, przydzialy