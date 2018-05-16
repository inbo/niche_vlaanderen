###################
Overstromingsmodule
###################
 
Inleiding
=========
De optionele post-hoc aftoetsing van de door NICHE Vlaanderen voorspelde potenties van de verschillende vegetatietypen aan de compatibiliteit met het overstromingsregime (cfr. :ref:`inundation_vegetation`) is erg beperkt, zowel naar mogelijke input als naar de nuancering van het eindoordeel. Dat eindoordeel van de post-hoc aftoetsing beperkt zich in NICHE Vlaanderen tot de uitspraak: voorspelde potentie blijft behouden of niet (binair dus). De input in het NICHE Vlaanderen rond overstromingen beperkt zich dan weer tot louter een inschatting van de frequentie van overstroming, en dan nog enkel de hoge frequenties (2-jaarlijks en 5-jaarlijks).
 
De kennis over de tolerantie van vegetaties ten aanzien van overstromingen is beperkt. Vegetaties bestaan immers uit vele plantensoorten die elk hun eigen tolerantie hebben ten aanzien van de verschillende aspecten van overstroming. Dat maakt het moeilijk om de reactie van het amalgaam van soorten, want dat is een vegetatietype in essentie, te voorspellen. Bovendien zijn overstromingen niet alleen verschillend in termen van **tijdstip** en **frequentie** van optreden, maar ook de **duur** en de **diepte** kunnen sterk verschillen. Daarnaast speelt ook de kwaliteit van het overstromingswater een niet onbelangrijke rol. En op al deze variabelen reageert elke plantensoort nog eens verschillend.
 
De invloed van bovengenoemde hoofdeigenschappen van overstromingen op een hele reeks aan vegetatietypen in Vlaanderen werd op basis van expertoordeel en literatuuronderzoek ingeschat door `De Nocker et al. (2007) <https://www.milieuinfo.be/dms/d/d/workspace/SpacesStore/75ad42af-2774-4c3c-8954-374c906c4f48/Eindrapport.pdf>`_ in de studie "Multifunctionaliteit van overstromingsgebieden: wetenschappelijke bepaling van de impact
van waterberging op natuur, bos en landbouw". Hun beoordelingskader werd overgenomen in deze overstromingsmodule na  afstemming op de NICHE Vlaanderen vegetatietypologie (zie :ref:`verder<vegtyp>`). Op die manier is er voor een selectie van de NICHE Vlaanderen vegetatietypen een meer genuanceerde uitspraak mogelijk over de overstromingstolerantie (niet, slecht, matig en goed combineerbaar in plaats van behoud vs verlies van potentie) die bovendien gebaseerd is op meerdere overstromingskarakteristieken die als invoerraster of instelwaarde door de module verwerkt worden (tijdstip, duur, frequentie en diepte). 

In de overstromingsmodule wordt wel abstractie gemaakt van de invloed van oppervlaktewaterkwaliteit. Die kwaliteit is immers moeilijk in te schatten door de sterke variatie ervan in zowel ruimte als tijd. De Nocker et al. (2007) geven wel een extra inschattingsmogelijkheid van de overstromingstolerantie die hiermee op een kwalitatieve manier rekening houdt (nutriëntenrijk vs -arm), maar die werd niet ingebouwd in de module. Het is wel zo dat de door NICHE Vlaanderen berekende potenties wel al indirect rekening houden met het al of niet optreden van overstromingen met :ref:`voedsel-<inundation_nutrient>` en :ref:`mineraalrijk<inundation_acidity>` oppervlaktewater via de berekening van respectievelijk de :doc:`trofie-<trofie>` en :doc:`zuurgraad<zuur>`. Op die manier zit de impact van de samenstelling van het overstromingswater wel al vervat in de potenties die in de overstromingsmodule dan verder afgetoetst worden naar tolerantieniveau met welbepaalde overstromingsregimes.
 
Werking overstromingsmodule
===========================

Werking
-------
De :doc:`overstromingsmodule<flooding>` doet een uitspraak over de overstromingstolerantie op basis van de ruimtelijk expliciete gebiedsinformatie over de waargenomen of gemodelleerde overstromingskarakteristieken (frequentie, tijdstip, duur en diepte). De module werkt als een eenvoudige aftoetsing aan de `referentietabel <https://github.com/inbo/niche_vlaanderen/blob/master/niche_vlaanderen/system_tables/floodplains/lnk_potential.csv>`_ uit De Nocker et al. (2007) die gekoppeld werd aan de verschillende :doc:`NICHE Vlaanderen vegetatietypen <vegetatietype>`. De module kan :doc:`interactief<flooding>` of via een :ref:`configuratiebestand<flood_config>` aangesproken worden.
 
.. _vegtyp:
 
Vegetatietypen
--------------
Niet voor alle 28 vegetatietypen die in NICHE Vlaanderen aan bod komen is er informatie uit De Nocker et al. (2007) voorhanden. De rompgemeenschappen vallen weg, m.u.v. gagelstruweel. In onderstaande tabel staan de NICHE Vlaanderen vegetatietypen opgelijst met hun overeenkomstige natuurtypecode uit de Nocker et al. (2007) waarvan de overstromingstolerantie werd overgenomen.

  .. csv-table:: NICHE Vlaanderen vegetatietypen waarvoor overstromingstolerantie bepaald kan worden (cfr. overeenkomstige natuurtypencode)
    :header-rows: 1
    :file: _data/vegetatietypen_DeNocker.csv
  
Input
=====

De benodigde input voor de overstromingsmodule bestaat uit een invoerraster met de *overstromingsdiepte* voor een welbepaalde *frequentie*/retourperiode. De duur en het tijdstip worden als parameter gespecifieerd.

Mogelijke waarden
-----------------
 
Overstromingsdiepte
^^^^^^^^^^^^^^^^^^^
De overstromingsdiepte dient als een raster aangeleverd te worden met voor elke rastercel de gemeten of voorspelde diepte van de overstroming in ordinale klassen:

  .. csv-table:: Mogelijke diepteklassen van overstroming
    :header-rows: 1
    :file: ../niche_vlaanderen/system_tables/floodplains/depths.csv
 
Het is belangrijk om een duidelijk onderscheid te maken tussen de plaatsen waar effectief geen overstroming voorkomt of voorspeld wordt, en de plaatsen waar er geen uitspraken mogelijk zijn omdat de informatie er ontbreekt en dus niet gekend is. In het eerste geval wordt de waarde 0 toegekend, in het laatste geval een waarde voor "no data".
 
Overstromingsfrequentie
^^^^^^^^^^^^^^^^^^^^^^^
Voor de volgende retourperioden wordt de overstromingstolerantie van de verschillende vegetatietypen ingeschat:

  .. csv-table:: Mogelijke overstromingsfrequenties waarvoor overstromingstolerantie berekend kan worden
    :header-rows: 1
    :file: ../niche_vlaanderen/system_tables/floodplains/frequency.csv

Overstromingsduur
^^^^^^^^^^^^^^^^^
Bij het inschatten van de overstromingstolerantie wordt een onderscheid gemaakt naar korte en langere perioden van aaneensluitende overstroming. Het omslagpunt ligt bij 2 weken.

- 1: < 14 dagen
- 2: > 14 dagen

Overstromingstijdstip
^^^^^^^^^^^^^^^^^^^^^
De impact van overstromingen verschilt alnaargelang het (groei)seizoen. Er wordt een grof onderscheid gemaakt tussen:

- winter
- zomer

Brongegevens
------------

Overstromingsdiepten worden nooit gebiedsdekkend opgemeten. Om toch een gebiedsdekkend beeld te krijgen van (kans op) overstromingen wordt veelal beroep gedaan op eenvoudige of meer complexe oppervlaktewatermodellen. In tegenstelling tot de beperkte informatie die nodig is voor de :doc:`invoerrasters<invoer>` voor NICHE Vlaanderen zelf die verband houden met overstromingen (vaak louter overstroming of geen overstroming), is er voor de overstromingsmodule wél een indicatie nodig van de overstromingsdiepte, duur, frequentie en tijdstip van overstroming. Overstromingsmodellen geven vaak een goed beeld van de diepte en de frequentie. Het tijdstip en de duur van overstroming zijn echter moeilijker te voorspellen. Vandaar is er voor die laatste parameters ook gekozen om ze kwalitatief te benaderen in telkens twee ruwe klassen.

Voor veel valleigebieden in Vlaanderen bestaan er gevalideerde overstromingsgevaarkaarten met een verwachte retourperiode van 10 jaar. Deze zijn raadpleegbaar via www.waterinfo.be of in te laden vanuit `deze ArcGis Map Server <http://inspirepub.waterinfo.be/arcgis/rest/services/gevaarkaarten/MapServer/>`_ ("Grote kans" = retourperiode 10 jaar; "Middelgrote kans" = retourperiode 100 jaar). Alvast voor de retourperiode van 10 jaar is er dus voor veel gebieden een kaart beschikbaar. De overige retourperioden (2, 25 en 50 jaar) worden niet afgedekt. Hiervoor dient de informatie dus zelf verwerkt te worden tot een gebiedsdekkende kaart. De onderscheiden diepteklassen in de overstromingsgevaarkaarten zijn 0-25 cm, 25-50 cm, 50-100 cm, 100-200 cm en >200 cm. De klassegrenzen zijn dus bruikbaar.

Output
======

Op basis van het invoerraster met de overstromingsdiepte bij een welbepaalde retourperiode, duur en periode kan de hypothetische overstromingstolerantie bepaald worden aan de hand van de referentietabel (`Creating a Floodplain model <https://inbo.github.io/niche_vlaanderen/flooding.html#Creating-a-Flooding-model>`_). De uitkomst is dan een raster per vegetatietype met de toleranties (niet, slecht, matig en goed combineerbaar) voor de opgegeven duur en periode. Die hypothetische tolerantie kan vervolgens gecombineerd worden met de voorspelde potenties volgens het NICHE Vlaanderen model (interactief via `Combining the output with niche <https://inbo.github.io/niche_vlaanderen/flooding.html#Combining-the-output-with-niche>`_ of via :ref:`configuratiebestand<flood_config>`). Door die combinatie wordt een meer realistisch beeld verkregen waar de potenties liggen binnen en buiten overstroombaar gebied enerzijds, en anderzijds in welke mate de potenties (voorspeld door NICHE Vlaanderen) behouden blijven binnen de overstroombare gebieden bij een welbepaald overstromingsregime (combinatie diepte-duur-frequentie-tijdstip). De rasters per vegetatietype kennen telkens de volgende mogelijke klassen:

  .. csv-table:: mogelijke codes voor overstromingstolerantie
    :header-rows: 1
    :file: ../niche_vlaanderen/system_tables/floodplains/potential.csv
	
De verschillende rasters zijn ook leerrijk bij het inschatten van de impact van wijzigende overstromingsregimes op de potenties voor vegetatietypen (scenario-analyse).
