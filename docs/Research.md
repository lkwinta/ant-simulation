# Pomysł
- Symulacja ruchu mrówek
- Każda mrówka porusza się zgodnie z kierunkiem silniejszego zapachu feromonu
- Mrówka może odkładać feromon 
- Ślad feromonu znika z czasem, może też ulegać lekkiej dyfuzji

# Opis agenta
Model który chciałbym zaimplementować opisuje artykuł [[2]](#2). Przestrzenią dla mrówek jest zwykła siatka $M \times N$, a mrówki reprezentowane są jako punkty. Wiele mrówek może znajdować się w tym samym miejscu na raz. Mrówki mogą być w dwóch stanach, poszukującym jedzenia *SEARCH* i powrotu do gniazda *RETURN*. Mrówka w fazie *SEARCH*, porusza się stochastycznie z prawdopodobieństwem określonym przez feromon. Mrówka w fazie *RETURN* wraca do gniazda niosąc jedzenie zostawiając feromonowy ślad. Zakładamy, że mrówki znają lokalizację gniazda i wracają prosto do niego używając heurystyki kierunku - w artykule zacytowano badania które pokazują, że mimo iż mrówki zostawiają także w fazie *SEARCH* feromon pomagający im wrócić do gniazda, to istnieje też dodatkowy **silniejszy** czynnik pozwalający mrówką na nawigację powrotną, gdyż nawet dołożenie sztucznych przeszkód spowoduje wybranie optymalnej trasy przez mrówki.

### Ruch agenta
Mrówka porusza się z prawdopodobieństwem zależnym od gradientu feromonu jak opisano w [[2]](#2):

#### Gradient feromonu:

Dla każdego potencjalnego kierunku ruchu $\mathbf{x_a} \in \mathcal{M}(\mathbf{x})$ definiujemy gradientu feromonu $\Delta F_a$ w danym kierunku.

$$
\Delta F_a = F(\mathbf{x}_a + \mathbf{d}_a) - F(\mathbf{x}_a)
$$

#### Waga ruchu w kierunku $a$
$$
\mathcal {W}_a = 
\begin{cases}  
\varepsilon , & 
\text {if} \quad \Delta F_a < 0\\ 
1, & \text {if} \quad \Delta F_a = 0\\ 
1 + \Delta F_a, & \text {if} \quad \Delta F_a > 0 
\end{cases} 
$$

#### Prawdopodobieństwo ruchu w kierunku $a$:

$$
P(a) = \frac{\mathcal{W}_a}{\sum_{b \in \mathcal{M}(\mathbf{x})} \mathcal{W}_b}
$$

### Feromon
W każdym kroku symulacji mrówki zostawiają feromon który "paruje" i ulega dyfuzji. W [[Równanie 1 w 2]](#2) zastosowano równanie różniczkowe opisujące dyfuzję i parowanie feromonu, ja zdecydowałem uprościć to i zastosować zdyskretyzowańą wersję. Depozycja feromonu przez mrówki w fazie *RETURN* jest wykładniczo malejąca z odległością od jedzenia.

#### Depozycja

$$
F(\mathbf{x}, t) = F(\mathbf{x}, t) + Ae^{-\left(\frac{||\mathbf{x}-\mathbf{x_f}||}{\sigma }\right)^2}
$$

gdzie:
* $\mathbf{x}$ - aktualne położenie mrówki
* $\mathbf{x_f}$ - położnie jedzenia z którego wraca mrówka
* $t$ - krok czasowy
* $A > 0$
* $\sigma > 0$

#### Parowanie:

$$
F(\mathbf{x}, t+1) = (1-\rho)F(\mathbf{x}, t)
$$

gdzie:
* $\mathbf{x}$ - aktualnie rozważany punkt siatki
* $\rho \in (0,1)$ - tempo parowania

#### Dyfuzja:

$$
F(\mathbf{x}, t+1) = (1-d)F(\mathbf{x}, t+1) + \frac{d}{|\mathcal{M}|}\sum_{\mathbf{y}\in \mathcal{M}(\mathbf{x})} F(\mathbf{y}, t+1)
$$

gdzie:
* $\mathbf{x}$ - aktualnie rozważany punkt siatki
* $d$ - współczynnik dyfuzji,
* $\mathcal{M}(\mathbf{x})$ - sąsiedztwo punktu $\mathbf{x}$

# Walidacja 
Walidację algorytmu można przeprowadzić poprzez zaobserwowanie zachowań mrówek które powinny być takie jak w prawdziwym świecie.

### Kolektywny wybór trasy
Jak pokazano na [[Fig.2 w 1]](#1) z dwóch równych tras mrówki kolektywnie wybiorą jedną. Na [[Fig.3 w 1]](#1) zaprezentowano rozkład przejść mrówek na jednej z tras w porównaniu do symulacji Monte Carlo, można spróbować porównać podobny rozkład.

### Wzmocnienie lepszej trasy
Zwykle istnieje wiele dróg do jedzenia, lecz poprzez dodatnie sprzężenie zwrotne, mrówki wybiorą krótszą trasę. Przez to, że mrówki daną trasą będą przechodzić szybciej i jest ona krótsza to ślad feromonu jest świeższy, więc więcej mrówek zaczyna nią chodzić wzmacniając ślad feromonu. Jak pokazano w [[3]](#3) 

### Eksploracja przestrzeni
Biorąc wyznaczony fragment przestrzeni eksperymentu możemy porównać rozkład ilości mrówek w czasie w wyznaczonej arenie jak i jej brzegu, rozkład rzeczywisty pokazano na [[Fig.2 w 4]](#4)

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
