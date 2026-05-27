# Ant Simulation

Symulacja ruchu mrowek w srodowisku z przeszkodami typu double-diamond. Model jest inspirowany pracami o samoorganizacji tras mrowek i formowaniu sladow feromonowych.

## Model

W symulacji mrowki poruszaja sie po siatce `M x N`. Kazda mrowka moze byc w jednym z dwoch stanow:

- `SEARCH` - szuka jedzenia i wybiera ruch stochastycznie na podstawie lokalnego gradientu feromonu,
- `RETURN` - wraca do gniazda z jedzeniem i zostawia slad feromonowy.

Aktualna implementacja zawiera:

- ruch po sasiedztwie Moore'a,
- blokowanie wejscia w sciany i przechodzenia po skosie przez narozniki przeszkod,
- powrot do gniazda po polu odleglosci liczonym algorytmem BFS,
- depozycje feromonu przez mrowki wracajace do gniazda,
- parowanie i dyfuzje feromonu,
- ograniczenie maksymalnej wartosci feromonu parametrem `max_feromone`,
- generowanie animacji oraz obrazow koncowego stanu symulacji.

Szczegolowy opis modelu znajduje sie w [docs/Research.md](docs/Research.md), scenariusze testowe w [docs/Validation.md](docs/Validation.md), a wnioski w [docs/Conlusion.md](docs/Conlusion.md).

## Zaleznosci

Projekt uzywa [uv](https://docs.astral.sh/uv/) do zarzadzania srodowiskiem. Z repozytorium uruchom:

```bash
uv sync
```

W `pyproject.toml` ustawiona jest wersja Pythona `3.14.*`.

## Uruchomienie pojedynczej symulacji

Glowny skrypt symulacji generuje animacje `.gif` oraz obraz koncowego stanu:

```bash
cd simulation
uv run python simulation.py
```

Domyslne parametry tej symulacji sa zdefiniowane na koncu pliku [simulation/simulation.py](simulation/simulation.py). Wyniki zapisywane sa jako:

- `sim_final.gif`,
- `imgs/sim_final.png`.

## Przeszukiwanie siatki parametrow

Skrypt [simulation/simulation_search.py](simulation/simulation_search.py) uruchamia wiele symulacji dla kombinacji parametrow `A`, `sigma` i `diffusion_rate`:

```bash
cd simulation
uv run python simulation_search.py
```

Obecna siatka parametrow obejmuje:

- `A`: `[3, 5.8, 6, 10]`,
- `sigma`: `[10, 15, 20, 25, 48, 50]`,
- `diffusion_rate`: 20 wartosci z zakresu `[0.005, 0.02]`.

Lacznie daje to 480 konfiguracji. Wyniki zapisywane sa w katalogu `simulation/simulations_full/`.

## Interaktywna wizualizacja

Do szybkiego podgladu modelu mozna uruchomic wizualizacje Mesa/Solara:

```bash
cd simulation
uv run python viz.py
```

Widok pozwala obserwowac agentow, sciany, warstwe feromonu oraz podstawowe metryki modelu.

## Struktura projektu

- [simulation/model.py](simulation/model.py) - glowny model Mesa, siatka, sciany, feromon, dyfuzja i metryki,
- [simulation/agents.py](simulation/agents.py) - agenci mrowek, gniazda i zrodla jedzenia,
- [simulation/double_diamond.py](simulation/double_diamond.py) - generator srodowiska double-diamond,
- [simulation/simulation.py](simulation/simulation.py) - pojedyncza dluga symulacja i zapis animacji,
- [simulation/simulation_search.py](simulation/simulation_search.py) - przeszukiwanie siatki parametrow,
- [simulation/viz.py](simulation/viz.py) - interaktywna wizualizacja Mesa/Solara,
- [docs/](docs/) - opis modelu, walidacja i wnioski.
