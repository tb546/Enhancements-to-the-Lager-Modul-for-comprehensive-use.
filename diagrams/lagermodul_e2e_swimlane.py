"""Swimlane-Prozessflow Lagermodul (End-to-End) als SVG."""
import html, sys

COLW, GAP = 230, 56
STEP = COLW + GAP
LANE_LABEL_W = 160
TOP = 120          # Platz für Titel + Phasen
PAD = 24
FONT = "Segoe UI, Helvetica, Arial, sans-serif"

LANES = [
    ("LV",  "Lager-\nverantwortliche:r\n/ Büro", 190),
    ("KA",  "Kalkulator:in /\nServiceberater:in", 200),
    ("WM",  "Werkstatt-\nMitarbeiter:in", 160),
    ("SYS", "System\nPDR.cloud", 200),
]
PHASES = [  # (label, col_from, col_to)
    ("1 · Stammdaten", 0, 0),
    ("2 · Kalkulation & Entnahme", 1, 3),
    ("3 · Bestellung", 4, 6),
    ("4 · Wareneingang", 7, 7),
    ("5 · Pflege & Inventur", 8, 9),
]
STYLE = {
    "new":      ("#E6F4EA", "#2E7D32", "#1B1B1B", ""),
    "existing": ("#EEF2F7", "#64748B", "#1B1B1B", ""),
    "core":     ("#1E3A5F", "#1E3A5F", "#FFFFFF", ""),
}
# id: (lane, col, colspan, text, style)
NODES = {
    "L1": ("LV", 0, 1, "Artikel anlegen\nStammdaten, Gebindegröße,\nFiliale, Lagerort, UPE/VK\nArchiv-Check (E6)", "new"),
    "K1": ("KA", 1, 1, "Vorgang → Kalkulation\nfrei oder DAT/AX (E9)", "existing"),
    "K2": ("KA", 2, 1, "„Lagerteil hinzufügen“\nFilialfilter (E8)\nMehrfachauswahl (E10)\nSpalten (E14)", "new"),
    "K3": ("KA", 3, 1, "Position angelegt\nUPE + VK vorbelegt,\nPreis prüfen (E5)", "new"),
    "W1": ("WM", 3, 1, "Verbrauchsmaterial\nentnehmen\n(Suche / QR-Scan)", "existing"),
    "S1": ("SYS", 2, 2, "Zentrale Bestandsbuchung\natomar · Bestand ≥ 0 (E3)\nInventur-Warnung (E12)\nBestandslog mit Vorgangsbezug", "core"),
    "K4": ("KA", 4, 1, "„Bestellungen“\nanklicken", "existing"),
    "S2": ("SYS", 4, 1, "Lagerabgleich\nArt.-Nr. + alt. Nr.\nnur Vorgangs-Filiale (E8)", "new"),
    "K5": ("KA", 5, 1, "Pop-up Lagertreffer\n„Nein“ vorausgewählt (E11)\nTeilbestand: X aus Lager,\nRest bestellen (E4)", "new"),
    "S3": ("SYS", 5, 1, "Positions-Split\n+ Entnahme\n(zentrale Buchung)", "new"),
    "L2": ("LV", 6, 1, "Warenkorb /\nNachbestellung\n(Mindestbestand)", "existing"),
    "K6": ("KA", 6, 1, "Bestellung\nversenden", "existing"),
    "L4": ("LV", 7, 1, "Wareneingang\n1 = +1 Gebinde (E13)\nLagerort zuweisen", "existing"),
    "S4": ("SYS", 7, 1, "Zugangsbuchung\n(zentrale Buchung)", "existing"),
    "L5": ("LV", 8, 1, "Inventur\nanlegen / abschließen", "existing"),
    "S5": ("SYS", 8, 1, "Korrekturbuchung\n(zentrale Buchung)", "existing"),
    "L6": ("LV", 9, 1, "Artikel „Löschen“\n= archivieren (E1)\nArchiv: wiederherstellen\noder endgültig löschen (E15)\nblockiert bei offener Inventur", "new"),
    "S6": ("SYS", 9, 1, "Archiv / Löschung\nSoft Delete: ausgeblendet\nEndgültig: Stammsatz weg,\nBelege + Bestandslog bleiben", "new"),
}
# (from, to, label, dashed)
EDGES = [
    ("K1", "K2", "", False),
    ("K2", "K3", "", False),
    ("K2", "S1", "Entnahme", False),
    ("W1", "S1", "Entnahme", False),
    ("K3", "K4", "", False),
    ("K4", "S2", "Abgleich", False),
    ("S2", "K5", "Treffer", False),
    ("K5", "S3", "Nein / Teilbestand", False),
    ("K5", "K6", "Ja / Rest", False),
    ("L2", "K6", "Lieferanten-\nbestellung", False),
    ("K6", "L4", "Lieferung", False),
    ("L4", "S4", "Zugang", False),
    ("L5", "S5", "Differenzen", False),
    ("L6", "S6", "archivieren /\nendgültig löschen", False),
    ("L1", "K2", "Artikel verfügbar", True),
]

NCOLS = 10
W = LANE_LABEL_W + PAD + NCOLS * STEP - GAP + PAD
lane_y, y = {}, TOP
for key, _, h in LANES:
    lane_y[key] = (y, h)
    y += h
H_LANES = y
FOOT = 92
H = H_LANES + FOOT

def col_x(c):
    return LANE_LABEL_W + PAD + c * STEP

LINE_H = 17
def node_box(nid):
    lane, c, span, text, _ = NODES[nid]
    ly, lh = lane_y[lane]
    w = span * COLW + (span - 1) * GAP
    lines = text.split("\n")
    h = max(64, len(lines) * LINE_H + 26)
    x = col_x(c)
    yy = ly + (lh - h) / 2
    return x, yy, w, h

out = []
add = out.append
add(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="{FONT}">')
add('<defs><marker id="ar" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
    '<path d="M0,0 L10,5 L0,10 z" fill="#334155"/></marker></defs>')
add(f'<rect width="{W}" height="{H}" fill="#FFFFFF"/>')
add(f'<text x="{PAD}" y="40" font-size="24" font-weight="700" fill="#0F172A">Lagermodul PDR.cloud – End-to-End-Prozess (Soll)</text>')
add(f'<text x="{PAD}" y="64" font-size="14" fill="#475569">Epic DEV-1722 · Basis PCD-162 · Entscheidungen E1–E15 · Stand 19.11.2026</text>')

# Phasen-Header
for label, c0, c1 in PHASES:
    x0 = col_x(c0) - GAP / 2 + 4
    x1 = col_x(c1) + COLW + GAP / 2 - 4
    add(f'<rect x="{x0}" y="{TOP-38}" width="{x1-x0}" height="28" rx="6" fill="#F1F5F9" stroke="#CBD5E1"/>')
    add(f'<text x="{(x0+x1)/2}" y="{TOP-19}" font-size="14" font-weight="600" fill="#334155" text-anchor="middle">{html.escape(label)}</text>')
    if c0 > 0:
        add(f'<line x1="{x0-4}" y1="{TOP}" x2="{x0-4}" y2="{H_LANES}" stroke="#E2E8F0" stroke-dasharray="4 4"/>')

# Lanes
fills = ["#FBFCFE", "#F7F9FC"]
for i, (key, label, h) in enumerate(LANES):
    ly, lh = lane_y[key]
    add(f'<rect x="0" y="{ly}" width="{W}" height="{lh}" fill="{fills[i%2]}" stroke="#CBD5E1"/>')
    add(f'<rect x="0" y="{ly}" width="{LANE_LABEL_W}" height="{lh}" fill="#E2E8F0" stroke="#CBD5E1"/>')
    ls = label.split("\n")
    for j, t in enumerate(ls):
        ty = ly + lh / 2 + (j - (len(ls) - 1) / 2) * 19 + 5
        add(f'<text x="{LANE_LABEL_W/2}" y="{ty}" font-size="14" font-weight="700" fill="#1E293B" text-anchor="middle">{html.escape(t)}</text>')

# Kanten (vor Knoten zeichnen)
def anchor(nid, side, xref=None):
    x, y, w, h = node_box(nid)
    if side == "r": return x + w, y + h / 2
    if side == "l": return x, y + h / 2
    cx = xref if xref is not None else x + w / 2
    if side == "t": return cx, y
    if side == "b": return cx, y + h

def label_box(x, y, text):
    ls = text.split("\n")
    wmax = max(len(t) for t in ls) * 7.2 + 12
    hh = len(ls) * 15 + 6
    add(f'<rect x="{x-wmax/2}" y="{y-hh/2}" width="{wmax}" height="{hh}" rx="4" fill="#FFFFFF" stroke="#CBD5E1"/>')
    for j, t in enumerate(ls):
        add(f'<text x="{x}" y="{y-hh/2+15+j*15-3}" font-size="12" fill="#334155" text-anchor="middle">{html.escape(t)}</text>')

for a, b, lab, dashed in EDGES:
    la, ca, sa = NODES[a][0], NODES[a][1], NODES[a][2]
    lb, cb, sb = NODES[b][0], NODES[b][1], NODES[b][2]
    dash = ' stroke-dasharray="6 5"' if dashed else ""
    ax, ay, aw, ah = node_box(a)
    bx, by, bw, bh = node_box(b)
    if la == lb:  # horizontal
        x1, y1 = anchor(a, "r"); x2, y2 = anchor(b, "l")
        d = f"M{x1},{y1} L{x2},{y2}"
        lx, lyy = (x1 + x2) / 2, y1 - 14
    elif ca <= cb < ca + sa or cb <= ca < cb + sb:  # vertikal (überlappende Spalte)
        cx = col_x(max(ca, cb)) + COLW / 2
        if ay < by:
            x1, y1 = cx, ay + ah; x2, y2 = cx, by
        else:
            x1, y1 = cx, ay; x2, y2 = cx, by + bh
        d = f"M{x1},{y1} L{x2},{y2}"
        lx, lyy = cx, (y1 + y2) / 2
    else:  # Ellbogen durch die Spaltenlücke vor dem Ziel
        x1, y1 = anchor(a, "r")
        x2, y2 = anchor(b, "l")
        mx = col_x(cb) - GAP / 2
        d = f"M{x1},{y1} L{mx},{y1} L{mx},{y2} L{x2},{y2}"
        lx, lyy = mx, (y1 + y2) / 2
    add(f'<path d="{d}" fill="none" stroke="#334155" stroke-width="1.6"{dash} marker-end="url(#ar)"/>')
    if lab:
        label_box(lx, lyy, lab)

# Knoten
for nid, (lane, c, span, text, st) in NODES.items():
    x, y, w, h = node_box(nid)
    fill, stroke, color, _ = STYLE[st]
    rx = 22 if st == "core" else 8
    add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="1.6"/>')
    ls = text.split("\n")
    for j, t in enumerate(ls):
        ty = y + h / 2 + (j - (len(ls) - 1) / 2) * LINE_H + 5
        fw = "700" if j == 0 else "400"
        add(f'<text x="{x+w/2}" y="{ty}" font-size="13.5" font-weight="{fw}" fill="{color}" text-anchor="middle">{html.escape(t)}</text>')

# Legende / Fußzeile
fy = H_LANES + 30
items = [("new", "Neu / geändert"), ("existing", "Besteht heute"), ("core", "Zentrale Buchungsfunktion")]
x = PAD
for st, lab in items:
    fill, stroke, _, _ = STYLE[st]
    add(f'<rect x="{x}" y="{fy-14}" width="26" height="18" rx="4" fill="{fill}" stroke="{stroke}"/>')
    add(f'<text x="{x+34}" y="{fy}" font-size="13" fill="#334155">{lab}</text>')
    x += 34 + len(lab) * 7.5 + 30
add(f'<line x1="{x}" y1="{fy-5}" x2="{x+34}" y2="{fy-5}" stroke="#334155" stroke-width="1.6" stroke-dasharray="6 5"/>')
add(f'<text x="{x+42}" y="{fy}" font-size="13" fill="#334155">Datenbezug (kein Prozessschritt)</text>')
add(f'<text x="{PAD}" y="{fy+32}" font-size="13" fill="#475569">Alle Bestandsänderungen (Entnahme, Split, Zugang, Korrektur, Archivierung) laufen über die zentrale Bestandsbuchung – '
    'gleiche Regeln überall, Ansatzpunkt für Folge-Ticket F2 (Mindestbestand-Alarm).</text>')
add("</svg>")
open(sys.argv[1], "w").write("\n".join(out))
print(W, H)
