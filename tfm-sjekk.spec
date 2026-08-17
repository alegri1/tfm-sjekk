# PyInstaller-oppskrift for frittstående binærfil (§6, §13).
#
# «Mange BIM-koordinatorer har ikke Python installert og får ikke lov til å
# installere det heller.» Derfor én fil de kan laste ned og kjøre.
#
#     uv run pyinstaller tfm-sjekk.spec --noconfirm
#
# Resultat: dist/tfm-sjekk[.exe]
#
# ifcopenshell er tung og delvis native — et kompilert wrapper-bibliotek pluss
# skjemadata den laster i drift. `collect_all` tar med alle tre delene
# (datafiler, binærfiler, skjulte importer); uten den bygger binæren fint og
# feiler først når noen åpner en IFC-fil.

from PyInstaller.utils.hooks import collect_all

ifc_datas, ifc_binaries, ifc_hidden = collect_all("ifcopenshell")

analyse = Analysis(  # noqa: F821  (PyInstaller injiserer navnene)
    ["src/tfm_sjekk/__main__.py"],
    pathex=["src"],
    binaries=ifc_binaries,
    datas=ifc_datas,
    hiddenimports=ifc_hidden,
    # Ingenting her brukes av verktøyet, og alt av det er stort.
    excludes=[
        "tkinter",
        "matplotlib",
        "IPython",
        "pytest",
        "hypothesis",
        "PIL",
    ],
    noarchive=False,
)

pyz = PYZ(analyse.pure)  # noqa: F821

exe = EXE(  # noqa: F821
    pyz,
    analyse.scripts,
    analyse.binaries,
    analyse.datas,
    [],
    name="tfm-sjekk",
    console=True,
    # Én fil, ikke en mappe: skal kunne sendes som vedlegg og kjøres direkte.
    onefile=True,
    upx=False,  # UPX gjør oppstarten tregere og trigger antivirus
    strip=False,
    disable_windowed_traceback=False,
)
