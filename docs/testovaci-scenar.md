# Ruční testovací scénář

Postup, jak hru ručně otestovat po spuštění (`python src/main.py`, na Windows případně `py src/main.py`). U každého kroku zapiš, jestli výsledek odpovídá očekávání.

| # | Krok | Očekávaný výsledek | OK? |
|---|---|---|---|
| 1 | Spustit hru | Hra se otevře přes celou obrazovku, obraz je ostrý (hrany nejsou zubaté). Zobrazí se načítání: název „DELAY“, pod ním ukazatel průběhu s vláčkem, který jede doprava, a tipy. | |
| 2 | Počkat, nebo kliknout na „Přeskočit“ | Objeví se hlavní menu přes ztmavenou mapu s tlačítky Hrát a Ukončit. České znaky (ž, ě, ř…) jsou správně. | |
| 3 | Kliknout na **Hrát** | Mapa s tratí z Kolína do Prahy hl. n. Nahoře lišta: Rozpočet 150 Kč, Zpoždění 0 / 60 min, Vlna 0 / 8. Nad Prahou panel se zpožděním. Vlevo dole výběr věží (vybraný Traťový dělník). Nahoře nápověda. | |
| 4 | Najet myší na trávu vedle trati | Místo kurzoru je vidět průhledná věž, políčko je bílé, kolem je kruh dosahu. Všechna volná místa ke stavbě jsou zvýrazněná. Nad tratí nebo silnicí je políčko červené. | |
| 5 | Kliknout na „Místa ke stavbě“ | Přepne se na ZAP a volná místa jsou zvýrazněná i bez držení věže. | |
| 6 | Vybrat Pracovní drezínu (karta nebo klávesa 2) | Karta drezíny má žlutý rámeček, pod myší je průhledná drezína s větším dosahem. | |
| 7 | Kliknout na **Další vlna** | Vlna 1 / 8, z levého okraje přijíždějí krávy a jdou po trati (hýbou nohama). Závory na přejezdu se sklopí a světla blikají. Tlačítko „Další vlna“ zešedne. | |
| 8 | Kliknout na **Pauza**, pak **Pokračovat** | Při pauze se vše zastaví a nahoře je „Pauza“; po pokračování jde hra dál. | |
| 9 | Kliknout na **2×** | Nepřátelé jedou dvakrát rychleji, na tlačítku je „1×“. | |
| 10 | Nechat krávu dojet do Prahy | Kráva zmizí u zarážedla, u panelu nad Prahou vyskočí červené „+5 min“, pruh zpoždění se posune. | |
| 11 | Postavit věž a nechat ji zničit nepřítele (po doplnění věží) | Nad zničeným nepřítelem vyletí „+10“ s mincí, rozpočet se zvýší. Na věž, na kterou nemáš peníze, je karta ztmavená a místo průhledné věže je normální kurzor. | |
| 12 | Nechat zpoždění dosáhnout 60 minut | Obrazovka „Cestující to vzdali“ se statistikou a tlačítky Hrát znovu a Hlavní menu. | |
| 13 | Kliknout na **Hrát znovu** | Nová hra: 150 Kč, zpoždění 0, vlna 0 / 8. | |
| 14 | Na konci kliknout na **Hlavní menu** | Návrat do menu. | |
| 15 | Odehrát všech 8 vln bez prohry | Obrazovka „Vlaky jedou včas!“. | |
| 16 | Stisknout **Esc** nebo v menu **Ukončit** | Hra se ukončí bez chybové hlášky v terminálu. | |
| 17 | Spustit `python src/main.py --okno` | Hra běží v okně 960 × 640. | |
