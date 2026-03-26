# Analiza dostępnych narzędzi

## NetLogo
- dostępny prosty model mrówek
- można modyfikować model, lecz nie znam składni tego narzędzia
- nie wiem jak z implementacją bardziej złożonych metryk i eksperymentów
- model podobny do opisanego przeze mnie lecz dystrybucja feromonu jest stała w każdym kroku
- wybór ruchu jest przez wybór silniejszego gradientu z lewo/prawo
- wydajność może być problemem

## GAMMA
- podobnie jak NetLogo, istnieje model mrówek, jest bardziej zaawansowany
- tak samo nie wiem jak z implementacją bardziej złożonych metryk i eksperymentów
- depozycja stała na krok
- ruch nie jest losowy lecz przez wybór trasy
- składnia wygląda na trudną

## MESA
- python, więc łatwość implementacji i modyfikacji modelu
- brak gotowego modelu, trzeba zaimplementować od zera, ale to nie jest duży problem
- duża kontrola, więc na pewno da się zaimplementować bardziej złożone metryki i eksperymenty

## MASON
- Java...
- najlepsza wydajność

# Podsumowanie
Zdecydowałem się wybrać implementację modelu przy pomocy nrzędzia MESA, głównie ze względu na znajomość języka i dużą kontrolę nad implementacją metryk i eksperymentów.