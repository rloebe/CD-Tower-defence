# Deník selhání AI – Robin

Zápis každého případu, kdy AI udělala něco špatně a já to musel opravit. Podle zadání alespoň 3 případy. Jen skutečné případy, nejnovější dole.

<!-- Šablona případu:

## Případ N: <krátký název> (<datum>)

- **Co jsem chtěl:**
- **Co AI udělala špatně:**
- **Jak jsem to poznal:**
- **Jak jsem to opravil:**
-->

## Případ 1: Hra nešla spustit podle README (23. 11. 2026)

- **Co jsem chtěl:** Spustit hru na svém počítači doma přesně podle návodu v README.
- **Co AI udělala špatně:** V README byl jen příkaz `python src/main.py`. AI nepočítala s tím, že na Windows často příkaz `python` nefunguje (Python není v PATH), a nenapsala, že se dá použít `py`.
- **Jak jsem to poznal:** Terminál napsal „Python nebyl nalezen“. Zkusil jsem `python --version` se stejnou chybou, ale `py --version` vypsal Python 3.13.7.
- **Jak jsem to opravil:** Spustil jsem hru přes `py src/main.py` a nechal jsem do README doplnit poznámku pro Windows, že když `python` nefunguje, má se použít `py`. To je důležité, protože podle zadání musí jít hra spustit na cizím počítači podle README.

## Případ 2: Hra nebyla přes celou obrazovku (23. 11. 2026)

- **Co jsem chtěl:** Aby hra běžela přes celou obrazovku jako normální hra.
- **Co AI udělala špatně:** Nastavila pevné okno 960 × 640 pixelů a nepočítala s tím, že monitor je mnohem větší. Hra tak byla jen malé okno uprostřed.
- **Jak jsem to poznal:** Po spuštění hry na svém počítači se otevřelo jen malé okno.
- **Jak jsem to opravil:** Řekl jsem to AI a hra se teď spouští přes celou obrazovku v rozlišení monitoru. Celá hra je navržená pro plochu 960 × 640 a při spuštění se spočítá, kolikrát ji zvětšit (`settings.SCALE`) a jak ji vycentrovat. Pro ladění jde pořád spustit v okně: `py src/main.py --okno`.

## Případ 3: Grafika byla „pixelatá“ (23. 11. 2026)

- **Co jsem chtěl:** Hladkou low-poly grafiku jako v designu.
- **Co AI udělala špatně:** Kreslila mnohoúhelníky bez vyhlazení hran, takže okraje byly zubaté. Navíc nepočítala s tím, že Windows při zvětšení zobrazení (125 % / 150 %) malé okno samy roztáhnou a obraz rozmažou.
- **Jak jsem to poznal:** Hra vypadala rozmazaně a kostičkovaně, ne hladce jako návrh na plátně.
- **Jak jsem to opravil:** Řekl jsem to AI. Hra teď (1) řekne Windows, že si kreslí ostře sama (DPI awareness v `main.py`), (2) kreslí v plném rozlišení monitoru a (3) mapu i postavičky kreslí 2× větší a pak je plynule zmenší, čímž se hrany vyhladí. Mapa se takhle kreslí jen jednou při spuštění, takže hra nezpomalí.
