
.. _vegetation:

#################################
Bepaling vegetatie ``vegetation``
#################################

Output
======

NICHE Vlaanderen levert als finaal resultaat een uitspraak over het al dan niet aanwezig zijn van potenties voor elk van de vegetatietypen voor elke rastercel binnen het studiegebied. Het is een binair oordeel: wel of geen potentie. Voor elk vegetatietype bestaat het eindresultaat dus uit een raster met waarde 0 (potentie) of 1 (geen potentie).

.. _vegetation_princ:

Principe
========

De uitspraak over wel of geen potentie is het resultaat van een aftoetsing van de afzonderlijke invoerlagen, inclusief de :doc:`trofie- <trofie>` en :doc:`zuurgraad <zuur>` als intermediaire modelresultaten, aan de standplaatsvereisten (referentiewaarden) van elk van de vegetatietypen. Die standplaatsvereisten zitten gebundeld in de zgn. `referentietabel <https://github.com/inbo/niche_vlaanderen/blob/master/niche_vlaanderen/system_tables/niche_vegetation.csv>`_. Op :doc:`deze pagina <vegetatie_reftabel>` wordt de opbouw van deze tabel en het principe van aftoetsing nader uitgelegd.

De standplaatsvereisten zitten vervat in 7 variabelen:

.. csv-table:: Standplaatsvereisten uit referentietabel
    :header-rows: 1

    Variabele, full model, simple model
    :ref:`Bodemtype <soil_code>`, X, X
    :doc:`Trofiegraad <trofie>`, X, 
    :doc:`Zuurgraad <zuur>`, X, 
    :ref:`Gemiddeld laagste grondwaterstand <mlw>`, X, X
    :ref:`Gemiddeld hoogste grondwaterstand <mhw>`, X, X
    :ref:`Aftoetsing potenties aan beheer <management_vegetation>`, ( X ), 
    :ref:`Aftoetsing potenties aan overstromingsregime <inundation_vegetation>`, ( X ), 

De potenties voor vegetatie-ontwikkeling kunnen op twee manieren worden berekend: 

- Enerzijds door het *volledige NICHE Vlaanderen model* (:doc:`full model <getting_started>`) te gebruiken, waarbij de berekende zuurgraad en trofie, het bodemtype en de gemiddelde laagste en hoogste grondwaterstanden mee de potenties bepalen;
- Anderzijds door een *afgeslankte/vereenvoudigde versie* (:ref:`simple model <simple>`) van NICHE Vlaanderen te gebruiken, waarbij enkel een aftoetsing aan de referentiewaarden gebeurt voor het bodemtype en de gemiddelde laagste en hoogste grondwaterstanden ter bepaling van de potenties.

De aftoetsing aan beheer en overstromingsregime is optioneel in het volledige NICHE Vlaanderen model, en gebeurt niet in het vereenvoudigde model.

.. _vegetation_input:

Invoergegevens
==============

- :ref:`Bodemtype <soil_code>`
- :doc:`Trofiegraad <trofie>`
- :doc:`Zuurgraad <zuur>`
- :ref:`Gemiddeld laagste grondwaterstand <mlw>` (min-max)
- :ref:`Gemiddeld hoogste grondwaterstand <mhw>` (min-max)
- :ref:`Aftoetsing potenties aan beheer <management_vegetation>`
- :ref:`Aftoetsing potenties aan overstromingsregime <inundation_vegetation>`

Zie ook bovenstaande tabel.

.. _vegetation_impl:

Implementatie in ``niche_vlaanderen``
=================================================

Voorbeeld volledig model
------------------------

.. topic:: Voorbeeld

  Gaan we uit van het voorbeeld, dan hebben we in vorige stappen bepaald:

   * Trofie: 5 (hypereutroof)
   * Zuurgraad: 3 (neutraal/basisch)
  
  Andere invoergegevens zijn:
   * GLG: 50 cm onder maaiveld
   * GHG: 10 cm onder maaiveld
   * bodemcode: humusarme leembodem L1 (14)

  Zoeken we dit op in de referentietabel van NICHE Vlaanderen, dan krijgen we volgende opties:

  .. csv-table:: potentiële vegetatie op basis van NICHE
    :header-rows: 1
    
    veg_code,veg_type,soil_name,nutrient_level,acidity,mhw_min,mhw_max,mlw_min,mlw_max,management,inundation
    7,Caricion gracilis,L1,4,3,31,-32,73,-1,1,1
    7,Caricion gracilis,L1,4,3,31,-32,73,-1,1,2
    7,Caricion gracilis,L1,4,3,31,-32,73,-1,3,1
    7,Caricion gracilis,L1,4,3,31,-32,73,-1,3,2
    8,Filipendulion,L1,4,3,80,-31,170,21,1,0
    8,Filipendulion,L1,4,3,80,-31,170,21,1,2
    12,Magnocaricion met Phragmites,L1,4,3,14,-37,55,-3,1,1
    12,Magnocaricion met Phragmites,L1,4,3,14,-37,55,-3,1,2
    16,Lolio-Potentillion anserinae,L1,4,3,30,-26,66,-3,2,0
    16,Lolio-Potentillion anserinae,L1,4,3,30,-26,66,-3,2,1
    16,Lolio-Potentillion anserinae,L1,4,3,30,-26,66,-3,2,2
    16,Lolio-Potentillion anserinae,L1,4,3,30,-26,66,-3,3,0
    16,Lolio-Potentillion anserinae,L1,4,3,30,-26,66,-3,3,1
    16,Lolio-Potentillion anserinae,L1,4,3,30,-26,66,-3,3,2

  Volgende vegetatiecodes kunnen dus voorkomen: 7, 8, 12 en 16.

  Indien ook nog inundatie wordt meegerekend, bvb regelmatig overstromen (1) valt een aantal mogelijke codes weg. Mogelijke vegetaties zijn dan 7, 12 en 16.

.. _simple:

Vereenvoudigd model
-------------------

Bij het vereenvoudigde NICHE Vlaanderen model wordt enkel rekening gehouden met :ref:`mhw`, :ref:`mlw` en :ref:`soil_code` als invoerlagen.

Een vereenvoudigd model is vooral geschikt om de directe invloed van (veranderingen in) de grondwaterstanden op de potentie na te gaan. Andere invloedsfactoren zoals de aanvoer van nutriënten, de impact van overstromingen en de mogelijke interactie met beheer worden immers buiten beschouwing gelaten. Een vereenvoudigd model is derhalve transparanter omdat de beslisregels bij de bepaling van de trofie- en zuurgraad niet toegepast worden. De resultaten zijn eenvoudiger te interpreteren, maar boeten uiteraard wel in op nauwkeurigheid/voorspellingskracht omdat abstractie gemaakt wordt van een deel van de realiteit.

Met het package ``niche_vlaanderen`` kan een vereenvoudigd model `interactief <https://inbo.github.io/niche_vlaanderen/getting_started.html#Creating-a-simple-NICHE-model>`_ of via een `configuratiebestand <https://inbo.github.io/niche_vlaanderen/cli.html#simple-model>`_ opgebouwd worden.

.. _deviation:

GXG-afwijkingskaarten voor vereenvoudigd model
----------------------------------------------

Voor veel studies is het niet enkel interessant om na te gaan welke vegetatie kan voorkomen, maar ook -als voor een vegetatietype geen potenties aangegeven worden- welke wijzigingen in glg en ghg vereist zijn om een bepaald vegetatietype alsnog ontwikkelingskansen te geven. Of anders gesteld: wat is de doelafstand tot de gewenste gemiddelde grondwaterstand (gxg) voor elk van de vegetatietypen. 

Met het package ``niche_vlaanderen`` kunnen GXG-afwijkingskaarten `interactief <https://inbo.github.io/niche_vlaanderen/getting_started.html#Creating-a-simple-NICHE-model>`_ of via een `configuratiebestand <https://inbo.github.io/niche_vlaanderen/cli.html#simple-model>`_ aangemaakt worden. Voor elk vegetatietype wordt een afwijkingskaart berekend voor zowel de gemiddelde hoogste als de gemiddelde laagste grondwaterstand. Negatieve waarden wijzen op te natte omstandigheden, positieve waarden op te droge omstandigheden.

.. _scenario_analysis:

Scenario-analyse
----------------

Vaak wordt in studies de impact van verschillende inrichtingsmaatregelen tegen elkaar afgewogen in termen van veranderingen in oppervlakte aan potenties voor welbepaalde vegetatietypen. Verschillende combinaties van inrichtingsmaatregelen worden dan doorgerekend, elk onder de vorm van een afzonderlijk NICHE Vlaanderen model met overeenkomstige invoerlagen die de impact van de maatregelen weerspiegelen. Elke combinatie zit gebundeld in een zgn. scenario. Scenario's worden dan onderling vergeleken door de verschuivingen in oppervlakte aan potenties van de beoogde vegetatietypen te begroten.

Met het package ``niche_vlaanderen`` kan een vergelijking tussen twee modellen/scenario's (volledig of vereenvoudigd) enkel `interactief <https://inbo.github.io/niche_vlaanderen/getting_started.html#Creating-a-simple-NICHE-model>`_ gemaakt worden, niet via een configuratiebestand. De vergelijking kan gebeuren in tabelvorm (voor alle vegetatietypen) of als verschilkaarten voor elk vegetatietype.

.. _zonal_stats:

Gebiedsstatistieken
-------------------

Naast een scenario-analyse is het vaak ook interessant om na te gaan in welke mate potenties verschillen in bepaalde deelzones van een studiegebied. 

Met het package ``niche_vlaanderen`` kan een samenvatting (tabel) van de oppervlakte aan potenties in specifieke deelzones van het studiegebied enkel `interactief <https://inbo.github.io/niche_vlaanderen/advanced_usage.html#Creating-statistics-per-shape-object>`_ opgevraagd worden, niet via een configuratiebestand.
