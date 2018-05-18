#########################
Referentietabel vegetatie
#########################

.. Mogelijke structuur en invulling; voel je vrij voor volledige make-over ...

Samen met de beslisregels voor de bepaling van de :doc:`trofie-<trofie>` en :doc:`zuurgraad<zuur>` vormt de referentietabel het hart van het NICHE Vlaanderen model. De tabel bevat de informatie die de standplaatsvereisten/tolerantiegrenzen (kortweg referentiewaarden) van elk NICHE vegetatietype omschrijft. Het gaat om onder- en bovengrenzen (of klassen) waarbinnen een vegetatietype kan voorkomen. Die grenzen worden gespecifieerd voor elk van de standplaatsfactoren die bepalend zijn voor de ontwikkelingskansen. De referentietabel bepaalt aldus de potenties van de verschillende vegetatietypen die het eindresultaat van NICHE Vlaanderen vormen.

Opbouw referentietabel
======================

De referentietabel van NICHE Vlaanderen kan je `hier <https://github.com/inbo/niche_vlaanderen/blob/master/niche_vlaanderen/system_tables/niche_vegetation.csv>`_ raadplegen. Ze bevat de standplaatsvereisten voor elk vegetatietype, vertaald naar 7 verschillende standplaatsfactoren. De links in onderstaand lijstje verwijzen door naar meer informatie bij de standplaatsfactoren en de aard van de gegevens.

- :doc:`Cijfercode NICHE vegetatietype <vegetatietype.rst>`
- :doc:`Wetenschappelijke naam NICHE vegetatietype <vegetatietype.rst>`
- :ref:`Bodemtype <soil_code>`
- :doc:`Trofiegraad <trofie>`
- :doc:`Zuurgraad <zuur>`
- :ref:`Gemiddeld laagste grondwaterstand <mlw>` (min-max)
- :ref:`Gemiddeld hoogste grondwaterstand <mhw>` (min-max)
- :ref:`Aftoetsing potenties aan beheer <management_vegetation>`
- :ref:`Aftoetsing potenties aan overstromingsregime <inundation_vegetation>`

Oorsprong referentiewaarden
===========================

De referentiewaarden zijn gebaseerd op een uitgebreide set van veldbemonstering van zowel de vegetatie als de (a)biotische omgevingsvariabelen die rechtstreeks of onrechtstreeks gekoppeld zijn aan elk van de :doc:`invoerlagen <invoer>` (zie `Callebaut et al. 2007 <https://pureportal.inbo.be/portal/files/5370206/Callebaut_etal_2007_NicheVlaanderen.pdf>`_).

Gebruik/implementatie
=====================

De referentietabel wordt in NICHE Vlaanderen gebruikt als een codetabel. Een codetabel maakt het mogelijk om een vertaling te maken van de ene waarde (klasse of bereik) naar een andere waarde (veelal een klasse). In het geval van de referentietabel is dat van de waarden voor de verschillende standplaatsfactoren naar één enkele uitspraak over de potentie voor elk van de vegetatietypen, nl. wel of geen potentie (1 of 0). In NICHE Vlaanderen worden ook nog andere codetabellen gebruikt, met name bij de implementatie van de beslisregels voor de trofie- en zuurgraad.

Voor categorische variabelen (nominaal of ordinaal) is de omzetting eenduidig. Voor continue variabelen wordt gewerkt met boven- en ondergrenzen (minimum en maximum). Hier is het belangrijk om duidelijk afspraken te maken:

- zijn de gespecifieerde minima en maxima al dan niet inbegrepen in het bereik
- hoe worden decimale waarden gebruikt bij het aftoetsen aan deze minima en maxima

De enige continue waarden in de referentietabel zijn de gemiddelde :ref:`hoogste <mhw>` en :ref:`laagste <mlw>` grondwaterstanden. De gespecifieerde minima en maxima zitten hier steeds *inbegrepen* in het bereik. En hoewel aangeraden wordt om vooraf de bijhorende invoerlagen van integere (dus geen decimale) waarden te voorzien, worden decimale waarden eerst *afgerond op twee cijfers* na de decimaal en vervolgens vergeleken met de minima en maxima.

Zie ook :doc:`vegetatie`.

Versiebeheer
============

Voortschrijdend wetenschappelijk inzicht en ervaring bij de praktische toepassing van NICHE Vlaanderen kan aanleiding geven tot aanpassingen in de referentietabel. Het is belangrijk dat deze wijzigingen traceerbaar zijn. Daarnaast is het belangrijk op te merken dat de code van ``niche_vlaanderen`` toelaat om de standaard referentietabel die vervat zit in de geïnstalleerde code te overschrijven met een aangepaste tabel.

Documentatie aanpassingen
-------------------------

Implementatie in ``niche_vlaanderen``
-------------------------------------

De laatste versie van de referentietabel wordt steeds mee geïnstalleerd met de laatste versie van NICHE Vlaanderen.
Een waarschuwing verschijnt als je niet over de laatste versie beschikt.

Gebruik van een eigen referentietabel
-------------------------------------

Het is mogelijk om een eigen referentietabel te gebruiken die dan de standaard tabel overschrijft (`interactief <https://inbo.github.io/niche_vlaanderen/advanced_usage.html#Overwriting-standard-code-tables>`_ of via :ref:`configuratiebestand <full_example>`).
Het wordt ten stelligste aangeraden om deze optie doordacht te gebruiken, en de tabel enkel aan te passen op basis van nauwkeurige meetgegevens die op wetenschappelijke wijze verzameld werden.
Bij het gebruik van een eigen referentietabel is het belangrijk te weten dat de tabel moet bestaan uit "comma separated values" (tekstbestand met extentie *.csv). Het scheidingsteken is dus de komma (",") en het decimaal teken bijgevolg de punt (".").

.. onduidelijk welke mogelijkheden er zijn bij de opmaak van een eigen tabel; de standplaatsfactoren liggen vast, maar kan je zomaar vegetatietypen toevoegen, en zoja hoeveel?

