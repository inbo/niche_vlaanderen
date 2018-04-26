###########################
Invoer rasters
###########################

NICHE Vlaanderen berekent de potenties voor vegetatietypes in een gebied op basis van informatie over de (abiotische) standplaatscondities. De standplaatscondities dienen vervat te zijn in de zgn. invoergegevens: ruimtelijke datalagen (rasters) met voor elke standplaatsfactor de toestand voor elke rastercel, uitgedrukt in numerieke vorm, als een continue, ordinale of nominale waarde. Het model combineert de verschillende rasters tot een uitspraak over de potentie voor de verschillende vegetatietypen in elke rastercel op basis van beslisregels.

De betrouwbaarheid van de berekende potenties wordt sterk bepaald door de kwaliteit van de invoergegevens. Het is dan ook nodig te streven naar invoergegevens die de toestand (actueel of toekomstig) zo nauwkeurig mogelijk beschrijven. Hydrologische informatie (grondwaterstanden, overstromingen, kwel) speelt een cruciale rol, aangezien ze doorweegt in zowel de beslisregels als de berekening van potenties voor de vegetatietypen zelf.

Alle invoerdatalagen dienen aangeleverd te worden als rasters (grids). Afhankelijk van de grootte van het studiegebied wordt een voorstel gedaan voor de rasterresolutie (afmetingen rastercel). Alle rasters dienen eenzelfde gebied af te dekken met eenzelfde resolutie. Ook het ruimtelijk referentiesysteem dient hetzelfde te zijn voor alle rasters. 

Om NICHE Vlaanderen in al zijn kunnen toe te passen, zijn 14 invoergrids noodzakelijk. Eén hiervan is optioneel.


.. _soil_code:

Bodemklasse ``soil_code``
=========================

Omschrijving
------------
De bodemkaart die als input dient voor NICHE Vlaanderen is een ecologisch getinte bodemkaart met klassen die niet enkel onderscheiden worden op basis van korrelgrootte (zand-leem-klei), maar ook het gehalte aan organische stof (zuiver mineraal-venig-veen).

Datatype
--------
Nominaal

Mogelijke waarden
-----------------
.. csv-table:: Onderscheiden bodemklassen met hun code en beschrijving ( :ref:`ct_soil_code`)
  :header-rows: 1
  :file: ../niche_vlaanderen/system_tables/soil_codes.csv
  
Eenheid
-------
Geen

Rol in model
------------
De NICHE bodemkaart speelt een rol:

- bij de berekening van zowel de trofie- als de zuurgraad
- bij het rechtstreeks aftoetsen aan de compatibele bodemklassen van elk vegetatietype in de referentietabel `(niche_vegetation.csv) <https://github.com/INBO/niche_vlaanderen/blob/master/niche_vlaanderen/system_tables/niche_vegetation.csv>`_.
- als input bij het doorlopen van bepaalde beslisregels


Beslisregels
Module (trofie/zuurgraad/vegetatie)
Verplicht/optioneel

Brongegevens
------------
Voor het aanmaken van deze ecologische NICHE bodemkaart kan er gebruik gemaakt worden van de Bodemkaart van België, van een gecorrigeerde bodemkaart (op basis van veldgegevens) of er kan gebruik gemaakt worden van een zelf aangemaakte bodemkaart. Er is een Vlaanderen dekkende NICHE bodemkaart voorhanden, waarin voor Vlaanderen de oorspronkelijke bodemcodes van de Belgische Bodemkaart werden omgezet naar de NICHE-codes via een bodemvertaalsleutel (Callebaut et al. 2007). Aan elke polygoon hangt dus de juiste NICHE bodemcode (zowel letter- als cijfercode). Deze NICHE bodemkaart is beschikbaar onder de vorm van een shapefile (link nog toevoegen). Uit deze shapefile kan met gepaste GIS-bewerkingen het gewenste studiegebied geknipt worden en vervolgens verrasterd met de gewenste extent en resolutie.

Opmerkingen
-----------

.. _mxw

Gemiddelde grondwaterstanden (GxG)
==================================

Omschrijving
------------
De diepte van het grondwaterpeil ten opzichte van het maaiveld is voor veel vegetatietypen een uiterst belangrijke standplaatsfactor. De kenmerkende plantensoorten van een (grondwaterafhankelijk) vegetatietype zijn voor hun voortbestaan immers aangewezen op een voldoende vochtvoorziening. Niet enkel de diepte van het grondwater, maar ook de fluctuatie hiervan doorheen het jaar zijn bepalend voor welke soorten op bepaalde plaatsen kunnen groeien.

De meeste plantensoorten verdwijnen ook niet zomaar na kortstondig afwijkende grondwaterpeilen. Vandaar wordt het voorkomen van vegetatietypen niet afgetoetst ten opzichte van grondwaterpeilen die gedurende één enkel jaar of seizoen waargenomen of modelmatig voorspeld worden, maar ten opzichte van gemiddelde grondwaterpeilen over meerdere jaren.

Vandaar wordt voor het berekenen van de invloed van grondwaterpeilen op de potenties van vegetatietypen in NICHE Vlaanderen gebruik gemaakt van gemiddelde grondwaterstanden op bepaalde momenten van het jaar. Er wordt gewerkt met drie afzonderlijke invoerrasters, nl. de Gemiddelde Laagste Grondwaterstand (GLG), de Gemiddelde Voorjaarsgrondwaterstand (GVG) en de Gemiddelde Hoogste Grondwaterstand (GHG).

De waterstandsparameters worden als volgt gedefinieerd (van der Veen et al., 1994)

.. _mhw:

GHG (Gemiddeld hoogste grondwaterstand) ``mhw``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

GHG - gemiddeld hoogste grondwaterstand: het gemiddelde van de drie hoogste grondwaterstanden (GH3) per (hydrologisch) jaar over tenminste 5 jaar bij kleine variatie tussen GH3 en LG3 en over 8 jaar bij grote variatie tussen GH3 en LG3.
Het is een maat voor het hoogste grondwaterniveau in een normale winter.

.. _mlw:

GLG (gemiddeld laagste grondwaterstand) ``mlw``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

GLG - gemiddeld laagste grondwaterstand: het gemiddelde van de drie laagste grondwaterstanden (GL3) per (hydrologisch) jaar over tenminste 5 jaar bij kleine variatie tussen GH3 en LG3 en over 8 jaar bij grote variatie tussen GH3 en LG3.
Het is een maat voor het laagste niveau in een gemiddelde zomer.

.. _msw:

GVG (gemiddeld voorjaarsgrondwaterstand) ``msw``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

GVG - gemiddelde voorjaarsgrondwaterstand: de gemiddelde grondwaterstand aan het begin van het groeiseizoen (= gemiddelde van de drie metingen die het dichtst bij 1 april liggen (GV3); kunnen metingen zijn van twee opeenvolgende hydrologische jaren aangezien hydrologisch jaar start op 1 april).
Indien niet gekend kan de GVG afgeleid worden uit de formule: GVG = 5,4 + 0,83*GHG + 0,19*GLG (in cm).

Datatype
--------
Continu, integer

Mogelijke waarden
-----------------
Voor NICHE Vlaanderen moeten de waarden van de gemiddelde grondwaterstanden uitgedrukt worden in centimeter ten opzichte van het maaiveld. Een tweede aandachtspunt is het teken van de waarden: GXG-waarden boven het maaiveld zijn negatief, waterstanden onder maaiveld positief. 

Eenheid
-------
cm; negatief boven maaiveld, positief onder maaiveld

Rol in model
------------
De gemiddelde grondwaterstanden spelen een rol:

- bij de berekening van zowel de trofie- (GVG) als de zuurgraad (GLG)
- bij het rechtstreeks aftoetsen aan de grenswaarden van GLG en GHG van elk vegetatietype in de referentietabel `(niche_vegetation.csv) <https://github.com/INBO/niche_vlaanderen/blob/master/niche_vlaanderen/system_tables/niche_vegetation.csv>`_.
- als input bij het doorlopen van bepaalde beslisregels

Brongegevens
------------
Indien nodig, moeten de oorspronkelijke waarden omgezet worden naar dit systeem.
Voor Vlaanderen zal dit meestal het geval zijn, vermits waarden boven het maaiveld vaak als positief worden uitgedrukt (bv. in de `WATINA+ databank <http://data.inbo.be/watina/Pages/Common/Default.aspx>`_).

Opmerkingen
------------

.. _seepage:

Kwel ``seepage``
================

Omschrijving
------------
De kwelkaart is een kaart die aangeeft welke kwelflux in iedere cel van toepassing is.
Hoewel deze kaart in principe bestaat uit continue waarden, maakt NICHE Vlaanderen gebruik van de volgende omslagpunten in de beslisregels van het model:

 * kwel < -1 mm/dag veel kwel
 * kwel -1 - -0.1 mm/dag weinig kwel
 * kwel > 0.1 mm/dag geen kwel
 
Negatieve waarden worden gebruikt voor plaatsen waar grondwater uittreedt, positieve waarden
duiden op infiltratie.

Datatype
--------
continu, integer

Mogelijke waarden
-----------------
Negatieve waarden worden gebruikt voor plaatsen waar grondwater uittreedt, positieve waarden
duiden op infiltratie.

Eenheid
-------
mm/dag; negatief waar grondwater uittreedt, postief waar grondwater infiltreert

Rol in model
------------
In NICHE Vlaanderen wordt de kwelflux samen met de :ref:`minerality` van het grondwater, de aanwezigheid van een :ref:´rainwater`, het optreden van overstromingen ( :ref:`inundation_acidity`) en de interactie tussen bodem en grondwaterstand gebruikt om de
zuur-basen toestand (zie :ref:`acidity`) van de bestudeerde locaties in te schatten. Kwel is niet belangrijk als fysische
parameter op zich. De relevante vraag voor het model is of er tijdens een belangrijk deel van het jaar
mineraalrijke kwel uittreedt in de wortelzone. Het type kwel dat van belang is voor NICHE Vlaanderen is een
opwaartse, oppervlakkige grondwaterstroming naar de wortelzone.

Brongegevens
------------
De kwelflux wordt op basis van de resultaten van een tijdsafhankelijk grondwatermodel bepaald. Idealiter wordt de gemiddelde kwel (in mm/dag) per cel en gemodelleerde periode berekend. De manier waarop dit gebeurt kan door de grondwatermodelleerder zelf worden gekozen afhankelijk van de opbouw van het model. 

Bijvoorbeeld:

* DRAIN module in MODFLOW gebruiken, met conditie opgelegd over de ganse gemodelleerde zone, om te bepalen hoeveel kwel al dan niet aanwezig is in een rastercel;
* kwel afleiden uit verschillen in stijghoogtes tussen 2 oppervlakkige lagen in het grondwatermodel: in zones met een ondiepe grondwaterstand (bv. ondieper dan 25 cm) én een opwaartse druk wordt de aanwezigheid van kwel verondersteld.

De gemiddelde kwelflux per cel en per gemodelleerde periode dient als basis voor de berekening van de invoerlagen voor NICHE Vlaanderen. Hiervoor wordt er gekeken in welke zones er gedurende respectievelijk minstens 8, 10 en 12 maanden per (hydrologisch) jaar een opwaarste kweldruk groter dan respectievelijk 0,1 en 1 mm/dag voorkomt, gemiddeld bekeken over de modelperiode. Met andere woorden: is er in cel x gemiddeld meer dan y maanden per jaar minstens z mm/d kwel?

Dit resulteert in 6 binaire invoerlagen die elk op hun verklarende waarde afgetoetst kunnen worden via expertoordeel of na kalibratie van een NICHE Vlaanderen modelrun met de betreffende kwelkaart als input:

Kwel 

-	zones met kwelflux minstens 8 maanden/j < -0,1 mm/dag, gemiddeld over de gemodelleerde periode
-	zones met kwelflux minstens 10 maanden/j < -0,1  mm/dag, gemiddeld over de gemodelleerde periode
-	zones met kwelflux minstens 12 maanden/j < -0,1  mm/dag, gemiddeld over de gemodelleerde periode

Veel kwel (is dus een onderdeel van de overeenkomende lagen voor “kwel”)

-	zones met kwelflux minstens 8 maanden/j < -1 mm/dag, gemiddeld over de gemodelleerde periode
-	zones met kwelflux minstens 10 maanden/j < -1 mm/dag, gemiddeld over de gemodelleerde periode
-	zones met kwelflux minstens 12 maanden/j < -1 mm/dag, gemiddeld over de gemodelleerde periode

Afhankelijk van de opbouw van het grondwatermodel kunnen alternatieve berekeningswijzen voorgesteld worden.

Opmerkingen
-----------

.. _inundation_nutrient:

Overstroming_trofie ``inundation_nutrient``
===========================================
Overstromingskaart – invloed op trofiebepaling

Overstromingen met voedselrijk water die met een zekere regelmaat terug komen, hebben invloed op de trofie van de standplaats die relevant is voor de vegetatie.
Meestal gaat het hier over overstromingen die frequent optreden, bijvoorbeeld jaarlijks.
Men kan bestaande overstromingskaarten gebruiken, eventuele eigen karteringen, of de resultaten van een oppervlaktewatermodel.
Na de omzetting wordt een grid bekomen met overstromingszones die de waarde 1 krijgen; de zones waar er geen overstroming plaats vindt, krijgen een 0-waarde.

Indien het overstromingswater betreft met weinig nutriënten, of wanneer er geen overstromingen plaatsvinden, dan heeft de kaart overal een 0-waarde.

* Mogelijke waarden: 0 of 1

.. _inundation_acidity:

Overstroming_zuurgraad ``inundation_acidity``
=============================================
Overstromingskaart – invloed op pH

Overstromingen hebben in NICHE-Vlaanderen een effect op de zuurgraad van de standplaats.
Overstromingswater heeft meestal een basisch karakter en dient dan mee in rekening gebracht te worden.
Daar waar overstromingen met een zekere regelmaat plaats vinden krijgt de kaart de waarde 1 elders de waarde 0.
Indien het overstromingen betreft met mineraalarm/zuur water (bvb in veengebieden) wordt overal een de waarde 0 gebruikt.

 * Mogelijke waarden: 0 of 1

.. _nitrogen_atmospheric:

Atmosferische depositie ``nitrogen_atmospheric``
================================================
Kaart met overal dezelfde waarde voor atmosferische stikstof depositie (bv 30 N kg/ha/j) of een onderscheid in bossen en graslanden (op basis van het VMM depositiemeetnet).

Er wordt een kaart aangemaakt met voor elke grid de waarde van de atmosferische stikstof depositie in kg-N/ha/jaar.
Informatie over atmosferische deposities vindt men terug in Mira-T-2001
Het gaat hier om een overzichtskaart voor heel Vlaanderen, waaruit de N-depositie van het bestudeerde gebied kan worden afgeleid.

Indien men beschikt over de gegevens van de meetstations uit het depositiemeetnet verzuring (VMM 2005), kan er eventueel ook een onderscheid gemaakt worden tussen de depositie op graslanden en in bossen.
Het onderscheid kan gemaakt worden op basis van een beheerkaart, een actuele vegetatiekaart indien voorhanden of op basis van de Biologische Waarderingskaart (BWK) van het studiegebied.

* Mogelijke waarden: Reële waarden

.. _nitrogen_animal:

Dierlijke bemesting ``nitrogen_animal``
=======================================

Dierlijke bemesting, N kg/ha/j 
Er wordt een kaart aangemaakt met voor elke grid de waarde van de hoeveelheid dierlijke mest in kg-N/ha/jaar. Dit kunnen reële gegevens zijn, of schattingen zoals deze die voor de Nederlandse landgebruikskaart werden ontwikkeld.

 * Mogelijke waarden: Reële waarden

.. _nitrogen_fertilizer:

Kunstmest ``nitrogen_fertilizer``
=================================

Toepassen van kunstmest, N kg/ha/j
Er wordt een kaart aangemaakt met voor elke grid de waarde van de hoeveelheid kunstmest in kg-N/ha/jaar. Dit kunnen reële gegevens zijn, of schattingen zoals deze die voor de Nederlandse landgebruikskaart werden ontwikkeld.

+-----------------------+---------------------------------------------+-----------------------------------------------------------------------------------------------+
| Landgebruik           | Bemesting                                   | Omschrijving                                                                                  |
+=======================+=============================================+===============================================================================================+
| Natuurgebieden        | 0 kg N/ha jaar                              | rietruigten, naaldbossen, loofbossen (broekbossen, populierenaanplanten,…)                    |
|                       |                                             | extensief begraasde gronden                                                                   |
|                       | geen enkele vorm van bemesting              +-----------------------------------------------------------------------------------------------+
|                       |                                             | natuurlijke graslanden, niet bemeste hooilanden                                               |
+-----------------------+---------------------------------------------+-----------------------------------------------------------------------------------------------+
| Extensief landgebruik | 75 kg N/ha jaar                             | intensief begraasde gronden                                                                   |
|                       | Extensieve bemestingsdruk (veelal dierlijk) +-----------------------------------------------------------------------------------------------+
|                       |                                             | weinig bemeste hooilanden                                                                     |
+-----------------------+---------------------------------------------+-----------------------------------------------------------------------------------------------+
| Intensief landgebruik | 350 kg N/ha jaar (dierlijke mest)           | het maaibeheer heeft door de hoge nutriënten-input geen invloed op de trofieberekening meer   |
|                       | + 250 kg N/ha jaar (kunstmest)              |                                                                                               |
+-----------------------+---------------------------------------------+-----------------------------------------------------------------------------------------------+

.. _management:

Beheer ``management``
=====================

Toegepast beheer op percelen.
Er zijn vier klassen gedefinieerd bij het beheer, in de tabel 

Bij de bepaling van trofie wordt enkel rekening gehouden met het hoog frequent beheer (duidelijke afvoer van maaisel).
Bij maaibeheer wordt de trofie één klasse verlaagd. 
Bij bepaling van het potentieel vegetatietype spelen alle beheersklassen een belangrijke rol. 

 * Mogelijke waarden: :ref:`ct_management`, kolom management.

.. _minerality:

Mineraalrijkdom ``minerality``
==============================

Elektrische conductiviteit van het grondwater in µS/cm.

De mineraalrijkdom van het grondwater bepaalt mede de zuurgraad van de standplaats.
et bepalen of een standplaats mineraalrijk dan wel mineraalarm grondwater heeft, kan afgeleid worden uit verschillende variabelen zoals de HCO\ :sup:`3-` en Ca\ :sup:`2+`- concentraties of elektrische conductiviteit van het grondwater.

De waarde bepaalt of er mineralenrijk (1) of mineralenarm (0) grondwater aanwezig is.

De mineraalrijkdom kan bepaald worden op basis van de conductiviteitswaarden (> 500µS/cm), maar ook op basis van expertkennis.

 * Mogelijke waarden: 0 of 1

.. _rainwater:

Regenlens ``rainwater``
=======================

Eventueel voorkomen van regenwaterlenzen wordt aangegeven.

NICHE-Vlaanderen heeft een optie om rekening te houden met de opbouw van regenwaterlenzen. 
Als regenwater onvoldoende kan worden afgevoerd door een drainagesysteem, stagneert het water, en geeft de standplaats een zuur karakter. 
Plaatsen waar de opbouw van regenwaterlenzen mogelijk is worden zuur, zelfs als de grondwaterstanden ondiep zijn en kwel een basisch karakter heeft. 
Er wordt een grid aangemaakt waarbij de locaties waar regenwaterlensen ontwikkelen, de code 1 krijgen. De overige locaties krijgen code 0. 
De informatie zal meestal bekomen worden via expertkennis over het gebied aangezien metingen moeilijk zijn.
Als de nodige informatie voorhanden is, kunnen de voorziene beslisregels worden toegepast.
Bij gebrek aan informatie krijgen alle gridcellen een waarde 0. 

  * Mogelijke waarden: 0 of 1

.. _inundation_vegetation:

Overstroming Vegetatie ``inundation_vegetation``
================================================

Overstromingskaart met invloed op een selectie van vegetatietypes. Er wordt nagegaan welke vegetatietypes kunnen voorkomen bij overstroming en welke niet.
Deze overstromingskaart wordt enkel gebruikt bij het aftoetsen van de vegetatietypes aan de standplaats, op basis van de NICHE-tabel. Er wordt nagegaan welke vegetatietypes kunnen voorkomen bij overstroming en welke niet. Er zijn 3 klassen onderscheiden, nl:

.. csv-table:: Overstromingsklassen
  :header-rows: 1
  :file: ../niche_vlaanderen/system_tables/inundation.csv

Deze overstromingskaart is een samenstelling van overstromingskaarten met verschillende retourperiodes (regelmatig= retourperiode 1 tot 2 jaar, incidenteel =  retourperiode van 5 jaar). 

 * Mogelijke waarden: 0,1 of 2
 * Optioneel grid - de berekening kan ook gebeuren zonder vegetatie.
