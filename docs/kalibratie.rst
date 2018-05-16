###########
Kalibratie 
###########

Het model moet gekalibreerd worden op basis van een gekende referentietoestand. Meestal (en ook verder als voorbeeld in dit document) wordt de actuele toestand hiervoor gebruikt. 

Bij de kalibratie worden **de beschikbare biotische** (vegetatiekaarten) 
**en abiotische gegevens** (terreinmetingen en modelberekeningen) **vergeleken met de outputlagen van NICHE** (zuur- en trofiegraad, potenties).

Kalibratie trofie- en zuurgraad
===============================

Tijdens een eerste kalibratiestap wordt er gekeken of de door NICHE berekende trofie en zuurgraad 
in overeenstemming zijn met de beschikbare abiotische gegevens. Hierbij kunnen bv. veldmetingen van bodem pH vergeleken 
worden met de voorspellingen van NICHE Vlaanderen voor de zuurgraad. 

Deze stap heeft natuurlijk enkel betrekking op de kalibratie voor het volledige (`full <https://inbo.github.io/niche_vlaanderen/getting_started.html#Running-a-full-Niche-model>`_) NICHE model. In het vereenvoudigde (`simple <https://inbo.github.io/niche_vlaanderen/getting_started.html#Creating-a-simple-NICHE-model>`_) model wordt immers geen rekening gehouden met de trofie- en zuurgraad bij de bepaling van de potenties.

Kalibratie potenties/vegetatievoorspellingen
============================================

Tijdens een tweede kalibratiestap wordt dan gekeken of op de plaatsen waar een vegetatietype actueel aanwezig is, 
ook effectief potenties voorspeld worden. Hoe groter de actuele oppervlakte waarvoor potentie opgegeven wordt, hoe beter. 
En, omgekeerd, hoe minder potentie voorspeld wordt binnen het actuele voorkomen, hoe slechter. 
Plaatsen waar potenties voorspeld worden, maar het vegetatietype actueel niet aanwezig is, zijn niet per se foutief, maar kunnen bv. het gevolg zijn 
van het toegepaste beheer. 

Om deze tweede kalibratiestap uit te voeren is er dus ook nood aan een overzicht van de *actuele verspreiding van de NICHE vegetatietypen*.
Hiervoor kan een beroep worden gedaan op 
eigen vegetatiekaarten of op de `Biologische Waarderingskaart(BWK)-Habitatkaart <https://www.inbo.be/nl/beschikbaarheid>`_ van het `Instituut voor Natuur- en Bosonderzoek <https://www.inbo.be>`_. 

Een indicatieve vertaalsleutel tussen de Europese habitattypen en regionaal belangrijke biotopen 
(rbb) die in de Habitatkaart worden gebruikt, en de NICHE vegetatietypen, wordt in de 
tabel `niche_hab_rbb.csv <https://github.com/inbo/niche_vlaanderen/blob/master/docs/_data/niche_hab_rbb.csv>`_ gegeven.

Een **kalibratiescore** kan per vegetatietype worden berekend als de mate waarin de actuele aanwezigheid van het type voorspeld wordt 
door het NICHE Vlaanderen model in het studiegebied. Hiervoor wordt gekeken *hoe groot de 
oppervlakte is met voorspelde potentie binnen elke polygoon van de actuele vegetatiekaart* (bv. de BWK-habitatkaart) waarbinnen het vegetatietype actueel 
aanwezig is. 

Als er gebruik wordt gemaakt van de BWK-habitatkaart moet ermee rekening gehouden worden dat niet elke polygoon uitsluitend één enkel vegetatietype bevat. 
Soms worden meerdere vegetatietypen 
toegekend aan één enkele polygoon. Elk aanwezig vegetatietype krijgt dan tijdens de kartering een aandeel (%) toegekend in de oppervlakte van de polygoon 
(veld “PHABx”, met x de volgorde volgens afnemend aandeel van de verschillende vegetatietypen). Dat aandeel kan worden verrekend 
in de kalibratiescore. Is een vegetatietype bv. slechts in 30% van de polygoonoppervlakte aanwezig, dan bedraagt de 
kalibratiescore op basis van die ene polygoon 100% van zodra er voor minstens  30% van de polygoonoppervlakte potenties 
worden voorspeld. Dit is een louter boekhoudkundige aftoetsing omdat er abstractie gemaakt wordt van de effectieve 
ruimtelijke overlap tussen potentie en aanwezigheid. De juiste actuele ligging van de oppervlakte van een vegetatie 
in “complex” is immers niet gekend.

Kalibratieresultaten verbeteren
===============================

Als er systematische afwijkingen tijdens de kalibratie aan het licht komen moeten de **invoerlagen** van het model onder de loep worden genomen.

Hieronder geven we een (niet limitatief) overzicht van de aandachtspunten per inputlaag:

* NICHE bodemkaart:  

	* is de kartering nog geldig voor de actuele situatie (de standaard NICHE bodemkaart is afgeleid uit de Vlaamse bodemkaart die gebaseerd is op terreinwerk uitgevoerd in de periode 1947-1973)? 
	* is de ligging en omvang van de veengronden realistisch? 
	* zijn er bijkomende gegevens beschikbaar om de kaart te valideren, aan te vullen of te verbeteren (o.a. in de niet gekarteerde zones, sterk vergraven gebieden, de militaire domeinen, ...)?
	* ...

* Grondwaterstanden: 

	* is de resolutie van het grondwatermodel en digitaal hoogtemodel hoog genoeg?
	* hoe goed zijn de kalibratieresultaten van het grondwatermodel? is de ruimtelijke verspreiding van de gebruikte meetpunten voldoende?
	* ...

* Trofie:

	* zowel de :ref:`inputgegevens <nutrient_level_input>` als de gevolgen van de :ref:`beslisregels <nutrient_level_princ>` moeten nader gecontroleerd worden.

* Zuurgraad:

	* zowel de :ref:`inputgegevens <acidity_input>` als de gevolgen van de :ref:`beslisregels <acidity_princ>` moeten nader gecontroleerd worden.

Voor het volledige (`full <https://inbo.github.io/niche_vlaanderen/getting_started.html#Running-a-full-Niche-model>`_) NICHE model is het ook mogelijk om de NICHE Vlaanderen **berekende zuurgraad- en trofiekaarten te overschrijven** (zie `hier <https://inbo.github.io/niche_vlaanderen/advanced_usage.html#Using-abiotic-grids>`_) met zelf aangemaakte of aangepaste zuurgraad- en/of trofiekaarten.
