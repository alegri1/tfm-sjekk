"""Kontrollene K1–K9 (§4).

Importrekkefølgen under er kjørerekkefølgen og rekkefølgen i rapporten.
Legger du til en kontroll: lag en fil, dekorer klassen med `@registrer`,
og importer den her.
"""

from tfm_sjekk.kontroller.base import Kontroll, alle_kontroller, kjor_alle, registrer

# Registrering skjer ved import — rekkefølgen er signifikant.
from tfm_sjekk.kontroller import k1_tilstedevaerelse  # noqa: F401  isort:skip
from tfm_sjekk.kontroller import k2_syntaks  # noqa: F401  isort:skip
from tfm_sjekk.kontroller import k3_systemkode  # noqa: F401  isort:skip
from tfm_sjekk.kontroller import k4_spesifisitet  # noqa: F401  isort:skip
from tfm_sjekk.kontroller import k5_komponentkode  # noqa: F401  isort:skip
from tfm_sjekk.kontroller import k6_unikhet  # noqa: F401  isort:skip
from tfm_sjekk.kontroller import k7_master  # noqa: F401  isort:skip
from tfm_sjekk.kontroller import k8_elektro  # noqa: F401  isort:skip
from tfm_sjekk.kontroller import k9_mmi  # noqa: F401  isort:skip

__all__ = ["Kontroll", "alle_kontroller", "kjor_alle", "registrer"]
