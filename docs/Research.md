# Pomysł
- Symulacja ruchu mrówek
- Każda mrówka porusza się zgodnie z kierunkiem silniejszego zapachu feromonu
- Mrówka może odkładać feromon
- Ślad feromonu znika z czasem, może też ulegać lekkiej dyfuzji
- Przestrzeń zawiera przeszkody, których mrówki nie mogą przekraczać

# Opis agenta
Model który chciałbym zaimplementować opisuje artykuł [[2]](#2). Przestrzenią dla mrówek jest siatka $M \times N$, a mrówki reprezentowane są jako punkty. Mapa zawiera 
ściany, czyli pozycje które są zabronione dla mrówek. Wiele mrówek może znajdować się w tym samym miejscu na raz. Mrówki mogą być w dwóch stanach, poszukującym jedzenia *SEARCH* i powrotu do gniazda *RETURN*. Mrówka w fazie *SEARCH*, porusza się stochastycznie z prawdopodobieństwem określonym przez feromon. Mrówka w fazie *RETURN* wraca do gniazda niosąc jedzenie zostawiając feromonowy ślad. Zakładamy, że mrówki znają lokalizację gniazda i wracają do niego używając pola odległości [[5]](#5) wyliczonego algorytmem BFS, dzięki czemu trasa powrotna respektuje przeszkody.

Ruch jest ograniczony do przechodnich sąsiadów Moore'a. Mrówka nie może wejść w ścianę ani przejść po skosie przez narożnik przeszkody.

### Ruch agenta *SEARCH*
Mrówka porusza się z prawdopodobieństwem zależnym od gradientu feromonu jak opisano w [[2]](#2). W implementacji gradient liczony jest po transformacji logarytmicznej feromonu, żeby ograniczyć wpływ bardzo dużych wartości.

<u>Zmiana względem [[2]](#2): w artykule waga ruchu zależy bezpośrednio od różnicy stężeń feromonu w sąsiedniej i aktualnej komórce. W tej implementacji najpierw stosuję transformację $G(\mathbf{x}) = \log(1 + F(\mathbf{x}))$, ponieważ w wersji dyskretnej okazała się stabilniejsza numerycznie i ogranicza dominację pojedynczych komórek o bardzo dużym stężeniu feromonu.</u>

#### Gradient feromonu:

Dla każdego potencjalnego kierunku ruchu do komórki $\mathbf{y} \in \mathcal{M}_p(\mathbf{x})$ definiujemy gradient feromonu $\Delta F(\mathbf{x}, \mathbf{y})$ w danym kierunku.

$$
G(\mathbf{x}) = \log(1 + F(\mathbf{x}))
$$

$$
\Delta F(\mathbf{x}, \mathbf{y}) = G(\mathbf{y}) - G(\mathbf{x})
$$

gdzie $\mathcal{M}_p(\mathbf{x})$ oznacza sąsiedztwo punktu $\mathbf{x}$ po odfiltrowaniu ścian i niedozwolonych ruchów diagonalnych.

#### Waga ruchu w kierunku $\mathbf{y}$
$$
\mathcal {W}(\mathbf{x}, \mathbf{y}) =
\begin{cases}
\varepsilon , &
\text {if} \quad \Delta F(\mathbf{x}, \mathbf{y}) < 0\\
1, & \text {if} \quad \Delta F(\mathbf{x}, \mathbf{y}) = 0\\
1 + \Delta F(\mathbf{x}, \mathbf{y}), & \text {if} \quad \Delta F(\mathbf{x}, \mathbf{y}) > 0
\end{cases}
$$

Jeżeli kandydat ruchu był odwiedzony niedawno, jego waga jest dodatkowo mnożona przez $0.01$. W implementacji mrówka pamięta ostatnie 10 pozycji, co ogranicza krótkie oscylacje.

#### Prawdopodobieństwo ruchu do komórki $\mathbf{y}$:

$$
P(\mathbf{x} \to \mathbf{y}) = \frac{\mathcal{W}(\mathbf{x}, \mathbf{y})}{\sum_{\mathbf{z} \in \mathcal{M}_p(\mathbf{x})} \mathcal{W}(\mathbf{x}, \mathbf{z})}
$$

### Ruch agenta *RETURN*
W fazie *RETURN* według artykułu [[2]](#2) mrówka porusza się do gniazda algorytmem Beeline, czyli wybiera kierunek który jest najbardziej zbliżony do kierunku gniazda. W obecnej implementacji zastąpiłem prostą heurystykę euklidesową polem odległości od gniazda, liczonym raz przy inicjalizacji modelu algorytmem BFS. Dzięki temu powrót uwzględnia ściany i dostępne korytarze.

#### Dystans od gniazda:
Podstawą wyboru kierunku jest dystans od gniazda w sensie najkrótszej liczby dozwolonych kroków po siatce, więc wprowadzam funkcję która dla danego punktu $\mathbf{y}$ zwraca jego odległość od gniazda:

$$
D(\mathbf{x_g}) = 0
$$

$$
D(\mathbf{y}) = \min_{\pi: \mathbf{y} \to \mathbf{x_g}} |\pi|
$$

gdzie:
* $\mathbf{y}$ - rozważany punkt
* $\mathbf{x_g}$ - położenie gniazda
* $\pi$ - ścieżka złożona tylko z dozwolonych ruchów po przechodnich komórkach

Jeżeli punkt nie jest osiągalny z gniazda, to $D(\mathbf{y}) = \infty$.

#### Wybór potencjalnych punktów ruchu:
Jako kandydatów do ruchu wybieram tylko te punkty które są bliżej gniazda niż aktualna pozycja mrówki, o ile to możliwe, czyli:

$$
\mathcal{B}(\mathbf{x}) = {\{\mathbf{y} \in \mathcal{M}_p(\mathbf{x}) : D(\mathbf{y}) < D(\mathbf{x})\}}
$$
gdzie:
* $\mathbf{x}$ - aktualne położenie mrówki
* $\mathbf{x_g}$ - położenie gniazda
* $\mathcal{M}_p(\mathbf{x})$ - sąsiedztwo punktu $\mathbf{x}$ po odfiltrowaniu ścian i niedozwolonych ruchów

W implementacji mrówka dodatkowo unika natychmiastowego powrotu do poprzedniej komórki, jeśli istnieje inny sensowny kandydat. Jeżeli nie ma ruchu zmniejszającego $D$, wybierany jest ruch o skończonej wartości $D$. Do losowania brane są maksymalnie trzy najlepsze komórki.

#### Prawdopobieństwo ruchu z $\mathbf{x}$ do $\mathbf{y}$:
$$
P(\mathbf{x} \to \mathbf{y}) = \frac{(D(\mathbf{y}) + \epsilon)^{-1}}{\sum_{\mathbf{z} \in \mathcal{B}(\mathbf{x})} (D(\mathbf{z}) + \epsilon)^{-1}}
$$

gdzie:
* $\mathbf{x}$ - aktualne położenie mrówki
* $\mathbf{y}$ - potencjalne nowe położenie mrówki
* $\mathbf{x_g}$ - położenie gniazda
* $\epsilon > 0$ - mała stała, żeby uniknąć dzielenia przez zero i dać możliwość eksploracji
* $\mathcal{B}(\mathbf{x})$ - zbiór sąsiadujących punktów do których mrówka może się poruszyć z $\mathbf{x}$
### Feromon
W każdym kroku symulacji mrówki w fazie *RETURN* zostawiają feromon który "paruje" i ulega dyfuzji. W [[Równanie 1 w 2]](#2) zastosowano równanie różniczkowe opisujące dyfuzję i parowanie feromonu, ja zdecydowałem uprościć to i zastosować zdyskretyzowaną wersję. Depozycja feromonu przez mrówki w fazie *RETURN* jest wykładniczo malejąca z odległością od jedzenia. Wartość feromonu jest ograniczana od góry parametrem $F_{max}$, czyli `max_feromone`.

#### Depozycja

W implementacji odległość od jedzenia liczona jest metryką Czebyszewa:

$$
d_f(\mathbf{x}) = \max(|x_1 - x_{f,1}|, |x_2 - x_{f,2}|)
$$

Depozycja ma postać:

$$
F(\mathbf{x}, t) = \min\left(F_{max}, F(\mathbf{x}, t) + Ae^{-\frac{d_f(\mathbf{x})}{\sigma}}\right)
$$

<u>Zmiana względem [[2]](#2): artykuł używa depozycji malejącej jak $Ae^{-\left(\frac{||\mathbf{x}-\mathbf{x_f}||}{\sigma}\right)^2}$, czyli z normą euklidesową i kwadratem w wykładniku. W implementacji dyskretnej zastąpiłem ją metryką Czebyszewa oraz pominąłem kwadraty, otrzymując prostszy spadek $Ae^{-d_f(\mathbf{x})/\sigma}$. Taka postać lepiej pasuje do ruchu po sąsiedztwie Moore'a, gdzie jeden krok diagonalny ma taki sam koszt jak krok poziomy lub pionowy.</u>

gdzie:
* $\mathbf{x}$ - aktualne położenie mrówki
* $\mathbf{x_f}$ - położnie jedzenia z którego wraca mrówka
* $t$ - krok czasowy
* $A > 0$
* $\sigma > 0$
* $F_{max}$ - maksymalna dopuszczalna wartość feromonu w komórce

#### Parowanie:

$$
F(\mathbf{x}, t+1) = (1-\rho)F(\mathbf{x}, t)
$$

gdzie:
* $\mathbf{x}$ - aktualnie rozważany punkt siatki
* $\rho \in (0,1)$ - tempo parowania

#### Dyfuzja:

Podczas implementacji wyszło, że prosty wzór może powodować niepożądane zachowanie na krawędziach i przeszkodach, więc dyfuzja jest liczona po ośmiu sąsiadach Moore'a, z wyzerowaniem wartości feromonu w ścianach.

$$
F_{new}(\mathbf{x}, t+1) = (1-\lambda)F(\mathbf{x}, t) + \frac{\lambda}{8}\sum_{\mathbf{s}\in \mathcal{S}} F(\mathbf{x}-\mathbf{s}, t)
$$

gdzie:
* $\mathbf{x}$ - aktualnie rozważany punkt siatki
* $\lambda$ - współczynnik dyfuzji,
* $\mathcal{S}$ - osiem przesunięć sąsiedztwa Moore'a

Przed dyfuzją i po dyfuzji feromon w ścianach jest ustawiany na $0$. Po parowaniu i dyfuzji wartości są obcinane do zakresu:

$$
0 \le F(\mathbf{x}, t) \le F_{max}
$$

# Walidacja
Walidację algorytmu można przeprowadzić poprzez zaobserwowanie zachowań mrówek które powinny być takie jak w prawdziwym świecie.

### Kolektywny wybór trasy
Jak pokazano na [[Fig.2 w 1]](#1) z dwóch równych tras mrówki kolektywnie wybiorą jedną. Na [[Fig.3 w 1]](#1) zaprezentowano rozkład przejść mrówek na jednej z tras w porównaniu do symulacji Monte Carlo, można spróbować porównać podobny rozkład.

### Wzmocnienie lepszej trasy
Zwykle istnieje wiele dróg do jedzenia, lecz poprzez dodatnie sprzężenie zwrotne, mrówki wybiorą krótszą trasę. Przez to, że mrówki daną trasą będą przechodzić szybciej i jest ona krótsza to ślad feromonu jest świeższy, więc więcej mrówek zaczyna nią chodzić wzmacniając ślad feromonu. Jak pokazano w [[3]](#3)

### Eksploracja przestrzeni
Biorąc wyznaczony fragment przestrzeni eksperymentu możemy porównać rozkład ilości mrówek w czasie w wyznaczonej arenie jak i jej brzegu, rozkład rzeczywisty pokazano na [[Fig.2 w 4]](#4)

### Przeszkody
W obecnym modelu dodatkowym testem jest sprawdzenie, czy mrówki respektują ściany: nie wchodzą w komórki ścian i nie przechodzą diagonalnie przez narożniki. Dotyczy to zarówno eksploracji, jak i powrotu do gniazda po polu BFS.

### Inne
Artykuł [[4]](#4) opisuje także więcej różnych bardziej wyrafinowanych cech mrówek, jak np. rozkład zmiany kierunku ruchu mrówek w czasie.
Ciekawym testem może być sprawdzenie czy zachodzi taka korelacja lub zmiana modelu ruchu na opisany w [[4]](#4) i [[1]](#1) i dany równaniem:

$$
P(i) = \frac{(\varepsilon + F_i)^\alpha}{\sum_{j \in \mathcal{N}} (\varepsilon + F_j)^\alpha}
$$

gdzie:

* $P(i)$ - prawdopodobienstwo ruchu w kierunku i
* $F_i$ - feromon w kierunku $i$
* $\alpha \ge 0$ - czułość na feromon,
* $\varepsilon > 0$ - mała stała, żeby mrówka umiała eksplorować bez feromonu
* $\mathcal{N}$ - zbiór rozważanych kierunków

# Istniejące narzędzia
- Net Logo - https://ccl.netlogo.org/netlogo/models/Ants
- GAMA - https://gama-platform.org/wiki/AntsForaging
- MESA - python
- MASON - java
- Agents.jl - julia

# Bibliografia
<a id="1">[1]</a>
Deneubourg, J.L., Aron, S., Goss, S. et al. The self-organizing exploratory pattern of the argentine ant. J Insect Behav 3, 159–168 (1990). https://doi.org/10.1007/BF01417909

<a id="2">[2]</a>
Hartman, S., Ryan, S.D. & Karamched, B.R. Walk this way: modeling foraging ant dynamics in multiple food source environments. J. Math. Biol. 89, 41 (2024). https://doi.org/10.1007/s00285-024-02136-2

<a id="3">[3]</a>
Goss, S., Aron, S., Deneubourg, J.L. et al. Self-organized shortcuts in the Argentine ant. Naturwissenschaften 76, 579–581 (1989). https://doi.org/10.1007/BF00462870

<a id="4">[4]</a>
Perna A, Granovskiy B, Garnier S, Nicolis SC, Labédan M, et al. (2012) Individual Rules for Trail Pattern Formation in Argentine Ants (Linepithema humile). PLOS Computational Biology 8(7): e1002592. https://doi.org/10.1371/journal.pcbi.1002592

<a id="5">[5]</a>
Simonin, O., Charpillet, F., Thierry, E. (2014). Revisiting wavefront construction with collective agents: an approach to foraging. Swarm Intelligence, 8, 113-138. DOI:  https://doi.org/10.1007/s11721-014-0093-3
