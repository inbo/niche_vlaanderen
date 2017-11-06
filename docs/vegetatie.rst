
.. _vegetatie:

#################################
Bepaling vegetatie ``vegetation``
#################################

Na de bepaling van de trofie en de zuurgraadklasse kan de eigenlijke bepaling van de mogelijke vegetatie gebeuren.

Dit gebeurt aan de hand van de tabel :ref:`_ct_niche`.

Optioneel kunnen :ref:`management` en de :ref:`inundation_vegetation` mee als selectiefactor gebruikt worden.


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
    12,Magnocaricion met Phragmites,140000,4,3,14,-37,55,-3,1,1,1
    12,Magnocaricion met Phragmites,140000,4,3,14,-37,55,-3,1,2,1
    16,Lolio-Potentillion anserinae,140000,4,3,30,-26,66,-3,2,0,1
    16,Lolio-Potentillion anserinae,140000,4,3,30,-26,66,-3,2,1,1
    16,Lolio-Potentillion anserinae,140000,4,3,30,-26,66,-3,2,2,1
    16,Lolio-Potentillion anserinae,140000,4,3,30,-26,66,-3,3,0,1
    16,Lolio-Potentillion anserinae,140000,4,3,30,-26,66,-3,3,1,1
    16,Lolio-Potentillion anserinae,140000,4,3,30,-26,66,-3,3,2,1

  Volgende vegetatiecodes kunnen dus voorkomen: 7, 8, 12 en 16.

  Indien ook nog inundantie wordt meegerekend, bvb regelmatig overstromen (1) valt een aantal mogelijke codes weg. Mogelijke codes zijn dan 7, 12 en 16.

.. _simple:

Eenvoudig niche model
=====================

Bij het eenvoudig Niche model wordt enkel rekening gehouden met :ref:`mhw`, :ref:`mlw` en :ref:`soil_code`.
De berekening gebeurt verder gelijkaardig aan bovenstaande berekening, maar vegetatie is mogelijk van zodra die mogelijk is, zonder rekening te houden met de andere invoerwaarden.

.. _deviation:

Afwijking van het eenvoudig niche model
=======================================

Voor veel studies is het niet enkel interessant om na te gaan welke vegetatie kan voorkomen, maar ook welke wijziging in glg of ghg vereist is om een bepaalde vegetatie mogelijk te maken.
Dit kan aan de hand van afwijkingskaarten.