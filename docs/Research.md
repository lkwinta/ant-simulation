# Pomysł
- Symulacja ruchu mrówek
- Każda mrówka porusza się zgodnie z kierunkiem silniejszego zapachu feromonu
- Mrówka może odkładać feromon 
- Ślad feromonu znika z czasem, może też ulegać lekkiej dyfuzji

# Walidacja 
Walidację algorytmu można przeprowadzić poprzez zaobserwowanie zachowań mrówek które powinny być takie jak w prawdziwym świecie.

### Samorzutne tworzenie się szlaków
Na początku mrówki będą błądzić prawie losowe, jednak gdy znajdą one jedzenie, wracają do gniazda zostawiając ślad feromonowy. Inne mrówki zaczynają podążać za feromonem do jedzenia, samemu też wzmacniając ślad, co zwabi kolejne mrówki. Stworzą się klasyczne autostrady mrówek które najczęściej obserwujemy w rzeczywistości.

### Wzmocnienie lepszej trasy
Zwykle istnieje wiele dróg do jedzenia, lecz zwykle mrówki wybiorą tą krótszą, powinno stać się to w naturalny sposób - ślad feromonowy na krótszej trasie będzie silniejszy i mrówki będą częściej nią wracać.

### Zanik szlaku po wyczerpaniu jedzenia
Gdy jedzenie się wyczerpie, mrówki przestaną zostawiać feromon i szlak powinien wygasnąć i mrówki powinny się rozproszyć.

### Eksploracja vs Eksploatacja
Manipulując parametrami zachowania mrówki, powinniśmy być w stanie wytworzyć dwa skrajne systemy - mrówki poruszają się chaotycznie, dużo eksplorują - bardzo zamknięty system, mrówki eksploatują pojedyńcze źródło jedzenia. Pośrednie parametry powinny dać stabilny system zbliżony do rzeczywistości.

# Opis agenta
W ruchu mrówki wyróżniamy fazę SEARCH - mrówka wyszła z gniazda i fazę RETURN, mrówka wraca z jedzeniem do gniazda. W fazie SEARCH mrówka zostawia feromon mówiący mrówką o drodze powrotnej do gniazda - "home feromone", a w fazie RETURN feromon prowadzący inne mrówki do jedzenia "food feromone". Analogicznie w fazie SEARCH podążają za "food feromone", a wracając za "home feromone".

### Ruch agenta
Mrówka porusza się z prawdopodobieństwem zależnym od feromonu:

$$
P(i) = \frac{w_i (\varepsilon + F_i)^\alpha}{\sum_{j \in \mathcal{N}} w_j(\varepsilon + F_j)^\alpha}
$$

gdzie:

* $P(i)$ - prawdopodobienstwo ruchu w kierunku i
* $F_i$ - feromon w kierunku $i$, odpowiedni dla fazy "food" lub "home" feromoe
* $\alpha \ge 0$ - czułość na feromon,
* $\varepsilon > 0$ - mała stała, żeby mrówka umiała eksplorować bez feromonu
* $\mathcal{N}$ - zbiór rozważanych kierunków
* $w_i$ - waga ruchu w danym kierunku, żeby mrówka miała "inercję"

### Depozycja feromonu
W fazier RETURN mrówka zostawia feromon na odwiedzanych polach:

$$
F(\mathbf{x}, t) \leftarrow F(\mathbf{x}, t) + q
$$

gdzie:
* $\mathbf{x}$ - aktualne położenie mrówki
* $t$ - krok czasowy
* $q$ - ilość feromonu na krok - można uzależnić od dystansu od jedzenia

### Dyfuzja i parowanie feromonu
W każdym kroku symulacji feromon "paruje" i ulega dyfuzji:

**Parowanie:**
$$
F(\mathbf{x}, t+1) = (1-\rho)F(\mathbf{x}, t)
$$
gdzie:
* $\rho \in (0,1)$ - tempo parowania

**Dyfuzja:**
$$
F(\mathbf{x}, t+1) \leftarrow (1-d)F(\mathbf{x}, t+1) + \frac{d}{|\mathcal{M}|}\sum_{\mathbf{y}\in \mathcal{M}(\mathbf{x})} P(\mathbf{y}, t+1)
$$

gdzie:
* $d$ 0 - współczynnik dyfuzji,
* $\mathcal{M}(\mathbf{x})$ - sąsiedztwo punktu $\mathbf{x}$

# Istniejące narzędzia 
- Net Logo - https://ccl.netlogo.org/netlogo/models/Ants
- GAMA - https://gama-platform.org/wiki/AntsForaging
- MESA - python
- MASON - java
- Agents.jl - julia

# Artykuły
- https://link.springer.com/article/10.1007/s00285-024-02136-2
- https://sci-hub.pl/10.1007/BF01417909
