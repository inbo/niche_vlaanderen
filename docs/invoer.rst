###########################
Invoer rasters
###########################

De betrouwbaarheid van de berekeningen wordt sterk bepaald door de kwaliteit van de invoergegevens. Het is dan ook nodig te streven naar zo nauwkeurig mogelijke invoergegevens.
De hydrologische informatie (grondwaterstanden, overstromingen, kwel) speelt een cruciale rol, aangezien zij doorweegt in zowel beslisregels als berekening van vegetatietypen zelf.
De graad van nauwkeurigheid daarvan bepaalt de kwaliteit van de NICHE berekeningen.

Alle invoerdatalagen worden aangeleverd onder de vorm van rasters (grids).
Afhankelijk van de grootte van het studiegebied wordt een voorstel gedaan voor de afmetingen van dit grid.
De voorkeur wordt gegeven aan één standaardgrid met één vaste rasterafmeting voor alle invoerdatalagen, dit om extra versnijdingen van de resultaten te vermijden.
Om NICHE toe te passen, zijn 14 invoergrids noodzakelijk.


.. _soil_code:

Bodemklasse ``soil_code``
=========================

Bodemkaart met toegekende NICHE-bodemcodes op basis van een vertaalsleutel of een bodemraster gebaseerd op veldgegevens.

 * Mogelijke waarden: :ref:`ct_soil_code`, kolom ``soil_code``

GxG
===

De gemiddelde grondwaterstanden zitten vervat in drie afzonderlijke invoerrasters, nl. de Gemiddelde Laagste Grondwaterstand (GLG), de Gemiddelde Voorjaarsgrondwaterstand (GVG) en de Gemiddelde Hoogste Grondwaterstand (GHG), in die volgorde.
Voor niche_vlaanderen moeten de waarden van de gemiddelde grondwaterstanden omgezet worden naar centimeter.
Een tweede aandachtspunt is het teken van de waarden.
Bij NICHE worden GXG-waarden boven het maaiveld negatief weergegeven, waterstanden onder maaiveld positief. 
Indien nodig, moeten de oorspronkelijke waarden omgezet worden naar dit systeem.
Voor Vlaanderen zal dit meestal het geval zijn, vermits waarden boven het maaiveld vaak als positief worden uitgedrukt (bvb. in de WATINA databank).

De waterstandsparameters worden als volgt gedefinieerd (van der Veen et al., 1994)

.. _mhw:

GHG (Gemiddeld hoogste grondwaterstand) ``mhw``
-----------------------------------------------

GHG - gemiddeld hoogste grondwaterstand: het gemiddelde van de drie hoogste grondwaterstanden (GH3) in de winterperiode (1 oktober tot 1 april) over tenminste 5 jaar bij kleine variatie tussen GH3 en LG3 en over 8 jaar bij grote variatie tussen GH3 en LG3.
Het is maat voor het hoogste grondwaterniveau in een normale winter.

 * Mogelijke waarden: reële waarden, uitgedruikt in cm onder maaiveld

.. _mlw:

GLG (gemiddeld laagste grondwaterstand) ``mlw``
-----------------------------------------------

GLG - gemiddeld laagste grondwaterstand: het gemiddelde van de drie laagste grondwaterstanden (GL3) in de zomerperiode (1 april tot 1 oktober) over tenminste 5 jaar bij kleine variatie tussen GH3 en LG3 en over 8 jaar bij grote variatie tussen GH3 en LG3.
Het is een maat voor het laagste niveau in een gemiddelde zomer.

 * Mogelijke waarden: reële waarden, uitgedruikt in cm onder maaiveld

.. _msw:

GVG (gemiddeld voorjaarsgrondwaterstand) ``msw``
------------------------------------------------

GVG - gemiddelde voorjaarsgrondwaterstand: de gemiddelde grondwaterstand aan het begin van het groeiseizoen (1 april).
Indien niet gekend kan de GVG afgeleid worden uit de formule: GVG = 5,4 + 0,83*GHG + 0,19*GLG (in cm).

 * Mogelijke waarden: reële waarden, uitgedruikt in cm onder maaiveld

.. _seepage:

Kwel ``seepage``
================

Gemiddelde kwel in mm/dag en negatieve waarden (negatieve waarden worden gebruikt voor plaatsen waar grondwater uittreedt). Positieve waarden duiden op infiltratie.
NICHE rekent met volgende klassegrenzen:

 * kwel < -1 mm/dag veel kwel
 * kwel -1 - -0.1 mm/dag weinig kwel
 * kwel > 0.1 mm/dag geen kwel

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