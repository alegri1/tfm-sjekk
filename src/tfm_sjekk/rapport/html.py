"""HTML-rapport — «én selvstendig fil, sorterbar tabell» (§5).

Selvstendig betyr uten eksterne ressurser: ingen CDN, ingen bilder. Den skal
kunne sendes som vedlegg i Teams og åpnes på en maskin uten nett.
"""

from __future__ import annotations

from collections import Counter
from pathlib import Path

from jinja2 import Template

from tfm_sjekk.modell import Alvorlighet, Funn

MAL = Template(
    """<!doctype html>
<html lang="no">
<meta charset="utf-8">
<title>TFM-rapport — {{ tittel }}</title>
<style>
  /* Hele paletten defineres her, for lys bakgrunn. Mørk modus under bytter
     bare ut verdiene — ingen farge har sin eneste definisjon der, ellers
     ville den manglet for alle andre. */
  :root {
    color-scheme: light dark;
    --bg: #ffffff;
    --tekst: #1a1a1a;
    --dempet: #5f5f5f;
    --ramme: #dddddd;
    --ramme-sterk: #cccccc;
    --th-bg: #f4f4f4;
    --ok: #2e7d32;
    --feil: #c0392b;
    --advarsel: #e67e22;
    --info: #7f8c8d;
  }
  @media (prefers-color-scheme: dark) {
    :root {
      --bg: #1a1a1a;
      --tekst: #e8e8e8;
      --dempet: #a3a3a3;
      --ramme: #3a3a3a;
      --ramme-sterk: #4a4a4a;
      --th-bg: #262626;
      /* Lysere varianter: de mettede fargene over forsvinner mot mørk bakgrunn. */
      --ok: #66bb6a;
      --feil: #e57373;
      --advarsel: #ffb74d;
      --info: #b0bec5;
    }
  }
  /* Bakgrunn og tekstfarge må stå eksplisitt. Uten dem arver sida browserens
     standardfarger, og da ble overskriftsraden hvit på hvitt i mørk modus. */
  body { font: 15px/1.5 system-ui, sans-serif; margin: 2rem auto;
         max-width: 1200px; padding: 0 1rem;
         background: var(--bg); color: var(--tekst); }
  h1 { margin-bottom: .25rem; }
  .meta { color: var(--dempet); margin-bottom: 1.5rem; }
  .tall { display: flex; gap: 1.5rem; margin-bottom: 1.5rem; flex-wrap: wrap; }
  .tall div { border: 1px solid var(--ramme-sterk); border-radius: 6px;
              padding: .6rem 1rem; }
  .tall b { display: block; font-size: 1.6rem; }
  table { border-collapse: collapse; width: 100%; }
  th, td { text-align: left; padding: .4rem .6rem; border-bottom: 1px solid var(--ramme);
           vertical-align: top; }
  th { cursor: pointer; user-select: none; background: var(--th-bg); color: var(--tekst);
       position: sticky; top: 0; }
  tr.feil td:first-child { border-left: 4px solid var(--feil); }
  tr.advarsel td:first-child { border-left: 4px solid var(--advarsel); }
  tr.info td:first-child { border-left: 4px solid var(--info); }
  code { font-size: .9em; }
  /* Arver fargen fra .meta, som finnes i BEGGE palettene. En ny farge her
     ville vært usynlig i den ene — det har skjedd før. */
  /* Dempet, ikke advarselsfarge. Et bevisst unntak er ikke en forglemmelse,
     og oransje stripe ved siden av «0 advarsler» motsa hverandre. */
  tr.unntatt td { color: var(--dempet); font-style: italic; }
  ul.hoppet { margin: 0 0 1.5rem 1.25rem; padding: 0; color: var(--dempet); font-size: 0.9rem; }
  ul.hoppet li { margin: 0.15rem 0; }
  table.dekning { width: auto; margin-bottom: 1.5rem; }
  table.dekning th { cursor: default; position: static; }
  table.dekning td { font-variant-numeric: tabular-nums; }
  .tom { padding: 2rem; text-align: center; color: var(--ok); font-size: 1.2rem; }
</style>
<h1>TFM-rapport</h1>
<p class="meta">{{ tittel }}</p>

<div class="tall">
  <div><b>{{ antall.feil }}</b>feil</div>
  <div><b>{{ antall.advarsel }}</b>advarsler</div>
  <div><b>{{ antall.info }}</b>info</div>
  <div><b>{{ i_omfang }}</b>objekter kontrollert</div>
  <div><b>{{ objekter }}</b>objekter lest</div>
</div>

{% if hoppet_over %}
<p class="meta">Hoppet over — disse kontrollene så ikke etter noe:</p>
<ul class="hoppet">
{% for id, grunn, raad in hoppet_over %}
  <li><code>{{ id }}</code> {{ grunn }}{% if raad %} — {{ raad }}{% endif %}</li>
{% endfor %}
</ul>
{% endif %}

{% if dekning %}
<table class="dekning">
<thead><tr><th>Fagmodell</th><th>I omfanget</th><th>Lest</th>
{% if uleselige %}<th>Uleselig TFM</th>{% endif %}</tr></thead>
<tbody>
{% for fil, tall in dekning.items() %}
{% if fil in unntatte %}
<tr class="unntatt">
  <td>{{ fil }}</td>
  <td colspan="{{ 3 if uleselige else 2 }}">unntatt — kontrolleres ikke for TFM
  ({{ tall[1] }} lest)</td>
</tr>
{% else %}
<tr{% if not tall[0] %} class="advarsel"{% endif %}>
  <td>{{ fil }}</td><td>{{ tall[0] }}</td><td>{{ tall[1] }}</td>
  {% if uleselige %}<td>{{ uleselige.get(fil, 0) or "" }}</td>{% endif %}
</tr>
{% endif %}
{% endfor %}
</tbody>
</table>
{% endif %}

{% if funn %}
<table id="t">
<thead><tr>
  <th onclick="sorter(0)">Kontroll</th>
  <th onclick="sorter(1)">Grad</th>
  <th onclick="sorter(2)">Fil</th>
  <th onclick="sorter(3)">Klasse</th>
  <th onclick="sorter(4)">TFM</th>
  <th onclick="sorter(5)">Melding</th>
</tr></thead>
<tbody>
{% for f in funn %}
<tr class="{{ f.alvorlighet.value }}">
  <td>{{ f.kontroll }}</td>
  <td>{{ f.alvorlighet.value }}</td>
  <td>{{ f.kildefil or '' }}</td>
  <td>{{ f.ifc_klasse or '' }}</td>
  <td><code>{{ f.tfm or '' }}</code></td>
  <td>{{ f.melding }}</td>
</tr>
{% endfor %}
</tbody>
</table>
<script>
let stigende = [];
function sorter(n) {
  const tbody = document.querySelector('#t tbody');
  const rader = [...tbody.rows];
  stigende[n] = !stigende[n];
  const retning = stigende[n] ? 1 : -1;
  rader.sort((a, b) =>
    retning * a.cells[n].innerText.localeCompare(b.cells[n].innerText, 'no'));
  rader.forEach(r => tbody.appendChild(r));
}
</script>
{% else %}
<p class="tom">Ingen funn. Alle aktive kontroller passerte.</p>
{% endif %}
</html>
"""
)


def skriv_html(
    funn: list[Funn],
    sti: Path,
    tittel: str,
    objekter: int = 0,
    hoppet_over: list[tuple[str, str, str]] | None = None,
    dekning: dict[str, tuple[int, int]] | None = None,
    unntatte: list[str] | None = None,
    uleselige: dict[str, int] | None = None,
) -> Path:
    """`dekning` er (i omfanget, lest) per fagmodell.

    Tabellen vises uansett utfall, ikke bare når noe mangler: det er den rene
    rapporten en leser trenger å kunne stole på.
    """
    teller = Counter(f.alvorlighet for f in funn)
    sti.parent.mkdir(parents=True, exist_ok=True)
    sti.write_text(
        MAL.render(
            funn=funn,
            tittel=tittel,
            objekter=objekter,
            hoppet_over=hoppet_over or [],
            dekning=dekning or {},
            unntatte=set(unntatte or []),
            # Kolonnen vises bare naar noe faktisk falt ut. En kolonne med
            # null i hver rad i hver kjoering blir ikke lest.
            uleselige=uleselige or {},
            i_omfang=sum(tall[0] for tall in (dekning or {}).values()),
            antall={
                "feil": teller[Alvorlighet.FEIL],
                "advarsel": teller[Alvorlighet.ADVARSEL],
                "info": teller[Alvorlighet.INFO],
            },
        ),
        encoding="utf-8",
    )
    return sti
