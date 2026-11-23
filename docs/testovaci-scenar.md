# Ruční testovací scénář

Postup, jak hru ručně otestovat po spuštění (`python src/main.py`). U každého kroku zapiš, jestli výsledek odpovídá očekávání.

| # | Krok | Očekávaný výsledek | OK? |
|---|---|---|---|
| 1 | Spustit hru | Otevře se okno s modrým menu a nápisem „Zpoždění“, české znaky (ž, ě, ř…) se zobrazují správně. | |
| 2 | Stisknout **Enter** | Zobrazí se mapa s tratí z Kolína do stanice Praha hl. n. Nahoře lišta: Rozpočet 150 Kč, Zpoždění 0 / 60 min, Vlna 0 / 8, nápis „Mezerník = další vlna“. | |
| 3 | Stisknout **mezerník** | Vlna se změní na 1 / 8, zleva přijíždějí krávy a jedou po kolejích. Nápis „Mezerník = další vlna“ zmizí. | |
| 4 | Během vlny znovu stisknout **mezerník** | Nic se nestane, další vlna se nespustí, dokud je někdo na trati. | |
| 5 | Nechat krávy dojet do stanice | Každá kráva po vjezdu do stanice zmizí a přidá 5 minut zpoždění. Od 30 minut je text zpoždění žlutý. | |
| 6 | Postavit věž kliknutím vedle trati (po doplnění věží) | Věž se postaví, z rozpočtu se odečte cena. Na trať postavit nejde. | |
| 7 | Nechat věž střílet (po doplnění věží) | Nepřátelé v dosahu ztrácejí životy (zelenočervený pruh), po zničení zmizí a rozpočet se zvýší o odměnu. | |
| 8 | Nechat zpoždění dosáhnout 60 minut | Objeví se obrazovka „Cestující to vzdali“ s počtem odstraněných problémů. | |
| 9 | Na konci stisknout **R** | Začne nová hra: rozpočet 150 Kč, zpoždění 0, vlna 0 / 8, žádné věže. | |
| 10 | Odehrát všech 8 vln bez prohry | Objeví se obrazovka „Vlaky jedou včas!“. | |
| 11 | Stisknout **Esc** (v menu i ve hře) | Hra se ukončí. | |
| 12 | Zavřít okno křížkem | Hra se ukončí bez chybové hlášky v terminálu. | |
