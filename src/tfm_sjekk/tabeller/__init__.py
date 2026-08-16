"""Kodetabeller og prosjektets TFM-master.

MERK (§8): NS 3451 og NS 3457-serien er betalte standarder fra Standard
Norge. Kodetabellene ligger IKKE i dette repoet og skal aldri legges hit.
Brukeren peker på sin egen CSV med ``--kodetabell``. Filene under
``eksempler/`` er fiktive og ikke-normative.
"""

from tfm_sjekk.tabeller.kodetabell import Kodetabell, les_kodetabell
from tfm_sjekk.tabeller.master import TfmMaster, les_master

__all__ = ["Kodetabell", "TfmMaster", "les_kodetabell", "les_master"]
