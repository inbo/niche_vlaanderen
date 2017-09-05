# Testcase Grote Nete

This folder contains a testcase from the original Niche Vlaanderen model with
it's results.

Original arcgis files were converted to ascii grid using gdal.
`gdal_translate -of 'AAIGrid' AbiotiekRef/ph/w001001.adf AbiotiekRef/ph.asc`

Orginal shapefiles were converted to geojson. Note that their projection
system is WGS84 (as required by the geoJSON standard).
