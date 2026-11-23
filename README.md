# Výluka – ČD Tower Defence

Školní projekt: hra žánru tower defence na téma České dráhy.

## Popis hry

Jsi dispečer železniční trati z Kolína do Prahy. Po trati ke stanici Praha hl. n. míří problémy, které zdržují vlaky: **krávy na trati, poruchy návěstidel, spadlé stromy** a nakonec celá **výluka**. Podél trati stavíš pracovníky a techniku ČD, kteří problémy odstraní dřív, než dojedou do stanice.

Každý problém, který do stanice dorazí, přidá vlakům zpoždění. Když zpoždění dosáhne **60 minut**, cestující to vzdají a prohráváš. Když přežiješ všech **8 vln**, vyhráváš.

Za každý odstraněný problém dostaneš peníze do rozpočtu, za které stavíš další věže.

Podrobnosti najdeš v [design dokumentu](docs/design-dokument.md).

## Ovládání

| Klávesa / myš | Akce |
|---|---|
| **libovolná klávesa / klik** | přeskočit načítání |
| **Enter** | začít hru (v menu) |
| **Levé tlačítko myši** | postavit věž na volnou trávu vedle trati |
| **Mezerník** | spustit další vlnu |
| **P** | pauza |
| **F** | zrychlení 2× |
| **R** / **M** | na konci hry: hrát znovu / hlavní menu |
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
| `src/ui.py` | menu, horní lišta, konec hry |
| `src/settings.py` | konstanty (velikost okna, barvy, pravidla) |
| `tests/` | automatické testy |
| `docs/` | design dokument, testovací scénář |
| `CORRECTIONS-<jméno>.md` | deník selhání AI každého z nás |
| `RETROSPEKTIVA-<jméno>.md` | retrospektiva každého z nás |

## Autoři

- Robin Loebe (`rloebe`)
- Matěj Volf (`VolfM`)

Při vývoji jsme používali AI asistenta Claude. Co AI udělala špatně a jak jsme to opravili, je v deníku selhání AI.
