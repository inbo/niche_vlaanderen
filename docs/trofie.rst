################################
Berekening Trofie
################################

Bepaling Stikstofmineralisatie
------------------------------

De stikstofmineralisatie wordt berekend aan de hand van volgende invoergegevens:

* GVG (Gemiddeld Vroegste grondwaterstand)
* Bodemklasse

In combinatie met de tabel `N_mineralisatie`

.. example:: Voor een leembodem (bodemcode L1, cijfercode 140000) en een GVG van 33 cm krijgen we waarde: 75

Bepaling Totale Stikstof
------------------------

De totale Stikstof (N_tot) wordt bepaald als de som van volgende stikstofbronnen:

* N_mineralisatie: Stikstofmineralisatie (vorige stap)
* N_Atm_Deposit: Atmosferische Stikstofdepositie
* N_Mest_Kunst: Kunstmest
* N_Mest_Dier: Dierlijke input 

.. example:: N_tot = N_mineralisatie + N_Atm_Deposit + N_Mest_Kunst + N_Mest_Dier = (75 + 20 + 350 + 0) = 445

Bepaling gecodeerde Trofie
--------------------------

De totale stikstof wordt gecombineerd met het management en het bodemtype om de gecodeerde Trofie te berekenen.
Mogelijke waarden van management worden gegeven in de tabel `Beheer`.

==================================
Cijfercode Beheer        Invloed
---------- ------        -------
0          geen          0
1          Laagfrequent  0
2          begrazing     1
3          hoogfrequent  1

De cijfercode kan met de totale stikstof gebruikt worden om in de tabel `Bodemtrofie` de gecodeerde trofie te berekenen

.. example:: N_tot = 445; Beheer = begrazing (2), dus Invloed = 1; Bodemtype = 14000
  De gecodeerde lithologie is dan  4
  
  management,bodemcijfercode,Ntot_min,Ntot_max,trofie_code,old_min,old_max
  1,140000,418,569,4,640418,640569


Invloed Overstroming
--------------------


