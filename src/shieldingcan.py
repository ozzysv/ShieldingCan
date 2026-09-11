# -*- coding: utf-8 -*-
"""
ShieldingCan v0.2.6 for KiCad 9.x

Rectangle-based via guard / via fence generator.


ViaFence - Place via fence along selected tracks
For KiCad 9.0+ (SWIG API for compatibility with wx dialogs)

# Copyright 2026 Sergiy Ozymok https://github.com/ozzysv
#
# original plugin         https://github.com/ozzysv/ShieldingCan
#
# GPL-3.0 license

"""

import math
import json
import os
import wx
import pcbnew

PLUGIN_NAME = "ShieldingCan"
GROUP_NAME = "SHIELDING_CAN"
OLD_GROUP_NAMES = ("GUARD_TRACE",)
VERSION = "0.4.10"
CONFIG_APP = "ShieldingCan"
SETTINGS_FILE_NAME = "shieldingcan_settings.json"
COURTYARD_VIA_EXTRA_MARGIN_MM = 0.00

LANGUAGES = {
    "English": "en",
    "Deutsch": "de",
    "Українська": "uk",
}

TRANSLATIONS = {
    "en": {
        "via_settings": "Via settings",
        "mask_settings": "Mask settings",
        "via_diameter": "Via diameter",
        "drill": "Drill",
        "desired_pitch": "Desired via pitch",
        "rows": "Rows",
        "row_spacing": "Row spacing",
        "first_row_offset": "First row offset",
        "collision_clearance": "Collision clearance",
        "staggered_pattern": "Staggered pattern",
        "mask_side": "Mask side",
        "mask_extra": "Mask extra per side",
        "keepout_margin": "Keepout break margin",
        "build_side": "Build side",
        "net_name": "Net name",
        "units": "Units",
        "language": "Language",
        "cleanup": "Delete previous SHIELDING_CAN group before build",
        "info": "Rectangle source: User.Drawings only. Zones/polygons are ignored.",
        "outside": "Outside rectangle",
        "inside": "Inside rectangle",
        "both": "Both",
        "none": "None",
        "tip_via_diameter": "Overall via pad diameter.",
        "tip_drill": "Finished drill diameter of the stitching vias.",
        "tip_desired_pitch": "Requested spacing between vias. The plugin adjusts the actual pitch so each allowed segment is filled evenly.",
        "tip_rows": "Number of parallel via rows generated around the rectangle.",
        "tip_row_spacing": "Center-to-center distance between adjacent via rows.",
        "tip_first_row_offset": "Distance from the selected User.Drawings rectangle to the centerline of the first via row.",
        "tip_collision_clearance": "Additional clearance kept between vias and copper obstacles such as tracks, pads and existing vias.",
        "tip_staggered_pattern": "Offsets every second via row by half a pitch to create a staggered pattern.",
        "tip_mask_side": "Choose which solder-mask layers receive the exposed shielding strip.",
        "tip_mask_extra": "Additional mask opening beyond the via diameter on each side.",
        "tip_keepout_margin": "Extra mask break distance added before and after an obstacle.",
        "tip_build_side": "Generate the shielding structure outside or inside the selected rectangle.",
        "tip_net_name": "Net assigned to all generated vias. The list is read from the current PCB.",
        "tip_units": "Display and edit dimensional values in millimeters or mils. Values are converted automatically.",
        "tip_language": "Select the interface language. The selection is saved in the JSON settings file.",
        "tip_cleanup": "Remove the previously generated SHIELDING_CAN group before creating a new one.",
        "report_finished": "finished.",
        "report_source_layer": "Source layer",
        "report_candidates": "Candidates",
        "report_placed_vias": "Placed vias",
        "report_skipped_keepout": "Skipped by mask keepout",
        "report_skipped_collision": "Skipped by tracks/pads/vias",
        "report_mask_segments": "Mask segments",
        "report_courtyard_boxes": "Courtyard keepout boxes",
        "report_zones": "Zones/polygons",
        "report_ignored": "ignored",
        "report_adjusted_pitch": "Adjusted pitch per side",
    },
    "de": {
        "via_settings": "Via-Einstellungen",
        "mask_settings": "Masken-Einstellungen",
        "via_diameter": "Via-Durchmesser",
        "drill": "Bohrung",
        "desired_pitch": "Gewünschter Via-Abstand",
        "rows": "Reihen",
        "row_spacing": "Reihenabstand",
        "first_row_offset": "Abstand der ersten Reihe",
        "collision_clearance": "Kollisionsabstand",
        "staggered_pattern": "Versetztes Muster",
        "mask_side": "Maskenseite",
        "mask_extra": "Maskenzugabe pro Seite",
        "keepout_margin": "Zusätzlicher Maskenabstand",
        "build_side": "Aufbauseite",
        "net_name": "Netzname",
        "units": "Einheiten",
        "language": "Sprache",
        "cleanup": "Vorherige SHIELDING_CAN-Gruppe vor dem Erstellen löschen",
        "info": "Rechteckquelle: nur User.Drawings. Zonen/Polygone werden ignoriert.",
        "outside": "Außerhalb des Rechtecks",
        "inside": "Innerhalb des Rechtecks",
        "both": "Beide",
        "none": "Keine",
        "tip_via_diameter": "Gesamtdurchmesser des Via-Pads.",
        "tip_drill": "Fertiger Bohrdurchmesser der Stitching-Vias.",
        "tip_desired_pitch": "Gewünschter Abstand zwischen den Vias. Der tatsächliche Abstand wird angepasst, damit jedes zulässige Segment gleichmäßig gefüllt wird.",
        "tip_rows": "Anzahl paralleler Via-Reihen um das Rechteck.",
        "tip_row_spacing": "Mitte-zu-Mitte-Abstand zwischen benachbarten Via-Reihen.",
        "tip_first_row_offset": "Abstand vom ausgewählten User.Drawings-Rechteck zur Mittellinie der ersten Via-Reihe.",
        "tip_collision_clearance": "Zusätzlicher Abstand zwischen Vias und Kupferhindernissen wie Leiterbahnen, Pads und vorhandenen Vias.",
        "tip_staggered_pattern": "Versetzt jede zweite Via-Reihe um einen halben Via-Abstand.",
        "tip_mask_side": "Wählt, auf welchen Lötmaskenlagen der freigelegte Abschirmstreifen erzeugt wird.",
        "tip_mask_extra": "Zusätzliche Maskenöffnung über den Via-Durchmesser hinaus, pro Seite.",
        "tip_keepout_margin": "Zusätzlicher Abstand des Maskenunterbruchs vor und nach einem Hindernis.",
        "tip_build_side": "Erzeugt die Abschirmstruktur außerhalb oder innerhalb des ausgewählten Rechtecks.",
        "tip_net_name": "Netz, das allen erzeugten Vias zugewiesen wird. Die Liste wird aus der aktuellen Leiterplatte gelesen.",
        "tip_units": "Maßwerte in Millimetern oder mils anzeigen und bearbeiten. Werte werden automatisch umgerechnet.",
        "tip_language": "Sprache der Benutzeroberfläche wählen. Die Auswahl wird in der JSON-Datei gespeichert.",
        "tip_cleanup": "Entfernt die zuvor erzeugte SHIELDING_CAN-Gruppe vor dem Neuerstellen.",
        "report_finished": "abgeschlossen.",
        "report_source_layer": "Quell-Layer",
        "report_candidates": "Kandidaten",
        "report_placed_vias": "Platzierte Vias",
        "report_skipped_keepout": "Durch Masken-Keepout übersprungen",
        "report_skipped_collision": "Durch Leiterbahnen/Pads/Vias übersprungen",
        "report_mask_segments": "Maskensegmente",
        "report_courtyard_boxes": "Courtyard-Keepout-Bereiche",
        "report_zones": "Zonen/Polygone",
        "report_ignored": "ignoriert",
        "report_adjusted_pitch": "Angepasster Via-Abstand pro Seite",
    },
    "uk": {
        "via_settings": "Налаштування via",
        "mask_settings": "Налаштування маски",
        "via_diameter": "Діаметр via",
        "drill": "Діаметр отвору",
        "desired_pitch": "Бажаний крок via",
        "rows": "Кількість рядів",
        "row_spacing": "Відстань між рядами",
        "first_row_offset": "Відступ першого ряду",
        "collision_clearance": "Зазор до перешкод",
        "staggered_pattern": "Шахове розташування",
        "mask_side": "Сторона маски",
        "mask_extra": "Додаткове відкриття маски",
        "keepout_margin": "Додатковий відступ розриву",
        "build_side": "Сторона побудови",
        "net_name": "Назва мережі",
        "units": "Одиниці",
        "language": "Мова",
        "cleanup": "Видалити попередню групу SHIELDING_CAN перед побудовою",
        "info": "Джерело прямокутника: тільки User.Drawings. Зони/полігони ігноруються.",
        "outside": "Зовні прямокутника",
        "inside": "Всередині прямокутника",
        "both": "Обидві",
        "none": "Немає",
        "tip_via_diameter": "Зовнішній діаметр контактної площадки via.",
        "tip_drill": "Діаметр готового отвору stitching via.",
        "tip_desired_pitch": "Бажана відстань між via. Плагін підлаштовує фактичний крок, щоб рівномірно заповнити кожен дозволений сегмент.",
        "tip_rows": "Кількість паралельних рядів via навколо прямокутника.",
        "tip_row_spacing": "Відстань між центрами сусідніх рядів via.",
        "tip_first_row_offset": "Відстань від вибраного прямокутника User.Drawings до осьової лінії першого ряду via.",
        "tip_collision_clearance": "Додатковий зазор між via та мідними перешкодами: доріжками, pads і наявними via.",
        "tip_staggered_pattern": "Зсуває кожен другий ряд via на половину кроку, утворюючи шахове розташування.",
        "tip_mask_side": "Вибір шарів solder mask, на яких створюється відкрита смуга екранування.",
        "tip_mask_extra": "Додаткове відкриття маски з кожного боку від діаметра via.",
        "tip_keepout_margin": "Додатковий відступ розриву маски до і після перешкоди.",
        "tip_build_side": "Побудова екранування зовні або всередині вибраного прямокутника.",
        "tip_net_name": "Мережа, яка буде призначена всім створеним via. Список береться з поточної плати.",
        "tip_units": "Відображення і редагування розмірів у міліметрах або mils. Значення перераховуються автоматично.",
        "tip_language": "Вибір мови інтерфейсу. Вибір зберігається у JSON-файлі налаштувань.",
        "tip_cleanup": "Видаляє раніше створену групу SHIELDING_CAN перед новою побудовою.",
        "report_finished": "завершено.",
        "report_source_layer": "Вихідний шар",
        "report_candidates": "Кандидатів",
        "report_placed_vias": "Розміщено via",
        "report_skipped_keepout": "Пропущено через keepout маски",
        "report_skipped_collision": "Пропущено через доріжки/pads/vias",
        "report_mask_segments": "Сегментів маски",
        "report_courtyard_boxes": "Областей Courtyard keepout",
        "report_zones": "Зони/полігони",
        "report_ignored": "ігноруються",
        "report_adjusted_pitch": "Скоригований крок для кожної сторони",
    },
}

def tr(lang, key):
    return TRANSLATIONS.get(lang, TRANSLATIONS["en"]).get(key, key)



def iu(mm):
    return int(pcbnew.FromMM(float(mm)))


def mm(value_iu):
    return float(pcbnew.ToMM(int(round(value_iu))))


def v2(x, y):
    try:
        return pcbnew.VECTOR2I(int(round(x)), int(round(y)))
    except Exception:
        return pcbnew.wxPoint(int(round(x)), int(round(y)))


def get_x(p):
    return p.x if hasattr(p, "x") else p.X


def get_y(p):
    return p.y if hasattr(p, "y") else p.Y


def pt_tuple(p):
    return (get_x(p), get_y(p))


def dist(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])


def item_bbox(item):
    try:
        return item.GetBoundingBox()
    except Exception:
        return None


def bbox_xy(box):
    if box is None:
        return None
    try:
        x0 = box.GetX(); y0 = box.GetY()
        x1 = x0 + box.GetWidth(); y1 = y0 + box.GetHeight()
        return min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1)
    except Exception:
        try:
            return min(box.GetLeft(), box.GetRight()), min(box.GetTop(), box.GetBottom()), max(box.GetLeft(), box.GetRight()), max(box.GetTop(), box.GetBottom())
        except Exception:
            return None


def bbox_intersects_circle(box, p, r):
    b = bbox_xy(box)
    if b is None:
        return False
    x0, y0, x1, y1 = b
    px, py = p
    cx = min(max(px, x0), x1)
    cy = min(max(py, y0), y1)
    return (px - cx) * (px - cx) + (py - cy) * (py - cy) <= r * r


def item_is_selected(item):
    try:
        return bool(item.IsSelected())
    except Exception:
        return False


def get_layer_by_name(board, name, fallback=None):
    try:
        return board.GetLayerID(name)
    except Exception:
        return fallback


def get_layer_name(board, layer):
    try:
        return board.GetLayerName(layer)
    except Exception:
        return str(layer)


def is_rect_shape(shape):
    if not isinstance(shape, pcbnew.PCB_SHAPE):
        return False
    try:
        s = shape.GetShape()
        for name in ("SHAPE_T_RECT", "SHAPE_T_RECTANGLE"):
            if hasattr(pcbnew, name) and s == getattr(pcbnew, name):
                return True
    except Exception:
        pass
    try:
        return "RECT" in str(shape.GetShape()).upper()
    except Exception:
        return False


def get_rect_bounds(shape):
    try:
        s = pt_tuple(shape.GetStart())
        e = pt_tuple(shape.GetEnd())
        x0, x1 = sorted((s[0], e[0]))
        y0, y1 = sorted((s[1], e[1]))
        if x1 > x0 and y1 > y0:
            return x0, y0, x1, y1
    except Exception:
        pass
    b = bbox_xy(item_bbox(shape))
    if b is None:
        raise RuntimeError("Cannot read selected rectangle geometry.")
    return b


def get_net_by_name(board, name):
    if not name:
        return None
    try:
        return board.FindNet(name)
    except Exception:
        pass
    try:
        return board.GetNetsByName().get(name, None)
    except Exception:
        return None


def get_board_net_names(board):
    names = []
    try:
        nets = board.GetNetsByName()
        for name in nets.keys():
            text = str(name)
            if text and text not in names:
                names.append(text)
    except Exception:
        pass
    try:
        netinfo = board.GetNetInfo()
        nets = netinfo.NetsByName()
        for name in nets.keys():
            text = str(name)
            if text and text not in names:
                names.append(text)
    except Exception:
        pass
    names = [n for n in names if n not in ("", "<no net>")]
    names.sort(key=lambda x: x.lower())
    return names


def make_segment(board, layer, start, end, width):
    seg = pcbnew.PCB_SHAPE(board)
    seg.SetShape(pcbnew.SHAPE_T_SEGMENT)
    seg.SetStart(v2(start[0], start[1]))
    seg.SetEnd(v2(end[0], end[1]))
    seg.SetLayer(layer)
    seg.SetWidth(int(width))
    board.Add(seg)
    return seg


def make_mask_square_segment(board, layer, start, end, width):
    """
    Backward-compatible helper: create a mask opening with square 90-degree ends.
    """
    items = make_mask_mixed_cap_segment(board, layer, start, end, width, False, False)
    return items[0] if items else None


def make_filled_circle(board, layer, center, radius):
    """Create a filled circle on a mask layer, used to round only selected ends."""
    try:
        c = pcbnew.PCB_SHAPE(board)
        c.SetShape(pcbnew.SHAPE_T_CIRCLE)
        c.SetLayer(layer)
        c.SetWidth(0)
        c.SetStart(v2(center[0], center[1]))
        c.SetEnd(v2(center[0] + radius, center[1]))
        try:
            c.SetFilled(True)
        except Exception:
            pass
        board.Add(c)
        return c
    except Exception:
        # If filled circles are not available, a zero-length wide segment is
        # usually rendered as a round dot in KiCad.
        return make_segment(board, layer, center, center, int(round(radius * 2)))


def make_mask_mixed_cap_segment(board, layer, start, end, width, round_start, round_end):
    """
    Create a mask opening on a horizontal/vertical side.

    Square 90-degree caps are used at obstacle breaks.  Rounded caps are added
    only at the real rectangle corners, where round_start/round_end is True.
    This avoids the stepped/squared corner artefacts while keeping obstacle
    gaps clean and perpendicular.
    """
    x0, y0 = start
    x1, y1 = end
    half = int(round(width / 2.0))
    items = []
    try:
        rect = pcbnew.PCB_SHAPE(board)
        rect.SetShape(pcbnew.SHAPE_T_RECT)
        rect.SetLayer(layer)
        rect.SetWidth(0)
        if abs(y1 - y0) <= abs(x1 - x0):
            # Horizontal. Square body ends are exactly at x0/x1.
            a = (min(x0, x1), y0 - half)
            b = (max(x0, x1), y0 + half)
        else:
            # Vertical. Square body ends are exactly at y0/y1.
            a = (x0 - half, min(y0, y1))
            b = (x0 + half, max(y0, y1))
        rect.SetStart(v2(a[0], a[1]))
        rect.SetEnd(v2(b[0], b[1]))
        try:
            rect.SetFilled(True)
        except Exception:
            pass
        board.Add(rect)
        items.append(rect)

        if round_start:
            items.append(make_filled_circle(board, layer, start, half))
        if round_end:
            items.append(make_filled_circle(board, layer, end, half))
        return items
    except Exception:
        # Fallback: KiCad round-cap segment. This is visually correct for
        # normal corners but not ideal for obstacle breaks.
        return [make_segment(board, layer, start, end, width)]

def make_via(board, pos, diameter, drill, net):
    via = pcbnew.PCB_VIA(board)
    via.SetPosition(v2(pos[0], pos[1]))
    via.SetWidth(int(diameter))
    via.SetDrill(int(drill))
    if net is not None:
        try:
            via.SetNetCode(net.GetNetCode())
        except Exception:
            try:
                via.SetNet(net)
            except Exception:
                pass
    board.Add(via)
    return via


def delete_guard_trace_groups(board):
    removed = 0
    try:
        groups = list(board.Groups())
    except Exception:
        try:
            groups = list(board.GetGroups())
        except Exception:
            groups = []
    for group in groups:
        try:
            if group.GetName() != GROUP_NAME and group.GetName() not in OLD_GROUP_NAMES:
                continue
            items = list(group.GetItemsDeque())
            for item in items:
                try:
                    board.Remove(item)
                except Exception:
                    pass
            try:
                board.Remove(group)
            except Exception:
                pass
            removed += 1
        except Exception:
            pass
    return removed


def create_group(board):
    try:
        group = pcbnew.PCB_GROUP(board)
        group.SetName(GROUP_NAME)
        board.Add(group)
        return group
    except Exception:
        return None


def group_add(group, item):
    if group is None:
        return
    try:
        group.AddItem(item)
    except Exception:
        pass


def get_all_tracks_and_vias(board):
    try:
        return list(board.GetTracks())
    except Exception:
        return []


def get_all_pads(board):
    pads = []
    try:
        for fp in board.GetFootprints():
            for pad in fp.Pads():
                pads.append(pad)
    except Exception:
        pass
    return pads




def is_via_item(item):
    try:
        return isinstance(item, pcbnew.PCB_VIA)
    except Exception:
        return item.__class__.__name__.upper().endswith("VIA")


def is_copper_layer(board, layer):
    if layer is None:
        return False
    try:
        return bool(board.IsCopperLayer(layer))
    except Exception:
        pass
    try:
        return layer in board.GetEnabledLayers().CuStack()
    except Exception:
        pass
    if layer in (pcbnew.F_Cu, pcbnew.B_Cu):
        return True
    try:
        return 0 <= int(layer) < 32
    except Exception:
        return False


def pad_on_layer(pad, layer):
    try:
        return bool(pad.IsOnLayer(layer))
    except Exception:
        pass
    try:
        return bool(pad.GetLayerSet().Contains(layer))
    except Exception:
        pass
    try:
        return pad.GetLayer() == layer
    except Exception:
        return True


def get_all_drawings(board):
    try:
        return list(board.GetDrawings())
    except Exception:
        return []


def _call_first(obj, method_names):
    for name in method_names:
        try:
            fn = getattr(obj, name)
        except Exception:
            continue
        try:
            return list(fn())
        except Exception:
            continue
    return []


def get_all_footprint_graphics(board):
    """Return graphical items that live inside footprints.

    KiCad courtyard outlines are usually footprint graphics, not board-level
    drawings.  They can be lines, rectangles, arcs, circles or polygons on
    F.CrtYd/B.CrtYd.  GetBoundingBox() is used later, so all these shape types
    are handled with the same interval code.
    """
    out = []
    try:
        footprints = list(board.GetFootprints())
    except Exception:
        footprints = []
    for fp in footprints:
        out.extend(_call_first(fp, (
            "GraphicalItems",
            "GetGraphicalItems",
            "GraphicItems",
            "Drawings",
            "GetDrawings",
        )))
    return out


def get_all_courtyard_graphics(board):
    # Board drawings + graphics embedded in footprints.
    return get_all_drawings(board) + get_all_footprint_graphics(board)


def union_bbox_xy(boxes):
    valid = [b for b in boxes if b is not None]
    if not valid:
        return None
    return (
        min(b[0] for b in valid),
        min(b[1] for b in valid),
        max(b[2] for b in valid),
        max(b[3] for b in valid),
    )


def get_courtyard_keepout_boxes(board):
    """Return F.CrtYd/B.CrtYd keepout boxes.

    Important: a component courtyard is a *closed keepout area*.  In real
    libraries it may be drawn as separate lines, rectangles, arcs or circles.
    If we only test those graphics as thin outlines, ShieldingCan can still be
    generated inside the courtyard.  Therefore each footprint's courtyard
    graphics are converted to a filled bounding keepout box.  Board-level
    courtyard drawings are also included individually.
    """
    fcrtyd = get_layer_by_name(board, "F.CrtYd", None)
    bcrtyd = get_layer_by_name(board, "B.CrtYd", None)
    courtyard_layers = set(x for x in (fcrtyd, bcrtyd) if x is not None)
    boxes = []

    # Board-level courtyard shapes.  If the user draws a rectangle/circle/arc
    # directly on F.CrtYd/B.CrtYd, treat its whole bbox as keepout.
    for d in get_all_drawings(board):
        try:
            layer = d.GetLayer()
        except Exception:
            layer = None
        if layer in courtyard_layers:
            b = bbox_xy(item_bbox(d))
            if b is not None:
                boxes.append(b)

    # Footprint courtyard outlines: union all courtyard graphics per footprint
    # and treat the result as a filled component keepout area.
    try:
        footprints = list(board.GetFootprints())
    except Exception:
        footprints = []
    for fp in footprints:
        per_fp = []
        for g in _call_first(fp, (
            "GraphicalItems",
            "GetGraphicalItems",
            "GraphicItems",
            "Drawings",
            "GetDrawings",
        )):
            try:
                layer = g.GetLayer()
            except Exception:
                layer = None
            if layer in courtyard_layers:
                b = bbox_xy(item_bbox(g))
                if b is not None:
                    per_fp.append(b)
        u = union_bbox_xy(per_fp)
        if u is not None:
            boxes.append(u)

    return boxes


def is_collision_with_snapshot(p, radius, tracks_vias, pads):
    for item in tracks_vias:
        if bbox_intersects_circle(item_bbox(item), p, radius):
            return True
    for pad in pads:
        if bbox_intersects_circle(item_bbox(pad), p, radius):
            return True
    return False


def side_points(a, b, desired_pitch, stagger_offset=0.0):
    length = dist(a, b)
    if length <= 0:
        return [], 0, 0
    intervals = max(1, int(round(length / desired_pitch)))
    real_pitch = length / intervals
    ux = (b[0] - a[0]) / length
    uy = (b[1] - a[1]) / length
    pts = []
    # Always include corners.
    pts.append(a)
    pts.append(b)
    # Interior points may be shifted by stagger_offset.
    i = 1
    while True:
        t = i * real_pitch + stagger_offset
        if t >= length:
            break
        if t > 0:
            pts.append((a[0] + ux * t, a[1] + uy * t))
        i += 1
    return pts, real_pitch, intervals


def unique_points(points):
    seen = set()
    out = []
    for p in points:
        key = (int(round(p[0])), int(round(p[1])))
        if key not in seen:
            seen.add(key)
            out.append(p)
    return out


def merge_close_points(points, min_dist):
    pts = list(points)
    changed = True
    while changed:
        changed = False
        out = []
        used = [False] * len(pts)
        for i, p in enumerate(pts):
            if used[i]:
                continue
            cluster = [p]
            used[i] = True
            for j in range(i + 1, len(pts)):
                if used[j]:
                    continue
                if dist(p, pts[j]) < min_dist:
                    cluster.append(pts[j])
                    used[j] = True
                    changed = True
            if len(cluster) == 1:
                out.append(cluster[0])
            else:
                out.append((sum(q[0] for q in cluster) / len(cluster), sum(q[1] for q in cluster) / len(cluster)))
        pts = out
    return pts


def normalize_intervals(intervals, length):
    if not intervals:
        return []
    clipped = []
    for a, b in intervals:
        a = max(0, min(length, a)); b = max(0, min(length, b))
        if b > a:
            clipped.append((a, b))
    if not clipped:
        return []
    clipped.sort()
    merged = [clipped[0]]
    for a, b in clipped[1:]:
        la, lb = merged[-1]
        if a <= lb:
            merged[-1] = (la, max(lb, b))
        else:
            merged.append((a, b))
    return merged


def invert_intervals(blocked, length):
    blocked = normalize_intervals(blocked, length)
    allowed = []
    cur = 0
    for a, b in blocked:
        if a > cur:
            allowed.append((cur, a))
        cur = max(cur, b)
    if cur < length:
        allowed.append((cur, length))
    return allowed


def interval_contains(intervals, t, margin=0):
    for a, b in intervals:
        if t >= a + margin and t <= b - margin:
            return True
    return False


def point_allowed_on_side(p, a, b, allowed, via_radius):
    """
    Check if a via center is inside a real mask segment.

    Interior mask ends caused by obstacles require via_radius margin so vias do
    not extend past square break cuts.  Real rectangle endpoints are rounded
    caps, so corner vias at t=0 or t=length are valid when the allowed segment
    reaches that endpoint.
    """
    length = dist(a, b)
    if length <= 0:
        return False

    t = point_to_side_param(p, a, b)

    # Interior part: keep the whole via inside square-cut mask segments.
    if interval_contains(allowed, t, via_radius):
        return True

    # Rounded real-corner caps: allow endpoint/corner via centers.  This fixes
    # missing corner vias caused by applying via_radius margin to t=0/length.
    endpoint_tol = max(2.0, via_radius * 0.20)
    cap_radius = via_radius * 1.20
    for aa, bb in allowed:
        if aa <= endpoint_tol and dist(p, a) <= cap_radius:
            return True
        if bb >= length - endpoint_tol and dist(p, b) <= cap_radius:
            return True
    return False


def point_to_side_param(p, a, b):
    length = dist(a, b)
    if length <= 0:
        return 0
    ux = (b[0] - a[0]) / length
    uy = (b[1] - a[1]) / length
    return (p[0] - a[0]) * ux + (p[1] - a[1]) * uy


def side_point_at(a, b, t):
    length = dist(a, b)
    if length <= 0:
        return a
    ux = (b[0] - a[0]) / length
    uy = (b[1] - a[1]) / length
    return (a[0] + ux * t, a[1] + uy * t)


def bbox_to_block_interval(box, a, b, corridor_half_width, extra):
    """
    Return a blocked interval [t0, t1] on the directed side a->b.

    The obstacle bbox is projected onto the guard side.  The resulting blocked
    span is enlarged by:
      - the requested keepout break margin;
      - the mask half-width along the line direction.

    The mask half-width enlargement is important because a mask opening has real
    width.  Without it, the visual opening can still touch or nearly touch a
    top/bottom track at the cut end.
    """
    bb = bbox_xy(box)
    if bb is None:
        return None

    x0, y0, x1, y1 = bb
    x0, x1 = sorted((x0, x1))
    y0, y1 = sorted((y0, y1))

    length = dist(a, b)
    if length <= 0:
        return None

    dx = (b[0] - a[0]) / length
    dy = (b[1] - a[1]) / length

    # Unit normal to the side.  Used for checking if the bbox touches the
    # solder-mask corridor around this side.
    nx = -dy
    ny = dx

    corners = [(x0, y0), (x0, y1), (x1, y0), (x1, y1)]

    # Perpendicular distances of bbox corners to the infinite side line.
    # If the whole bbox lies outside the corridor on one side, there is no block.
    n_values = [(c[0] - a[0]) * nx + (c[1] - a[1]) * ny for c in corners]
    if max(n_values) < -corridor_half_width or min(n_values) > corridor_half_width:
        return None

    # Projection along the side direction.  This gives the obstacle span on the
    # guard trace path.
    t_values = [(c[0] - a[0]) * dx + (c[1] - a[1]) * dy for c in corners]
    longitudinal_extra = extra + corridor_half_width
    t0 = min(t_values) - longitudinal_extra
    t1 = max(t_values) + longitudinal_extra

    # Ignore obstacles that only exist far before/after the side segment.
    if t1 <= 0 or t0 >= length:
        return None

    return (t0, t1)


def bbox_xy_to_block_interval(bb, a, b, corridor_half_width, extra):
    class _Box:
        pass
    if bb is None:
        return None
    # Reuse bbox_to_block_interval math by providing a tiny adapter with KiCad-like methods.
    x0, y0, x1, y1 = bb
    class BoxAdapter:
        def GetX(self): return x0
        def GetY(self): return y0
        def GetWidth(self): return x1 - x0
        def GetHeight(self): return y1 - y0
    return bbox_to_block_interval(BoxAdapter(), a, b, corridor_half_width, extra)


def build_courtyard_blocked_intervals_for_side(a, b, corridor_half_width, extra, courtyard_keepout_boxes=None):
    """Build blocked intervals only from filled F.CrtYd/B.CrtYd keepout boxes."""
    blocked = []
    length = dist(a, b)
    for bb in (courtyard_keepout_boxes or []):
        iv = bbox_xy_to_block_interval(bb, a, b, corridor_half_width, extra)
        if iv:
            blocked.append(iv)
    return normalize_intervals(blocked, length)


def build_blocked_intervals_for_side(board, a, b, corridor_half_width, extra, snapshot_tracks_vias, snapshot_pads, courtyard_keepout_boxes=None, mode="both"):
    """Build blocked intervals for one guard side.

    mode:
      - "via":     all copper tracks/vias + all pads + courtyard keepout boxes.
      - "f_mask":  only same-side F.Cu obstacles + F-side pads + courtyard boxes.
      - "b_mask":  only same-side B.Cu obstacles + B-side pads + courtyard boxes.
      - "both":    compatibility mode, top/bottom copper + pads + courtyard boxes.

    Zones/polygons are intentionally ignored.  Courtyard boxes are intentionally
    unchanged from v0.2.5: they are filled keepout areas and block both masks and vias.
    """
    blocked = []
    length = dist(a, b)
    target_layer = None
    if mode == "f_mask":
        target_layer = pcbnew.F_Cu
    elif mode == "b_mask":
        target_layer = pcbnew.B_Cu

    for item in snapshot_tracks_vias:
        try:
            layer = item.GetLayer()
        except Exception:
            layer = None

        include = False
        if mode == "via":
            include = is_via_item(item) or is_copper_layer(board, layer)
        elif mode in ("f_mask", "b_mask"):
            # A copper obstacle breaks only the mask on the same external side.
            # Existing vias are visible on both external sides, so they break both masks.
            include = is_via_item(item) or (layer == target_layer)
        else:
            include = is_via_item(item) or layer in (pcbnew.F_Cu, pcbnew.B_Cu)

        if include:
            iv = bbox_to_block_interval(item_bbox(item), a, b, corridor_half_width, extra)
            if iv:
                blocked.append(iv)

    for pad in snapshot_pads:
        include = False
        if mode == "via":
            include = True
        elif mode == "f_mask":
            include = pad_on_layer(pad, pcbnew.F_Cu)
        elif mode == "b_mask":
            include = pad_on_layer(pad, pcbnew.B_Cu)
        else:
            include = True
        if include:
            iv = bbox_to_block_interval(item_bbox(pad), a, b, corridor_half_width, extra)
            if iv:
                blocked.append(iv)

    # Courtyard behavior is unchanged from v0.2.5: filled F/B courtyard areas are
    # complete keepouts for both mask sides and for vias.
    for bb in (courtyard_keepout_boxes or []):
        iv = bbox_xy_to_block_interval(bb, a, b, corridor_half_width, extra)
        if iv:
            blocked.append(iv)

    return normalize_intervals(blocked, length)

def get_settings_path():
    """Return path to JSON settings file.

    Settings are stored next to shieldingcan.py. This is predictable and works
    well for KiCad action plugins installed in the user plugins folder.
    """
    try:
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), SETTINGS_FILE_NAME)
    except Exception:
        return os.path.join(os.getcwd(), SETTINGS_FILE_NAME)


def load_json_settings():
    path = get_settings_path()
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict):
            return data
    except Exception:
        pass
    return {}


def save_json_settings(data):
    path = get_settings_path()
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception:
        return False



class ShieldingCanDialog(wx.Dialog):
    def __init__(self, parent, board):
        super().__init__(parent, title=f"{PLUGIN_NAME} {VERSION}")
        
        icon_path = os.path.join(os.path.dirname(__file__), "shieldingcan.png")
        if os.path.exists(icon_path):
           icon = wx.Icon(icon_path, wx.BITMAP_TYPE_PNG)
           self.SetIcon(icon)
            
        self.board = board
        self.settings = load_json_settings()

        main = wx.BoxSizer(wx.VERTICAL)

        def cfg_read(name, default):
            try:
                return str(self.settings.get(name, default))
            except Exception:
                return default

        units_cfg = cfg_read("units_mm", "mm")
        self.units_mm = str(units_cfg).lower() not in ("0", "mils")

        self.lang = cfg_read("language", "en")
        if self.lang not in TRANSLATIONS:
            self.lang = "en"

        net_names = get_board_net_names(board)
        saved_net = cfg_read("net", "GND")
        if saved_net and saved_net not in net_names:
            net_names.insert(0, saved_net)
        elif not saved_net and net_names:
            saved_net = net_names[0]
        self.net = wx.ComboBox(self, value=saved_net, choices=net_names, style=wx.CB_READONLY)
        self.unit_mm = wx.RadioButton(self, label="mm", style=wx.RB_GROUP)
        self.unit_mils = wx.RadioButton(self, label="mils")
        self.unit_mm.SetValue(self.units_mm)
        self.unit_mils.SetValue(not self.units_mm)

        self.language = wx.Choice(self, choices=list(LANGUAGES.keys()))
        lang_index = 0
        for i, (_name, code) in enumerate(LANGUAGES.items()):
            if code == self.lang:
                lang_index = i
                break
        self.language.SetSelection(lang_index)

        self.via_dia = wx.TextCtrl(self, value=cfg_read("via_dia", "0.60"))
        self.drill = wx.TextCtrl(self, value=cfg_read("drill", "0.30"))
        self.pitch = wx.TextCtrl(self, value=cfg_read("pitch", "1.20"))
        self.rows = wx.SpinCtrl(self, min=1, max=10, initial=int(cfg_read("rows", "3")))
        self.edge_offset = wx.TextCtrl(self, value=cfg_read("edge_offset", "0.50"))
        self.row_spacing = wx.TextCtrl(self, value=cfg_read("row_spacing", "0.80"))
        self.clearance = wx.TextCtrl(self, value=cfg_read("clearance", "0.50"))
        self.mask_extra = wx.TextCtrl(self, value=cfg_read("mask_extra", "0.25"))
        self.keepout_margin = wx.TextCtrl(self, value=cfg_read("keepout_margin", "0.50"))

        # Stored numeric values in JSON are always millimeters.
        # If the user selected mils last time, convert displayed fields now.
        if not self.units_mm:
            for ctrl in (
                self.via_dia, self.drill, self.pitch,
                self.edge_offset, self.row_spacing,
                self.clearance, self.mask_extra, self.keepout_margin
            ):
                try:
                    v_mm = float(ctrl.GetValue().replace(",", "."))
                    ctrl.SetValue(f"{v_mm / 0.0254:.2f}".rstrip("0").rstrip("."))
                except Exception:
                    pass

        self.side = wx.Choice(self, choices=[tr(self.lang, "outside"), tr(self.lang, "inside")])
        self.side.SetSelection(int(cfg_read("side", "0")))
        self.mask_side = wx.Choice(self, choices=[tr(self.lang, "both"), "F.Mask", "B.Mask", tr(self.lang, "none")])
        self.mask_side.SetSelection(int(cfg_read("mask_side", "0")))
        self.stagger_label = wx.StaticText(self, label=tr(self.lang, "staggered_pattern"))
        stagger_label = self.stagger_label
        stagger_label.SetToolTip(tr(self.lang, "tip_staggered_pattern"))
        self.staggered = wx.CheckBox(self, label="")
        self.staggered.SetValue(cfg_read("staggered", "0") == "1")
        self.cleanup = wx.CheckBox(self, label=tr(self.lang, "cleanup"))
        self.cleanup.SetToolTip(tr(self.lang, "tip_cleanup"))
        self.cleanup.SetValue(cfg_read("cleanup", "1") == "1")


        self.unit_fields = []

        def fmt_value(v_mm):
            if self.unit_mm.GetValue():
                return f"{v_mm:.3f}".rstrip("0").rstrip(".")
            mil = v_mm / 0.0254
            return f"{mil:.2f}".rstrip("0").rstrip(".")

        def parse_field(ctrl):
            val = float(ctrl.GetValue().replace(",", "."))
            if self.unit_mm.GetValue():
                return val
            return val * 0.0254

        def convert_units(to_mm):
            fields = [
                self.via_dia, self.drill, self.pitch,
                self.edge_offset, self.row_spacing,
                self.clearance, self.mask_extra,
                self.keepout_margin
            ]
            values_mm = []
            old_mm = not to_mm
            for f in fields:
                try:
                    v = float(f.GetValue().replace(",", "."))
                except Exception:
                    continue
                if old_mm:
                    values_mm.append(v)
                else:
                    values_mm.append(v * 0.0254)

            for f, mmv in zip(fields, values_mm):
                if to_mm:
                    f.SetValue(f"{mmv:.3f}".rstrip("0").rstrip("."))
                else:
                    mil = mmv / 0.0254
                    f.SetValue(f"{mil:.2f}".rstrip("0").rstrip("."))

        self.unit_mm.Bind(wx.EVT_RADIOBUTTON, lambda evt: convert_units(True))
        self.unit_mils.Bind(wx.EVT_RADIOBUTTON, lambda evt: convert_units(False))

        def add_field(grid, label, ctrl, tip=None):
            label_ctrl = wx.StaticText(self, label=label)
            if tip:
                label_ctrl.SetToolTip(tip)
            grid.Add(label_ctrl, 0, wx.ALIGN_CENTER_VERTICAL)
            grid.Add(ctrl, 1, wx.EXPAND)
            return label_ctrl

        self.via_box = wx.StaticBoxSizer(wx.VERTICAL, self, tr(self.lang, "via_settings"))
        via_box = self.via_box
        via_grid = wx.FlexGridSizer(cols=2, hgap=8, vgap=8)
        via_grid.AddGrowableCol(1, 1)
        self.via_labels = {}
        for key, ctrl, tip_key in [
            ("via_diameter", self.via_dia, "tip_via_diameter"),
            ("drill", self.drill, "tip_drill"),
            ("desired_pitch", self.pitch, "tip_desired_pitch"),
            ("rows", self.rows, "tip_rows"),
            ("row_spacing", self.row_spacing, "tip_row_spacing"),
            ("first_row_offset", self.edge_offset, "tip_first_row_offset"),
            ("collision_clearance", self.clearance, "tip_collision_clearance"),
        ]:
            self.via_labels[key] = add_field(
                via_grid, tr(self.lang, key), ctrl, tr(self.lang, tip_key)
            )
        via_box.Add(via_grid, 0, wx.ALL | wx.EXPAND, 8)

        self.mask_box = wx.StaticBoxSizer(wx.VERTICAL, self, tr(self.lang, "mask_settings"))
        mask_box = self.mask_box
        mask_grid = wx.FlexGridSizer(cols=2, hgap=8, vgap=8)
        mask_grid.AddGrowableCol(1, 1)

        self.mask_labels = {}
        for key, ctrl, tip_key in [
            ("mask_side", self.mask_side, "tip_mask_side"),
            ("mask_extra", self.mask_extra, "tip_mask_extra"),
            ("keepout_margin", self.keepout_margin, "tip_keepout_margin"),
        ]:
            self.mask_labels[key] = add_field(
                mask_grid, tr(self.lang, key), ctrl, tr(self.lang, tip_key)
            )

        mask_box.Add(mask_grid, 0, wx.ALL | wx.EXPAND, 8)

        self.mask_labels["build_side"] = add_field(
            mask_grid, tr(self.lang, "build_side"), self.side, tr(self.lang, "tip_build_side")
        )

        main_grid = wx.FlexGridSizer(cols=2, hgap=8, vgap=8)
        main_grid.AddGrowableCol(1, 1)

        self.net_label = add_field(
            main_grid, tr(self.lang, "net_name"), self.net, tr(self.lang, "tip_net_name")
        )

        units_row = wx.BoxSizer(wx.HORIZONTAL)
        self.units_label = wx.StaticText(self, label=tr(self.lang, "units"))
        units_label = self.units_label
        units_label.SetToolTip(tr(self.lang, "tip_units"))
        units_row.Add(units_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 8)
        units_row.Add(self.unit_mm, 0, wx.RIGHT, 10)
        units_row.Add(self.unit_mils, 0)

        language_row = wx.BoxSizer(wx.HORIZONTAL)
        self.language_label = wx.StaticText(self, label=tr(self.lang, "language"))
        language_label = self.language_label
        language_label.SetToolTip(tr(self.lang, "tip_language"))
        language_row.Add(language_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 8)
        language_row.Add(self.language, 1)


        self.info = wx.StaticText(self, label=(tr(self.lang, "info")))
        info = self.info

        btns = self.CreateSeparatedButtonSizer(wx.OK | wx.CANCEL)
        stagger_row = wx.BoxSizer(wx.HORIZONTAL)
        stagger_row.Add(stagger_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 8)
        stagger_row.Add(self.staggered, 0, wx.ALIGN_CENTER_VERTICAL)
        via_box.Add(stagger_row, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 8)

        main.Add(via_box, 0, wx.ALL | wx.EXPAND, 12)
        main.Add(mask_box, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, 12)
        main.Add(main_grid, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, 12)
        main.Add(units_row, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 12)
        main.Add(language_row, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, 12)
        main.Add(self.cleanup, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 12)
        main.Add(info, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 12)
        main.Add(btns, 0, wx.ALL | wx.EXPAND, 12)
        self.language.Bind(wx.EVT_CHOICE, self.on_language_changed)
        self.SetSizer(main)
        main.Fit(self)
        self.SetMinSize(self.GetSize())
        self.Centre()

    def on_language_changed(self, event):
        self.lang = LANGUAGES.get(self.language.GetStringSelection(), "en")
        self.apply_language()

        # Save language immediately, even if the dialog is later cancelled.
        try:
            data = dict(self.settings)
            data["language"] = self.lang
            save_json_settings(data)
            self.settings = data
        except Exception:
            pass

        event.Skip()

    def apply_language(self):
        side_sel = self.side.GetSelection()
        mask_sel = self.mask_side.GetSelection()

        self.via_box.GetStaticBox().SetLabel(tr(self.lang, "via_settings"))
        self.mask_box.GetStaticBox().SetLabel(tr(self.lang, "mask_settings"))

        via_tip_keys = {
            "via_diameter": "tip_via_diameter",
            "drill": "tip_drill",
            "desired_pitch": "tip_desired_pitch",
            "rows": "tip_rows",
            "row_spacing": "tip_row_spacing",
            "first_row_offset": "tip_first_row_offset",
            "collision_clearance": "tip_collision_clearance",
        }
        for key, ctrl in self.via_labels.items():
            ctrl.SetLabel(tr(self.lang, key))
            ctrl.SetToolTip(tr(self.lang, via_tip_keys[key]))

        mask_tip_keys = {
            "mask_side": "tip_mask_side",
            "mask_extra": "tip_mask_extra",
            "keepout_margin": "tip_keepout_margin",
            "build_side": "tip_build_side",
        }
        for key, ctrl in self.mask_labels.items():
            ctrl.SetLabel(tr(self.lang, key))
            ctrl.SetToolTip(tr(self.lang, mask_tip_keys[key]))

        self.net_label.SetLabel(tr(self.lang, "net_name"))
        self.net_label.SetToolTip(tr(self.lang, "tip_net_name"))

        self.stagger_label.SetLabel(tr(self.lang, "staggered_pattern"))
        self.stagger_label.SetToolTip(tr(self.lang, "tip_staggered_pattern"))

        self.units_label.SetLabel(tr(self.lang, "units"))
        self.units_label.SetToolTip(tr(self.lang, "tip_units"))

        self.language_label.SetLabel(tr(self.lang, "language"))
        self.language_label.SetToolTip(tr(self.lang, "tip_language"))

        self.cleanup.SetLabel(tr(self.lang, "cleanup"))
        self.cleanup.SetToolTip(tr(self.lang, "tip_cleanup"))
        self.info.SetLabel(tr(self.lang, "info"))

        self.side.SetItems([tr(self.lang, "outside"), tr(self.lang, "inside")])
        self.side.SetSelection(0 if side_sel < 0 else min(side_sel, 1))

        self.mask_side.SetItems([tr(self.lang, "both"), "F.Mask", "B.Mask", tr(self.lang, "none")])
        self.mask_side.SetSelection(0 if mask_sel < 0 else min(mask_sel, 3))

        self.Layout()
        sizer = self.GetSizer()
        if sizer is not None:
            sizer.Fit(self)
        self.SetMinSize(self.GetSize())
        self.CentreOnParent()

    def read_float(self, ctrl, name):
        try:
            val = float(ctrl.GetValue().replace(",", "."))
            if self.unit_mils.GetValue():
                val *= 0.0254
        except Exception:
            raise ValueError(f"Invalid value for {name}")
        if val < 0:
            raise ValueError(f"{name} must be >= 0")
        return val

    def values(self):
        cfg = {
            "net": self.net.GetValue().strip(),
            "via_dia": self.read_float(self.via_dia, "via diameter"),
            "drill": self.read_float(self.drill, "drill"),
            "pitch": self.read_float(self.pitch, "pitch"),
            "rows": int(self.rows.GetValue()),
            "edge_offset": self.read_float(self.edge_offset, "first row offset"),
            "row_spacing": self.read_float(self.row_spacing, "row spacing"),
            "clearance": self.read_float(self.clearance, "collision clearance"),
            "mask_extra": self.read_float(self.mask_extra, "mask extra"),
            "keepout_margin": self.read_float(self.keepout_margin, "keepout break margin"),
            "outside": self.side.GetSelection() == 0,
            "side_index": self.side.GetSelection(),
            "mask_side": (
                "Both" if self.mask_side.GetSelection() == 0 else
                "F.Mask" if self.mask_side.GetSelection() == 1 else
                "B.Mask" if self.mask_side.GetSelection() == 2 else
                "None"
            ),
            "mask_side_index": self.mask_side.GetSelection(),
            "staggered": self.staggered.GetValue(),
            "cleanup": self.cleanup.GetValue(),
            "language": LANGUAGES.get(self.language.GetStringSelection(), "en"),
        }
        self.save(cfg)
        return cfg

    def save(self, cfg):
        try:
            data = {}
            data["net"] = cfg["net"]
            for key in ("via_dia", "drill", "pitch", "edge_offset", "row_spacing", "clearance", "mask_extra", "keepout_margin"):
                data[key] = cfg[key]
            data["rows"] = cfg["rows"]
            data["side"] = cfg["side_index"]
            data["mask_side"] = cfg["mask_side_index"]
            data["staggered"] = 1 if cfg["staggered"] else 0
            data["cleanup"] = 1 if cfg["cleanup"] else 0
            data["units_mm"] = "mm" if self.unit_mm.GetValue() else "mils"
            data["language"] = LANGUAGES.get(self.language.GetStringSelection(), "en")
            save_json_settings(data)
        except Exception:
            pass


class ShieldingCanPlugin(pcbnew.ActionPlugin):
    def defaults(self):
        self.name = PLUGIN_NAME
        self.category = "Modify PCB"
        self.description = "Generate rectangle-based via guard trace with solder-mask opening"
        self.show_toolbar_button = True
        self.icon_file_name = os.path.join(os.path.dirname(__file__), "shieldingcan.png")

    def Run(self):
        board = pcbnew.GetBoard()
        dlg = ShieldingCanDialog(None, board)
        try:
            if dlg.ShowModal() != wx.ID_OK:
                return
            cfg = dlg.values()
        except Exception as e:
            wx.MessageBox(str(e), PLUGIN_NAME, wx.OK | wx.ICON_ERROR)
            return
        finally:
            dlg.Destroy()
        try:
            report = self.build(board, cfg)
            try:
                pcbnew.Refresh()
            except Exception:
                pass
            wx.MessageBox(report, PLUGIN_NAME, wx.OK | wx.ICON_INFORMATION)
        except Exception as e:
            wx.MessageBox(str(e), PLUGIN_NAME, wx.OK | wx.ICON_ERROR)

    def find_selected_rectangle(self, board):
        selected = []
        user_drawings = get_layer_by_name(board, "User.Drawings", None)
        for d in get_all_drawings(board):
            if item_is_selected(d) and is_rect_shape(d):
                selected.append(d)
        if len(selected) != 1:
            raise RuntimeError("Select exactly one graphic rectangle on User.Drawings, then run ShieldingCan.")
        rect = selected[0]
        if user_drawings is not None and rect.GetLayer() != user_drawings:
            raise RuntimeError("The selected source rectangle must be on User.Drawings.")
        return rect

    def build(self, board, cfg):
        rect = self.find_selected_rectangle(board)
        if cfg["pitch"] <= 0:
            raise RuntimeError("Desired via pitch must be greater than zero.")
        if cfg["drill"] > cfg["via_dia"]:
            raise RuntimeError("Drill must not be larger than via diameter.")
        net = get_net_by_name(board, cfg["net"])
        if cfg["net"] and net is None:
            raise RuntimeError(f"Net '{cfg['net']}' was not found in this board.")

        if cfg["cleanup"]:
            delete_guard_trace_groups(board)

        # Snapshot existing objects AFTER cleanup, before adding new guard trace.
        snapshot_tracks_vias = get_all_tracks_and_vias(board)
        snapshot_pads = get_all_pads(board)
        courtyard_keepout_boxes = get_courtyard_keepout_boxes(board)

        group = create_group(board)
        x0, y0, x1, y1 = get_rect_bounds(rect)
        sign = 1 if cfg["outside"] else -1

        via_dia = iu(cfg["via_dia"])
        drill = iu(cfg["drill"])
        desired_pitch = iu(cfg["pitch"])
        edge_offset = iu(cfg["edge_offset"])
        row_spacing = iu(cfg["row_spacing"])
        clearance = iu(cfg["clearance"])
        keepout_margin = iu(cfg["keepout_margin"])
        collision_radius = via_dia // 2 + clearance
        mask_width = via_dia + 2 * iu(cfg["mask_extra"])
        mask_half = mask_width / 2.0

        mask_layers = []
        if cfg["mask_side"] in ("Both", "F.Mask"):
            mask_layers.append(pcbnew.F_Mask)
        if cfg["mask_side"] in ("Both", "B.Mask"):
            mask_layers.append(pcbnew.B_Mask)

        total_candidates = 0
        placed = 0
        skipped_collision = 0
        skipped_keepout = 0
        mask_segments = 0
        pitch_reports = []

        all_points = []
        allowed_by_side = []

        for row in range(cfg["rows"]):
            off = sign * (edge_offset + row * row_spacing)
            rx0 = x0 - off; ry0 = y0 - off; rx1 = x1 + off; ry1 = y1 + off
            if rx1 <= rx0 or ry1 <= ry0:
                continue
            corners = [(rx0, ry0), (rx1, ry0), (rx1, ry1), (rx0, ry1)]
            sides = [(corners[0], corners[1]), (corners[1], corners[2]), (corners[2], corners[3]), (corners[3], corners[0])]
            row_stagger = (row % 2) == 1 and cfg["staggered"]

            for si, (a, b) in enumerate(sides):
                length = dist(a, b)
                # Via keepout and mask keepout use different rules:
                # - vias are blocked by obstacle half-width + via radius + Collision clearance
                # - mask openings are blocked by obstacle half-width + mask half-width + Keepout break margin
                via_blocked = build_blocked_intervals_for_side(board, a, b, via_dia / 2.0, clearance, snapshot_tracks_vias, snapshot_pads, courtyard_keepout_boxes, mode="via")

                # Courtyard keepouts use the same via spacing rule as copper obstacles:
                # obstacle boundary + via radius + Collision clearance.
                # This keeps the visual via distance near Courtyard equal to the
                # distance near tracks/pads.
                courtyard_via_blocked = build_courtyard_blocked_intervals_for_side(
                    a, b,
                    via_dia / 2.0,
                    clearance + iu(COURTYARD_VIA_EXTRA_MARGIN_MM),
                    courtyard_keepout_boxes
                )
                via_blocked = normalize_intervals(via_blocked + courtyard_via_blocked, length)
                via_allowed = invert_intervals(via_blocked, length)
                allowed_by_side.append((a, b, via_allowed))

                f_allowed = None
                b_allowed = None
                if pcbnew.F_Mask in mask_layers:
                    f_blocked = build_blocked_intervals_for_side(board, a, b, mask_half, keepout_margin, snapshot_tracks_vias, snapshot_pads, courtyard_keepout_boxes, mode="f_mask")
                    f_allowed = invert_intervals(f_blocked, length)
                if pcbnew.B_Mask in mask_layers:
                    b_blocked = build_blocked_intervals_for_side(board, a, b, mask_half, keepout_margin, snapshot_tracks_vias, snapshot_pads, courtyard_keepout_boxes, mode="b_mask")
                    b_allowed = invert_intervals(b_blocked, length)

                # Draw each mask side with its own same-side obstacle intervals.
                # F.Cu cuts only F.Mask; B.Cu cuts only B.Mask; inner copper cuts vias only.
                for layer, allowed in ((pcbnew.F_Mask, f_allowed), (pcbnew.B_Mask, b_allowed)):
                    if allowed is None:
                        continue
                    for aa, bb in allowed:
                        # Very short segments do not create useful mask opening and cause visual clutter.
                        if bb - aa <= mask_width:
                            continue
                        p0 = side_point_at(a, b, aa)
                        p1 = side_point_at(a, b, bb)
                        # Rounded mask caps only at real rectangle corners.
                        # Internal ends are obstacle breaks and must stay 90-degree square.
                        eps = max(2, int(mask_width * 0.02))
                        round_start = aa <= eps
                        round_end = bb >= length - eps
                        seg_items = make_mask_mixed_cap_segment(board, layer, p0, p1, mask_width, round_start, round_end)
                        for seg in seg_items:
                            group_add(group, seg)
                        mask_segments += 1

                # Fill each allowed via segment independently.
                # Do not place endpoint vias directly at the beginning/end of an
                # allowed segment created by a keepout (especially Courtyard).
                # Real rectangle corners are still included because their allowed
                # segment starts at 0 or ends at side length.
                segment_reports = []
                endpoint_margin = via_dia / 2.0 + clearance

                for va, vb in via_allowed:
                    seg_len = vb - va
                    if seg_len <= 0:
                        continue

                    intervals = max(1, int(round(seg_len / desired_pitch)))
                    real_pitch = seg_len / intervals
                    segment_reports.append(f"{mm(real_pitch):.3f}")

                    local_ts = []

                    # Include only real side endpoints, not keepout-cut endpoints.
                    if va <= max(2, int(via_dia * 0.02)):
                        local_ts.append(va)
                    else:
                        first = va + endpoint_margin
                        if first < vb:
                            local_ts.append(first)

                    if vb >= length - max(2, int(via_dia * 0.02)):
                        local_ts.append(vb)
                    else:
                        last = vb - endpoint_margin
                        if last > va:
                            local_ts.append(last)

                    # Interior points, fitted to this allowed segment.
                    stagger_offset = real_pitch / 2.0 if row_stagger else 0.0
                    for ii in range(1, intervals):
                        tt = va + ii * real_pitch + stagger_offset
                        if tt > va + endpoint_margin and tt < vb - endpoint_margin:
                            local_ts.append(tt)

                    for tt in local_ts:
                        p = side_point_at(a, b, tt)
                        all_points.append((p, a, b, via_allowed, tt))

                if segment_reports:
                    pitch_reports.append(f"R{row+1} S{si+1}: " + "/".join(segment_reports) + " mm")
                else:
                    pitch_reports.append(f"R{row+1} S{si+1}: no allowed via segment")

        # Merge points that are too close, mainly for staggered corner conflicts.
        raw_points = [p for (p, _a, _b, _allowed, _t) in all_points]
        merged_points = unique_points(merge_close_points(raw_points, via_dia * 0.95))

        for p in merged_points:
            total_candidates += 1
            # A via may be created only if it fits inside at least one actual mask segment.
            inside_mask = False
            for a, b, allowed in allowed_by_side:
                # It must lie near this side line and inside an allowed interval.
                length = dist(a, b)
                if length <= 0:
                    continue
                horizontal = abs(a[1] - b[1]) <= abs(a[0] - b[0])
                if horizontal:
                    if abs(p[1] - a[1]) > 1:
                        continue
                else:
                    if abs(p[0] - a[0]) > 1:
                        continue
                # via_allowed already contains via radius + clearance, so do
                # not shrink the interval once more by via radius here.
                if point_allowed_on_side(p, a, b, allowed, 0):
                    inside_mask = True
                    break
            if not inside_mask:
                skipped_keepout += 1
                continue
            if is_collision_with_snapshot(p, collision_radius, snapshot_tracks_vias, snapshot_pads):
                skipped_collision += 1
                continue
            via = make_via(board, p, via_dia, drill, net)
            group_add(group, via)
            placed += 1

        lang = cfg.get("language", "en")
        return (
            f"ShieldingCan {VERSION} {tr(lang, 'report_finished')}\n\n"
            f"{tr(lang, 'report_source_layer')}: {get_layer_name(board, rect.GetLayer())}\n"
            f"{tr(lang, 'report_candidates')}: {total_candidates}\n"
            f"{tr(lang, 'report_placed_vias')}: {placed}\n"
            f"{tr(lang, 'report_skipped_keepout')}: {skipped_keepout}\n"
            f"{tr(lang, 'report_skipped_collision')}: {skipped_collision}\n"
            f"{tr(lang, 'report_mask_segments')}: {mask_segments}\n"
            f"{tr(lang, 'report_courtyard_boxes')}: {len(courtyard_keepout_boxes)}\n"
            f"{tr(lang, 'report_zones')}: {tr(lang, 'report_ignored')}\n\n"
            f"{tr(lang, 'report_adjusted_pitch')}:\n" + "\n".join(pitch_reports[:16]) +
            ("\n..." if len(pitch_reports) > 16 else "")
        )


ShieldingCanPlugin().register()
