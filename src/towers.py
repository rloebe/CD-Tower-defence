"""Věže: pracovníci a technika ČD, kteří brání trať před problémy.

Co tu je:
- třída Tower = jedna postavená věž (kde stojí, jaký je to typ, kdy smí znovu střílet),
- třída TowerManager = všechny věže, jejich střely a pulzy výpravčího.

Jak to zapadá do hry:
- main.py volá TowerManager.handle_event (klik na trávu = stavba),
  update (věže míří a střílejí) a draw (kreslení).
- Vlastnosti věží (cena, dosah, poškození...) jsou v settings.TOWER_TYPES,
  stejná čísla ukazuje i panel výběru v ui.py.
- Věže jen ubírají životy (enemy.take_damage) a zpomalují (enemy.apply_slow).
  Odměnu, počítání zničených a "+10" nad nepřítelem řeší game.py.

Všechny pozice jsou v políčkách. Na pixely se převádí až při kreslení (iso.to_screen).
Chování je stejné jako v prototypu (docs/design-prototyp/Hra.dc.html, funkce step).
"""

import math

import pygame

import iso
import settings
import sprites
import track

# Jak rychle letí střela (políček za sekundu). Je výrazně rychlejší než nejrychlejší
# nepřítel (2,4 políčka/s), takže ho střela vždycky dožene.
SHOT_SPEED = 9.0

# Jak vysoko nad zemí střela vyletí (z v políčkách) a kam klesne, když doletí k cíli.
# Díky tomu to vypadá, že dělník hází ze zvednuté ruky na nepřítele na zemi.
SHOT_START_Z = 1.1
SHOT_END_Z = 0.5

# Vzhled střel (jen grafika, proto není v settings.py): barva a velikost v logických pixelech.
SHOT_LOOK = {
    "worker": {"color": (233, 236, 239), "size": 8},  # světle šedý "klíč"
    "draisine": {"color": (255, 176, 32), "size": 11},  # žlutá, větší
}

# Jak dlouho (sekundy) se věž po výstřelu "hýbe" (dělník máchne klíčem, výpravčí zvedne plácačku).
FLASH_TIME = 0.3

# Jak dlouho (sekundy) se rozpíná modrý kruh pulzu výpravčího.
PULSE_LIFE = 0.6
PULSE_COLOR = (127, 184, 255)

# Velikost postavičky věže v logických pixelech (stejně jako "duch" věže v ui.py).
TOWER_SIZE = 54


class Tower:
    """Jedna postavená věž.

    kind      = typ věže: "worker" | "draisine" | "dispatcher" (klíč do settings.TOWER_TYPES)
    col, row  = políčko, na kterém stojí (celá čísla); čte je i ui.py
    number    = pořadové číslo věže, jen aby se postavičky nehýbaly všechny naráz
    """

    def __init__(self, kind, col, row, number=0):
        self.kind = kind
        self.col = col
        self.row = row
        self.number = number
        # Věž stojí uprostřed políčka, proto + 0.5. Odsud se měří dosah.
        self.x = col + 0.5
        self.y = row + 0.5
        # Za kolik sekund smí znovu vystřelit. 0 = hned, jakmile je někdo v dosahu.
        self.cooldown = 0.0
        # Kolik sekund ještě trvá pohyb po výstřelu (pro animaci).
        self.flash = 0.0

    @property
    def stats(self):
        """Vlastnosti tohoto typu věže ze settings.TOWER_TYPES (cena, dosah, poškození...)."""
        return settings.TOWER_TYPES[self.kind]

    def in_range(self, enemy):
        """True, když je nepřítel živý, ještě nedojel do Prahy a je v dosahu věže."""
        if not enemy.alive or enemy.reached_end:
            return False
        # Vzdálenost počítáme v políčkách na zemi, ne v pixelech: na obrazovce je
        # svět zploštělý kamerou, takže by dosah do strany a dopředu nebyl stejný.
        distance = math.hypot(enemy.x - self.x, enemy.y - self.y)
        return distance <= self.stats["range"]


class TowerManager:
    """Všechny věže ve hře, jejich střely a pulzy.

    towers = postavené věže (seznam Tower); ui.py z nich čte col, row a kind
    shots  = letící střely (slovníky: x, y, z, target, damage, kind)
    pulses = rozpínající se kruhy výpravčího (slovníky: x, y, range, t)
    """

    def __init__(self):
        self.towers = []
        self.shots = []
        self.pulses = []
        self.built_count = 0  # kolik věží se za hru postavilo (pro Tower.number)

    def reset(self):
        """Volá se při nové hře (game.reset). Smaže všechny věže, střely i pulzy."""
        self.towers = []
        self.shots = []
        self.pulses = []
        self.built_count = 0

    # ---------- stavění ----------

    def tower_at(self, col, row):
        """Vrátí věž stojící na políčku (col, row), nebo None, když je políčko volné."""
        for tower in self.towers:
            if tower.col == col and tower.row == row:
                return tower
        return None

    def try_build(self, col, row, game):
        """Zkusí postavit věž typu game.selected_tower na políčko (col, row).

        Postaví ji jen tehdy, když:
        1) na políčko se smí stavět (track.can_build = volná tráva),
        2) na políčku ještě žádná věž nestojí,
        3) hráč na ni má peníze.
        Pak odečte cenu z game.money. Vrací True, když se věž postavila, jinak False.

        Je to samostatná funkce (ne přímo v handle_event), aby se dala testovat
        bez myši a bez okna.
        """
        kind = game.selected_tower
        price = settings.TOWER_TYPES[kind]["price"]
        if not track.can_build(col, row):
            return False
        if self.tower_at(col, row) is not None:
            return False
        if game.money < price:
            return False
        game.money -= price
        self.towers.append(Tower(kind, col, row, self.built_count))
        self.built_count += 1
        return True

    def handle_event(self, event, game):
        """Klik levým tlačítkem na mapu postaví vybranou věž.

        main.py sem posílá jen události, které nezpracovalo rozhraní (ui.py vrátilo
        None), takže klik na tlačítko nebo panel výběru sem vůbec nedojde.
        Když stavět nejde, nic se nestane: ui.py už předem ukazuje políčko červeně.
        """
        if game.state != "playing":
            return
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # pozice myši (pixely) -> políčko na zemi pod ní
            col, row = iso.to_tile(*event.pos)
            self.try_build(col, row, game)

    # ---------- střelba ----------

    def update(self, dt, game):
        """Jeden krok věží: míření, střelba, pohyb střel a pulzů.

        dt = čas od minulého kroku v sekundách. Je už vynásobený rychlostí hry
        (game.update to dělá před voláním), takže při 2× věže střílí 2× rychleji
        a nic dalšího tu řešit nemusíme. Při pauze se update vůbec nevolá.
        """
        for tower in self.towers:
            self._update_tower(tower, dt, game.enemies)
        self._update_shots(dt)
        self._update_pulses(dt)

    def _update_tower(self, tower, dt, enemies):
        """Odpočítá čas do dalšího výstřelu a když může, vystřelí (nebo pulzne)."""
        tower.cooldown -= dt
        tower.flash = max(0.0, tower.flash - dt)
        if tower.cooldown > 0:
            return

        targets = [enemy for enemy in enemies if tower.in_range(enemy)]
        if not targets:
            # Nikdo v dosahu: cooldown necháme na nule, aby věž vystřelila hned,
            # jakmile někdo do dosahu vjede.
            return

        stats = tower.stats
        if tower.kind == "dispatcher":
            # Výpravčí nestřílí: zpomalí naráz všechny v dosahu.
            for enemy in targets:
                enemy.apply_slow(stats["slow"], stats["slow_time"])
            self.pulses.append({"x": tower.x, "y": tower.y, "range": stats["range"], "t": 0.0})
        else:
            # Míříme na toho, kdo je nejdál po trati (nejvyšší progress) = nejblíž Praze,
            # protože ten je nejnebezpečnější: nejdřív by způsobil zpoždění.
            target = max(targets, key=lambda enemy: enemy.progress)
            self.shots.append({
                "x": tower.x,
                "y": tower.y,
                "z": SHOT_START_Z,
                "target": target,
                "damage": stats["damage"],
                "kind": tower.kind,
            })

        tower.cooldown = stats["rate"]  # další výstřel až za "rate" sekund
        tower.flash = FLASH_TIME

    def _update_shots(self, dt):
        """Posune střely za jejich cílem. Když střela doletí, ubere mu životy."""
        flying = []
        for shot in self.shots:
            enemy = shot["target"]
            # Cíl mezitím zmizel (zničila ho jiná střela, nebo dojel do Prahy):
            # střela zmizí taky, aby nelétala donekonečna.
            if not enemy.alive or enemy.reached_end:
                continue

            dx = enemy.x - shot["x"]
            dy = enemy.y - shot["y"]
            distance = math.hypot(dx, dy)
            step = SHOT_SPEED * dt  # kolik políček střela uletí za tento krok
            if distance <= step:
                enemy.take_damage(shot["damage"])  # zásah; odměnu řeší game.py
                continue

            # Posun o "step" směrem k cíli (dx / distance = jednotkový směr).
            # Cíl se hýbe, proto směr počítáme každý snímek znovu (střela ho "navádí").
            shot["x"] += dx / distance * step
            shot["y"] += dy / distance * step
            # Výška klesá k SHOT_END_Z tím víc, čím blíž je cíl, takže střela
            # dopadne zhruba ve výšce těla nepřítele.
            shot["z"] += (SHOT_END_Z - shot["z"]) * min(1.0, step / distance)
            flying.append(shot)
        self.shots = flying

    def _update_pulses(self, dt):
        """Nechá pulzy výpravčího stárnout a staré smaže."""
        for pulse in self.pulses:
            pulse["t"] += dt
        self.pulses = [pulse for pulse in self.pulses if pulse["t"] < PULSE_LIFE]

    # ---------- kreslení ----------

    def draw(self, surface, game):
        """Nakreslí pulzy (na zemi), věže a nakonec střely (letí nad vším)."""
        for pulse in self.pulses:
            self._draw_pulse(surface, pulse)

        # Odzadu dopředu podle hloubky: věž blíž ke kameře musí překrýt tu za ní.
        for tower in sorted(self.towers, key=lambda t: iso.depth(t.x, t.y)):
            self._draw_tower(surface, tower, game)

        for shot in self.shots:
            self._draw_shot(surface, shot)

    def _draw_tower(self, surface, tower, game):
        """Nakreslí postavičku věže na jejím políčku."""
        sx, sy = iso.to_screen(tower.x, tower.y)
        # Postavička je posunutá nahoru o 16/60 své velikosti, aby stála podstavcem
        # na středu políčka (stejně jako "duch" věže v ui.py).
        center = (sx, sy - iso.px(TOWER_SIZE) * 16 / 60)
        # action: 1 hned po výstřelu, pak během FLASH_TIME klesne na 0 (animace máchnutí)
        action = tower.flash / FLASH_TIME
        # Každá věž má fázi trochu posunutou, aby se všechny nehýbaly úplně stejně.
        phase = game.time + tower.number * 0.7
        sprites.draw_sprite(surface, tower.kind, center, TOWER_SIZE, phase=phase, action=action)

    def _draw_shot(self, surface, shot):
        """Střela = malý kosočtverec (čtverec otočený o 45°) s tmavým okrajem."""
        look = SHOT_LOOK[shot["kind"]]
        cx, cy = iso.to_screen(shot["x"], shot["y"], shot["z"])
        half = iso.px(look["size"]) / 2
        outline = half + iso.px(2)  # tmavý okraj 2 px kolem, aby byla vidět i na trávě
        pygame.draw.polygon(surface, (28, 36, 48), _diamond(cx, cy, outline))
        pygame.draw.polygon(surface, look["color"], _diamond(cx, cy, half))

    def _draw_pulse(self, surface, pulse):
        """Pulz výpravčího = modrý kruh na zemi, který se rozpíná a mizí."""
        progress = pulse["t"] / PULSE_LIFE  # 0 na začátku, 1 na konci
        # Kruh začne na čtvrtině dosahu a roste až na celý dosah.
        radius = pulse["range"] * (0.25 + 0.75 * progress)
        # Kruh na zemi kamera zploští na elipsu: šířka podle velikosti políčka,
        # výška ještě krát SIN_PITCH (sklon kamery zkrátí hloubku).
        width = radius * 2 * settings.TILE * settings.SCALE
        height = width * settings.SIN_PITCH
        rect = pygame.Rect(0, 0, max(1, round(width)), max(1, round(height)))
        rect.center = iso.to_screen(pulse["x"], pulse["y"])
        # Průhlednost jde jen přes vlastní obrázek s alfa kanálem (SRCALPHA).
        layer = pygame.Surface(rect.size, pygame.SRCALPHA)
        alpha = round(255 * (1 - progress))  # postupně mizí
        pygame.draw.ellipse(layer, (*PULSE_COLOR, alpha), layer.get_rect(), max(1, round(iso.px(3))))
        surface.blit(layer, rect)


def _diamond(cx, cy, half):
    """Body kosočtverce se středem (cx, cy) a "poloměrem" half (pixely)."""
    return [(cx, cy - half), (cx + half, cy), (cx, cy + half), (cx - half, cy)]
