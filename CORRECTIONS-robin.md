# Deník selhání AI – Robin

Zápis každého případu, kdy AI udělala něco špatně a já to musel opravit. Podle zadání alespoň 3 případy. Jen skutečné případy, nejnovější dole.

<!-- Šablona případu:

## Případ N: <krátký název> (<datum>)

- **Co jsem chtěl:**
- **Co AI udělala špatně:**
- **Jak jsem to poznal:**
- **Jak jsem to opravil:**
-->

## Případ 1: Příliš mnoho malých commitů (23. 11. 2026)

- **Co jsem chtěl:** Čistou a čitelnou historii v gitu, jak chce zadání: jeden commit za každou větší, důležitou změnu.
- **Co AI udělala špatně:** Rozdělila práci na moc malých commitů. Jen větev `robin/iso-core` měla 5 commitů a v historii jich bylo celkově zbytečně hodně, i na věci, které patřily k sobě.
- **Jak jsem to poznal:** Podíval jsem se na seznam commitů na GitHubu a bylo jich na tak krátkou dobu práce moc.
- **Jak jsem to opravil:** Řekl jsem AI, ať dělá jeden commit na každou důležitou věc. Staré commity už byly sloučené do `main`, takže jsme je nemazali: přepsání historie na `main` by rozbilo kopii repozitáře, kterou má Matěj. Pravidlo „jeden commit na větší změnu, historie na `main` se nepřepisuje“ je teď v `CLAUDE.md`, takže ho dodržuje i Matějův Claude.

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
