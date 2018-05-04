###########################
Werking NICHE Vlaanderen
###########################

NICHE Vlaanderen (*Nature Impact Assessment of Changes in Hydro-Ecological Systems*) is een 
**hydro-ecologisch model** dat de **potenties voor (grond)waterafhankelijke vegetatietypes** in een 
gebied berekent **op basis van** informatie over de **(abiotische) standplaatscondities**. 
Het model baseert zich hierbij op vier typen standplaatsfactoren (bodemtype, grondwaterstanden, 
voedselrijkdom en zuurgraad) die bepalend zijn voor de aard en de soortensamenstelling van 
vegetaties die zich op een locatie kunnen ontwikkelen.

De figuur hieronder geeft een overzicht van de verschillende inputgegevens en stappen van het model. De :doc:`invoerlagen <invoer>` worden ingelezen als (gebiedsdekkende) rasterkaarten.

.. figure:: _static/png/niche_principle.png
   :scale: 100%
	 
   Schematische weergave van de werking van het NICHE Vlaanderen model, met in het geel de invoergegevens ter berekening van de trofie en de zuurgraad (pH). Beide berekende standplaatsfactoren worden samen met de grondwaterstanden en het bodemtype (groen) afgetoetst aan de referentiewaarden/tolerantiegrenzen voor elk van de vegetatietypen in de referentiedataset (blauw omlijnd) om zo de potentie van elke locatie te bepalen. Optioneel worden die potenties nog verder begrensd door ook de tolerantie ten aanzien van overstromingen en het gevoerde beheer mee in beschouwing te nemen (blauwgrijs). GVG: gemiddelde voorjaarsgrondwaterstand.

Berekening standplaatscondities 
==================================

Eerst worden de standplaatscondities (:doc:`zuurgraad <zuur>` en :doc:`trofie <trofie>`) aan de hand van beslisregels berekend op basis van verschillende kenmerken met betrekking tot de waterhuishouding (overstroming, grondwaterstanden, kwel,...), bodem en landgebruik (bemesting, beheer, ...).  Deze (optionele) stap (in de figuur in het geel aangeduid) genereert twee vereenvoudigde kaarten die de zuurgraad en trofiegraad van de standplaats beschrijven.

Berekening potenties voor vegetatie-ontwikkeling 
===================================================

Vervolgens worden de standplaatskarakteristieken in het studiegebied afgetoetst aan zogenaamde tolerantie-intervallen van plantengemeenschappen (figuur hierboven, in het blauw). Deze tolerantiegrenzen (ook referentiewaarden genoemd) zijn 
gebaseerd op veldwaarnemingen waarbij de plantengemeenschappen en standplaatscondities zijn beschreven.

De potenties voor vegetatie-ontwikkeling kunnen op twee manieren worden berekend: 

Enerzijds door het *volledige NICHE model* te gebruiken, waarbij de berekende zuurgraad en trofie, het bodemtype en de gemiddelde laagste en hoogste grondwaterstanden mee de potenties bepalen (figuur hierboven, inputlagen in het geel en in het groen). Of anderzijds door enkel de referentiewaarden voor het *bodemtype en de karakteristieke grondwaterstanden* (gxg) in beschouwing te nemen (enkel inputlagen in het groen).

Optioneel kunnen de berekende potenties nog beperkt worden naargelang de beheersintensiteit 
of overstromingsfrequentie (figuur hierboven, in het blauwgrijs): bv. vegetatietypen die geen zuurstoftekort verdragen komen  
op frequent overstroomde locaties niet voor, of: er kan geen bos voorkomen in zones die regelmatig gemaaid worden.

Voor elk :doc:`NICHE vegetatietype <vegetatietype>` wordt een binaire rasterkaart geproduceerd (1: kan voorkomen of 0: kan niet voorkomen). 
Potenties voor verschillende typen kunnen dus overlappen in de ruimte.

Kenmerken van het model
=======================

NICHE houdt geen rekening met biotische processen zoals kolonisatie, migratie, kieming e.d. Het model geeft enkel potenties 
aan en bevat ook geen werkelijke kansberekening op het voorkomen van vegetatietypen. Een interpretatie van de resultaten is dus nodig. 
Met NICHE Vlaanderen kunnen ook geen uitspraken worden gedaan over individuele locaties. Het model is daarentegen perfect geschikt om patronen van de berekende 
vegetaties te bestuderen en kan inzicht geven in het ecosysteem of het gebied, wat het tot een geschikt model maakt voor scenario-analyses. 

Vooraleer eventuele scenarioberekeningen kunnen worden uitgevoerd, moet het model eerst :doc:`gekalibreerd <kalibratie>` worden op basis van een gekende 
referentietoestand (meestal de actuele toestand).  

*Referentie*
*Callebaut J., De Bie E., De Becker P., Huybrechts W (2007). NICHE Vlaanderen. Rapporten van het Instituut voor Natuur en Bosonderzoek INBO.R.2007.3. SVW, 1-7*
`Rapport <https://pureportal.inbo.be/portal/files/5370206/Callebaut_etal_2007_NicheVlaanderen.pdf>`_




