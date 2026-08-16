"""Rapportformater (§5).

Prioritet: BCF er viktigst — «forskjellen mellom «interessant skript» og
«noe vi tar i bruk»». HTML er det folk deler i Teams. CSV er for videre
analyse. Exit-koden gjør verktøyet kjørbart som port i en leveranseprosess.
"""

from tfm_sjekk.rapport.bcf import skriv_bcf
from tfm_sjekk.rapport.csv_rapport import skriv_csv
from tfm_sjekk.rapport.html import skriv_html

__all__ = ["skriv_bcf", "skriv_csv", "skriv_html"]
