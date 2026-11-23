# Prototyp designu (jen předloha)

Zdrojové soubory hratelného prototypu z design plátna v Claude. Samy o sobě se v prohlížeči nespustí (potřebují prostředí plátna) a **nejsou součástí hry**. Slouží jako přesná předloha pro pygame:

- `Hra.dc.html` – celá hra: načítání, menu, mapa (funkce `K()` = všechny souřadnice, barvy a objekty mapy), herní logika, rozhraní.
- `Sprite.dc.html` – tvary a animace všech postav (seznam `SPRITES`: barva, body od −30 do 30, značka animace).
- `Styl.dc.html` – paleta, písmo, pravidla stylu.

Popis slovy je v `docs/vizualni-design.md`.
