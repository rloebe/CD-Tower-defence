# Vizuální design – Výluka

Takhle má hra vypadat. Předloha je hratelný prototyp na design plátně v Claude (odkaz má Robin). Zdrojové soubory prototypu jsou v `docs/design-prototyp/` – jsou tam přesné souřadnice, barvy a tvary všech postav, takže se dají přenést do pygame 1:1. Prototyp je jen předloha, není součástí hry.

## Styl

- **Low poly / voxel**, podobně jako hra Unrailed. Všechno je z kvádrů a rovných ploch, žádné obrázky – vše se kreslí kódem (`pygame.draw.polygon`).
- Každý objekt má 2–3 odstíny jedné barvy: vršek nejsvětlejší, přední bok střední, levý bok nejtmavší. Žádné obrysy, žádné přechody.
- Stín = tmavý poloprůhledný mnohoúhelník na zemi vpravo od objektu.
- Písmo **Exo 2** (Google Fonts, licence OFL), soubor do `assets/fonts/`. Když nebude čas, výchozí písmo pygame.

## Kamera a souřadnice

Svět je mřížka políček: **x** doprava, **y** k divákovi, **z** nahoru. Veškerá logika hry (pohyb, dosah věží, stavění) počítá v políčkách. Na obrazovku se převádí až při kreslení.

Kamera: shora pod úhlem 55°, pootočená o −12°. Okno 960 × 640, horní lišta 56 px.

```
obrazovka_x = 10  + 46 · (0,9781·x + 0,2079·y)
obrazovka_y = 168 + 46 · ((−0,2079·x + 0,9781·y) · 0,8192 − 0,5736·z)
```

Klik myší → políčko (na zemi, z = 0):

```
a = (sx − 10) / 46
b = (sy − 168) / 46 / 0,8192
x = 0,9781·a − 0,2079·b
y = 0,2079·a + 0,9781·b      → políčko = (floor(x), floor(y))
```

Pořadí kreslení: odzadu dopředu podle hloubky `−0,2079·x + 0,9781·y` (menší = dál = kreslit dřív).

Kvádr se kreslí jako 3 mnohoúhelníky: **levý bok** (x = x0), **přední bok** (y = y1) a **vršek** (z = z1).

## Mapa (souřadnice v políčkách)

- **Trať** (nepřátelé jedou po ní): `(-2,5; 3,5) → (3,5; 3,5) → (3,5; 9,5) → (7,5; 9,5) → (7,5; 4,5) → (11,5; 4,5) → (11,5; 10,5) → (14,5; 10,5) → (14,5; 7,5) → (18,2; 7,5)`
- **Kolín** (začátek): malé žluté nádraží x 0,3–2,5, y 1,7–2,75, nástupiště před ním.
- **Praha hl. n.** (cíl): žlutá budova x 15–18,5, y 4,6–6,4, s věžičkou a hodinami; nástupiště, lampy, lavička, zarážedlo na konci trati (x 18,25).
- **Odstavená souprava ČD** (modrá lokomotiva + vagon) na vedlejší koleji y = 9.
- **Skalní plošina** vzadu (výška 1): řádky y ≤ 0, a y = 1 pro x ≤ −1 nebo x ≥ 13. Na ní skály a les.
- **Silnice**: svislá x = 9,5 (od stodoly k dolní silnici), vodorovná y = 13,5. **Přejezd** s výstražnými kříži a závorami v místě (9,5; 4,5) – závory dole a světla blikají, když jede vlna.
- **Stodola** (červená) x 8,6–10,4, y 1,3–2,5; **stohy sena**; **pšeničné pole** s plotem x 6,5–12,5, y 11,2–13; **oranice** x 12,6–18,6, y 2,2–4,3.
- **Vesnice**: 3 domky za silnicí (y ≈ 11,6–12,9), bílé/krémové zdi, červené střechy, komíny.
- **Hlavní trať dole** y = 14,6 – jen dekorace, občas projede souprava ČD.
- Stožáry trolejového vedení podél trati, 2 návěstidla, stromy, keře, kameny, trsy trávy a kytky.
- Stavět věže jde jen na **volnou trávu** (ne trať, silnice, pole, budovy, plošina, dekorace).

## Obrazovky

1. **Načítání:** mapa ztmavená, uprostřed velký název hry, pod ním malý ukazatel průběhu a malý vláček, který po něm jede. Tipy dole. Pak samo do menu.
2. **Menu:** mapa ztmavená, tmavě modrý panel se zkosenými rohy: „ČESKÉ DRÁHY · TOWER DEFENCE“, název, podtitul, tlačítka **Hrát** (žluté) a **Ukončit**.
3. **Hra:**
   - Horní lišta (ČD modrá, fasety): Rozpočet (ikona mince), Zpoždění (pruh), Vlna, tlačítka Pauza, 2×, **Další vlna**.
   - **Panel nad Prahou:** „Praha hl. n.“, pruh zpoždění 0–60 min (zelená → žlutá od 30 → červená od 45).
   - **Výběr věží** vlevo dole: 3 karty (postavička, název, cena) + přepínač „Místa ke stavbě“.
   - Když máš na vybranou věž peníze: místo kurzoru se pod myší ukazuje průhledná věž, políčko bílé (jde stavět) / červené (nejde), kolem kruh dosahu a zvýrazní se všechna volná místa ke stavbě. Když nemáš peníze: normální kurzor.
   - Po zničení nepřítele vyletí nad ním „+10“ s mincí (asi 1 s). Když nepřítel dojede do Prahy, vyletí u panelu červené „+5 min“.
4. **Konec hry:** panel „Vlaky jedou včas!“ (zelená) / „Cestující to vzdali“ (červená), statistika, tlačítka **Hrát znovu** a **Hlavní menu**.

## Postavy

Tvary všech postav jsou v `docs/design-prototyp/Sprite.dc.html` (seznam mnohoúhelníků se souřadnicemi −30 až 30 a barvami). Postavy jsou „billboardy“ (stojí čelem ke kameře) a otáčejí se podle směru jízdy.

| Postava | Animace |
|---|---|
| Kráva na trati | chodí (nohy, kývání hlavou, ocas) |
| Porucha návěstidla | poskakuje, jiskra a červené světlo blikají |
| Spadlý strom | listí se třese |
| Výluka (boss) | chodí na dvou nohách, bliká oranžová lampa |
| Traťový dělník | při zásahu máchne klíčem |
| Pracovní drezína | otřásá se, bliká maják |
| Výpravčí | při pulzu zvedne plácačku |

## Hodnoty (návrh, doladit při testu)

| Věž | Cena | Dosah (políčka) | Účinek | Střelba |
|---|---|---|---|---|
| Traťový dělník | 50 Kč | 2,3 | 10 poškození | 1× za 1 s |
| Pracovní drezína | 120 Kč | 3,1 | 25 poškození | 1× za 1,2 s |
| Výpravčí | 80 Kč | 2,1 | zpomalí na 50 % na 1,5 s | puls 1× za 1 s |

| Nepřítel | Rychlost (políčka/s) | Odolnost | Zpoždění | Odměna |
|---|---|---|---|---|
| Kráva | 1,4 | 30 | 5 min | 10 Kč |
| Porucha návěstidla | 2,4 | 15 | 3 min | 8 Kč |
| Spadlý strom | 0,9 | 80 | 8 min | 20 Kč |
| Výluka (boss) | 0,6 | 600 | 30 min | 100 Kč |

## Barvy

| Název | Hex |
|---|---|
| ČD modrá / světlá / tmavá | `#00549F` / `#0A62B3` / `#003A70` |
| Panel | `#0A182C` |
| Signální žlutá (tlačítka) | `#FFB020` |
| Tráva | `#8DCB4F`, `#88C64C`, `#93D054` |
| Štěrk | `#ADA18C` (okraj `#8E826F`) |
| Pražce | `#6B4B2E` |
| Kolejnice | `#E1E4EA` |
| Nádraží (zeď / střecha) | `#E9C46A` / `#A0463A` |
| Zpoždění: OK / pozor / kritické | `#3FB05A` / `#FFB020` / `#E0342F` |

## Okolní život (až nakonec, když zbude čas)

Projíždějící vlaky na hlavní trati dole, auta na silnici, traktor na oranici, dvě pasoucí se krávy u stodoly, kouř z komínů.
