.. _vegetatie:

##################
Bepaling vegetatie
##################

Na de bepaling van de trofie en de zuurgraadklasse kan de eigenlijke bepaling van de mogelijke vegetatie gebeuren.

Dit gebeurt aan de hand van de tabel `NicheVlTabel <https://github.com/inbo/niche-vlaanderen/blob/master/SystemTables/NicheVlTabel.csv>`_.

Optioneel kunnen :ref:`beheer` en de :ref:`overstroming_vegetatie` mee als selectiefactor gebruikt worden.


.. topic:: Voorbeeld

  Gaan we uit van het voorbeeld dan hebben we in vorige stappen bepaald:

   * Trofie: 4
   * Zuurgraad: 3
  
  Andere invoergegevens zijn:
   * GLG: 50 cm
   * GHG: 10 cm
   * bodemcode: L1 (140000)

  Zoeken we dit op in de tabel NicheVl dan krijgen we volgende opties:

  .. csv-table:: potentiële vegetatie op basis van NICHE
    :header-rows: 1
    
    VEG_CODE,VEG_TYPE,SOIL,TROFIE,ZUURGRAAD,GHG_MIN,GHG_MAX,GLG_MIN,GLG_MAX,MANAGEMENT,INUNDATIE,NAT_SCORE
    7,Caricion gracilis,140000,4,3,31,-32,73,-1,1,1,1
    7,Caricion gracilis,140000,4,3,31,-32,73,-1,1,2,1
    7,Caricion gracilis,140000,4,3,31,-32,73,-1,3,1,1
    7,Caricion gracilis,140000,4,3,31,-32,73,-1,3,2,1
    8,Filipendulion,140000,4,3,80,-31,170,21,1,0,1
    8,Filipendulion,140000,4,3,80,-31,170,21,1,2,1
    9,Galio - Alliarion,140000,4,3,76,14,157,30,1,2,1
    12,Magnocaricion met Phragmites,140000,4,3,14,-37,55,-3,1,1,1
    12,Magnocaricion met Phragmites,140000,4,3,14,-37,55,-3,1,2,1
    13,RG Glyceria maxima,140000,4,3,3,-75,75,30,1,0,1
    13,RG Glyceria maxima,140000,4,3,3,-75,75,30,1,1,1
    13,RG Glyceria maxima,140000,4,3,3,-75,75,30,1,2,1
    16,Lolio-Potentillion anserinae,140000,4,3,30,-26,66,-3,2,0,1
    16,Lolio-Potentillion anserinae,140000,4,3,30,-26,66,-3,2,1,1
    16,Lolio-Potentillion anserinae,140000,4,3,30,-26,66,-3,2,2,1
    16,Lolio-Potentillion anserinae,140000,4,3,30,-26,66,-3,3,0,1
    16,Lolio-Potentillion anserinae,140000,4,3,30,-26,66,-3,3,1,1
    16,Lolio-Potentillion anserinae,140000,4,3,30,-26,66,-3,3,2,1

  Volgende vegetatiecodes kunnen dus voorkomen: 7, 8, 9, 12, 13 en 16.

  Indien ook nog inundantie wordt meegerekend, bvb regelmatig overstromen (1) valt een aantal mogelijke codes weg. Mogelijke codes zijn dan 7, 9, 12, 13 en 16.
