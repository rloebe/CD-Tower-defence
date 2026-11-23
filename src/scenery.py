"""Kreslení mapy podle designu: tráva, skalní plošina, trať, silnice, pole, nádraží, domy, stromy…

Proč je to takhle rozdělené:
- Kreslit stovky mnohoúhelníků 60× za sekundu by bylo pomalé. Proto se mapa
  nakreslí JEN JEDNOU při spuštění hry:
    * "zem" (všechno ploché) do jednoho velkého obrázku,
    * každý vysoký objekt (strom, dům, stožár…) do svého malého obrázku.
- Každý snímek se pak už jen tyto hotové obrázky "nalepí" (blit) na obrazovku.
- Vysoké objekty se lepí společně s nepřáteli seřazené podle hloubky
  (odzadu dopředu), aby strom před tratí správně zakryl krávu za ním.

- Aby hrany nebyly "zubaté", kreslí se všechno 2× větší (SUPERSAMPLE) a pak
  se to plynule zmenší. Zmenšení zprůměruje okrajové pixely = vyhlazení.
  Dělá se to jen jednou při spuštění, takže to hru nezpomalí.

Rozložení mapy (kde co stojí) je v world.py, převod na obrazovku v iso.py.
"""

import math
import random

import pygame

import iso
import settings
import track
import world


# ---------- pomocné funkce pro barvy a tvary ----------

def shade(color, k):
    """Ztmaví barvu: k = 1 beze změny, k = 0.7 o 30 % tmavší."""
    c = pygame.Color(color)
    return (int(c.r * k), int(c.g * k), int(c.b * k))


def tri(color):
    """Tři odstíny pro kvádr: (vršek, přední bok, levý bok). Světlo svítí shora zleva."""
    return (pygame.Color(color), shade(color, 0.84), shade(color, 0.7))


def P(x, y, z=0.0):
    """Zkratka: bod ve světě (políčka) -> pixely na obrazovce."""
    return iso.to_screen(x, y, z)


def quad(x0, y0, x1, y1, z=0.0):
    """Vodorovný obdélník na zemi (nebo ve výšce z) jako 4 body na obrazovce."""
    return [P(x0, y0, z), P(x1, y0, z), P(x1, y1, z), P(x0, y1, z)]


def box(x0, y0, w, d, z0, h, cols):
    """Kvádr jako 3 viditelné stěny: levý bok, přední bok, vršek.

    x0, y0 = levý zadní roh (políčka), w = šířka (x), d = hloubka (y),
    z0 = výška spodku, h = výška kvádru, cols = (vršek, přední, levý) z tri().
    Ostatní 3 stěny kamera nevidí, takže je nekreslíme.
    """
    x1, y1, z1 = x0 + w, y0 + d, z0 + h
    top, front, left = cols
    return [
        (left, [P(x0, y0, z0), P(x0, y1, z0), P(x0, y1, z1), P(x0, y0, z1)]),
        (front, [P(x0, y1, z0), P(x1, y1, z0), P(x1, y1, z1), P(x0, y1, z1)]),
        (top, [P(x0, y0, z1), P(x1, y0, z1), P(x1, y1, z1), P(x0, y1, z1)]),
    ]


def face_front(x0, x1, y, z0, z1):
    """Obdélník na přední stěně (okno, dveře): od x0 do x1, ve výšce z0–z1."""
    return [P(x0, y, z0), P(x1, y, z0), P(x1, y, z1), P(x0, y, z1)]


def face_left(x, y0, y1, z0, z1):
    """Obdélník na levé stěně: od y0 do y1, ve výšce z0–z1."""
    return [P(x, y0, z0), P(x, y1, z0), P(x, y1, z1), P(x, y0, z1)]


SUPERSAMPLE = 2  # mapa se předkreslí 2× větší a pak plynule zmenší (hladké hrany)


def bake(shapes):
    """Nakreslí seznam tvarů [(barva, body)] do malého průhledného obrázku.

    Vrátí (obrázek, levý horní roh na obrazovce). Obrázek je jen tak velký,
    jak je potřeba, takže jeho nalepení každý snímek je rychlé.
    """
    xs = [p[0] for _, pts in shapes for p in pts]
    ys = [p[1] for _, pts in shapes for p in pts]
    left, top = math.floor(min(xs)) - 1, math.floor(min(ys)) - 1
    width, height = math.ceil(max(xs)) - left + 2, math.ceil(max(ys)) - top + 2
    image = pygame.Surface((width, height), pygame.SRCALPHA)
    for color, pts in shapes:
        pygame.draw.polygon(image, color, [(x - left, y - top) for x, y in pts])
    return image, (left, top)


def wheat_parts():
    """Pšeničné pole rozdělené silnicí: vrátí [(x_od, x_do), ...] obou polovin."""
    x0, w = world.WHEAT[0], world.WHEAT[2]
    gap = world.ROAD_HALF + 0.15  # kousek místa mezi polem a silnicí
    return [(x0, world.ROAD_X - gap), (world.ROAD_X + gap, x0 + w)]


def shrink(image, pos):
    """Plynule zmenší 2× větší obrázek objektu na skutečnou velikost (hladké hrany)."""
    w, h = image.get_size()
    small = pygame.transform.smoothscale(image, (max(1, round(w / SUPERSAMPLE)), max(1, round(h / SUPERSAMPLE))))
    return small, (round(pos[0] / SUPERSAMPLE), round(pos[1] / SUPERSAMPLE))


def offset_line(path, d, z):
    """Čára rovnoběžná s tratí, posunutá o d políček do strany (kolejnice).

    V rozích se bod posune po ose úhlu (tzv. miter), aby kolejnice v zatáčce
    navazovala a neměla mezeru.
    """
    out = []
    for i, p in enumerate(path):
        prev = path[i - 1] if i > 0 else None
        nxt = path[i + 1] if i < len(path) - 1 else None
        normals = []
        for a, b in ((prev, p), (p, nxt)):
            if a is None or b is None:
                continue
            dx, dy = b[0] - a[0], b[1] - a[1]
            length = math.hypot(dx, dy)
            normals.append((-dy / length, dx / length))
        mx = sum(n[0] for n in normals)
        my = sum(n[1] for n in normals)
        ml = math.hypot(mx, my)
        mx, my = mx / ml, my / ml
        k = d / (mx * normals[0][0] + my * normals[0][1])
        out.append(P(p[0] + mx * k, p[1] + my * k, z))
    return out


# ---------- barvy z designu ----------
GRASS = [pygame.Color("#8DCB4F"), pygame.Color("#88C64C"), pygame.Color("#93D054")]
SHADOW = (30, 60, 20, 56)
TRUNK = tri("#8A5A33")
TREE_PALETTES = [(tri("#4FAE57"), tri("#62BF68")), (tri("#93D152"), tri("#A6DD66")), (tri("#3B9353"), tri("#4FA764"))]
GREYS = [tri("#BDC1C7"), tri("#B0B5BB"), tri("#A3A8AF")]
STATION_WALL = tri("#E9C46A")
ROOF_FRONT = pygame.Color("#A0463A")
ROOF_BACK = pygame.Color("#7E352B")
GLASS = pygame.Color("#A7D8F2")
GLASS_SIDE = pygame.Color("#86BEDD")
DOOR = pygame.Color("#6B4A2B")
CD_BLUE_BOX = (pygame.Color("#2A6CB5"), pygame.Color("#00549F"), pygame.Color("#004585"))


class Scenery:
    """Celá mapa: předkreslená zem + seznam předkreslených vysokých objektů."""

    def __init__(self):
        self.time = 0.0  # vlastní hodiny scény (blikání přejezdu běží i v menu)
        self.rng = random.Random(777)  # pevný seed = mapa vypadá pokaždé stejně
        self.font = pygame.font.Font(None, max(12, round(iso.px(22))))

        # vysoké objekty: seznam (hloubka, obrázek, pozice)
        self.objects = []
        ss = SUPERSAMPLE
        big_size = (settings.SCREEN_W * ss, settings.SCREEN_H * ss)

        # Vše se kreslí 2× větší (iso.supersample zvětší i souřadnice z iso.to_screen)
        with iso.supersample(ss):
            self.ground = pygame.Surface(big_size)
            self._build_ground()
            self._build_objects()
            self._build_crossing()
            # Všechny ploché vrstvy slepíme do JEDNOHO obrázku: zem, stíny dole,
            # skalní plošina a stíny na ní. Každý snímek se pak lepí jen tenhle jeden.
            self.ground.blit(self.shadows_low, (0, 0))
            for color, pts in self._cliffs + self._plateau_tops:
                pygame.draw.polygon(self.ground, color, pts)
            self.ground.blit(self.shadows_high, (0, 0))

        # ...a pak plynule zmenšíme na skutečnou velikost obrazovky
        self.ground = pygame.transform.smoothscale(self.ground, (settings.SCREEN_W, settings.SCREEN_H))
        del self.shadows_low, self.shadows_high, self._cliffs, self._plateau_tops

        # tohle se počítá už v normální velikosti (kreslí se každý snímek)
        # dráty trolejového vedení se kreslí úplně navrch (jsou vysoko nad vším)
        self.wires = [[P(x, y, z) for x, y in track.PATH] for z in (1.62, 1.78)]
        self.crossing_lights = []  # (x, y na obrazovce, pořadí blikání)
        for px_, py_, _ in world.CROSSING_POSTS:
            for i, ox in enumerate((-0.09, 0.09)):
                sx, sy = P(px_ + ox, py_ + 0.07, 0.78)
                self.crossing_lights.append((sx, sy, i))

    # =====================================================================
    # Zem (všechno ploché) – nakreslí se jednou do self.ground
    # =====================================================================
    def _build_ground(self):
        g = self.ground
        size = g.get_size()
        self.shadows_low = pygame.Surface(size, pygame.SRCALPHA)
        self.shadows_high = pygame.Surface(size, pygame.SRCALPHA)
        u = iso.px(1)  # jeden logický pixel ve skutečných (2× zvětšených) pixelech

        # 1) tráva dole: každé políčko jeden ze tří odstínů zelené
        # (mapa je větší než obrazovka, aby vyplnila i široké monitory)
        for r in range(-8, 22):
            for c in range(-12, 30):
                if not world.is_plateau(c, r):
                    pygame.draw.polygon(g, self.rng.choice(GRASS), quad(c, r, c + 1, r + 1, 0))

        # 2) trsy trávy a kytičky (náhodně, ale ne na trati, silnici a polích)
        for _ in range(560):
            x, y = -3 + self.rng.random() * 25, 1 + self.rng.random() * 16
            if world.is_plateau(math.floor(x), math.floor(y)) or world.on_road(x, y, 0.1) or world.in_rect(x, y):
                continue
            if min(world.path_dist(x, y, p) for p in (track.PATH, world.SIDING, world.MAINLINE)) < 0.6:
                continue
            sx, sy = P(x, y)
            t = self.rng.random()
            if t < 0.62:
                blades = [(-4, 0), (-2, -6), (0, -1), (2, -7), (3, -1), (5, -4), (5, 0)]
                pygame.draw.polygon(g, (111, 174, 61), [(sx + bx * u, sy + by * u) for bx, by in blades])
            else:
                color = (255, 255, 255) if t < 0.77 else (255, 216, 74) if t < 0.9 else (242, 155, 181)
                pygame.draw.polygon(g, color, [(sx, sy - 2 * u), (sx + 2 * u, sy), (sx, sy + 2 * u), (sx - 2 * u, sy)])

        # 3) pole: pšenice (jen hlína, klasy jsou objekty) a oranice s brázdami
        # pole je rozdělené silnicí na dvě poloviny
        wy, wd = world.WHEAT[1], world.WHEAT[3]
        for x_from, x_to in wheat_parts():
            pygame.draw.polygon(g, (164, 122, 74), quad(x_from, wy, x_to, wy + wd))
        px, py, pw, pd = world.PLOW
        pygame.draw.polygon(g, (138, 94, 59), quad(px, py, px + pw, py + pd))
        y = py + 0.1
        while y < py + pd - 0.1:
            pygame.draw.polygon(g, (110, 74, 46), quad(px, y, px + pw, y + 0.12, 0.005))
            y += 0.3

        # 4) silnice: svislá od stodoly k vodorovné dole, s okraji a vyjetými kolejemi
        rx, ry, rh = world.ROAD_X, world.ROAD_Y, world.ROAD_HALF
        for half, color in ((rh + 0.07, (156, 116, 74)), (rh, (194, 154, 102))):
            pygame.draw.polygon(g, color, quad(rx - half, 2.5, rx + half, ry + half))
            pygame.draw.polygon(g, color, quad(-12, ry - half, 30, ry + half))
        for a, b in ((-0.22, -0.15), (0.15, 0.22)):
            pygame.draw.polygon(g, (212, 175, 124), quad(rx + a, 2.7, rx + b, ry - 0.3))
            pygame.draw.polygon(g, (212, 175, 124), quad(-12, ry + a, 30, ry + b))

        # 5) koleje: štěrk, pražce, kolejnice (hlavní trať, vedlejší kolej, trať dole)
        for path in (track.PATH, world.SIDING, world.MAINLINE):
            self._draw_track(g, path)

        # 6) přejezd: prkna přes koleje
        cx, cy = world.CROSSING
        pygame.draw.polygon(g, (122, 90, 60), quad(cx - rh, cy - 0.4, cx + rh, cy + 0.4, 0.045))
        y = cy - 0.22
        while y < cy + 0.35:
            pygame.draw.polygon(g, (94, 65, 41), quad(cx - rh, y, cx + rh, y + 0.03, 0.05))
            y += 0.2
        for path in (track.PATH,):
            self._draw_rails(g, path)

        # 7) stíny objektů dole (kreslí se během _build_objects do shadows_low) – nalepí se později

        # 8) skalní plošina vzadu: stěny (kámen, hlína, tráva nahoře) a pak travnatý vršek
        bands = [(0, 0.35, "#8A8E95", "#6F737A"), (0.35, 0.82, "#A0704A", "#835B3B"), (0.82, 1.0, "#79B544", "#679C38")]
        self._cliffs = []
        for r in range(-8, 22):
            for c in range(-12, 30):
                if not world.is_plateau(c, r):
                    continue
                # přední stěna je vidět jen tam, kde je před plošinou nižší zem
                if not world.is_plateau(c, r + 1):
                    for z0, z1, front, _ in bands:
                        self._cliffs.append((front, face_front(c, c + 1, r + 1, z0, z1)))
                # levá stěna je vidět, když je vlevo nižší zem
                if not world.is_plateau(c - 1, r):
                    for z0, z1, _, left in bands:
                        self._cliffs.append((left, face_left(c, r, r + 1, z0, z1)))
        self._plateau_tops = [(self.rng.choice(GRASS), quad(c, r, c + 1, r + 1, 1))
                              for r in range(-8, 22) for c in range(-12, 30) if world.is_plateau(c, r)]

    def _draw_track(self, surface, path):
        """Štěrkové lože a pražce jedné trati (bez kolejnic)."""
        for a, b in zip(path, path[1:]):
            x0, x1 = min(a[0], b[0]), max(a[0], b[0])
            y0, y1 = min(a[1], b[1]), max(a[1], b[1])
            pygame.draw.polygon(surface, settings.BALLAST_EDGE, quad(x0 - 0.47, y0 - 0.47, x1 + 0.47, y1 + 0.47))
            pygame.draw.polygon(surface, settings.BALLAST, quad(x0 - 0.4, y0 - 0.4, x1 + 0.4, y1 + 0.4, 0.01))
        for a, b in zip(path, path[1:]):
            length = math.hypot(b[0] - a[0], b[1] - a[1])
            ux, uy = (b[0] - a[0]) / length, (b[1] - a[1]) / length
            t = 0.17
            while t < length:
                cx, cy = a[0] + ux * t, a[1] + uy * t
                if uy == 0:  # vodorovný úsek: pražce napříč (ve směru y)
                    pts = quad(cx - 0.06, cy - 0.32, cx + 0.06, cy + 0.32, 0.03)
                else:
                    pts = quad(cx - 0.32, cy - 0.06, cx + 0.32, cy + 0.06, 0.03)
                pygame.draw.polygon(surface, settings.SLEEPER, pts)
                t += 0.34
        if path is not track.PATH:
            self._draw_rails(surface, path)

    def _draw_rails(self, surface, path):
        """Dvě kolejnice (světlá čára + tmavý stín pod ní)."""
        width = max(1, round(iso.px(2)))  # 2 logické pixely
        for side in (0.17, -0.17):
            line = offset_line(path, side, 0.06)
            pygame.draw.lines(surface, settings.RAIL_SHADOW, False, [(x, y + iso.px(1.5)) for x, y in line], width)
            pygame.draw.lines(surface, settings.RAIL, False, line, width)

    # =====================================================================
    # Vysoké objekty – každý do vlastního malého obrázku
    # =====================================================================
    def _add(self, depth_x, depth_y, shapes):
        """Předkreslí objekt a uloží ho s hloubkou jeho "středu" pro řazení."""
        self.objects.append((iso.depth(depth_x, depth_y),) + shrink(*bake(shapes)))

    def _shadow(self, x0, y0, x1, y1, z=0.0):
        """Stín na zemi vpravo od objektu (poloprůhledný)."""
        layer = self.shadows_high if z else self.shadows_low
        pygame.draw.polygon(layer, SHADOW, quad(x0, y0, x1, y1, z))

    def _build_objects(self):
        rng = self.rng

        # --- skály na plošině ---
        for c, r, h in world.ROCKS_HIGH:
            b0 = rng.randrange(3)
            shapes = []
            for z in range(h):  # kostky naskládané na sebe, každá trochu jiným odstínem
                shapes += box(c, r, 1, 1, 1 + z, 1, GREYS[(b0 + z) % 3])
            self._shadow(c + 1, r + 0.1, c + 1 + 0.35 * h, r + 1, 1)
            self._add(c + 0.5, r + 0.5, shapes)

        # --- stromy (na plošině i dole) ---
        for c, r in world.TREES_HIGH:
            self._tree(c + 0.5 + (rng.random() - 0.5) * 0.2, r + 0.5 + (rng.random() - 0.5) * 0.2, 1)
        for x, y in world.DECOR["trees"]:
            self._tree(x, y, 0)
        for x, y in world.DECOR["bushes"]:
            self._shadow(x + 0.2, y - 0.15, x + 0.55, y + 0.2)
            self._add(x, y, box(x - 0.25, y - 0.2, 0.5, 0.4, 0, 0.28, tri("#5DA944"))
                      + box(x - 0.15, y - 0.12, 0.3, 0.24, 0.28, 0.14, tri("#71BC52")))
        for x, y, size, h in world.DECOR["rocks"]:
            self._add(x, y, box(x - size / 2, y - size / 2, size, size * 0.8, 0, h, rng.choice(GREYS))
                      + box(x - size / 4, y - size / 4, size * 0.5, size * 0.4, h, h * 0.5, GREYS[0]))

        # --- domky ---
        for x0, y0, w, d, wall, roof in world.HOUSES:
            self._house(x0, y0, w, d, wall, roof)

        # --- stodola, stohy sena, pšenice, plot ---
        self._barn()
        for x, y in world.HAYSTACKS:
            self._shadow(x + 0.25, y - 0.2, x + 0.7, y + 0.3)
            self._add(x, y, box(x - 0.3, y - 0.3, 0.6, 0.6, 0, 0.35, tri("#E3B84F"))
                      + box(x - 0.2, y - 0.2, 0.4, 0.4, 0.35, 0.22, tri("#EDC966")))
        wy = world.WHEAT[1]
        for x_from, x_to in wheat_parts():
            for i in range(6):  # řádky klasů
                row_y = wy + 0.1 + i * 0.29
                color = "#E8C35A" if i % 2 else "#DDB54C"
                self._add((x_from + x_to) / 2, row_y + 0.09, box(x_from + 0.05, row_y, x_to - x_from - 0.1, 0.18, 0, 0.26, tri(color)))
            self._fence(x_from, x_to - 0.08, wy - 0.12)

        # --- nádraží ---
        self._station_praha()
        self._station_kolin()
        self._parked_train()

        # --- stožáry trolejového vedení a návěstidla ---
        for qx, qy, px, py in world.POLES:
            ax0, ay0 = min(qx, px) - 0.03, min(qy, py) - 0.03
            self._add(qx, qy, box(qx - 0.05, qy - 0.05, 0.1, 0.1, 0, 1.8, tri("#8E939A"))
                      + box(ax0, ay0, abs(qx - px) + 0.06, abs(qy - py) + 0.06, 1.66, 0.06, tri("#6F747B")))
        for sx, sy in world.SIGNALS:
            self._add(sx, sy, box(sx - 0.04, sy - 0.04, 0.08, 0.08, 0, 1.3, tri("#9AA0A8"))
                      + box(sx - 0.12, sy - 0.06, 0.24, 0.12, 1.3, 0.46, tri("#2A2E35"))
                      + [((63, 176, 90), face_front(sx - 0.05, sx + 0.05, sy + 0.06, 1.62, 1.7)),
                         ((74, 26, 26), face_front(sx - 0.05, sx + 0.05, sy + 0.06, 1.44, 1.52))])

    def _tree(self, x, y, z0):
        """Voxelový strom: kmen + dvě patra koruny. z0 = 1 na plošině, 0 dole."""
        top, upper = self.rng.choice(TREE_PALETTES)
        k = 0.85 + self.rng.random() * 0.45  # každý strom trochu jinak vysoký
        self._shadow(x + 0.15, y - 0.25, x + 0.8, y + 0.3, z0)
        self._add(x, y, box(x - 0.08, y - 0.08, 0.16, 0.16, z0, 0.4 * k, TRUNK)
                  + box(x - 0.36, y - 0.36, 0.72, 0.72, z0 + 0.35 * k, 0.55 * k, top)
                  + box(x - 0.22, y - 0.22, 0.44, 0.44, z0 + 0.9 * k, 0.45 * k, upper))

    def _gable_roof(self, x0, y0, w, d, zt, zr, roof_front, roof_back, gable, overhang):
        """Sedlová střecha s hřebenem podél osy x: zadní a přední plocha + levý štít.

        zt = výška okapu, zr = výška hřebene. Štít se kreslí první, plochy střechy přes něj.
        """
        x1, y1, ym = x0 + w, y0 + d, y0 + d / 2
        ov = overhang
        return [
            (gable, [P(x0, y0, zt), P(x0, y1, zt), P(x0, ym, zr)]),
            (roof_back, [P(x0 - ov, y0 - ov, zt), P(x1 + ov, y0 - ov, zt), P(x1 + ov, ym, zr), P(x0 - ov, ym, zr)]),
            (roof_front, [P(x0 - ov, ym, zr), P(x1 + ov, ym, zr), P(x1 + ov, y1 + ov, zt), P(x0 - ov, y1 + ov, zt)]),
        ]

    def _house(self, x0, y0, w, d, wall, roof):
        walls = tri(wall)
        x1, y1 = x0 + w, y0 + d
        shapes = box(x0, y0, w, d, 0, 0.85, walls)
        for t in (0.18, 0.66):  # dvě okna vpředu
            shapes.append((GLASS, face_front(x0 + w * t, x0 + w * t + 0.22, y1, 0.35, 0.62)))
        shapes.append((GLASS_SIDE, face_left(x0, y0 + d * 0.35, y0 + d * 0.35 + 0.25, 0.35, 0.62)))
        shapes.append((DOOR, face_front(x0 + w * 0.44, x0 + w * 0.6, y1, 0, 0.55)))
        shapes += self._gable_roof(x0, y0, w, d, 0.85, 1.4, pygame.Color(*roof), shade(roof, 0.72), walls[2], 0.12)
        shapes += box(x0 + w * 0.7, y0 + d * 0.2, 0.18, 0.18, 1.05, 0.55, tri("#8A4A3A"))  # komín
        self._shadow(x1, y0 + 0.15, x1 + 0.5, y1 + 0.1)
        self._add(x0 + w / 2, y0 + d / 2, shapes)

    def _barn(self):
        x0, y0, w, d = world.BARN
        x1, y1 = x0 + w, y0 + d
        walls = tri("#A13D2D")
        shapes = box(x0, y0, w, d, 0, 0.95, walls)
        shapes.append(((94, 34, 25), face_front(9.15, 9.85, y1, 0, 0.75)))  # velká vrata
        # bílý kříž na vratech (dvě šikmé lišty)
        shapes.append(((242, 235, 221), [P(9.15, y1, 0), P(9.21, y1, 0), P(9.85, y1, 0.75), P(9.79, y1, 0.75)]))
        shapes.append(((242, 235, 221), [P(9.85, y1, 0), P(9.79, y1, 0), P(9.15, y1, 0.75), P(9.21, y1, 0.75)]))
        shapes += self._gable_roof(x0, y0, w, d, 0.95, 1.55, pygame.Color("#6A6F77"), pygame.Color("#4A4E55"), walls[2], 0.1)
        self._shadow(x1, y0 + 0.15, x1 + 0.55, y1)
        self._add(x0 + w / 2, y0 + d / 2, shapes)

    def _fence(self, x_from, x_to, y):
        """Dřevěný plot: sloupky po 1 políčku a dvě vodorovné latě."""
        wood = tri("#9A6B42")
        shapes = []
        x = x_from
        while x <= x_to + 0.01:
            shapes += box(x, y - 0.04, 0.08, 0.08, 0, 0.45, wood)
            x += 1
        shapes += box(x_from, y + 0.05, x_to - x_from + 0.08, 0.03, 0.14, 0.06, wood)
        shapes += box(x_from, y + 0.05, x_to - x_from + 0.08, 0.03, 0.32, 0.06, wood)
        self._add((x_from + x_to) / 2, y, shapes)

    def _station_praha(self):
        """Cílové nádraží Praha hl. n.: žlutá budova s věžičkou, nástupiště, lampy, lavička."""
        x0, y0, w, d = world.PRAHA
        x1, y1, ym = x0 + w, y0 + d, y0 + d / 2
        zt, zr = 1.45, 2.15
        shapes = box(x0, y0, w, d, 0, 0.18, tri("#B78F4A"))[:2]  # sokl (vršek není vidět)
        shapes += box(x0, y0, w, d, 0.18, zt - 0.18, STATION_WALL)
        for i in range(5):  # dvě řady oken, uprostřed dole jsou dveře
            wx = x0 + 0.28 + i * 0.66
            for z in (0.25, 0.85):
                if i != 2 or z > 0.5:
                    shapes.append((GLASS, face_front(wx, wx + 0.3, y1, z, z + 0.38)))
        for yy in (y0 + 0.35, y0 + 1.1):
            for z in (0.25, 0.85):
                shapes.append((GLASS_SIDE, face_left(x0, yy, yy + 0.32, z, z + 0.38)))
        shapes.append((DOOR, [P(x0 + 1.6, y1, 0), P(x0 + 1.95, y1, 0), P(x0 + 1.95, y1, 0.62),
                              P(x0 + 1.775, y1, 0.7), P(x0 + 1.6, y1, 0.62)]))
        shapes.append(((247, 235, 200), face_front(x0, x1, y1, 0.74, 0.8)))  # římsa
        shapes += self._gable_roof(x0, y0, w, d, zt, zr, ROOF_FRONT, ROOF_BACK, STATION_WALL[2], 0.15)
        # věžička s hodinami na hřebeni
        cx = x0 + 1.75
        shapes += box(cx - 0.25, ym - 0.25, 0.5, 0.5, zr - 0.3, 0.6, STATION_WALL)
        shapes += box(cx - 0.31, ym - 0.31, 0.62, 0.62, zr + 0.3, 0.1, tri("#7E352B"))
        cy, cz = ym + 0.25, zr + 0.07
        shapes.append(((255, 255, 255), [P(cx - 0.13, cy, cz), P(cx - 0.065, cy, cz + 0.12), P(cx + 0.065, cy, cz + 0.12),
                                         P(cx + 0.13, cy, cz), P(cx + 0.065, cy, cz - 0.12), P(cx - 0.065, cy, cz - 0.12)]))
        shapes.append(((28, 36, 48), face_front(cx - 0.01, cx + 0.01, cy, cz, cz + 0.1)))
        shapes.append(((28, 36, 48), face_front(cx, cx + 0.08, cy, cz - 0.01, cz + 0.01)))
        self._shadow(x1, y0 + 0.2, x1 + 0.8, y1)
        self._add(x0 + w / 2, ym, shapes)

        # nástupiště za tratí a před ní (se žlutou bezpečnostní čarou)
        for py, pd in ((6.45, 0.6), (7.92, 0.5)):
            edge = py + pd - 0.1 if py < 7 else py
            self._add(16.8, py + pd / 2, box(15.0, py, 3.6, pd, 0, 0.22, tri("#BFC3C9"))
                      + [((255, 216, 74), quad(15.0, edge, 18.6, edge + 0.07, 0.221))])
        for lx in (15.7, 17.7):  # lampy
            ly = 8.25
            self._add(lx, ly, box(lx - 0.03, ly - 0.03, 0.06, 0.06, 0.22, 1.05, tri("#3A3F47"))
                      + box(lx - 0.1, ly - 0.1, 0.2, 0.2, 1.27, 0.1, tri("#2A2E35"))
                      + box(lx - 0.07, ly - 0.07, 0.14, 0.14, 1.2, 0.07, tri("#FFE08A")))
        self._add(16.65, 8.2, box(16.4, 8.12, 0.5, 0.18, 0.22, 0.12, tri("#8A5A33"))
                  + box(16.4, 8.12, 0.5, 0.04, 0.34, 0.2, tri("#8A5A33")))  # lavička
        for bx, by, bw, bd in ((18.25, 7.15, 0.3, 0.7), (14.95, 8.68, 0.25, 0.64)):  # zarážedla
            self._add(bx + bw / 2, by + bd / 2, box(bx, by, bw, bd, 0, 0.45, tri("#C8553D"))
                      + [((242, 244, 247), face_front(bx, bx + bw, by + bd, 0.25, 0.33))])

    def _station_kolin(self):
        """Malé nádraží Kolín na začátku trati."""
        x0, y0, w, d = world.KOLIN
        x1, y1, ym = x0 + w, y0 + d, y0 + d / 2
        shapes = box(x0, y0, w, d, 0, 0.14, tri("#B78F4A"))[:2]
        shapes += box(x0, y0, w, d, 0.14, 1.0 - 0.14, STATION_WALL)
        for wx in (0.25, 0.75, 1.65):
            shapes.append((GLASS, face_front(x0 + wx, x0 + wx + 0.28, y1, 0.32, 0.66)))
        shapes.append((GLASS_SIDE, face_left(x0, y0 + 0.35, y0 + 0.65, 0.32, 0.66)))
        shapes.append((DOOR, face_front(x0 + 1.25, x0 + 1.55, y1, 0, 0.62)))
        shapes.append(((247, 235, 200), face_front(x0, x1, y1, 0.72, 0.77)))
        shapes += self._gable_roof(x0, y0, w, d, 1.0, 1.5, ROOF_FRONT, ROOF_BACK, STATION_WALL[2], 0.12)
        shapes += box(x0 + 1.6, y0 + 0.25, 0.16, 0.16, 1.15, 0.5, tri("#8A4A3A"))
        self._shadow(x1, y0 + 0.15, x1 + 0.6, y1)
        self._add(x0 + w / 2, ym, shapes)
        self._add(1.4, 2.93, box(0.1, 2.8, 2.55, 0.25, 0, 0.2, tri("#BFC3C9"))
                  + [((255, 216, 74), quad(0.1, 2.97, 2.65, 3.03, 0.201))])

    def _parked_train(self):
        """Odstavená souprava ČD (lokomotiva + vagon) na vedlejší koleji v Praze."""
        y0, y1 = 8.72, 9.28
        x0, x1 = 15.35, 17.25
        loco = box(x0 + 0.1, y0 + 0.05, x1 - x0 - 0.2, 0.46, 0.02, 0.16, tri("#2A2E35"))
        loco += box(x0, y0, x1 - x0, y1 - y0, 0.18, 0.82, CD_BLUE_BOX)
        loco.append(((242, 244, 247), face_front(x0, x1, y1, 0.36, 0.43)))
        wx = x0 + 0.55
        while wx < x1 - 0.2:
            loco.append(((191, 228, 255), face_front(wx, wx + 0.2, y1, 0.6, 0.82)))
            wx += 0.35
        loco.append(((191, 228, 255), face_left(x0, y0 + 0.08, y1 - 0.08, 0.6, 0.86)))
        loco.append(((255, 199, 44), face_left(x0, y0, y1, 0.18, 0.36)))
        loco += box(x0 + 0.5, y0 + 0.12, 0.9, 0.32, 1.0, 0.07, tri("#8E939A"))
        self._shadow(x1, y0 + 0.1, x1 + 0.4, y1)
        self._add((x0 + x1) / 2, 9.0, loco)

        cy0, cy1, cx0, cx1 = 8.74, 9.26, 17.4, 20.2
        coach = box(cx0 + 0.1, cy0 + 0.05, cx1 - cx0 - 0.2, 0.42, 0.02, 0.16, tri("#2A2E35"))
        coach += box(cx0, cy0, cx1 - cx0, cy1 - cy0, 0.18, 0.78, (pygame.Color("#D2D5DC"), pygame.Color("#00549F"), pygame.Color("#004585")))
        coach.append(((242, 244, 247), face_front(cx0, cx1, cy1, 0.55, 0.92)))
        coach.append(((242, 244, 247), face_left(cx0, cy0, cy1, 0.55, 0.92)))
        wx = cx0 + 0.2
        while wx < cx1 - 0.2:
            coach.append(((111, 166, 204), face_front(wx, wx + 0.22, cy1, 0.6, 0.82)))
            wx += 0.34
        coach.append(((42, 46, 53), face_left(cx0, cy0 + 0.14, cy1 - 0.14, 0.2, 0.8)))
        self._add((cx0 + cx1) / 2, 9.0, coach)

    # =====================================================================
    # Přejezd – sloupky se závorou ve dvou stavech (nahoře / dole)
    # =====================================================================
    def _build_crossing(self):
        self.crossing = {"up": [], "down": []}
        for px, py, direction in world.CROSSING_POSTS:
            for state in ("up", "down"):
                shapes = box(px - 0.05, py - 0.05, 0.1, 0.1, 0, 1.15, tri("#E9ECEF"))
                yf = py + 0.06
                # výstražný kříž: dvě šikmé bílé lišty
                shapes.append(((255, 255, 255), [P(px - 0.24, yf, 0.98), P(px - 0.18, yf, 0.94), P(px + 0.24, yf, 1.3), P(px + 0.18, yf, 1.34)]))
                shapes.append(((255, 255, 255), [P(px - 0.24, yf, 1.3), P(px - 0.18, yf, 1.34), P(px + 0.24, yf, 0.98), P(px + 0.18, yf, 0.94)]))
                shapes.append(((28, 36, 48), face_front(px - 0.17, px + 0.17, yf, 0.71, 0.85)))  # štítek se světly
                # závora z 6 kousků, střídavě červený a bílý
                for i in range(6):
                    color = (214, 51, 47) if i % 2 == 0 else (242, 244, 247)
                    if state == "down":  # vodorovně přes silnici
                        xa = px + direction * (0.08 + i * 1.1 / 6)
                        xb = px + direction * (0.08 + (i + 1) * 1.1 / 6)
                        shapes += box(min(xa, xb), py - 0.03, abs(xb - xa), 0.06, 0.62, 0.07, (color, shade(color, 0.84), shade(color, 0.7)))
                    else:  # svisle nahoru
                        bx = px + direction * 0.08
                        shapes += box(bx - 0.035, py - 0.03, 0.07, 0.06, 0.62 + i * 1.1 / 6, 1.1 / 6, (color, shade(color, 0.84), shade(color, 0.7)))
                self.crossing[state].append((iso.depth(px, py),) + shrink(*bake(shapes)))

    # =====================================================================
    # Každý snímek
    # =====================================================================
    def update(self, dt):
        """Posune vlastní hodiny scény (pro blikání a později okolní život)."""
        self.time += dt

    def draw(self, screen, game, extra=()):
        """Nakreslí celou mapu a nepřátele ve správném pořadí podle hloubky.

        extra = další věci, které se mají zařadit podle hloubky (okolní život z ambient.py):
                seznam dvojic (hloubka, funkce), kde funkce(screen) danou věc nakreslí.
        """
        # 1) celá předkreslená zem jedním nalepením (rychlé)
        screen.blit(self.ground, (0, 0))

        # 2) vše vysoké + nepřátelé (+ okolní život), seřazené odzadu dopředu
        busy = game.state == "playing" and game.wave_in_progress
        items = [(d, 0, img, pos) for d, img, pos in self.objects]
        items += [(d, 0, img, pos) for d, img, pos in self.crossing["down" if busy else "up"]]
        for enemy in game.enemies:
            items.append((iso.depth(enemy.x, enemy.y), 1, enemy, None))
        for depth, draw_function in extra:
            items.append((depth, 2, draw_function, None))
        items.sort(key=lambda item: (item[0], item[1]))
        for _, kind, thing, pos in items:
            if kind == 0:
                screen.blit(thing, pos)  # předkreslený objekt mapy
            elif kind == 1:
                thing.draw(screen)  # nepřítel
            else:
                thing(screen)  # věc z okolního života

        # 3) blikající světla přejezdu (střídavě levé a pravé), když jede vlna
        blink = int(self.time * 3) % 2
        radius = max(2, round(iso.px(3)))
        for sx, sy, order in self.crossing_lights:
            on = busy and order == blink
            pygame.draw.circle(screen, (255, 59, 48) if on else (74, 26, 26), (sx, sy), radius)

        # 4) dráty trolejového vedení nad vším a cedule Kolín
        for wire in self.wires:
            pygame.draw.aalines(screen, (58, 63, 71), False, wire)
        self._sign(screen, "Kolín", P(1.4, 2.25, 2.1))

    def _sign(self, screen, text, at):
        """Modrá cedule s bílým nápisem (název stanice)."""
        label = self.font.render(text, True, settings.WHITE)
        rect = label.get_rect(midbottom=(at[0], at[1]))
        pygame.draw.rect(screen, settings.CD_BLUE, rect.inflate(iso.px(16), iso.px(8)))
        screen.blit(label, rect)
