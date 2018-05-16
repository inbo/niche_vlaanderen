.. _nutrient_level:

####################################
Berekening trofie ``nutrient_level``
####################################

Output 
======

De trofie (``nutrient_level``) is de mate van voedselrijkdom van de bodem.
NICHE Vlaanderen genereert een vereenvoudigde kaart van de trofie ingedeeld in 5 klassen (veld ``code``):

.. csv-table:: Trofie klassen
  :header-rows: 1
  :file: ../niche_vlaanderen/system_tables/nutrient_level.csv

Principe
========

NICHE berekent de **stikstofbeschikbaarheid als maat voor de trofie van de standplaats** op basis van:

* het bodemtype
* de gemiddelde voorjaarsgrondwaterstanden (GVG)
* de bemesting met kunstmest
* de bemesting met diermest
* de atmosferische stikstofdepositie
* het beheer
* het al dan niet overstromen met nutriëntenrijk water

Eerst wordt de *jaarlijkse stikstofmineralisatie* bepaald aan de hand van het bodemtype en van de gemiddelde voorjaarsgrondwaterstanden.
De stikstofmineralisatie wordt afgeleid uit de volgende mineralisatiecurven:

.. image:: _static/png/nutrient_mineralcurve.png
   :width: 500px
   :height: 250px

De *totale hoeveelheid stikstof* wordt vervolgens berekend als de som van de mineralisatie, atmosferische depositie en bemesting.

Deze wordt omgezet in een *trofieklasse* rekening houdend met het bodemtype en het beheer (`omzettingstabel <https://github.com/inbo/niche_vlaanderen/blob/master/niche_vlaanderen/system_tables/lnk_soil_nutrient_level.csv>`_):

* de grenzen tussen de trofieklassen variëren naargelang het bodemtype;
* als een hoogfrequent beheer wordt toegepast, verschuiven de grenzen tussen de trofieklassen: een gegeven trofieklasse komt dan overeen met een hogere stikstofhoeveelheid (of met andere woorden: een bepaalde locatie kan meer stikstof tolereren vooraleer de biomassaproductie/trofiegraad toeneemt).

Op de locaties met oligotrofe, mesotrofe en meso-eutrofe condities wordt uiteindelijk nog rekening gehouden met de gevolgen van eventuele overstromingen:
indien er zich overstromingen met nutriëntenrijk water voordoen, wordt er in NICHE Vlaanderen aangenomen dat de nutriëntenrijkdom daardoor met een trofieklasse (extra) toeneemt.

.. image:: _static/png/nutrient_principle.png
     :scale: 100%

.. _nutrient_level_input:

Invoergegevens
==============

 * :ref:`soil_code`
 * :ref:`msw`
 * :ref:`nitrogen_fertilizer`
 * :ref:`nitrogen_animal`
 * :ref:`nitrogen_atmospheric`
 * :ref:`management`
 * :ref:`inundation_nutrient`

Implementatie in het package ``niche_vlaanderen``
=================================================

De berekening gebeurt in volgende 4 stappen:
 * `Stikstofmineralisatie`_
 * `Bepaling Totale Stikstof`_
 * :ref:`trofie_code`
 * `Invloed Overstroming`_

.. topic:: Voorbeeld

  De berekening van de trofie wordt in de volgende paragrafen geïllustreerd aan de hand van volgende waarden:
   * GVG: 33 cm onder maaiveld
   * Bodemcode: L1 (humusarme leemgrond)
   * N atmosferiche depositie: 20 kg/ha/j
   * N kunstmest: 0 kg/ha
   * N diermest: 350 kg/ha
   * Beheer: begrazing (2) 
   * Overstroming met nutriëntenrijk water (1)

.. _stikstofmineralisatie:

Stikstofmineralisatie
---------------------

De stikstofmineralisatie (`nitrogen_mineralisation`) wordt berekend aan de hand van volgende invoergegevens:

* :ref:`msw`
* :ref:`soil_code`

In combinatie met de tabel `nitrogen_mineralisation <https://github.com/inbo/niche_vlaanderen/blob/master/niche_vlaanderen/system_tables/nitrogen_mineralisation.csv>`_.
Daar wordt de N_mineralisatie bepaald met de bodemcijfercode en de min en max waarde voor gvg.

.. topic:: Voorbeeld
  
  Voor een humusarme leembodem (bodemcode L1, bodemcijfercode 14) en een GVG van 33 cm onder maaiveld krijgen we waarde: 75 kg N/ha
  
  =============== ======= ======= =======================
  soil_code       msw_min msw_max nitrogen_mineralisation
  --------------- ------- ------- -----------------------
  L1              30      35       **75**
  =============== ======= ======= =======================

Bepaling totale stikstof
------------------------

De totale stikstof (N_tot) wordt bepaald als de som van volgende stikstofbronnen:

* :ref:`stikstofmineralisatie` (vorige stap)
* :ref:`nitrogen_atmospheric` (input raster)
* :ref:`nitrogen_fertilizer` (input raster)
* :ref:`nitrogen_animal` (input raster)

.. topic:: Voorbeeld
  
  .. math:: N_{tot} &= N_{mineralisatie} + N_{Atm\_Deposit} + N_{Mest\_Kunst} + N_{Mest\_Dier} \\
                  &= (75 + 20 + 0 + 350) \\
                  &= 445 kg N/ha

.. _trofie_code:

Bepaling gecodeerde trofie
--------------------------

De totale stikstof wordt gecombineerd met het type beheer en het bodemtype om de gecodeerde trofie te berekenen.
Mogelijke waarden van beheer worden gegeven in de tabel `Management <https://github.com/inbo/niche_vlaanderen/blob/master/niche_vlaanderen/system_tables/management.csv>`_.

.. csv-table:: Management
  :header-rows: 1
  :file: ../niche_vlaanderen/system_tables/management.csv


De "invloed" die correspondeert met het gekozen management kan met het bodemtype en de
    totale stikstof gebruikt worden om in de tabel `lnk_soil_nutrient_level <https://github.com/inbo/niche_vlaanderen/blob/master/niche_vlaanderen/system_tables/lnk_soil_nutrient_level.csv>`_ de gecodeerde trofie te berekenen

.. topic:: Voorbeeld

  * Beheer = begrazing(2) dus Invloed = 0
  * Bodemtype = L1
  * N_tot = 445 kg N/ha
  
  ==================== ========= ================== ================== ===========  
  management_influence soil_code total_nitrogen_min total_nitrogen_max nutrient_level
  -------------------- --------- ------------------ ------------------ -----------
  0                    L1        400                10000                 **5**
  ==================== ========= ================== ================== ===========
  
  De gecodeerde trofie is dus 5.

Invloed overstroming
--------------------

De waarden voor trofie die in de vorige stap berekend werden worden met 1 verhoogd
indien er zich overstromingen voordoen én de trofie 3 of lager is.

.. topic:: Voorbeeld

  De oorspronkelijk gecodeerde trofie is 5.
  Door invloed van overstroming blijft dit 5.
