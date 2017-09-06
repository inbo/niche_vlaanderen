################################
Berekening Trofie
################################

De Trofie is de mate van voedselrijkdom van de bodem. Deze wordt in NICHE weergegeven als een klassevariabele met waarden tussen 1 en 5.

TODO: figuur

Voorbeeld
~~~~~~~~~
De berekening van de Trofie wordt hieronder geïllustreerd aan de hand van volgende waarden:
 * GVG: 33 cm
 * bodemcode: L1
 * N_mineralisatie: 75
 * N_Atm_Deposit: 20
 * N_Mest_Kunst: 350
 * N_Mest_Dier: 445
 * Management: begrazing (2) 
 * Invloed overstroming: 1

Bepaling Stikstofmineralisatie
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

De stikstofmineralisatie wordt berekend aan de hand van volgende invoergegevens:

* GVG (Gemiddeld Vroegste grondwaterstand)
* Bodemklasse

In combinatie met de tabel `N_mineralisatie`. Daar wordt de N_mineralisatie bepaald met de bodemcijfercode en de min en max waarde voor gvg.

Voorbeeld
---------
Voor een leembodem (bodemcode L1, bodemcijfercode 140000) en een GVG van 33 cm krijgen we waarde: 75

=============== ======= ======= =============== ======= =======
bodemcijfercode gvg_min gvg_max N_mineralisatie old_min old_max
--------------- ------- ------- --------------- ------- -------
140000          30      35       **75**         140030  140035
=============== ======= ======= =============== ======= =======

Bepaling Totale Stikstof
~~~~~~~~~~~~~~~~~~~~~~~~

De totale Stikstof (N_tot) wordt bepaald als de som van volgende stikstofbronnen:

* N_mineralisatie: Stikstofmineralisatie (vorige stap)
* N_Atm_Deposit: Atmosferische Stikstofdepositie
* N_Mest_Kunst: Kunstmest
* N_Mest_Dier: Dierlijke input 

Voorbeeld
---------

N_tot = N_mineralisatie + N_Atm_Deposit + N_Mest_Kunst + N_Mest_Dier = (75 + 20 + 350 + 0) = 445

Bepaling gecodeerde Trofie
~~~~~~~~~~~~~~~~~~~~~~~~~~

De totale stikstof wordt gecombineerd met het management en het bodemtype om de gecodeerde Trofie te berekenen.
Mogelijke waarden van management worden gegeven in de tabel `Management`. 

========== ============= =========
Cijfercode Beheer        Invloed
---------- ------------- ---------
0          geen          0
1          Laagfrequent  0
2          begrazing     1
3          hoogfrequent  1
========== ============= =========

De Invloed die correspondeert met het gekozen management kan met het bodemtype en de totale stikstof gebruikt worden om in de tabel `Bodemtrofie` de gecodeerde trofie te berekenen

Voorbeeld
---------
N_tot = 445; Beheer = begrazing (2), dus Invloed = 1; Bodemtype = 14000

========== =============== ======== ======== =========== ======= =======  
management bodemcijfercode Ntot_min Ntot_max trofie_code old_min old_max
---------- --------------- -------- -------- ----------- ------- -------
1          140000          418      569         **4**    640418  640569
========== =============== ======== ======== =========== ======= =======

De gecodeerde lithologie is dus 4.

Invloed Overstroming
~~~~~~~~~~~~~~~~~~~~

De waarden voor trofie die in de vorige stap berekend werden worden met 1 verhoogd indien er zich overstromingen voordoen. Het is echter niet mogelijk dat de waarde hoger wordt dan 5.

Voorbeeld
---------
De oorspronkelijk gecodeerde lithologie is 4. Door invloed van overstroming wordt dit 5.
