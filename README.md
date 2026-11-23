# Delay – ČD Tower Defence

Školní projekt: hra žánru tower defence na téma České dráhy.

## Popis hry

Jsi dispečer železniční trati z Kolína do Prahy. Po trati ke stanici Praha hl. n. míří problémy, které zdržují vlaky: **krávy na trati, poruchy návěstidel, spadlé stromy** a nakonec celá **výluka**. Podél trati stavíš pracovníky a techniku ČD, kteří problémy odstraní dřív, než dojedou do stanice.

Každý problém, který do stanice dorazí, přidá vlakům zpoždění. Když zpoždění dosáhne **60 minut**, cestující to vzdají a prohráváš. Když přežiješ všech **8 vln**, vyhráváš.

Za každý odstraněný problém dostaneš peníze do rozpočtu, za které stavíš další věže.

Podrobnosti najdeš v [design dokumentu](docs/design-dokument.md).

## Ovládání

Hra se ovládá hlavně myší (tlačítka na obrazovce), klávesy jsou zkratky.

| Myš / klávesa | Akce |
|---|---|
| **klik / libovolná klávesa** | přeskočit načítání |
| tlačítko **Hrát** / **Enter** | začít hru |
| karta věže vlevo dole / **1**, **2**, **3** | vybrat věž |
| **levé tlačítko myši** na trávě | postavit vybranou věž (průhledná věž ukazuje kam, kruh její dosah) |
| přepínač **Místa ke stavbě** | zvýraznit všechna volná místa |
| tlačítko **Další vlna** / **mezerník** | spustit další vlnu |
| tlačítko **Pauza** / **P** | pauza |
| tlačítko **2×** / **F** | zrychlení |
| **Hrát znovu** / **R**, **Hlavní menu** / **M** | na konci hry |
| **Esc** | ukončit hru |

## Postup spuštění

Potřebuješ **Python 3.12 nebo novější** a **Git**.

1. **Nainstaluj Python** z [python.org/downloads](https://www.python.org/downloads/). Na Windows v instalátoru zaškrtni **„Add python.exe to PATH“**.
   Ověř v terminálu: `python --version`
2. **Stáhni projekt:**
   ```
   git clone https://github.com/rloebe/CD-Tower-defence.git
   cd CD-Tower-defence
   ```
   (Bez Gitu: na GitHubu tlačítko **Code → Download ZIP**, rozbalit a otevřít složku v terminálu.)
3. **Nainstaluj knihovny:**
   ```
   python -m pip install -r requirements.txt
   ```
4. **Spusť hru:**
   ```
   python src/main.py
   ```
   Hra se spustí přes celou obrazovku. Pro spuštění v okně: `python src/main.py --okno`.

**Windows – když `python` hlásí „Python nebyl nalezen“:** Python není v PATH. Použij místo `python` příkaz `py` (např. `py -m pip install -r requirements.txt` a `py src/main.py`). Ověříš ho přes `py --version`.

Na macOS/Linuxu použij místo `python` příkaz `python3`.

### Spuštění testů

```
python -m pytest
```

Ruční testovací scénář je v [docs/testovaci-scenar.md](docs/testovaci-scenar.md).

## Použité technologie

- **Python 3.12+**
- **pygame-ce**: knihovna pro okno, kreslení a ovládání (komunitní verze pygame, funguje i s nejnovějším Pythonem)
- **pytest**: automatické testy
- **Git + GitHub**: správa verzí
- Grafika je kreslená přímo v kódu, hra nepotřebuje žádné obrázky.

## Struktura projektu

| Cesta | Obsah |
|---|---|
| `src/main.py` | spuštění hry a hlavní smyčka |
| `src/game.py` | stav hry a pravidla (peníze, zpoždění, výhra/prohra) |
| `src/iso.py` | kamera: převod políček na pixely a zpět |
| `src/world.py` | rozložení mapy (kde co stojí, kde se dá stavět) |
| `src/scenery.py` | kreslení mapy |
| `src/sprites.py` | postavičky a jejich animace |
| `src/track.py` | trať, po které jedou nepřátelé |
| `src/enemies.py` | nepřátelé |
| `src/waves.py` | vlny nepřátel |
| `src/towers.py` | věže |
| `src/ui.py` | obrazovky: načítání, menu, horní lišta, výběr věží, konec hry |
| `src/settings.py` | konstanty (velikost okna, barvy, pravidla) |
| `tests/` | automatické testy |
| `docs/` | zadání, design dokument, vizuální design, testovací scénář |
| `CORRECTIONS-<jméno>.md` | deník selhání AI každého z nás |
| `RETROSPEKTIVA-<jméno>.md` | retrospektiva každého z nás |

## Autoři

- Robin Loebe (`rloebe`)
- Matěj Volf (`VolfM`)

Při vývoji jsme používali AI asistenta Claude. Co AI udělala špatně a jak jsme to opravili, je v deníku selhání AI.
