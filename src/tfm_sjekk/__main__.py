"""Gjør pakka kjørbar: `python -m tfm_sjekk`.

Dette er også inngangspunktet PyInstaller bygger fra. Konsollskriptet i
pyproject peker på `cli:app`, som er et objekt og ikke en fil — PyInstaller
trenger en modul den kan starte.

De to grepene under ser like ut, men løser hver sin variant av samme
problem: federeringen (§3) leser filene i egne prosesser, og en ny prosess
startes ved å kjøre dette inngangspunktet om igjen.

`freeze_support()` er for den frosne binæren. Der starter arbeidsprosessen
hele exe-en på nytt med `--multiprocessing-fork` blant argumentene, og uten
dette kallet havner de argumentene i Typer, som svarer «No such option» og
lar prosesspoolen kollapse.

`if __name__` er for `python -m tfm_sjekk`. Der importerer barneprosessen
denne modulen på nytt, og uten vakta ville `app()` kjørt en gang til i hvert
barn — altså hele kontrollkjøringen, rekursivt.
"""

import multiprocessing

if __name__ == "__main__":
    multiprocessing.freeze_support()

    from tfm_sjekk.cli import main

    main()
