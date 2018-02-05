#######################
Niche Floodplain module
#######################

Het is mogelijk een verdere verfijning van het NICHE model door te voeren voor
gebieden waar frequent overstromingen voorkomen. Hierbij wordt aangegeven in
hoeverre de gegeven vegetatie combineerbaar is met de gemodelleerde
overstromingen.

  .. csv-table:: mogelijke codes voor diepte van overstroming
    :header-rows: 1
    :file: ../niche_vlaanderen/system_tables/floodplains/potential.csv


Hierbij wordt rekening gehouden met de overstromingsfrequentie, de diepte,
tijdstip en duur.

Deze overstromingsdiepete wordt beschreven met volgende codes

  .. csv-table:: mogelijke codes voor diepte van overstroming
    :header-rows: 1
    :file: ../niche_vlaanderen/system_tables/floodplains/depths.csv

Deze overstromingsdiepte wordt in 4 invoerrasters aangeleverd, met 1 raster per
frequentie.

  .. csv-table:: gebruikte frequenties
    :header-rows: 1
    :file: ../niche_vlaanderen/system_tables/floodplains/frequency.csv

De gegevens uit deze tabel worden vergeleken met de tabel lnk_potential

  .. csv-table:: Potentiële vegetatie op basis van de andere invoerparameters.
    :header-rows: 1

    veg_code,period,frequency,duration,depth,potential
    1,winter,T50,1,1,3
    1,winter,T50,1,2,3
    1,winter,T50,1,3,3
    1,winter,T50,2,1,3

De module kan uitgevoerd worden door inundation aan te roepen vanuit de
configfile:

  .. code-block:: yaml

    inundation:
     - name: T20-winter
       file: T20.tif
       frequency: T20
       duration: short
       period: winter
     - name: T20-zomer
       ....

Hierbij kunnen verschillende scenario's gespecifieerd worden.