.. _acidity:

###########################################
Bepaling van de zuurgraadklasse ``acidity``
###########################################

.. csv-table:: Zuurgraadklassen in NICHE
  :header-rows: 1
  :file: ../niche_vlaanderen/system_tables/acidity.csv

NICHE berekent de zuurgraad van de standplaats op basis van de :ref:`glg` en het bodemtype. Verdere aanvullingen gebeuren door het in
rekening brengen van overstroming, kwel, en het eventueel voorhanden zijn van
regenwaterlenzen.

Als uitgangspunt geldt dat bij hoge grondwaterstanden de standplaats beïnvloed wordt
door de kenmerken van het grondwater. Bij lage grondwaterstanden kan regenwater
infiltreren en wordt de standplaats zuurder.

Invoergegevens zijn dus:
 * :ref:`bodemklasse`
 * :ref:`glg`
 * :ref:`overstroming_zuur`
 * :ref:`kwel`
 * :ref:`regenlens`

.. _soil_glg_class:

Bepaling Bodem GLG klasse
=========================

In eerste instantie worden 3 bodemgroepen onderscheiden (opm: in het Nederlands model waren dit er 4).

 * Z1 of Z2 of ZV of L of K of KV (minerale bodems);
 * V of V2 (organische bodems);
 * P, HV of KX (hoogveen of keileemgronden).

Elke bodemcode wordt aan een bodemgroep gekoppeld in de tabel `soil_codes.csv <https://github.com/inbo/niche_vlaanderen/blob/master/system_tables/soil_codes.csv>`_.

Op basis van de bodemgroep en de GLG wordt de soil_mlw klasse bepaald.
Dit gebeurt aan de hand van de tabel `soil_mlw_class.csv <https://github.com/inbo/niche_vlaanderen/blob/master/system_tables/soil_mlw_class.csv>`_.

.. topic:: Voorbeeld

  Voor een leembodem (bodemcode L1, bodemcijfercode 140000) en een GLG van 50 cm krijgen we:
  
  .. csv-table:: bodemgroep op basis van bodemcode
    :header-rows: 1

    soil_code,short_code,beschrijving,soil_group
    140000,L1,leem,**1**

  Kijken we verder in de tabel soil_mlw_class met deze bodemgroep (1) en de GLG van 50 cm krijgen we:

  .. csv-table:: soil_mlw_class op basis van bodemtype en GLG
    :header-rows: 1

    soil_group,mlw_min,mlw_max,soil_mlw_class
    1,-999,80,**1**

Bepaling Mineraalrijkdom_klasse
===============================

De reële waarden uit het grid :ref:`mineraalrijkdom` worden geklasseerd op basis van 1 drempelwaarde:
Indien groter dan 500 µS/cm krijgt deze de waarde 2, anders de waarde 1.

.. topic:: Voorbeeld

  In het voorbeeld werd de waarde 400 µS/cm gebruikt. Dit wordt dus klasse 1.

Bepaling Zuurcode
=================

Aan de hand van deze BodemGLGKlasse, de mineralenrijkdom en de gegevens :ref:`regenlens`, overstroming, kwel wordt de zuurcode bepaald.
Dit gebeurt aan de hand van de tabel `lnk_acidity.csv <https://github.com/inbo/niche_vlaanderen/blob/master/system_tables/lnk_acidity.csv>`_.

.. topic:: Voorbeeld

  In de vorige stap werd de BodemGLGKlasse bepaald op 1. Andere invoerwaarden zijn:
   * Regenlens = 1 (niet aanwezig)
   * Mineralenrijkdom: 1
   * Overstroming_zuurgraad = 1
   * Kwel = 1

   Zoeken we deze waarde op in de tabel lnk_acidity.csv krijgen we:

   .. csv-table:: lnk_acidity
     :header-rows: 1
    
     rainwater,mineral_richness,inundation,seepage,soil_mlw_class,acidity
     1,1,1,1,1,**3**

  De bepaalde zuurgraad is dus **3** (neutraal/basisch)
   
