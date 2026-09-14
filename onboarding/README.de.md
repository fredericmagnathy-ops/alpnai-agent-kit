# CSV-Import für ALPNAI

[Français](README.fr.md) · [English](README.md)

Wandeln Sie erfasste Versuche in JSON für **Spend Proof, Latency Lab und Quality Gate** um. Python ab Version 3.10; keine zusätzlichen Pakete. Die Umwandlung erfolgt vollständig auf Ihrem Computer, ohne Konto, Schlüssel oder Netzwerkanfrage.

## In einer Minute ausprobieren

Führen Sie diese Befehle in diesem Verzeichnis aus:

```sh
mkdir -p .alpnai
python3 csv_to_alpnai.py --input fixtures/attempts.synthetic.csv --output .alpnai/beispiel.json
```

Die Beispieldaten sind **fiktiv**: 10 Versuche, 4 Aufgaben pro Variante, insgesamt 2 Wiederholungen und vollständig erfasste Dauern. Die Berechnung ergibt für Referenz / Kandidat Gesamtkosten von 0,18 / 0,09 USD, jeweils 3 erfolgreiche Aufgaben von 4 und ein erfasstes P95 von 3.200 / 1.800 ms. Diese Werte prüfen die Berechnung; sie belegen keine Kundeneinsparungen. Mit vier Aufgaben pro Variante bleibt die Standardentscheidung `collect_more_data`.

Ersetzen Sie danach `--input` durch Ihren Export und wählen Sie einen neuen Ausgabedateinamen. Vorhandene Dateien werden nie überschrieben. Im Terminal erscheinen nur Anzahlen und Formatfehler; die JSON-Datei enthält Ihre Kennungen und Messwerte. Neue Dateien erhalten auf kompatiblen Systemen die Berechtigung `0600`.

## Was eine Zeile bedeutet

**Eine Zeile = ein vollständiger Versuch einer Aufgabe.** Bewahren Sie jeden fehlgeschlagenen Versuch und jede Wiederholung mit eigenen Kosten und eigener Dauer auf. Umfasst ein Versuch mehrere Anbieteraufrufe, fassen Sie diese vorher in Ihrer Telemetrie zusammen. Ein einzelner Anbieteraufruf ist dann kein eigener Aufgabenversuch. Erfinden Sie keine Zeilen aus einer zusammengefassten Anzahl von Wiederholungen.

| Spalte | Erwarteter Wert |
|---|---|
| `task_id` | Stabile, nicht personenbezogene Aufgabenkennung; dieselben Kennungen für beide Varianten. 1–128 UTF-16-Codeeinheiten. |
| `workflow` | Prozessname mit 1–80 UTF-16-Codeeinheiten. Eine Aufgabenkennung darf nicht zu mehreren Prozessen gehören. |
| `variant` | Genau `baseline` oder `candidate`. |
| `cost_usd` | Vollständige erfasste Kosten **dieses Versuchs** in USD, einschließlich Modelle, Werkzeuge, Suche und anderer Aufrufe. Von 0 bis 10.000 USD, höchstens sechs Nachkommastellen. |
| `success` | `true` / `false` unabhängig von Groß-/Kleinschreibung oder `1` / `0`, anhand Ihrer Bewertung des Aufgabenergebnisses. HTTP 200 beweist keinen Aufgabenerfolg. |
| `latency_ms` | Optional: erfasste Versuchsdauer in Millisekunden, von 0 bis 86.400.000. Eine leere Zelle bleibt ein fehlender Wert. |
| `attempt_id` | Optional: eindeutige Versuchskennung innerhalb einer Aufgabe und Variante, 1–256 UTF-16-Codeeinheiten. Wiederholte Kennungen lösen einen Fehler aus. Diese Spalte wird nicht in das JSON übernommen. |

Kennungen dürfen keine Steuerzeichen oder Leerzeichen am Anfang/Ende enthalten. Spaltennamen unterscheiden Groß- und Kleinschreibung. Andere Spalten werden ignoriert und nicht in das JSON übernommen. Tragen Sie keine Prompts, Dokumente oder Geheimnisse in die ausgewählten Felder ein.

Der Konverter **erfindet keine Preise, rechnet keine Währungen um und schätzt keine Kosten aus Tokens**. Wenn nur Tokenzahlen vorliegen, stellen Sie zuerst gemessene Kosten aus Ihrem System bereit. Verwenden Sie einen Dezimalpunkt, auch bei CSV-Dateien mit Semikolon. Bruchteile eines Mikro-USD werden ohne Rundung abgelehnt; fassen Sie die Kosten vorher korrekt zusammen.

ALPNAI gruppiert Versuche nach `workflow`, `variant`, `task_id`. Eine Aufgabe ist erfolgreich, wenn mindestens ein Versuch erfolgreich ist. Alle erfassten Versuchskosten zählen. P95 basiert auf der Summe der erfassten Versuchsdauern je Aufgabe. Diese Summe ist keine tatsächlich verstrichene Zeit bei parallelen Vorgängen. Eine fehlende Dauer verhindert ein vollständiges P95 für die betreffende Variante.

## Vorhandene Exportspalten zuordnen

`--map FELD=SPALTE` ordnet einem ALPNAI-Feld Ihre CSV-Spalte zu. Enthält der Spaltenname Leerzeichen, setzen Sie die gesamte Zuordnung in Anführungszeichen. Dieses Beispiel ist direkt ausführbar:

```sh
python3 csv_to_alpnai.py --input fixtures/export.synthetic.csv --output .alpnai/zugeordneter-export.json --delimiter ';' --map task_id=job_id --map workflow=pipeline --map variant=arm --map cost_usd=measured_usd --map success=passed --map latency_ms=duration_ms --map attempt_id=request_id
```

Unterstützte Trennzeichen: Komma (Standard), `;` und `tab`. Die Datei muss UTF-8 verwenden; eine UTF-8-BOM wird akzeptiert. Lokale CSV-Grenze: 2 MiB. ALPNAI-Grenzen: 1.000 Versuche und 512.000 UTF-8-Bytes JSON. Teilen Sie große Exporte in vollständige Aufgabensätze auf und behalten Sie dabei alle Versuche einer Aufgabe sowie beide Varianten zusammen.

Ohne `attempt_id` bleiben identische Messwerte erhalten und werden gemeldet: Es können echte Wiederholungen oder doppelt erfasste Telemetriedaten sein. Prüfen Sie den ursprünglichen Export. Der Konverter entfernt solche Zeilen niemals stillschweigend.

## JSON verwenden

**Browser:** Öffnen Sie [Spend Proof](https://alpnai.com/de/tools/spend-proof), [Latency Lab](https://alpnai.com/de/tools/latency-lab) oder [Quality Gate](https://alpnai.com/de/tools/quality-gate) und fügen Sie das JSON in das Datenfeld ein. Die Berechnung im Browser erfolgt lokal. Das Speichern in Projects ist eine separate Aktion, die Daten an den Dienst übermittelt.

**Python-Kit:** Stellen Sie im Stammverzeichnis des [ALPNAI-Agenten-Kits](https://github.com/fredericmagnathy-ops/alpnai-agent-kit) einen aktiven Schlüssel über die Geheimnisverwaltung Ihres Prozesses als `ALPNAI_AGENT_KEY` bereit. Geben Sie dann die tatsächlichen Pfade zum JSON und zu einem neuen Bericht an:

```sh
python3 examples/audit.py --input /privater/pfad/meine-versuche.json --report /privater/pfad/mein-bericht.json
```

Dieser Befehl sendet die Aufzeichnungen mit Bearer-Authentifizierung an `POST /api/v1/spend-proof`. Das Audit ist kostenlos und liefert `payment_required:false` sowie `persisted:false`; es speichert keinen Bericht in Projects. Die weiteren kostenlosen APIs akzeptieren dasselbe JSON: `POST /api/v1/latency` und `POST /api/v1/quality-gate`. Der vorhandene Client `audit.py` ist für Spend Proof vorgesehen.

Ein Vergleich benötigt übereinstimmende Aufgabenkennungen, dieselbe Erfolgsdefinition und standardmäßig mindestens 30 verschiedene Aufgaben je Variante. Ein erfolgreicher Import beweist weder vollständige Kostendaten noch eine unverzerrte Stichprobe. Er autorisiert keine automatische Bereitstellung.

## Optionale Grenzwerte und Prüfung

`--config fixtures/config.example.json` übernimmt die ausdrücklichen Grenzwerte aus der Datei: mindestens 30 Aufgaben, mindestens 95 % Erfolg, höchstens 2 Prozentpunkte Erfolgsrückgang und ein P95-Limit von 3.000 ms. Passen Sie das Latenzlimit an Ihren Anwendungsfall an. Ohne diese Option fehlt die Konfiguration im JSON; die Berechnung verwendet ihre Standardwerte. `monthlyTasks` kann für einen einzigen Prozess ergänzt werden und bezeichnet gestartete Referenzaufgaben pro Monat. Eine mögliche Hochrechnung bleibt bedingt.

```sh
python3 -m unittest discover -s tests -p 'test_*.py' -v
```

20 Offline-Tests prüfen Werte, Wiederholungen, Fehler, Zuordnungen, Grenzen und Dateien. Zum Prüfen des tatsächlichen Kit-Befehls ersetzen Sie den Pfad:

```sh
python3 tests/check_kit_command.py --kit /pfad/zum/alpnai-agent-kit
```

