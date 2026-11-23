# Design dokument – Delay

**Žánr:** Tower defence
**Téma:** České dráhy
**Autoři:** Robin Loebe, Matěj Volf
**Technologie:** Python 3, pygame-ce

## 1. Koncept

Hráč je dispečer jedné železniční trati. Po trati k cílové stanici míří různé problémy, které způsobují zpoždění: krávy na kolejích, poruchy návěstidel, spadlé stromy a nakonec celá výluka. Hráč staví podél trati pracovníky a techniku Českých drah, kteří problémy odstraní dřív, než dorazí do stanice.

Každý problém, který do stanice dojede, přidá vlakům zpoždění. Když celkové zpoždění dosáhne limitu, cestující to vzdají a hra je prohraná.

## 2. Cíl hry

- **Výhra:** přežít všech 8 vln, aniž by zpoždění dosáhlo limitu.
- **Prohra:** celkové zpoždění dosáhne 60 minut.

## 3. Herní smyčka

1. Mezi vlnami hráč za peníze (rozpočet v Kč) staví věže vedle trati.
2. Hráč spustí další vlnu.
3. Problémy jedou po trati, věže na ně automaticky střílejí.
4. Za každý odstraněný problém dostane hráč peníze.
5. Problém, který dojede do stanice, přidá zpoždění.
6. Po vyčištění vlny se pokračuje bodem 1.

## 4. Nepřátelé (problémy na trati)

| Název | Rychlost | Odolnost | Zpoždění při průjezdu | Odměna |
|---|---|---|---|---|
| Kráva na trati | střední | střední | 5 min | 10 Kč |
| Porucha návěstidla | rychlá | nízká | 3 min | 8 Kč |
| Spadlý strom | pomalá | vysoká | 8 min | 20 Kč |
| Výluka (boss) | velmi pomalá | velmi vysoká | 30 min | 100 Kč |

## 5. Věže (pracovníci a technika ČD)

Navrhuje a programuje Matěj (`src/towers.py`). Hodnoty jsou v `src/settings.py` (`TOWER_TYPES`), stejná čísla ukazuje i panel výběru věží.

| Název | Cena | Dosah | Účinek | Jak často | Role |
|---|---|---|---|---|---|
| Traťový dělník | 50 Kč | 2,3 políčka | 10 poškození | 1× za 1 s | levná základní věž, střílí na jeden cíl |
| Pracovní drezína | 120 Kč | 3,1 políčka | 25 poškození | 1× za 1,2 s | dražší, větší dosah a poškození |
| Výpravčí | 80 Kč | 2,1 políčka | zpomalí na 50 % na 1,5 s | 1× za 1 s | nestřílí, zpomalí všechny v dosahu |

- Dělník a drezína míří na problém, který je nejdál po trati (nejblíž Praze), protože ten by nejdřív způsobil zpoždění.
- Střela letí za cílem a ubere mu životy, až doletí. Když cíl mezitím zmizí, zmizí i střela.
- Věž se staví kliknutím na volnou trávu: ne na trať, silnici, pole, budovy, plošinu ani na jinou věž. Cena se odečte z rozpočtu; když na věž nejsou peníze, nepostaví se.

## 6. Ekonomika

- Startovní rozpočet: 150 Kč.
- Peníze za každý odstraněný problém (viz tabulka nepřátel).
- Ceny věží: dělník 50 Kč, výpravčí 80 Kč, drezína 120 Kč. Na začátku jdou koupit 3 dělníci, nebo dělník a výpravčí. Při zkušební simulaci celé hry šlo všech 8 vln vyhrát bez zpoždění se 13 věžemi.

## 7. Ovládání

- **Myš:** výběr a stavba věží (levé tlačítko).
- **Mezerník:** spustit další vlnu.
- **Enter:** začít hru v menu.
- **R:** nová hra na konci.
- **Esc:** ukončit hru.

## 8. Obrazovky

1. Načítání (název hry, malý ukazatel průběhu s vláčkem)
2. Hlavní menu
3. Hra (mapa s tratí, horní lišta: rozpočet, zpoždění, vlna, pauza, zrychlení; panel zpoždění nad Prahou; výběr věží)
4. Konec hry (výhra / prohra)

## 9. Grafika a zvuk

Low-poly / voxel styl (jako hra Unrailed), kamera shora pod úhlem. Vše je kreslené kódem z mnohoúhelníků, žádné obrázky. Barvy inspirované ČD (modrá, bílá, žlutá nádraží). Podrobně v `docs/vizualni-design.md`, hratelná předloha v `docs/design-prototyp/`. Zvuk není v plánu.

## 10. Rozsah

**Povinné (MVP):** 1 mapa, 4 nepřátelé, 3 věže, 8 vln, menu, konec hry, testy, README.

**Když zbude čas:** vylepšování věží, druhá mapa, zvuky, rychlejší přehrávání.

## 11. Rozdělení práce

| Část | Kdo |
|---|---|
| Herní smyčka, stavy hry, mapa a trať | Robin |
| Nepřátelé, vlny | Robin |
| Testy, testovací scénář, README | Robin |
| Věže, střelba, stavění, utrácení peněz | Matěj |
| Okolní život: vlaky, auta, traktor, krávy, kouř | Matěj |
| Postavičky, menu, horní lišta, výběr věží, obrazovka konce hry | Robin (původně Matěj, převzal je Robin, protože Matěj začínal později) |
| Design dokument | oba |
| Deník selhání AI, retrospektiva | každý svůj |
