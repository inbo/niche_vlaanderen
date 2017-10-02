.. niche_vlaanderen documentation master file, created by
   sphinx-quickstart on Wed Sep  6 18:36:23 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

niche_vlaanderen documentatie
============================================

Het Python package ``niche_vlaanderen`` laat de gebruiker toe om op basis van een aantal :doc:`invoer` de mogelijke vegetatietypes te berekenen.

De berekening gebeurt in drie stappen:

 * :ref:`trofie`
 * :ref:`zuur` 
 * :ref:`vegetatie`

In de Python module ``niche_vlaanderen`` kan de berekening op twee manieren gebeuren

 * High-level: Met behulp van de ``Niche`` klasse, die rechtstreeks werkt met GIS bestanden.
   Meer in :doc:`niche`.
 * Low-level: Deze geavanceerde methode laat toe om de berekening uit te voeren op (numpy) arrays, waarbij de gebruiker een grotere flexibiliteit heeft.

Contents:

.. toctree::
  :maxdepth: 2

  invoer
  trofie
  zuur
  vegetatie
  niche
  lowlevel
  codetables


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

