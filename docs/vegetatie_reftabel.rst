#########################
Referentietabel vegetatie
#########################

.. Mogelijke structuur

Opbouw referentietabel
======================

Variabelen
----------

- veg_code
- veg_type
- :ref:`Bodemtype <soil_code>`
- :doc:`Trofiegraad <trofie>`
- :doc:`Zuurgraad <zuur>`
- :ref:`Gemiddeld laagste grondwaterstand <mlw>` (min-max)
- :ref:`Gemiddeld hoogste grondwaterstand <mhw>` (min-max)
- :ref:`Aftoetsing potenties aan beheer <management_vegetation>`
- :ref:`Aftoetsing potenties aan overstromingsregime <inundation_vegetation>`

Oorsprong referentiewaarden
===========================
Callebaut et al. 2007

Gebruik/implementatie
=====================
Aftoetsingswijze; gebruik van boven- (max; incl.) en ondergrenzen (min; incl.) bij continue variabelen `mhw` en `mlw`

Zie :doc:`vegetatie`

Versiebeheer
============

Documentatie aanpassingen
-------------------------

Implementatie in NICHE Vlaanderen
---------------------------------

De laatste versie van de referentietabel wordt steeds mee geïnstalleerd met de laatste versie van NICHE Vlaanderen.
Een waarschuwing verschijnt bij als je niet over de laatste versie beschikt.

Gebruik van een eigen referentietabel
-------------------------------------

Het is mogelijk om een `eigen referentietabel te gebruiken <https://inbo.github.io/niche_vlaanderen/advanced_usage.html#Overwriting-standard-code-tables>`_ die dan de standaard tabel overschrijft.
Het wordt ten stelligste aangeraden om deze optie doordacht te gebruiken, en de tabel enkel aan te passen op basis van nauwkeurige meetgegevens die op wetenschappelijke wijze verzameld werden. 

csv bestanden: sep = "," en dec = "."

