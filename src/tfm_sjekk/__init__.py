"""tfm-sjekk — validerer TFM-merking i IFC-modeller.

Se `specification/tfm-sjekk-spesifikasjon.md` for hele spesifikasjonen.
Paragrafhenvisninger i koden (§4, §8, …) peker dit.
"""

from tfm_sjekk.kontekst import Kontekst
from tfm_sjekk.modell import Alvorlighet, Funn, IfcObjekt, TfmId
from tfm_sjekk.parser import ParseFeil, parse

__version__ = "0.1.0"

__all__ = [
    "Alvorlighet",
    "Funn",
    "IfcObjekt",
    "Kontekst",
    "ParseFeil",
    "TfmId",
    "parse",
]
