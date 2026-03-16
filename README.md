# Pretix Custom Fonts Plugin

Dieses Plugin ermöglicht es, eigene Schriftarten (TTF/OTF) in Pretix hochzuladen und für PDF-Ausgaben (z.B. Tickets) zu verwenden.

## Features

- **Organizer-weite Verwaltung**: Schriftarten werden auf Organizer-Ebene hochgeladen und verwaltet.
- **Sicherer Upload**: Validierung von Dateitypen (.ttf, .otf).
- **PDF-Integration**: Automatische Registrierung der Schriftarten in ReportLab (Pretix PDF-Engine), sobald ein Ticket generiert wird.
- **Nahtlose UI**: Integration in das Pretix-Backend unter Organizer -> Eigene Schriftarten.

## Installation

1. Klonen Sie dieses Repository in Ihr Pretix-Plugin-Verzeichnis oder installieren Sie es via pip:
   ```bash
   pip install .
   ```

2. Führen Sie die Datenbank-Migrationen aus:
   ```bash
   python -m pretix migrate
   ```

3. Starten Sie Ihren Pretix-Server neu.

## Nutzung

1. Gehen Sie im Pretix-Backend zu Ihrem **Organizer**.
2. Klicken Sie in der linken Navigation auf **Eigene Schriftarten**.
3. Laden Sie eine .ttf oder .otf Datei hoch und geben Sie ihr einen Namen.
4. Die Schriftart ist nun unter dem angegebenen Namen in ReportLab-basierten Plugins (wie dem Ticket-Designer) verfügbar.

## Technische Details & Grenzen

### PDF-Integration
Die Schriftarten werden über den `register_ticket_outputs` Signal-Hook registriert. Dies stellt sicher, dass die Fonts geladen sind, bevor die PDF-Generierung beginnt. In ReportLab werden sie über `pdfmetrics.registerFont` verfügbar gemacht.

### Ticket-Designer
Um diese Schriftarten im grafischen Ticket-Designer von Pretix auszuwählen, müsste das Ticket-Designer-Plugin selbst erweitert werden (dieses Plugin bietet aktuell nur eine begrenzte Liste an Standardschriftarten an). Dieses Plugin stellt jedoch die infrastrukturelle Basis bereit, damit die Schriftarten vom System erkannt und gerendert werden können, wenn sie in Custom-Implementierungen oder manuell in PDF-Templates referenziert werden.

### Speicherort
Schriftarten werden im `MEDIA_ROOT` unter `pub/<organizer>/fonts/` gespeichert. In einer Docker-Umgebung sollte sichergestellt sein, dass das Medienverzeichnis auf einem persistenten Volume liegt (standardmäßig `/data` im Pretix-Image).

## Docker-Integration

Um das Plugin in einer Docker-Umgebung zu nutzen, können Sie das mitgelieferte `Dockerfile` verwenden, um ein eigenes Pretix-Image zu bauen, das das Plugin bereits enthält.

### Docker Compose Snippet
```yaml
  pretix:
    image: ghcr.io/magicalwig34653/pretix-modify-custom-fonts:stable
    volumes:
      - /path/to/data:/data
    # ... weitere Konfiguration
```

## Lizenz
Apache License 2.0
