"""Tester for kommandolinja, kjørt som egen prosess.

CliRunner fanger utdata i sin egen strøm og sier derfor ingenting om hva som
skjer i en ekte terminal. Testene her starter en faktisk prosess, fordi det
er den eneste måten å treffe kodesida i konsollen på — og det er nettopp der
exit-koden kan bli feil av grunner som ikke har noe med modellen å gjøre.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from conftest import uten_ansi
from fixtures.syntetisk import GYLDIG, lag_modell, lag_modell_pa_avveie


def kjor(
    argumenter: list[str],
    koding: str | None = None,
    mappe: Path | None = None,
) -> subprocess.CompletedProcess:
    """Kjører CLI-en som egen prosess.

    `mappe` setter arbeidskatalogen. Den betyr noe siden verktøyet leter etter
    «tfm-sjekk.toml» der: uten den kjører testene fra repoets rot, som har en —
    og da prøver de noe annet enn de tror.
    """
    miljo = dict(os.environ)
    if koding:
        miljo["PYTHONIOENCODING"] = koding
    return subprocess.run(
        [sys.executable, "-m", "tfm_sjekk.cli", *argumenter],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=miljo,
        cwd=str(mappe) if mappe else None,
    )


def test_ren_modell_gir_exit_0(tmp_path):
    modell = lag_modell([("IfcFlowTerminal", GYLDIG)], tmp_path / "ren.ifc")
    resultat = kjor(["sjekk", str(modell), "--ut", str(tmp_path / "ut")])
    assert resultat.returncode == 0, resultat.stdout + resultat.stderr


def test_modell_med_feil_gir_exit_1(tmp_path):
    modell = lag_modell([("IfcFlowTerminal", None)], tmp_path / "feil.ifc")
    resultat = kjor(["sjekk", str(modell), "--ut", str(tmp_path / "ut")])
    assert resultat.returncode == 1


def test_exit_koden_overlever_en_cp1252_konsoll(tmp_path):
    """«→» i oppsummeringslinja finnes ikke i cp1252.

    Uten omkodingen i cli-en kastet den avsluttende utskriften
    UnicodeEncodeError etter at rapportene var skrevet, og en ren modell fikk
    exit 1 — altså «underkjent» av kodesida i terminalen, ikke av kontrollene.
    Dette er standardoppsettet på en norsk Windows-maskin (§6: BIM-koordinatorer
    kjører Windows).
    """
    modell = lag_modell([("IfcFlowTerminal", GYLDIG)], tmp_path / "ren.ifc")
    resultat = kjor(["sjekk", str(modell), "--ut", str(tmp_path / "ut")], koding="cp1252")

    assert resultat.returncode == 0, resultat.stdout + resultat.stderr
    assert "UnicodeEncodeError" not in resultat.stderr
    assert "ingen funn" in resultat.stdout  # oppsummeringslinja kom ut


def test_federering_over_prosessgrensa(tmp_path):
    """`python -m tfm_sjekk` med flere filer starter arbeidsprosesser, og de
    importerer __main__ på nytt. Uten `if __name__`-vakta ville hele
    kontrollkjøringen startet om igjen i hvert barn."""
    modeller = [
        str(lag_modell([("IfcFlowTerminal", GYLDIG)], tmp_path / f"m{i}.ifc")) for i in range(3)
    ]
    resultat = kjor(["sjekk", *modeller, "--ut", str(tmp_path / "ut")])

    assert resultat.returncode == 1, resultat.stdout + resultat.stderr  # K6: samme ID i tre filer
    assert resultat.stdout.count("Leser 3 modell(er)") == 1, "kjørte flere ganger"
    assert "multiprocessing-fork" not in resultat.stderr


def test_filsti_forst_virker_uten_kommandoord(tmp_path):
    """Dra-og-slipp i Utforskeren sender bare filstier — «sjekk» settes inn."""
    modell = lag_modell([("IfcFlowTerminal", GYLDIG)], tmp_path / "ren.ifc")
    resultat = kjor([str(modell), "--ut", str(tmp_path / "ut")])
    assert resultat.returncode == 0, resultat.stdout + resultat.stderr
    assert "ingen funn" in resultat.stdout


def test_skrivefeil_i_kommandoen_gir_fortsatt_kommandofeil():
    """«sjekk» settes bare inn foran stier som finnes. Ellers ville en
    skrivefeil gitt «Path does not exist» i stedet for noe forståelig."""
    resultat = kjor(["kontrolller"])
    assert resultat.returncode != 0
    assert "No such command" in uten_ansi(resultat.stdout + resultat.stderr)


def test_standardkommando_er_rein_argumentbehandling():
    from tfm_sjekk.cli import _med_standardkommando

    assert _med_standardkommando([]) == []
    assert _med_standardkommando(["kontroller"]) == ["kontroller"]
    assert _med_standardkommando(["--help"]) == ["--help"]
    assert _med_standardkommando(["finnes-ikke.ifc"]) == ["finnes-ikke.ifc"]


def test_rapportmappa_legges_hos_modellen(tmp_path):
    """Ved dobbeltklikk er arbeidskatalogen exe-ens egen mappe, ikke modellens."""
    from tfm_sjekk.cli import _med_rapportmappe

    modell = tmp_path / "modell.ifc"
    modell.write_text("")

    ut = _med_rapportmappe(["sjekk", str(modell)])
    assert ut[-2] == "--ut"
    assert Path(ut[-1]) == tmp_path / "rapport"

    # Har brukeren sagt --ut selv, skal vi ikke overstyre.
    eget = ["sjekk", str(modell), "--ut", "et-annet-sted"]
    assert _med_rapportmappe(eget) == eget


def test_kontroller_listes_i_cp1252_konsoll():
    """Kontrolltitlene har æ, ø og å."""
    resultat = kjor(["kontroller"], koding="cp1252")
    assert resultat.returncode == 0
    assert resultat.stdout.count("\n") >= 9


# --- oppsett: forslag til tfm-sjekk.toml ---


def test_oppsett_skriver_forslag_til_skjermen(tmp_path):
    modell = lag_modell_pa_avveie(tmp_path / "avveie.ifc")
    resultat = kjor(["oppsett", str(modell)])
    assert resultat.returncode == 0, resultat.stdout + resultat.stderr
    assert '"Data"' in resultat.stdout
    assert '"Merking"' in resultat.stdout
    assert '"IfcBuildingElementProxy"' in resultat.stdout
    # Forkastelsen skal ikke ha blitt til konfigurasjon.
    assert "Fabrikat" not in resultat.stdout


def test_oppsett_skriver_til_fil(tmp_path):
    modell = lag_modell_pa_avveie(tmp_path / "avveie.ifc")
    fil = tmp_path / "forslag.toml"
    resultat = kjor(["oppsett", str(modell), "--ut", str(fil)])
    assert resultat.returncode == 0, resultat.stdout + resultat.stderr
    assert '"Data"' in fil.read_text(encoding="utf-8")


def test_oppsett_nekter_a_overskrive(tmp_path):
    modell = lag_modell_pa_avveie(tmp_path / "avveie.ifc")
    fil = tmp_path / "tfm-sjekk.toml"
    fil.write_text("# arbeidet mitt\n", encoding="utf-8")

    resultat = kjor(["oppsett", str(modell), "--ut", str(fil)])
    assert resultat.returncode == 1
    assert fil.read_text(encoding="utf-8") == "# arbeidet mitt\n"
    assert "--overskriv" in uten_ansi(resultat.stderr)

    resultat = kjor(["oppsett", str(modell), "--ut", str(fil), "--overskriv"])
    assert resultat.returncode == 0
    assert '"Data"' in fil.read_text(encoding="utf-8")


def test_oppsett_i_cp1252_konsoll(tmp_path):
    """Kommentarene i forslaget er norske og bruker «»."""
    modell = lag_modell_pa_avveie(tmp_path / "avveie.ifc")
    resultat = kjor(["oppsett", str(modell)], koding="cp1252")
    assert resultat.returncode == 0, resultat.stdout + resultat.stderr
    assert "objekter" in resultat.stdout


def test_oppsett_sier_at_alt_la_der_det_skulle(tmp_path):
    modell = lag_modell([("IfcFlowTerminal", GYLDIG)], tmp_path / "ren.ifc")
    resultat = kjor(["oppsett", str(modell)])
    assert resultat.returncode == 0
    assert "dekker modellene som de er" in uten_ansi(resultat.stderr)


def test_oppsett_skiller_ingenting_a_bygge_pa(tmp_path):
    modell = lag_modell([("IfcFlowTerminal", None)], tmp_path / "umerket.ifc")
    resultat = kjor(["oppsett", str(modell)])
    assert resultat.returncode == 0
    assert "ingen TFM-verdier" in uten_ansi(resultat.stderr)


def test_forslaget_kan_brukes_som_config(tmp_path):
    """Rundturen mot en ekte IFC-fil: fila verktøyet skriver, leser det selv.

    Uten forslaget finner K1 objektet i klassen utenfor omfanget aldri; med
    forslaget er både egenskapssettet, feltnavnet og klassen på plass.
    """
    modell = lag_modell_pa_avveie(tmp_path / "avveie.ifc")
    forslag = tmp_path / "forslag.toml"
    assert kjor(["oppsett", str(modell), "--ut", str(forslag)]).returncode == 0

    resultat = kjor(["sjekk", str(modell), "--config", str(forslag), "--ut", str(tmp_path / "ut")])
    assert resultat.returncode in (0, 1), resultat.stdout + resultat.stderr
    assert "Traceback" not in resultat.stderr


def test_forslaget_er_stabilt_over_to_kjoringer(tmp_path):
    modell = lag_modell_pa_avveie(tmp_path / "avveie.ifc")
    forste = tmp_path / "forste.toml"
    assert kjor(["oppsett", str(modell), "--ut", str(forste)]).returncode == 0

    andre = kjor(["oppsett", str(modell), "--config", str(forste)])
    assert andre.returncode == 0
    assert "dekker modellene som de er" in uten_ansi(andre.stderr)


def test_fil_som_heter_som_en_kommando_gar_til_sjekk(tmp_path):
    """Dra-og-slipp av «oppsett.ifc» skal sjekke fila, ikke treffe kommandoordet.

    Uten kommandoord er det `_med_standardkommando` som avgjør, og den ser bare
    på om første argument er et kjent kommandoord. «oppsett.ifc» er det ikke,
    så «sjekk» skal settes inn som for enhver annen fil.
    """
    modell = lag_modell([("IfcFlowTerminal", GYLDIG)], tmp_path / "oppsett.ifc")
    resultat = kjor([str(modell), "--ut", str(tmp_path / "ut")])
    assert resultat.returncode == 0, resultat.stdout + resultat.stderr
    assert "ingen funn" in resultat.stdout


def test_oppsett_listes_i_hjelpeteksten():
    resultat = kjor(["--help"])
    assert "oppsett" in uten_ansi(resultat.stdout)


def test_oppsett_foreslar_grammatikk_for_tidligfase(tmp_path):
    """Uttrekket er feilfritt, men grammatikken avviser alt.

    Verktøyet vet hvilken regel som avviser dem, og skal si det.
    """
    from fixtures.syntetisk import lag_tidligfasemodell

    modell = lag_tidligfasemodell(tmp_path / "tidligfase.ifc")
    resultat = kjor(["oppsett", str(modell)])
    assert resultat.returncode == 0, resultat.stdout + resultat.stderr
    assert "krev_plassering = false" in resultat.stdout
    assert "[grammatikk]" in resultat.stdout
    assert "dekker modellene som de er" not in uten_ansi(resultat.stderr)


def test_grammatikkforslaget_virker_som_config(tmp_path):
    """Rundturen: fem syntaksfunn skal bli til duplikatet som lå under dem."""
    from fixtures.syntetisk import lag_tidligfasemodell

    modell = lag_tidligfasemodell(tmp_path / "tidligfase.ifc")
    forslag = tmp_path / "forslag.toml"
    assert kjor(["oppsett", str(modell), "--ut", str(forslag)]).returncode == 0

    uten = kjor(["sjekk", str(modell), "--ut", str(tmp_path / "a")])
    med = kjor(["sjekk", str(modell), "--config", str(forslag), "--ut", str(tmp_path / "b")])
    assert "5 feil" in uten.stdout
    assert "2 feil" in med.stdout


def test_oppsett_med_grammatikk_i_cp1252_konsoll(tmp_path):
    """Kommentarene bruker «» og norske tegn."""
    from fixtures.syntetisk import lag_tidligfasemodell

    modell = lag_tidligfasemodell(tmp_path / "tidligfase.ifc")
    resultat = kjor(["oppsett", str(modell)], koding="cp1252")
    assert resultat.returncode == 0, resultat.stdout + resultat.stderr
    assert "krev_plassering = false" in resultat.stdout


# --- Oppsettet finnes uten flagg ---


def prosjekt(tmp_path):
    """En mappe som ligner et ekte prosjekt: modeller, tabeller, oppsett."""
    import shutil

    eks = Path(__file__).parent.parent / "eksempler"
    (tmp_path / "modeller").mkdir()
    (tmp_path / "tabeller").mkdir()
    modell = lag_modell([("IfcFlowTerminal", GYLDIG)], tmp_path / "modeller" / "rie.ifc")
    shutil.copy(eks / "FIKTIV-systemkoder.csv", tmp_path / "tabeller" / "ns3451.csv")
    shutil.copy(eks / "FIKTIV-tfm-master.csv", tmp_path / "TFM-master.csv")
    (tmp_path / "modeller" / "tfm-sjekk.toml").write_text(
        'tfm_master = "../TFM-master.csv"\nsystemtabell = "../tabeller/ns3451.csv"\n',
        encoding="utf-8",
    )
    return modell


def test_full_kjoring_uten_et_eneste_flagg(tmp_path):
    """Poenget med hele endringen: kommandoen skal kunne skrives fra hodet."""
    modell = prosjekt(tmp_path)
    resultat = kjor(["sjekk", str(modell), "--ut", str(tmp_path / "ut")])
    ut = uten_ansi(resultat.stdout)
    assert "tfm-sjekk.toml" in ut
    assert "K3: hoppet over" not in ut  # tabellen ble funnet via oppsettet
    assert "K7: hoppet over" not in ut  # mastera også


def test_kjoringen_sier_hvilket_oppsett_den_leste(tmp_path):
    modell = prosjekt(tmp_path)
    resultat = kjor(["sjekk", str(modell), "--ut", str(tmp_path / "ut")])
    linjer = uten_ansi(resultat.stdout).splitlines()
    assert linjer[0].startswith("Oppsett: ")
    assert "modeller" in linjer[0]


def test_uten_oppsett_sies_det_ogsaa(tmp_path):
    tom = tmp_path / "tom"
    tom.mkdir()
    modell = lag_modell([("IfcFlowTerminal", GYLDIG)], tmp_path / "ren.ifc")
    resultat = kjor(["sjekk", str(modell), "--ut", str(tmp_path / "ut")], mappe=tom)
    assert "ingen funnet" in uten_ansi(resultat.stdout).splitlines()[0]


def test_flagget_vinner_over_oppsettet(tmp_path):
    """Flagget er det brukeren skrev nettopp nå."""
    modell = prosjekt(tmp_path)
    annen = tmp_path / "annen.toml"
    annen.write_text("[grammatikk]\nplassering_siffer = 7\n", encoding="utf-8")

    resultat = kjor(["sjekk", str(modell), "--config", str(annen), "--ut", str(tmp_path / "ut")])
    ut = uten_ansi(resultat.stdout)
    assert "annen.toml" in ut.splitlines()[0]
    assert "K7: hoppet over" in ut  # den andre fila oppgir ingen master


def test_skrivefeil_i_sti_er_en_feil_ikke_et_hopp(tmp_path):
    """Uten dette ville en skrivefeil gitt «K7: hoppet over».

    Det er nøyaktig det samme verktøyet melder når du bevisst kjørte uten
    master — og brukeren ville trodd hun kjørte med.
    """
    modell = prosjekt(tmp_path)
    (tmp_path / "modeller" / "tfm-sjekk.toml").write_text(
        'tfm_master = "../TFM-mastr.csv"\n', encoding="utf-8"
    )
    resultat = kjor(["sjekk", str(modell), "--ut", str(tmp_path / "ut")])
    ut = uten_ansi(resultat.stdout + resultat.stderr)
    assert resultat.returncode == 2
    assert "TFM-mastr.csv" in ut
    assert "hoppet over" not in ut


def test_oppsett_kommandoen_finner_ogsaa_fila(tmp_path):
    modell = prosjekt(tmp_path)
    resultat = kjor(["oppsett", str(modell)])
    assert "tfm-sjekk.toml" in uten_ansi(resultat.stderr)


# --- En ukjent nøkkel i oppsettet stopper kjøringen ---


def test_ukjent_nokkel_gir_exit_2(tmp_path):
    """Samme kode som en sti i oppsettet som peker feil. Samme slags feil."""
    (tmp_path / "tfm-sjekk.toml").write_text(
        '[elektro]\nforing_systemkode = ["4360"]\n', encoding="utf-8"
    )
    modell = lag_modell([("IfcFlowTerminal", GYLDIG)], tmp_path / "rie.ifc")
    r = kjor(["sjekk", str(modell), "--ut", str(tmp_path / "ut")], mappe=tmp_path)
    assert r.returncode == 2, r.stdout + r.stderr


def test_ukjent_nokkel_gir_ingen_rapport(tmp_path):
    """Poenget er ikke exit-koden, men at det ikke kommer en rapport.

    En rapport laget med andre regler enn brukeren ba om, ser like ren ut som
    en riktig — og den blir delt i Teams.
    """
    (tmp_path / "tfm-sjekk.toml").write_text(
        '[elektro]\nforing_systemkode = ["4360"]\n', encoding="utf-8"
    )
    modell = lag_modell([("IfcFlowTerminal", GYLDIG)], tmp_path / "rie.ifc")
    ut = tmp_path / "ut"
    kjor(["sjekk", str(modell), "--ut", str(ut)], mappe=tmp_path)
    assert not (ut / "rapport.html").exists()


def test_meldingen_sier_hva_som_er_galt(tmp_path):
    (tmp_path / "tfm-sjekk.toml").write_text(
        '[elektro]\nforing_systemkode = ["4360"]\n', encoding="utf-8"
    )
    modell = lag_modell([("IfcFlowTerminal", GYLDIG)], tmp_path / "rie.ifc")
    r = kjor(["sjekk", str(modell), "--ut", str(tmp_path / "ut")], mappe=tmp_path)
    tekst = uten_ansi(r.stdout + r.stderr).replace("\n", " ")
    assert "foring_systemkode" in tekst
    assert "elektro" in tekst


# --- Oppsummeringslinja skal stemme med rapporten den nettopp skrev ---


ROT = Path(__file__).parent.parent


def demomodellene(tmp_path: Path) -> list[str]:
    """De tre demomodellene, bygget i tmp_path.

    Bygges her framfor å leses fra `eksempler/`: de filene er genererte og
    gitignorerte, og finnes ikke i en fersk klone.
    """
    sys.path.insert(0, str(ROT / "eksempler"))
    from fixtures.syntetisk import lag_elektromodell
    from lag_demomodell import ELEKTRO, RIE, RIV

    return [
        str(lag_modell(RIE, tmp_path / "demo-rie.ifc", plassering=True)),
        str(lag_modell(RIV, tmp_path / "demo-riv.ifc", plassering=True)),
        str(lag_elektromodell(ELEKTRO, tmp_path / "demo-elektro.ifc", geometri=True)),
    ]


def oppsummeringen(tmp_path: Path) -> tuple[str, Path]:
    ut = tmp_path / "ut"
    r = kjor(
        [
            "sjekk",
            *demomodellene(tmp_path),
            "--config",
            str(ROT / "eksempler" / "tfm-sjekk-full.toml"),
            "--ut",
            str(ut),
        ]
    )
    assert r.returncode == 1, r.stdout + r.stderr
    linjer = [linje for linje in uten_ansi(r.stdout).splitlines() if "→" in linje]
    assert linjer, r.stdout
    return linjer[-1], ut


def test_oppsummeringen_teller_alle_gradene(tmp_path):
    """Linja sa «13 feil, 1 advarsler» om en kjøring med sytten funn.

    De tre infofunnene sto i HTML-en, i CSV-en, i regnearket og i BCF-en — bare
    ikke i linja brukeren leser først. Et funn ingen vet om er like usynlig som
    et funn som aldri ble meldt.
    """
    import csv

    linje, ut = oppsummeringen(tmp_path)

    assert "13 feil" in linje
    assert "3 info" in linje

    with (ut / "funn.csv").open(encoding="utf-8-sig", newline="") as f:
        rader = list(csv.DictReader(f, delimiter=";"))
    assert len(rader) == 13 + 1 + 3, linje


def test_en_grad_uten_funn_nevnes_ikke(tmp_path):
    """Fraværet av ordet er beskjeden. «0 info» ville gjort linja lengre uten
    å si noe."""
    modell = lag_modell([("IfcFlowTerminal", GYLDIG)], tmp_path / "ren.ifc")
    r = kjor(["sjekk", str(modell), "--ut", str(tmp_path / "ut")])

    linje = [linje for linje in uten_ansi(r.stdout).splitlines() if "→" in linje][-1]
    assert "0 " not in linje
    assert "ingen funn" in linje


def test_entallsformen_er_riktig(tmp_path):
    """«1 advarsler» er ikke norsk, og flertall her er ikke en «+s»."""
    linje, _ = oppsummeringen(tmp_path)

    assert "1 advarsel" in linje
    assert "1 advarsler" not in linje


def test_oppsummeringen_navngir_hver_fil_som_ble_skrevet(tmp_path):
    """En bruker som ikke vet at et format finnes, leter ikke etter det.

    Linja navnga rapport.html og funn.bcfzip. CSV-en og regnearket ble skrevet
    til ingen.
    """
    linje, ut = oppsummeringen(tmp_path)

    skrevet = sorted(p.name for p in ut.iterdir())
    assert skrevet == ["funn.bcfzip", "funn.csv", "funn.xlsx", "rapport.html"]
    for navn in skrevet:
        assert navn in linje, f"{navn} ble skrevet, men ikke nevnt"


def test_stien_er_skrevet_i_plattformens_form(tmp_path):
    r"""`f"{ut}/rapport.html"` ga «...\ut/rapport.html» på Windows."""
    linje, ut = oppsummeringen(tmp_path)

    B = chr(92)  # ren backslash; en literal her ville vært en escape-sekvens
    stier = linje.split("→", 1)[1]
    assert str(ut / "rapport.html") in stier
    assert B + "/" not in stier and "/" + B not in stier
