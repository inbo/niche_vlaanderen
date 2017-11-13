.. _trofie:

####################################
Berekening Trofie ``nutrient_level``
####################################

De Trofie (``nutrient_level``) is de mate van voedselrijkdom van de bodem.
Deze wordt in NICHE weergegeven als een klassevariabele met waarden tussen 1 en 5.
Mogelijke waarden worden gegeven in de tabel `nutrient_level.csv <https://github.com/inbo/niche_vlaanderen/blob/master/system_tables/nutrient_level.csv>`_.

.. csv-table:: Trofie klassen
  :header-rows: 1
  :file: ../niche_vlaanderen/system_tables/nutrient_level.csv


De berekening gebeurt in volgende 4 stappen:
 * `Stikstofmineralisatie`_
 * `Bepaling Totale Stikstof`_
 * :ref:`trofie_code`
 * `Invloed Overstroming`_

.. topic:: Voorbeeld

  De berekening van de Trofie wordt in de volgende paragrafen geïllustreerd aan de hand van volgende waarden:
   * GVG: 33 cm
   * bodemcode: L1
   * N_Atm_Deposit: 20
   * N_Mest_Kunst: 0
   * N_Mest_Dier: 350
   * Management: begrazing (2) 
   * Invloed overstroming: 1

.. _stikstofmineralisatie:

Stikstofmineralisatie
=====================

De stikstofmineralisatie (`nitrogen_mineralisation`) wordt berekend aan de hand van volgende invoergegevens:

* :ref:`msw`
* :ref:`soil_code`

In combinatie met de tabel `nitrogen_mineralisation <https://github.com/inbo/niche_vlaanderen/blob/master/system_tables/nitrogen_mineralisation.csv>`_.
Daar wordt de N_mineralisatie bepaald met de bodemcijfercode en de min en max waarde voor gvg.

.. topic:: Voorbeeld
  
  Voor een leembodem (bodemcode L1, bodemcijfercode 140000) en een GVG van 33 cm krijgen we waarde: 75
  
  =============== ======= ======= =======================
  soil_code       msw_min msw_max nitrogen_mineralisation
  --------------- ------- ------- -----------------------
  140000          30      35       **75**        
  =============== ======= ======= =======================

Bepaling Totale Stikstof
========================

De totale Stikstof (N_tot) wordt bepaald als de som van volgende stikstofbronnen:

* :ref:`stikstofmineralisatie` (vorige stap)
* :ref:`nitrogen_atmospheric` (input raster)
* :ref:`nitrogen_fertilizer` (input raster)
* :ref:`nitrogen_animal` (input raster)

.. topic:: Voorbeeld
  
  .. math:: N_{tot} &= N_{mineralisatie} + N_{Atm\_Deposit} + N_{Mest\_Kunst} + N_{Mest\_Dier} \\
                  &= (75 + 20 + 0 + 350) \\
                  &= 445

.. _trofie_code:

Bepaling gecodeerde Trofie
==========================

De totale stikstof wordt gecombineerd met het management en het bodemtype om de gecodeerde Trofie te berekenen.
Mogelijke waarden van beheer worden gegeven in de tabel `Management <https://github.com/inbo/niche_vlaanderen/blob/master/system_tables/management.csv>`_.

.. csv-table:: Management
  :header-rows: 1
  :file: ../niche_vlaanderen/system_tables/management.csv


De Invloed die correspondeert met het gekozen management kan met het bodemtype en de totale stikstof gebruikt worden om in de tabel `lnk_soil_nutrient_level <https://github.com/inbo/niche_vlaanderen/blob/master/system_tables/lnk_soil_nutrient_level.csv>`_ de gecodeerde trofie te berekenen

.. topic:: Voorbeeld

  * Beheer = begrazing(2) dus Invloed = 0
  * Bodemtype = 140000
  * N_tot = 445
  
  ==================== ========= ================== ================== ===========  
  management_influence soil_code total_nitrogen_min total_nitrogen_max nutrient_level
  -------------------- --------- ------------------ ------------------ -----------
  0                    140000    400                10000                 **5**   
  ==================== ========= ================== ================== ===========
  
  De gecodeerde trofie is dus 5.

Invloed Overstroming
====================

De waarden voor trofie die in de vorige stap berekend werden worden met 1 verhoogd indien er zich overstromingen voordoen én de trofie 3 of lager is.

Opmerking: het Vlaamse model wijkt hier af van het oorspronkelijke Nederlandse Niche model waarbij ook waarden van 4 stijgen tot 5 bij overstroming.

.. topic:: Voorbeeld

  De oorspronkelijk gecodeerde trofie is 5.
  Door invloed van overstroming blijft dit 5.
