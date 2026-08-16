"""IFC-lesing. Eneste sted i pakken som importerer ifcopenshell.

Grensen er bevisst: `les_modell` returnerer `IfcObjekt`-lister av ren
picklebar data. Det gjør federering over prosesser mulig, lar kontrollene
testes uten en eneste IFC-fil, og isolerer et bytte til IFC5 til denne mappa.
"""

from tfm_sjekk.ifc.federering import les_modeller
from tfm_sjekk.ifc.loader import les_modell

__all__ = ["les_modell", "les_modeller"]
