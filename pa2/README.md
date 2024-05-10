# Druga seminarska naloga pri predmetu Iskanje in ekstrakcija podatkov s spleta

V projektu se nahaja implementacija druge seminarske naloge pri predmetu Iskanje 
in ekstrakcija podatkov s spleta.
V direktoriju *input-extraction* se nahajajo vse datoteke treh vrst spletnih strani,
ki smo jih uporabili pri implementaciji različnih strategij za ekstrakcijo podaktov
iz spletnih strani.

Poleg spletnih strani **rtvslo.si** ter **overstock.com**, smo si kot trejo vrsto
spletne strani izbrali spletno stran prodajalne knjig **emka.si**.
Par podobnih spletnih strani smo izbali tako, da smo dobili rezultate ponudbe knjig
v prodajalni za dva različna iskalna niza.

V direktoriju *implemetation-extraction* se nahajaja implementacija strategij za
ekstrakcijo podatkov iz spletnih strani.
V datoteki `run-extraction.py` se nahaja skripta, ki jo pokličemo z ukazom
`python run-extraction.py <nacin>`.
Kjer je `<nacin>` eden izmed znakov **A** (uporaba regex vzorcec), **B** (uporaba
xPath vzorcev) ali **C** (uporaba roadrunner algoritma).
Skripta nato v standardni izhod izpiše ekstrahiratne podatke za vse tri pare spletnih
strani, oz. wrapper v primeru uporabe algoritma RoadRunner.

V skripti `regex.py` se nahajajo regularni izrazi za ekstrakcijo podatkov iz vseh treh
tipov spletnih strani.
V skripti `xPath-extract.py` se nahajajo xPath izrazi za ekstrakcijo podatkov iz vseh treh
tipov spletnih strani.
Funkcije za ekstrakcije podatkov iz posameznega tipa spletne strani pokličemo tako, da
jim podamo html vsebino spletne strani v obliki niza.
V skripti `roadrunner.py` se nahajaja implementacija algoritma RoadRunner.
Funkcijo `get_wrapper(htmls1, htmls2)` za generiranje wrapperja za tip spletne strani pokličemo z dvema nizoma, ki
predstavljata html vsebine sorodnih spletnih strani.