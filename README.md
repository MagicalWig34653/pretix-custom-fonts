# Pretix Custom Fonts Plugin

Dieses Plugin erweitert Pretix um eine Organizer-weite Verwaltung eigener Schriftarten und stellt diese für PDF- und Theme-Nutzung bereit.

## Kompatibilität

- Pretix `>= 4.0.0`
- Schriftdateien: `.ttf` und `.otf`

## Funktionsumfang

- Organizer-weite Font-Verwaltung im Control-Interface (`Custom Fonts`)
- Upload, Bearbeiten und Löschen von Schriftarten pro Font-Familie und Stil
- Mehrere Stil-Varianten pro Familie:
  `regular`, `italic`, `bold`, `bolditalic`, `thin`, `thinitalic`, `extralight`, `light`, `medium`, `italicbold`, `black`
- Eindeutigkeit je Organizer/Familie/Stil (keine Dubletten)
- Automatische Zuordnung auf Pretix-Slots (`regular`, `bold`, `italic`, `bolditalic`) über Prioritätsregeln
- Kennzeichnung, ob eine Familie vollständig nutzbar ist (mindestens `regular`)
- PDF-Kompatibilitätsprüfung:
  OTF-Dateien mit PostScript/CFF-Outlines (`OTTO`-Header) werden für PDF als nicht kompatibel markiert
- Bereitstellung für Webfonts/Themes über `register_fonts` inkl. statischer Materialisierung

## Installation (lokal aus diesem Repository)

Die Python-Paketquelle liegt in `pretix_custom_fonts/`:

```bash
pip install ./pretix_custom_fonts
python -m pretix migrate
python -m pretix rebuild
```

Danach den Pretix-Prozess neu starten.

## Nutzung im Pretix-Backend

1. Organizer öffnen
2. Navigation: `Custom Fonts`
3. Neue Schrift hochladen (Familienname, Stil, Datei)
4. Optional weitere Stile derselben Familie hochladen
5. In der Liste prüfen:
   - `PDF compatible` (Ja/Nein)
   - Slot-Mapping auf Pretix-Stile
   - Familienstatus `Active` oder `Incomplete`

Hinweis: Eine Familie ist erst vollständig nutzbar, wenn ein `regular`-Stil vorhanden ist.

## Technische Hinweise

- Speicherung der Dateien unter: `pub/<organizer>/fonts/<datei>`
- Hook für Font-Bereitstellung: `pretix.plugins.ticketoutputpdf.signals.register_fonts`
- Falls möglich, werden Fonts zusätzlich nach `pretix_custom_fonts/fonts/<organizer>/<datei>` in ein Static-Verzeichnis materialisiert
- Wenn Materialisierung nicht möglich ist, wird auf direkte Medien-URLs zurückgefallen

## Docker

Im Repository ist ein `Dockerfile` enthalten, das auf `pretix/standalone:stable` basiert, das Plugin installiert und anschließend `pretix rebuild` ausführt.

Beispiel:

```bash
docker build -t pretix-custom-fonts:local .
```

In der CI wird ein Image nach `ghcr.io/magicalwig34653/pretix-modify-custom-fonts` veröffentlicht (Tags u.a. `latest`, `stable`).

## Lizenz

Apache License 2.0
