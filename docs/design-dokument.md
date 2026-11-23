# Design dokument – Zpoždění

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

Navrhuje a programuje Matěj. Základní návrh (3 typy):

| Název | Role |
|---|---|
| Traťový dělník | levná základní věž, střílí na jeden cíl |
| Pracovní drezína | dražší, větší dosah a poškození |
| Výpravčí | zpomaluje problémy v dosahu |

Věže se nesmí stavět na trať ani na sebe navzájem.

## 6. Ekonomika

- Startovní rozpočet: 150 Kč.
- Peníze za každý odstraněný problém (viz tabulka nepřátel).
- Ceny věží určí Matěj při vyvažování.

## 7. Ovládání

- **Myš:** výběr a stavba věží (levé tlačítko).
- **Mezerník:** spustit další vlnu.
- **Enter:** začít hru v menu.
- **R:** nová hra na konci.
- **Esc:** ukončit hru.

## 8. Obrazovky

1. Hlavní menu
2. Hra (mapa s tratí + horní lišta: rozpočet, zpoždění, číslo vlny)
3. Konec hry (výhra / prohra)

## 9. Grafika a zvuk

Grafika je kreslená přímo v kódu (tvary a text), žádné obrázky nejsou potřeba. Barvy inspirované ČD (modrá, bílá). Zvuk není v plánu.

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
| Menu, horní lišta, obrazovka konce hry | Matěj |
| Design dokument | oba |
| Deník selhání AI, retrospektiva | každý svůj |
