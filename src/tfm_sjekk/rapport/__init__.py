"""Rapportformater (§5).

Prioritet: BCF er viktigst — «forskjellen mellom «interessant skript» og
«noe vi tar i bruk»». HTML er det folk deler i Teams. CSV er for videre
analyse. Exit-koden gjør verktøyet kjørbart som port i en leveranseprosess.
"""

from tfm_sjekk.rapport.bcf import normaliser_tidsstempel, skriv_bcf
from tfm_sjekk.rapport.csv_rapport import skriv_csv
from tfm_sjekk.rapport.html import skriv_html
from tfm_sjekk.rapport.xlsx import skriv_xlsx

__all__ = ["normaliser_tidsstempel", "skriv_bcf", "skriv_csv", "skriv_html", "skriv_xlsx"]
