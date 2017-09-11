# NICHE_Vlaanderen_10.py                                  Tony Van Tilborgh  INBO  08/07/14
#                                                              opkuis, reorg kode: 03/09/14
#                                                                      pH, Trofie: 23/09/14
#                                                       GXG_FAKTOR,LogTbl,Gn_pHTr: 09/12/14
#                                                      PLAFOND_GXG in score-getal: 05/01/15
# -----------------------------------------------------------------------------------------
# uitbreiding versie 24/02/13:
# - toolinterface en parametertabel ipv oproep uit mxd-VBA (OK 08/07/14)
# - ook pH en Trofie kunnen berekend worden ( ... )

# NICHE-GIS = potentiebepaling voor waterafhankelijke vegetatietypes.
# Berekening vegetatie-voorspelling, gebaseerd op ranges in de NICHE-tabel, vanuit abiot
# kaarten => per vegetatietype: rasterkaart met 1 (geschikt) of 0 (ongeschikt).

# SPATIAL ANALYST vereist.

#| opm1: Reclassify mogelijkheden...
#| Ipv allemaal aparte reclass tables (dbf voor iedere VegKode) te gebruiken, bv:
#|   ap.ReclassByTable_sa(somGLG,ReclTbl_GLGvegX,"FROM","TO","OUT",ReclResGLG,"NODATA")
#| rechtstreeks de ranges:
#|   reclassifyRanges = "0.000000 30.000000 1;31.000000 270.000000 2;..."
#|   ap.Reclassify_sa(inRaster, "Value", reclassifyRanges, outRaster, "NODATA")
#| Maar !!! BUFFER OVERFLOW => toch ReclassByTable (tabel mag .tab zijn), ofwel:
#|   ap.ReclassByASCIIFile_sa(inRaster, inASCIIfile, outRaster, "DATA")
#|   #(formaat: geen header, en alles scheiden met spaties: 1 3 : 4
#|   #                                                      3 5 : 6   (...)
#| Nog altijd probleem: rangelijst MOET GESORTEERD ZIJN (behalve voor RclByTable als het
#| 'echte' tabellen zijn zoals bv .dbf => ! dus wel voor .tab tabellen)
#|   => dict (key=VegKode) van lists van tuples (v integers !) gebruiken
#|   => dan list sorteren, dan gebuiken
#| Overlappingen in de ranges worden samengenomen (anders geeft reclass een fout);
#| kontrole of de tuples zelf in orde zijn: (FROM,TO): FROM<TO (anders raise error).
#|  !! Minstens 1 range moet niet-NoData values vd kaart omvatten, zie ReclassifySomGxG !!

#| opm2: Alle parameters via 1 tabel (dus 1 parameter) => interface kompakter.

#| opm3: in het 'huidige' concept van NICHE kunnen de wegingsfaktoren zijn:
#|  B_fakt = 100         Bodem [10000-990000]         ==>   xX......   # bezette posities
#|  Z_fakt = 10000       Zuur [1-9]                   ==>      X....   # in samenvattend
#|  T_fakt = 100000      Trofie [1-9]                 ==>     X.....   # "score"getal
#|  I_fakt = 100000000   Inundatie [0-9]              ==>  X........   #
#|  M_fakt = 1000000000  Beheer='Management' [0-9]    ==> X.........   #
#|  PLAFOND_GXG = 1000   (=> neg GxG hiervan afgetr)  ==> ......1000   #
#|    ==> mogelijke posities GxG waarden in scoregetal:          XXX   #
#|    dus hier mag abs(GxG) nooit > 999 (diepte grondwater in cm) => aftoppen indien nodig
#|    ... want NICHE bepaalt geen potentie voor grondwateronfhankel. vegetatietypen:
#|    " In principe komen dergelijke waterstanden (dieper dan 10 m) niet voor in studie- "
#|    " gebieden waarvoor NICHE is ontworpen (grondwaterafhankelijke systemen), maar het "
#|    " is niet uit te sluiten dat in de resultaten van grondwatermodellen (die meestal  "
#|    " gebruikt worden om de potenties te bepalen) peilen dieper dan 10 m voorkomen. WM "
#|  Al deze faktoren kunnen echter aangepast w in de parametertabel (rechtstreekse invloed
#|  op de berekeningen !), de gebruiker moet kontroleren voor juiste kombinatie ...
#|
#| opm4: "ReclassifySomGxG": omdat Reclassify 'NoData' invult in de cellen die buiten de
#|       opgegeven ranges vallen, moeten die uitdrukkelijk op 0 (ongeschikt) gezet w binnen
#|       het studiegebied: behoud van 'NoData' heeft hier geen zin want gaat over waarde
#|       "binnen de ranges" (="geschikt"="1") of "buiten de ranges" (="ongeschikt"="0").
#|       [moet alleszins gebeuren VOOR de allerlaatste stap (= ReclResGHG * ReclResGLG )].
#|
#| opm5: NULras: wordt intern berekend !!!
#|       => uit bodemrasterkaart (noodzakelijk aanwezig voor alle types berekening)
#|          dus veronderstelt GEVULDE Bodemkaart/GrensFC, 'interne' NoData w overgezet !
#|       Door NULras te gebruiken in een "+" is extent automatisch beperkt
#|        -> extra ExtractByMask vermijden (kost meer dan dubbel zoveel tijd !)
#|        -> ook ap.env.mask niet nodig
#|       [opm "ap.env.mask = NULras" => fout, want is rasterOBJEKT, moet dataset zijn]
#|       [opm 'cell alignment' onvoorspelbaar, 'cell size' = grootste ]
#|
#| opm6: +,*,...operators: minstens 1 moet rasterOBJEKT zijn; andere wel automat omgezet

#| Oorspronkelijke versie: gxg in cm onder maaiveld (dus negatief boven maaiveld):
#|                         GxGmin = dieper =  groter ; GxGmax = hoger = kleiner
#| intern blijft dit, maar data (gxg-kaarten EN !! gxgmax,gxgmin in NicheTbl !!) kunnen
#| in m en negatief onder maaiveld (output van oa WATINA)
#|  => gxgFaktor ingevoerd: gxgFaktor=1 -> zoals vroeger; =-100 -> m,neg (bv)
#| !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
#| !!! PLAFOND_GXG blijft zoals vroeger in cm beneden maaiveld !!!
#| !!! idem RCLASSTBL...GxG..                                  !!!
#| !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!


#! Vereiste struktuur voor de reclassify-txtbestanden (indien pH- of Trofieberekening):
#! = de ArcGIS "ASCII remap file" -> zie [Help] "How Reclass by ASCII File works"
#! => geen hoofdinglijn, spatiegescheiden, de te "remappen" waarden in stijgende volgorde
#! bv:     5 : 100           # te "remappen" waarden mogen float zijn (w afgekapt !)
#!         7 : 200           # !!! maar de "doel"waarden moeten INTEGER zijn !!!
#! ofwel:     10 30 : 4
#!            30 50 : 6
#!            50 70 : 8
#! opm: waarden buiten de opgegeven bereiken  ==> NODATA

#!! Voorwaarden voor basisrasters (niet strikt, vooral voor rekentijden):
#!! - dezelfde 'cell size' en 'alginment'
#!! - 'dekking' minstens even groot als begrenzend polygoon, anders als bodemrasterkaart
#!! - begrenzend polygoon (of bodemrasterkaart) geen "interne" NoData
#!! - geen projektie (op geen enkel basisraster, ook niet pH, Trofie, ook niet ev GrensFC)
#!!   ... ?? maar niet meer intern verplichten, => vroegere truk met 'SnijFC' zonder prj
#!!       (zie hieronder) eruit -- opgelet, snapRaster behouden anders verschuiving !
#!!#if GrensFC:
#!!#  SnijFC = tmpdir +SEP+ "SNIJ_FC.shp"  #".shp" nodig anders niet herkend na del prj
#!!#  DM.CopyFeatures(GrensFC,SnijFC)   #prj->"Unknown" =>gridberek. sneller (geen SR-def)
#!!#  if ap.Exists(SnijFC.replace(".shp",".prj")): os.remove(SnijFC.replace(".shp",".prj"))
#!!#  ap.RefreshCatalog(tmpdir)
#!!#  ap.env.snapRaster = KrtPadDct[KAART_BODEM]
#!!#  BodemRas = ap.sa.ExtractByMask(BodemRas,SnijFC)  #uitknippen: buiten=NoData
#!!#  ap.env.snapRaster = ""   #! terug afzetten => sneller ? minder kontroles op positie ?
#!!#  DM.Delete(SnijFC)
#!!#NULras = ap.sa.Diff(BodemRas,BodemRas)

#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
#!! op te nemen in 'description' vd tool:
#!! -> VERPLICHTE STRUKTUUR vh parameterbestand
#!! -> Voorwaarden voor ev reclass tabellen
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!


class FOUT(Exception):
  pass

import sys, string, os, arcpy as ap
from shutil import rmtree  #voor rekursieve rm (gaat niet rechtstreek met os.rmdir)
ap.env.overwriteOutput = 1
RbAf = ap.sa.ReclassByASCIIFile  # korter
SEP = os.sep
ap.AddMessage("[aut. Tony Van Tilborgh, INBO 05/01/15]")


ParamTBL  = ap.GetParameterAsText(0)           #TableView; inp,req
InputRWS = ap.GetParameterAsText(1)            #(grid)workspace; inp,req
pH_berekenen = ap.GetParameter(2)              #Boolean; inp,req,DEF=False
Trofie_berekenen = ap.GetParameter(3)          #Boolean; inp,req,DEF=False
Vegetatie_berekenen = ap.GetParameter(4)       #Boolean; inp,req,DEF=False
Overstroming_gebruiken = ap.GetParameter(5)    #Boolean; inp,req,DEF=False
Beheer_gebruiken = ap.GetParameter(6)          #Boolean; inp,req,DEF=False
GEEN_pH_Trofie = ap.GetParameter(7)            #Boolean; inp,req,DEF=False
pH_Trofie_RWS = ap.GetParameterAsText(8)       #(grid)workspace; inp,opt
ReclassTblWs = ap.GetParameterAsText(9)        #workspace; inp,opt
NicheTbl = ap.GetParameterAsText(10)           #TableView; inp,opt
VegResRWS = ap.GetParameterAsText(11)          #workspace; inp,opt
GrensFC = ap.GetParameterAsText(12)            #PolygFeatClass; inp,opt
# workspace --> ev afsluitende separator(s) (gwl "\") automatisch eraf gestript
# ToolValidator => bovenstaande inputs zijn geldig en logisch:
#      bv INDIEN pH_berekenen DAN een (geldige) waarde voor ReclassTblWs
#      bv INDIEN GEEN_pH_Trofie_gebruiken DAN geen waarde nodig (/mogelijk) v pH/Tr dir/gdb
#                                         DAN ook geen pH/Tr berekening mogelijk


# Vaste parameterbenamingen en Parameters
#========================================
# ! vars = de parameterbenamingen (strings), dan enkel hier aan te passen indien nodig
# ! -- betekenis zie "def ParametersInlezenKontroleren()" --

PARAMETER="PARAMETER"   # ParamTBL-kolom (verplicht te gebruiken benamingen hieronder)
WAARDE="WAARDE"         # ParamTBL-kolom (door gebruiker in te vullen parameterwaarde)

KAART_BODEM="KAART_BODEM"                       #-> pH; Trofie; Veget
KAART_GLG="KAART_GLG"                           #-> pH;   --  ; Veget
KAART_GVG="KAART_GVG"                           #-> --; Trofie
KAART_GHG="KAART_GHG"                           #-> --;   --  ; Veget
KAART_FLUX="KAART_FLUX"                         #-> pH
KAART_REGENLENS="KAART_REGENLENS"               #-> pH
KAART_OVERSTR_TROFIE="KAART_OVERSTR_TROFIE"     #-> --; Trofie
KAART_OVERSTR_ZUUR="KAART_OVERSTR_ZUUR"         #-> pH
KAART_OVERSTR_VEGET="KAART_OVERSTR_VEGET"       #-> --;   --  ; Veget+Overstr
KAART_BEHEER="KAART_BEHEER"                     #-> --; Trofie; Veget+Beheer
KAART_N_ATM_DEPOSIT="KAART_N_ATM_DEPOSIT"       #-> --; Trofie
KAART_N_MEST_DIER="KAART_N_MEST_DIER"           #-> --; Trofie
KAART_N_MEST_KUNST="KAART_N_MEST_KUNST"         #-> --; Trofie
KAART_MINERAALRIJKDOM="KAART_MINERAALRIJKDOM"   #-> pH
KAART_ZUUR="KAART_ZUUR"                         #-> pH;   --  ; Veget  [pH-resultaat]
KAART_TROFIE="KAART_TROFIE"                     #-> --; Trofie; Veget  [Trofie-resultaat]
RCLSTBL_BODEM="RECLASSTBL_BODEM"             #-> pH
RCLSTBL_BODEMGLG="RECLASSTBL_BODEMGLG"       #-> pH
RCLSTBL_CONDUCTIV="RECLASSTBL_CONDUCTIV"     #-> pH
RCLSTBL_FLUX="RECLASSTBL_FLUX"               #-> pH
RCLSTBL_REGENLENS="RECLASSTBL_REGENLENS"     #-> pH
RCLSTBL_OEVER="RECLASSTBL_OEVER"             #-> pH
RCLSTBL_ZUUR="RECLASSTBL_ZUUR"               #-> pH
RCLSTBL_BGVGTROFIE="RECLASSTBL_BGVGTROFIE"   #-> --; Trofie
RCLSTBL_BNTROFIE="RECLASSTBL_BNTROFIE"       #-> --; Trofie
KOLOM_KODE="KOLOM_KODE"                   #->(NICHETBL)Veget
KOLOM_BODEM="KOLOM_BODEM"                 #->(NICHETBL)Veget
KOLOM_ZUUR="KOLOM_ZUUR"                   #->(NICHETBL)Veget
KOLOM_TROFIE="KOLOM_TROFIE"               #->(NICHETBL)Veget
KOLOM_GHGMIN="KOLOM_GHGMIN"               #->(NICHETBL)Veget
KOLOM_GHGMAX="KOLOM_GHGMAX"               #->(NICHETBL)Veget
KOLOM_GLGMIN="KOLOM_GLGMIN"               #->(NICHETBL)Veget
KOLOM_GLGMAX="KOLOM_GLGMAX"               #->(NICHETBL)Veget
KOLOM_OVERSTROMING="KOLOM_OVERSTROMING"   #->(NICHETBL)Veget+Overstr
KOLOM_BEHEER="KOLOM_BEHEER"               #->(NICHETBL)Veget+Beheer
GXG_FAKTOR="GXG_FAKTOR"                      #-> pH; Trofie; Veget
PLAFOND_GXG="PLAFOND_GXG"                    #-> Veget
FAKTOR_BODEM="FAKTOR_BODEM"                  #-> Veget
FAKTOR_ZUUR="FAKTOR_ZUUR"                    #-> Veget
FAKTOR_TROFIE="FAKTOR_TROFIE"                #-> Veget
FAKTOR_OVERSTROMING="FAKTOR_OVERSTROMING"    #-> Veget+Overstr
FAKTOR_BEHEER="FAKTOR_BEHEER"                #-> Veget+Beheer

KrtNodigVr_pH=[KAART_BODEM,KAART_GLG,KAART_FLUX,KAART_REGENLENS,
  KAART_OVERSTR_ZUUR,KAART_MINERAALRIJKDOM,KAART_ZUUR]
RclTblNodigVr_pH=[RCLSTBL_BODEM,RCLSTBL_BODEMGLG,RCLSTBL_FLUX,RCLSTBL_REGENLENS,
  RCLSTBL_OEVER,RCLSTBL_CONDUCTIV,RCLSTBL_ZUUR]
FaktNodigVr_pH=[GXG_FAKTOR]
KrtNodigVr_Trofie=[KAART_BODEM,KAART_GVG,KAART_OVERSTR_TROFIE,KAART_N_ATM_DEPOSIT,
  KAART_N_MEST_DIER,KAART_N_MEST_KUNST,KAART_BEHEER,KAART_TROFIE]
RclTblNodigVr_Trofie=[RCLSTBL_BGVGTROFIE,RCLSTBL_BNTROFIE]
FaktNodigVr_Trofie=[GXG_FAKTOR]
KrtNodigVr_Veget=[KAART_BODEM,KAART_GLG,KAART_GHG,KAART_ZUUR,KAART_TROFIE]
KolNodigVr_Veget=[KOLOM_KODE,KOLOM_BODEM,KOLOM_ZUUR,KOLOM_TROFIE,KOLOM_GHGMIN,KOLOM_GHGMAX,
  KOLOM_GLGMIN,KOLOM_GLGMAX]
FaktNodigVr_Veget=[PLAFOND_GXG,GXG_FAKTOR,FAKTOR_BODEM,FAKTOR_ZUUR,FAKTOR_TROFIE]
NodigVoor_Beheer=[KAART_BEHEER,KOLOM_BEHEER,FAKTOR_BEHEER]
NodigVoor_Overstr=[KAART_OVERSTR_VEGET,KOLOM_OVERSTROMING,FAKTOR_OVERSTROMING]
#! "dubbels" hierboven (=> direkt bij begin rasters maken):
#!   KAART_BODEM: Veget,pH,Trofie (dus ALTIJD nodig)
#!   KAART_ZUUR, KAART_TROFIE: Veget, pH resp Trofie (ev te berekenen)
#!   KAART_GLG: Veget, pH
#!   KAART_BEHEER: (Veget)Beheer, Trofie
#! GXG_FAKTOR: nodig voor alles (pH,Trofie,Veget)


def ParametersInlezenKontroleren():
#==================================
  # VEREISTE VASTE BENAMINGEN IN ParamTBL  --> zie boven
  # ! EXCEL TOONT LEIDENDE SPATIES NIET ALTIJD ! ...hoewel: uitschrijven achteraf => ook vr
  # ! lege cellen in excel wordt " " doorgeg als waarde => ? (maar OK dr testen op beide)
  # opm: <dict>.get(par,def) => als geen def dan <None> ... [hier overbodig, dict gevuld]

  ParamDict={}    # volledig "opvullen", ook als parameters niet zullen gebruikt worden
  for lst in [KrtNodigVr_pH,RclTblNodigVr_pH,FaktNodigVr_pH,KrtNodigVr_Trofie,
              RclTblNodigVr_Trofie,FaktNodigVr_Trofie,KrtNodigVr_Veget,KolNodigVr_Veget,
              FaktNodigVr_Veget,NodigVoor_Beheer,NodigVoor_Overstr]:
    for par in lst: ParamDict[par]=""

  ParMsg = "Parametertabel '"+ParamTBL+"':\n\t--> "
  for kol in [PARAMETER,WAARDE]:
    if not kol in [f.name for f in ap.ListFields(ParamTBL)]:
      raise FOUT(ParMsg+"Vereiste kolom '"+kol+"' ontbreekt !")
  ParTBLrows = ap.SearchCursor(ParamTBL)
  row_tel=0
  for ParTBLrow in ParTBLrows:
    row_tel+=1
    RowMsg = ParMsg+"rij "+str(row_tel)+": "
    param=ParTBLrow.getValue(PARAMETER)
    if param not in ParamDict: raise FOUT(RowMsg+"ongeldige PARAMETER '"+param+"'")
    waarde=str(ParTBLrow.getValue(WAARDE))  #str want mogelijk een getal (excel!)
    if waarde and waarde[:1] == " ":      # 1ste test op 'niks' want slice van "" onmogel
      if len(waarde)>1:
        raise FOUT(RowMsg+param+" = '"+waarde+ "': leidende spatie.")
      else: waarde=""
    if waarde == "None": waarde=""   #testen hieronder gemakkelijker
    ParamDict[param]=waarde
  del ParTBLrow, ParTBLrows

  errlst=[]
  if pH_berekenen:
    for lst in [KrtNodigVr_pH,RclTblNodigVr_pH,FaktNodigVr_pH]:
      for par in lst:
        if not ParamDict[par]: errlst.append((par,"pH"))
  if Trofie_berekenen:
    for lst in [KrtNodigVr_Trofie,RclTblNodigVr_Trofie,FaktNodigVr_Trofie]:
      for par in lst:
        if not ParamDict[par]: errlst.append((par,"Trofie"))
  if Vegetatie_berekenen:
    for lst in [KrtNodigVr_Veget,KolNodigVr_Veget,FaktNodigVr_Veget]:
      for par in lst:
        if not ParamDict[par]: errlst.append((par,"Vegetatie"))
  if Overstroming_gebruiken:
    for par in NodigVoor_Overstr:
      if not ParamDict[par]: errlst.append((par,"Vegetatie+Overstroming"))
  if Beheer_gebruiken:
    for par in NodigVoor_Beheer:
      if not ParamDict[par]: errlst.append((par,"Vegetatie+Beheer"))
  if len(errlst):
    emsg = ParMsg+"Vereiste parameter(s) niet opgenomen of lege waarde:\n"
    for tpl in errlst: emsg = emsg +"\t\t=> '"+tpl[0]+"'  (berekening "+tpl[1]+")\n"
    raise FOUT(emsg)

  return ParamDict


def TestSchrijfbaarheidDoelen():
#===============================
  # opm: => mode = os.stat(pathname)[ST_MODE] --> te omslachtig, onduidelijk
  # => gewoon een schrijftestje doen, eerst een klein testraster aanmaken
  # bv: testRas = ap.sa.CreateConstantRaster(1, "INTEGER", 1, ap.sa.Extent(50,50,52,52))
  #     ?? maar dit geeft soms probl, tot zelfs crash, afh van extent ?? => BodemRas gebr
  # !! wat zeker crash geeft als alles (pH,Trofie, Veget) gevraagd wordt: 1 gemeensch ras
  # => voor beide testen: afzonderlijk testras aanmaken en saven om dit te vermijden

  BodKrt = KrtPadDct[KAART_BODEM]         # BodemKaart oblig aanw in alle gevallen
  X = float(ap.management.GetRasterProperties(BodKrt,"LEFT").getOutput(0))+0.1
  Y = float(ap.management.GetRasterProperties(BodKrt,"BOTTOM").getOutput(0))+0.1
  if Vegetatie_berekenen:
    testRas = ap.sa.ExtractByPoints(BodKrt,[ap.Point(X,Y)])   # 1 gridcel gebruiken
    testRasKrt = VegResRWS+SEP+"schrTEST"
    try:
      testRas.save(testRasKrt); ap.RefreshCatalog(VegResRWS)
      ap.Delete_management(testRasKrt); ap.RefreshCatalog(VegResRWS)
    except: raise FOUT("Probleem bij schrijftest naar doelpad '" +VegResRWS+ "' "+ \
      "(voor resultaten vegetatiebereking) -- SCHRIJFRECHTEN OK ?-\n"+ \
      str(sys.exc_type)+ ": "+str(sys.exc_value))
    del testRas
  if (pH_berekenen or Trofie_berekenen):
    testRas2 = ap.sa.ExtractByPoints(BodKrt,[ap.Point(X,Y)])   # 1 gridcel gebruiken
    testRasKrt2 =  pH_Trofie_RWS+SEP+"schrTEST2"
    try:
      testRas2.save(testRasKrt2); ap.RefreshCatalog(pH_Trofie_RWS)
      ap.Delete_management(testRasKrt2); ap.RefreshCatalog(pH_Trofie_RWS)
    except: raise FOUT("Probleem bij schrijftest naar doelpad '" +pH_Trofie_RWS+ "' "+ \
      "(voor pH/Trofie berekening) -- SCHRIJFRECHTEN OK ?\n"+ \
      str(sys.exc_type)+ ": "+str(sys.exc_value))
    del testRas2


def MaakTempDir(DoelDir):
#========================
  DoelDir_DT = ap.Describe(DoelDir).DataType
  if DoelDir_DT == "Folder": tempdirPad = DoelDir
  elif DoelDir_DT == "Workspace": tempdirPad = os.path.dirname(DoelDir)
  else: raise FOUT("Doelpad '"+DoelDir+"' heeft een onverwacht datatype !?!")
  tempdir = tempdirPad +SEP+ "___tmpdir_NICHE___"
  try:
    if ap.Exists(tempdir): rmtree(tempdir)
    os.mkdir(tempdir); ap.RefreshCatalog(tempdirPad)
  except:
    raise FOUT("Probleem bij aanmaken tijdelijke werkdir (onder '"+tempdirPad+"') !\n"+ \
                str(sys.exc_type)+ ": "+str(sys.exc_value))
  return tempdir


def LogInputGegevensNrDBF(dir):
#==============================
  #opm: naast ap.CopyRows_management(...) is er ook ap.Append_management(inputs, target),
  #     maar hier niet bruikbaar omdat toe te voegen rijen niet in tabel zitten
  try:
    pad_nm_ini = dir +SEP+ "NICHE_invoer_LOG"
    tel=0
    LOGtbl = pad_nm_ini + ".dbf"
    while ap.Exists(LOGtbl):
      tel+=1
      LOGtbl = pad_nm_ini +"_" + str(tel) + ".dbf"
    ap.CopyRows_management(ParamTBL,LOGtbl)
    ToolParams = [("ParameterTabel",ParamTBL),("InputRWS",InputRWS),
      ("Bereken_pH",str(pH_berekenen)),("BerekenTrofie",str(Trofie_berekenen)),
      ("BerekenVegetatie",str(Vegetatie_berekenen)),
      ("GebruikOverstroming",str(Overstroming_gebruiken)),
      ("GebruikBeheer",str(Beheer_gebruiken)),("GEEN_pH_Trofie",str(GEEN_pH_Trofie)),
      ("pH_Trofie_RWS",pH_Trofie_RWS),("ReclassTabellenWS",ReclassTblWs),
      ("NicheTabel",NicheTbl),("VegetatieResultRWS",VegResRWS),("GrensFC",GrensFC)]
    rows = ap.InsertCursor(LOGtbl)
    for tpl in ToolParams:
      row = rows.newRow()
      row.setValue(PARAMETER,tpl[0])
      row.setValue(WAARDE,tpl[1])
      rows.insertRow(row)
    del row,rows
    ap.AddMessage("LOGtabel invoergegevens = " + LOGtbl +"\n")
  except: raise FOUT("bij invullen van InputGegevens-LOGtabel !" \
                     +"\n"+str(sys.exc_type)+": "+str(sys.exc_value))


def PadOfRasFout(KaartPad):
#==========================
  msg = ""
  if not ap.Exists(KaartPad): msg = "\t=> Onbestaande kaart of foutief pad: "+KaartPad+"\n"
  elif ap.Describe(KaartPad).dataType != "RasterDataset":
    msg = "\t=> Kaart is geen raster: " + KaartPad +"\n"
  return msg


def KaartPadNamenVormenKontroleren():
#====================================
  # [ apart v ParametersInlezenKontroleren(): duidelijker, gewoon enkele if testen meer ]
  # onderstaande volgorde belangrijk voor testen al dan niet bestaan v kaarten
  # als pH of Trofie nog m berekend w dan wel padnaam zetten maar niet testen
  # opm: KAART_BODEM moet vr alles bestaan (en w getest): pH,Trofie,Veget

  PadNaamDct = {}
  emsg = ""
  if pH_berekenen:   # indien niet dan w ze getest in Veg...berek... indien vereist
    for krt in KrtNodigVr_pH:
      if krt == KAART_ZUUR: PadNaamDct[krt] = pH_Trofie_RWS +SEP+ ParDct[krt]
      else:
        PadNaamDct[krt] = InputRWS +SEP+ ParDct[krt]
        emsg =  emsg + PadOfRasFout(PadNaamDct[krt])

  if Trofie_berekenen:  # indien niet dan w ze getest in Veg...berek... indien vereist
    for krt in KrtNodigVr_Trofie:
      if krt == KAART_TROFIE: PadNaamDct[krt] = pH_Trofie_RWS +SEP+ ParDct[krt]
      elif krt not in PadNaamDct:  # testen -- niet KAART_TROFIE zelf want moet nog berek w
        PadNaamDct[krt] = InputRWS +SEP+ ParDct[krt]
        emsg =  emsg + PadOfRasFout(PadNaamDct[krt])

  if Vegetatie_berekenen:
    for krt in KrtNodigVr_Veget:
      # pH,Trofie: als GEEN_pH_Trofie==true dan w krtn niet toegevoegd
      #            anders MOETEN ze BESTAAN, nog toev indien hierboven nog niet gedef
      if krt == KAART_ZUUR:
        if not pH_berekenen and not GEEN_pH_Trofie:
          PadNaamDct[krt] = pH_Trofie_RWS +SEP+ ParDct[krt]
          emsg =  emsg + PadOfRasFout(PadNaamDct[krt])
      elif krt == KAART_TROFIE:
        if not Trofie_berekenen and not GEEN_pH_Trofie:
          PadNaamDct[krt] = pH_Trofie_RWS +SEP+ ParDct[krt]
          emsg =  emsg + PadOfRasFout(PadNaamDct[krt])
      elif krt not in PadNaamDct:
        PadNaamDct[krt] = InputRWS +SEP+ ParDct[krt]
        emsg =  emsg + PadOfRasFout(PadNaamDct[krt])

  if Beheer_gebruiken and not Trofie_berekenen:  # nog niet gedef en MOET BESTAAN
    PadNaamDct[KAART_BEHEER] = InputRWS +SEP+ ParDct[KAART_BEHEER]
    emsg =  emsg + PadOfRasFout(PadNaamDct[KAART_BEHEER])
  if Overstroming_gebruiken:
    PadNaamDct[KAART_OVERSTR_VEGET] = InputRWS +SEP+ ParDct[KAART_OVERSTR_VEGET]
    emsg =  emsg + PadOfRasFout(PadNaamDct[KAART_OVERSTR_VEGET])

  if emsg: raise FOUT("Basiskaartfout(en):\n" + emsg)

  return PadNaamDct


def RclTblPadNamenVormenKontroleren():
#=====================================
  PadNaamDct = {}
  emsg = ""
  if pH_berekenen:
    for tbl in RclTblNodigVr_pH:
      PadNaamDct[tbl] = ReclassTblWs +SEP+ ParDct[tbl]
      if not ap.Exists(PadNaamDct[tbl]):
         emsg = emsg +"\t=> Onbestaande tabel of foutief pad: "+PadNaamDct[tbl]+"\n"
  if Trofie_berekenen:
    for tbl in RclTblNodigVr_Trofie:
      PadNaamDct[tbl] = ReclassTblWs +SEP+ ParDct[tbl]
      if not ap.Exists(PadNaamDct[tbl]):
         emsg = emsg +"\t=> Onbestaande tabel of foutief pad: "+PadNaamDct[tbl]+"\n"
  if emsg: raise FOUT("ReclassifyTabel(padnaam)fout(en):\n" + emsg)
  return PadNaamDct


def RasterUitsnijden(rasterkaart):
#=================================
  # ap.env.snapRaster = KrtPadDct[KAART_BODEM] overbodig want NULras OK
  try:
    raster_xtr = ap.sa.ExtractByMask(rasterkaart,NULras)  #uitknippen: buiten=NoData
  except:
    raise FOUT("Probleem bij uitsnijden van raster: '"+rasterkaart+"' !\n"+ \
                             str(sys.exc_type)+ ": "+str(sys.exc_value))
  return raster_xtr


def SomGewogenBasisRasters():
#=========================
  # BodemRas, ZuurRas, TrofieRas bestaan al
  # Ook ManagRas bestaat al indien nodig

  if Overstroming_gebruiken:
    I_gewR = I_fakt * RasterOfUitsnijden(KrtPadDct[KAART_OVERSTR_VEGET])
  else: I_gewR = NULras
  if Beheer_gebruiken:
    M_gewR = M_fakt * ManagRas
  else: M_gewR = NULras

  B_gewR = B_fakt * BodemRas
  Z_gewR = Z_fakt * ZuurRas
  T_gewR = T_fakt * TrofieRas
  return B_gewR + Z_gewR + T_gewR + I_gewR + M_gewR    # rasterobjekt !


def BerekenSomGxG(GxGras):
#=========================
  # Som met gewogen basisrasters (= BZTIM, moet reeds bestaan; NULras bepaalt 'extent').
  # Begrenzing tot plaf_GxG-1, ook negatief.
  # Result is rasterOBJEKT, niet een rasterkaart !

  GxGras_plaf1 = ap.sa.Con(GxGras,(plaf_GxG-1)*(-1),GxGras,"VALUE <= "+str(plaf_GxG*(-1)))
  GxGras_plaf2 = ap.sa.Con(GxGras_plaf1,plaf_GxG-1,GxGras_plaf1,"VALUE >= "+str(plaf_GxG))
  return NULras + GxGras_plaf2 + plaf_GxG + BZTIMgewR


def ReclassifySomGxG(somGxG,RngGxG,VegKode,sGxGtype):
#====================================================
  # De "range-tuples" voor deze VegKode eerst sorteren: anders fout bij reclass !!!
  # De tuples(FROM,TO) zelf zijn al in orde: FROM<TO en INTEGER (anders sortering fout !).
  # Overlaps vd "ranges" en dubbels eruit halen want reclass geeft anders fout: hiervoor
  # gemakshalve de "range-tuples" lijst voor deze VegKode er apart uit halen
  # => "RngLst" is list van "Range-tuples" voor deze VegKode
  # => "rclRng2Val" = string van de regels om daarna ineens naar reclass ASCII-txt te schr.
  #! Minstens 1 range moet niet-NoData values vd kaart omvatten, anders reclass-fout: di
  #! -OF- als alle ranges < min gridvalue -OF- als alle ranges > max gridvalue
  #! -OF- ranges vallen tussen de ranges met niet-NoData gridvalues (= geen overlap).
  #! 1 geldige range aan de ASCIIFile toevoegen is voldoende om error te vermijden.
  #! Pragmatisch: als GxGmax in laatste behandelde range zit => OK (en 'break'), maar als
  #! GxGmax overgeslagen wordt in laatste range: laatste range niet uitschrijven maar
  #! dummy range die reclass doet op waarde 0 (OK want is "ongeschikt") (en 'break'), dus
  #! ook als er eventueel al geldige ranges uitgeschreven waren.
  #! Opgelet: alle ranges kunnen < GxGmin => ook uitdrukkelijk testen (als laatste)
  #! Zie #| opm4 => NoData binnen kaart (= buiten ranges = ongeschikt) -> 0 .
  #
  #!!!  rcl_f_nm reeds globaal gedefinieerd   !!!

  #RPres=ap.GetRasterProperties_management(somGxG,"MAXIMUM");GxGmax=int(RPres.getOutput(0))
  #RPres=ap.GetRasterProperties_management(somGxG,"MINIMUM");GxGmin=int(RPres.getOutput(0))
  #opm: int nodig want output is blijkbaar "UNICODE"-string )
  # # nieuwe iplem.: somGxG = Raster obj ==> properties rechtstr bruikb

  ap.CalculateStatistics_management(somGxG)   #! anders soms crash !
  GxGmax, GxGmin  = int(somGxG.maximum), int(somGxG.minimum)     #double!
  RngLst = RngGxG[VegKode];  RngLst.sort();
  sRclVal, rclRng2Val = "1", ""
  FROM, TO = RngLst[0][0], RngLst[0][1]
  for j in range(1,len(RngLst)):   # (FROM,TO) is de vorige (ev uitgebreide) range
    if RngLst[j][0] <= TO:   # huidige benedengrens is <= vorige bovengrens
      TO=RngLst[j][1]   # dus breidt range uit (ondergrens blijft, bovengrens verschuift)
    else:  # geen overlap dus eerst vorige range uitschrijven, dan nieuwe range defin
      if GxGmax <= TO:  # !BREAK!: verdergaan zinloos, maar wel 2 mogelijkheden:
        if FROM <= GxGmax: break #OK, inbegrepen; "1" uitschrijven (+ verdergaan zinloos)
        else: # NIET inbegrepen, dus "0" uitschrijven (+ verdergaan zinloos)
          FROM=GxGmax-1;  TO=GxGmax;   sRclVal="0";  break
      rclRng2Val = rclRng2Val + str(FROM) +" "+ str(TO) +" : " +sRclVal+ "\n"
      FROM=RngLst[j][0];  TO=RngLst[j][1]
  rclRng2Val = rclRng2Val + str(FROM) +" "+ str(TO) +" : " +sRclVal+ "\n"    #(laatste)
  if TO < GxGmin: # (= laatste TO) voorgaande rclRng2Val zinloos, enkel dummy waarde nodig
    rclRng2Val = str(GxGmin) + " " + str(GxGmin+1) + " : 0\n"
  rcl_f = open(rcl_f_nm, 'w')    #'w' = overschrijven (of aanmaken)
  rcl_f.write(rclRng2Val); rcl_f.close()   #zie #| opm1
  try: uitRcl = RbAf(somGxG,rcl_f_nm,"NODATA")
  except: raise FOUT("Reclassify mislukt: [vegetatiekode]= '" +VegKode \
                     +"', [somraster]= '" +sGxGtype+ "'.\n" \
                     +str(sys.exc_type)+ ": "+str(sys.exc_value))
  return ap.sa.Con(ap.sa.IsNull(uitRcl),NULras,uitRcl)  # NoData binnen 'kaart' -> 0


try:
 #| SAcheck; params,kaartpaden; tmpdir,LOGdbf; BodemRas,NULras; GLGras,ManagRas
 #| ===========================================================================
  tmpdir = "__tmpdir_nog_niet_aangemaakt__"
  prgblok = "[-INIT-]"
  if ap.CheckExtension("spatial") == "Available": ap.CheckOutExtension("spatial")
  else: raise FOUT("Extensie 'Spatial Analyst' niet beschikbaar !")

  ParDct = ParametersInlezenKontroleren()
  KrtPadDct = KaartPadNamenVormenKontroleren()
  RclTblPadDct = RclTblPadNamenVormenKontroleren()
  TestSchrijfbaarheidDoelen()
  if Vegetatie_berekenen: RWS = VegResRWS  # min 1 v Veg/pH/Trofie moet berek w (toolvalid)
  else: RWS = pH_Trofie_RWS  # pH/Trofie m berek w, dus WS moet schrijfb zijn
  tmpdir = MaakTempDir(RWS)
  LogInputGegevensNrDBF(os.path.dirname(tmpdir))
  try:
    gxgFaktor = int(float(ParDct[GXG_FAKTOR]))
  except: raise FOUT("Fout in PARAMETERBESTAND: "+GXG_FAKTOR+" : "  +str(sys.exc_value))
  if not gxgFaktor: raise FOUT("PARAMETERBESTAND: "+GXG_FAKTOR+" mag niet 0 zijn !")

  try:                      # BodemKaart oblig aanw in alle gevallen
    if GrensFC:
      ap.env.snapRaster = KrtPadDct[KAART_BODEM]   # noodzakel anders verschuiving
      BodemRas = ap.sa.ExtractByMask(KrtPadDct[KAART_BODEM],GrensFC)  # buiten=NoData
      ap.env.snapRaster = ""   #! terug afzetten => sneller ? minder kontroles op positie ?
      RasterOfUitsnijden = RasterUitsnijden
    else:
      BodemRas = ap.Raster(KrtPadDct[KAART_BODEM])
      RasterOfUitsnijden = ap.Raster
    NULras = ap.sa.Diff(BodemRas,BodemRas)
    # dus veronderstelt GEVULDE Bodemkaart/GrensFC, 'interne' NoData w overgezet !
  except:
    raise FOUT("Probleem bij aanmaken NULraster (of BodemRaster) !\n"+ \
                             str(sys.exc_type)+ ": "+str(sys.exc_value))

  if Vegetatie_berekenen or pH_berekenen:
    GLGras = RasterOfUitsnijden(KrtPadDct[KAART_GLG])* gxgFaktor
  else: GLGras = 0              # w toch niet gebruikt; ev del geeft dan geen problemen
  if Beheer_gebruiken or Trofie_berekenen:
    ManagRas = RasterOfUitsnijden(KrtPadDct[KAART_BEHEER])
  else: ManagRas = 0            # w toch niet gebruikt; ev del geeft dan geen problemen

 #| ZuurRas, TrofieRas (ev berekening)
 #| ==================================
  rtmsg = "-berekening, mogelijk een fout in de ASCII-remap txtbestanden -> "+ \
      'zie [ArcGIS-Help] "How Reclass by ASCII File works" (laatste bestand: '

  prgblok = "[-pH_berekening-]"
  if pH_berekenen:
    ap.AddMessage("pH berekening ...")
    try:
      rt = RCLSTBL_BODEM
      BodGlg = GLGras + RbAf(BodemRas,RclTblPadDct[rt],"NODATA")
      rt = RCLSTBL_BODEMGLG
      BodGlgRcl = RbAf(BodGlg,RclTblPadDct[rt],"NODATA")
      rt = RCLSTBL_REGENLENS
      ReglRcl = RbAf(KrtPadDct[KAART_REGENLENS],RclTblPadDct[rt],"NODATA")
      rt = RCLSTBL_CONDUCTIV
      CondRcl=RbAf(KrtPadDct[KAART_MINERAALRIJKDOM],RclTblPadDct[rt],"NODATA")
      rt = RCLSTBL_OEVER
      OevRcl = RbAf(KrtPadDct[KAART_OVERSTR_ZUUR],RclTblPadDct[rt],"NODATA")
      rt = RCLSTBL_FLUX
      FluxRcl = RbAf(KrtPadDct[KAART_FLUX],RclTblPadDct[rt],"NODATA")
      CpH = BodGlgRcl + ReglRcl + CondRcl + OevRcl + FluxRcl
      rt = RCLSTBL_ZUUR
      ZuurRas = RbAf(CpH,RclTblPadDct[rt],"NODATA")
    except: raise FOUT("pH"+rtmsg +rt +"):\n" +str(sys.exc_type)+": "+str(sys.exc_value))
    ZuurRas.save(KrtPadDct[KAART_ZUUR])
    del BodGlg,BodGlgRcl,ReglRcl,CondRcl,OevRcl,FluxRcl,CpH  # ! GLGras,ZuurRas niet !
  elif Vegetatie_berekenen:
    if GEEN_pH_Trofie: ZuurRas = 0
    else: ZuurRas = RasterOfUitsnijden(KrtPadDct[KAART_ZUUR])

  prgblok = "[-Trofie_berekening-]"
  if Trofie_berekenen:
    ap.AddMessage("Trofie berekening ...")
    OverstRas = RasterOfUitsnijden(KrtPadDct[KAART_OVERSTR_TROFIE])
    BodGvg = BodemRas + RasterOfUitsnijden(KrtPadDct[KAART_GVG]) * gxgFaktor
    try:
      rt = RCLSTBL_BGVGTROFIE
      Nminer = RbAf(BodGvg,RclTblPadDct[rt],"NODATA")
    except: raise FOUT("Trofie"+rtmsg+rt+"):\n"+str(sys.exc_type)+ ": "+str(sys.exc_value))
    Natmosf = RasterOfUitsnijden(KrtPadDct[KAART_N_ATM_DEPOSIT])
    Ndiermest = RasterOfUitsnijden(KrtPadDct[KAART_N_MEST_DIER])
    Nkunstmest = RasterOfUitsnijden(KrtPadDct[KAART_N_MEST_KUNST])
    BodNtot = BodemRas + Nminer + Natmosf + Ndiermest + Nkunstmest
    CodTrofie = ap.sa.Con(ManagRas<=2, BodNtot, BodNtot+500000)
    try:
      rt = RCLSTBL_BNTROFIE
      CodTrRcl = RbAf(CodTrofie,RclTblPadDct[rt],"NODATA")
    except: raise FOUT("Trofie"+rtmsg+rt+"):\n" +str(sys.exc_type)+": "+str(sys.exc_value))
    InitTrofie = ap.sa.Con((OverstRas>0) & (CodTrRcl<=3), CodTrRcl+1, CodTrRcl)
    TrofieRas = ap.sa.Con((InitTrofie>=1) & (InitTrofie<=5), InitTrofie, 0)
    TrofieRas.save(KrtPadDct[KAART_TROFIE])
    del OverstRas,BodGvg,Nminer,Natmosf,Ndiermest,Nkunstmest,BodNtot
    del CodTrofie,CodTrRcl,InitTrofie     # ! Managras, TrofieRas niet !
  elif Vegetatie_berekenen:
    if GEEN_pH_Trofie: TrofieRas = 0
    else: TrofieRas = RasterOfUitsnijden(KrtPadDct[KAART_TROFIE])


 #| Vegetatie berekening
 #| ====================
  if Vegetatie_berekenen:

   # -> Veg1: Nichetabel en -kolommen (def uit parameterbestand)
   # --------------------------------
    prgblok = "[-Veg1-]"
    ap.AddMessage("Vegetatie: NicheTabel ...")
    KodeKol=ParDct[KOLOM_KODE]
    B_Kol=ParDct[KOLOM_BODEM]
    Z_Kol=ParDct[KOLOM_ZUUR]
    T_Kol=ParDct[KOLOM_TROFIE]
    I_Kol=ParDct[KOLOM_OVERSTROMING]  #"Inundatie"    |niet leeg bij *_gebruiken, zie
    M_Kol=ParDct[KOLOM_BEHEER]        #"Management"   |   ParametersInlezenKontroleren
    GHGminKol=ParDct[KOLOM_GHGMIN]
    GHGmaxKol=ParDct[KOLOM_GHGMAX]
    GLGminKol=ParDct[KOLOM_GLGMIN]
    GLGmaxKol=ParDct[KOLOM_GLGMAX]
    tbl_kols=[f.name for f in ap.ListFields(NicheTbl)]
    errmsg=""
    for knm in [KodeKol,B_Kol,Z_Kol,T_Kol,GHGminKol,GHGmaxKol,GLGminKol,GLGmaxKol]:
      if knm not in tbl_kols: errmsg = errmsg+"  '"+knm+"'"
    if Overstroming_gebruiken and I_Kol not in tbl_kols: errmsg = errmsg+"  '"+I_Kol+"'"
    if Beheer_gebruiken and M_Kol not in tbl_kols: errmsg = errmsg+"  '"+M_Kol+"'"
    if errmsg: raise FOUT("NICHETABEL: ontbrekende kolom(men): "+errmsg+" !")

   # -> Veg2: gewogen basisrasters, GLG/GHG-rasters, somGHG/GLG
   # ----------------------------------------------------------
    # INTEGER: mogelijke fout bij "999.0" want ingelezen als string ('literal') en daarop
    # werkt int niet (wel bij "999"); wat wel werkt: int(float("999.0")) ! MAAR: AFGEKAPT !
    # PLAFOND_GXG (of plaf_GxG): zie hieronder Veg3
    prgblok = "[-Veg2-]"
    ap.AddMessage("Vegetatie: rasters ...")
    try:
      plaf_GxG = int(float(ParDct[PLAFOND_GXG]))  #begrenzing "diepte" grondwstand (cm)
      B_fakt = int(float(ParDct[FAKTOR_BODEM]))
      if GEEN_pH_Trofie: # => geen bijdrage in somGxg en OOK NIET in BZTIM (in -Veg3-)
        Z_fakt = 0
        T_fakt = 0
      else:
        Z_fakt = int(float(ParDct[FAKTOR_ZUUR]))
        T_fakt = int(float(ParDct[FAKTOR_TROFIE]))
      #I_fakt = 0;   M_fakt = 0     # overbodig, testen bij uiteindelijk gebruik
      if Overstroming_gebruiken: I_fakt = int(float(ParDct[FAKTOR_OVERSTROMING]))
      if Beheer_gebruiken: M_fakt = int(float(ParDct[FAKTOR_BEHEER]))
    except: raise FOUT("Fout in PARAMETERBESTAND (wegingsfaktoren): " +str(sys.exc_value))

    BZTIMgewR = SomGewogenBasisRasters()
    del BodemRas,ZuurRas,TrofieRas,ManagRas

    #GLGras bestaat al
    GHGras = RasterOfUitsnijden(KrtPadDct[KAART_GHG]) * gxgFaktor
    somGHG, somGLG = BerekenSomGxG(GHGras), BerekenSomGxG(GLGras)    #rasterOBJEKTEN
    del BZTIMgewR, GHGras, GLGras

   # -> Veg3: Berekenen vegetatie-voorspelling
   # -----------------------------------------
    # GxG: waterstanden tov maaiveld
    # Eerste versie NICHE: in cm en positief naar beneden, negatief boven maaiveld:
    # DUS:  GxGmin = dieper =  groter   EN:   GxGmax = hoger = kleiner
    # => voor reclass: from=max en to=min
    # In de berekening blijft dit behouden, maar GXG_FAKTOR geeft mogelijkheid tot andere
    # eenheden (bv m) en ander teken (positief boven, negatief onder) voor de input
    # PLAFOND_GXG (of plaf_GxG) ook in (pos.)cm: boven/ondergrens GxG; moet veelvoud van
    # 10 zijn (bv 1000) want is positiebepalend (zie #| opm3), dus:
    #   - optellen in BZTIM voor de range-bepaling om ev neg NicheTbl-GxG af te trekken
    #   - optellen in somGxG zodat eventuele negatieve GxG ervan kunnen afgetrokken w
    # !! GXG_FAKTOR moet dus zowel op GXG-rasters als op GXGmax,min toegepast worden !!
    # Opm indien GEEN_pH_Trofie dan Z_fakt en T_fakt =0 (hierboven), dus geen bijdrage in
    #     BZTIM hieronder: nodig anders (omdat er dan wel waarden staan voor Z en T) vallen
    #     somGxG altijd buiten de ranges (=voldoen niet voor Z en T) !!!

    prgblok = "[-Veg3-]"
    RngGHG, RngGLG = {}, {}
    I_term, M_term = 0, 0
    rcl_f_nm = tmpdir+SEP+"reclassASCII.txt"  # vr ReclassifySomGxG  (1x del bij Opruimen)

    ap.AddMessage("Vegetatie: reclass-ranges berekenen ...")
    for rowNT in ap.SearchCursor(NicheTbl):
      VegKode = "v" + str(int(float(rowNT.getValue(KodeKol))))
      if VegKode not in RngGHG: RngGHG[VegKode]=[]; RngGLG[VegKode]=[]
      if Overstroming_gebruiken: I_term = I_fakt * int(float(rowNT.getValue(I_Kol)))
      if Beheer_gebruiken: M_term = M_fakt * int(float(rowNT.getValue(M_Kol)))
      BZTIM = B_fakt * int(float(rowNT.getValue(B_Kol))) + \
              Z_fakt * int(float(rowNT.getValue(Z_Kol))) + \
              T_fakt * int(float(rowNT.getValue(T_Kol))) + I_term + M_term + plaf_GxG
      GHGfrom = BZTIM + int(float(rowNT.getValue(GHGmaxKol))*gxgFaktor)
      GHGto = BZTIM + int(float(rowNT.getValue(GHGminKol))*gxgFaktor)
      GLGfrom = BZTIM + int(float(rowNT.getValue(GLGmaxKol))*gxgFaktor)
      GLGto = BZTIM + int(float(rowNT.getValue(GLGminKol))*gxgFaktor)
      if GHGfrom>GHGto: raise FOUT("GHGfrom>GHGto bij VegetatieKode "+VegKode)
      if GLGfrom>GLGto: raise FOUT("GLGfrom>GLGto bij VegetatieKode "+VegKode)
      # (from,to) opslaan als tuples van ints om naderhand te kunnen sorteren
      # zeker niet als strings want dan mgl sorteren fout: "100 999" is < "2 999"
      RngGHG[VegKode].append((GHGfrom,GHGto))
      RngGLG[VegKode].append((GLGfrom,GLGto))

    ap.AddMessage("Vegetatie: verwachtingskaarten ...")
    for VegKode in RngGHG:     #! telt ineens ook voor RngGLG !
      ap.AddMessage("\t\t ... "+VegKode)
      VegKansResult = VegResRWS +SEP+ VegKode
      if ap.Exists(VegKansResult): ap.Delete_management(VegKansResult)
      #!! optellen van nulraster (## opm4) moet gebeuren in ReclassifySomGxG, want de 2
      #!! rasters ReclResGxG moeten al 0/1 waarden hebben VOOR de vermenigvuldiging hier !
      RclsSomGHGras = ReclassifySomGxG(somGHG,RngGHG,VegKode,"somGHG")
      RclsSomGLGras = ReclassifySomGxG(somGLG,RngGLG,VegKode,"somGLG")
      uitTms = RclsSomGHGras * RclsSomGLGras
      uitTms.save(VegKansResult)

    ap.Delete_management(rcl_f_nm)
    del somGLG, somGHG, RclsSomGHGras, RclsSomGLGras, uitTms


 # Opruimen
 # --------
  ap.AddMessage("\n")
  try:
    if ap.Exists(tmpdir):
      rmtree(tmpdir)
      ap.RefreshCatalog(os.path.dirname(tmpdir))
  except:
    ap.AddWarning("Mogelijk probleempje bij opruimen tijdelijke TEMPdir '"+tmpdir+"'; " \
                  "deze mag gewist worden.\n" +str(sys.exc_value))

except FOUT as f:
  ap.AddError("\nFOUT-> "+f.message+"\n")
  if ap.Exists(tmpdir):
    rmtree(tmpdir)
    ap.AddWarning("Mogelijk blijft een tijdelijke TEMPdir '"+tmpdir+ \
                  "' achter; deze mag gewist worden.\n")

except:
  ap.AddError("\nFOUT in blok "+prgblok+"\n"+str(sys.exc_type)+ ": "+str(sys.exc_value))
  if ap.Exists(tmpdir):
    rmtree(tmpdir)
    ap.AddWarning("Mogelijk blijft een tijdelijke TEMPdir '"+tmpdir+ \
                  "' achter; deze mag gewist worden.\n")


#|###################################################################################
# class ToolValidator:
#
#   """Class for validating a tool's parameter values and controlling
#   the behavior of the tool's dialog."""
#
#   def __init__(self):
#     """Setup arcpy and the list of tool parameters."""
#     import arcpy
#     self.params = arcpy.GetParameterInfo()
#
#   def initializeParameters(self):
#     """Refine the properties of a tool's parameters.  This method is
#     called when the tool is opened."""
#     self.params[5].enabled = 0
#     self.params[6].enabled = 0
#     self.params[7].enabled = 0
#     self.params[8].enabled = 0
#     self.params[9].enabled = 0
#     self.params[10].enabled = 0
#     self.params[11].enabled = 0
#     return
#
#   def updateParameters(self):
#     """Modify the values and properties of parameters before internal
#     validation is performed.  This method is called whenever a parmater
#     has been changed."""
#     if self.params[7].value:  #dus GEEN gebruik v pH,Trofie
#       self.params[2].enabled = 0
#       self.params[2].value = 0
#       self.params[3].enabled = 0
#       self.params[3].value = 0
#     else:
#       self.params[2].enabled = 1
#       self.params[3].enabled = 1
#     if self.params[2].value or self.params[3].value or self.params[4].value:
#       if not self.params[7].value:  #dus WEL gebruik v pH,Trofie
#         self.params[8].enabled = 1
#       else:
#         self.params[8].enabled = 0
#         self.params[8].value = ""
#     else:
#       self.params[8].enabled = 0
#       self.params[8].value = ""
#     if self.params[2].value or self.params[3].value:
#       self.params[9].enabled = 1
#     else:
#       self.params[9].enabled = 0
#       self.params[9].value = ""
#     if self.params[4].value:
#       self.params[5].enabled = 1
#       self.params[6].enabled = 1
#       self.params[7].enabled = 1
#       self.params[10].enabled = 1
#       self.params[11].enabled = 1
#     else:
#       self.params[5].enabled = 0
#       self.params[5].value = 0
#       self.params[6].enabled = 0
#       self.params[6].value = 0
#       self.params[7].enabled = 0
#       self.params[7].value = 0
#       self.params[10].enabled = 0
#       self.params[10].value = ""
#       self.params[11].enabled = 0
#       self.params[11].value = ""
#     if self.params[0].value and str(self.params[0].value)[:1] == " ":
#       self.params[0].value = "---"
#     if self.params[1].value and str(self.params[1].value)[:1] == " ":
#       self.params[1].value = "---"
#     if self.params[8].value and str(self.params[8].value)[:1] == " ":
#       self.params[8].value = "---"
#     if self.params[9].value and str(self.params[9].value)[:1] == " ":
#       self.params[9].value = "---"
#     if self.params[10].value and str(self.params[10].value)[:1] == " ":
#       self.params[10].value = "---"
#     if self.params[11].value and str(self.params[11].value)[:1] == " ":
#       self.params[11].value = "---"
#     if self.params[12].value and str(self.params[12].value)[:1] == " ":
#       self.params[12].value = "---"
#     return
#
#   def updateMessages(self):
#     """Modify the messages created by internal validation for each tool
#     parameter.  This method is called after internal validation."""
#     if arcpy.CheckExtension("Spatial") != "Available":
#       self.params[0].setErrorMessage("Spatial Analyst vereist !")
#       self.params[1].setErrorMessage("Spatial Analyst niet beschikbaar !")
#     #if self.params[8].enabled and not self.params[8].altered:
#     if self.params[8].enabled and not self.params[8].value:
#       self.params[8].value = "---"
#     if self.params[9].enabled and not self.params[9].altered:
#       self.params[9].value = "---"
#     if self.params[10].enabled and not self.params[10].altered:
#       self.params[10].value = "---"
#     if self.params[11].enabled and not self.params[11].altered:
#       self.params[11].value = "---"
#       #self.params[11].setErrorMessage("Een geldige 'workspace' opgeven !")
#     if not(self.params[2].value or self.params[3].value or self.params[4].value):
#     #if not(self.params[2].altered or self.params[3].altered or self.params[4].altered):
#       self.params[2].setErrorMessage("Minstens 1 berekening selekteren !")
#       self.params[3].setErrorMessage("Minstens 1 berekening selekteren !")
#       self.params[4].setErrorMessage("Minstens 1 berekening selekteren !")
#     return
#
