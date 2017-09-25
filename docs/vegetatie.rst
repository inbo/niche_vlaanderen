.. _vegetatie:

##################
Bepaling vegetatie
##################

Na de bepaling van de trofie en de zuurgraadklasse kan de eigenlijke bepaling van de mogelijke vegetatie gebeuren.

Dit gebeurt aan de hand van de tabel `niche_vegetation <https://github.com/inbo/niche_vlaanderen/blob/master/SystemTables/niche_vegetation.csv>`_.

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

Example
=======
 .. code-block:: pycon

    >>> import numpy as np
    >>> import niche_vlaanderen
    >>> nutrient_level = np.array([4])
    >>> acidity = np.array([3])
    >>> mlw = np.array([50])
    >>> mhw = np.array([10])
    >>> soil_codes = np.array([140000])
    >>> nv = niche_vlaanderen.Vegetation()
    >>> veg_predict = nv.get_vegetation(soil_codes, nutrient_level, acidity, mhw, mlw)
    >>> for v in veg_predict:
    ...     if (veg_predict[v] == np.array([1])):
    ...             print(v)
    7
    8
    12
    16

Gebruiken we ook de waarde voor overstromingen dan wordt dit.

 .. code-block:: pycon

    >>> inundation = np.array([1])
    >>> veg_predict = nv.get_vegetation(soil_codes, nutrient_level, acidity, 
    ...                 mhw, mlw, inundation=inundation)
    7
    12
    16
