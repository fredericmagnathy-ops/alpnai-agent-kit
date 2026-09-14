# Berichte automatisch zustellen

Nach jeder Auswertung einen Projects-Bericht speichern, ohne manuellen Upload.

[Dokumentationsbibliothek](README.md) · [ALPNAI](https://alpnai.com/de/docs)

[Français](../fr/projects-automation.md) · [English](../en/projects-automation.md) · [Deutsch](../de/projects-automation.md)

## Nach der Auswertung steht der Bericht bereit

Eine Agentur mit mehreren Agenten muss Ergebnisse zusammenführen. Ergänzen Sie Ihre eigene Pipeline um einen ALPNAI-Aufruf: Der Server berechnet Kosten, Latenz und Qualitätsprüfungen und speichert das Ergebnis in Projects.

Ihr Team erhält einen privaten Verlauf, um zwei Versionen zu vergleichen und Berichte herunterzuladen. Sie liefern Messdaten und Erfolgskriterien; ALPNAI führt keine Modelle aus und verändert deren Konfiguration nicht.

## Ein Ziel einmalig freigeben

Melden Sie sich unter https://alpnai.com/projects mit dem Konto des Berichtseigentümers an. Aktivieren Sie gegebenenfalls unter https://alpnai.com/account Ihren Schlüssel. Unter „Berichte direkt von Ihrem Agenten“ das Projekt wählen, der Kontingentnutzung zustimmen und „Berichte erlauben“ auswählen.

Die Freigabe gilt für Ihren aktiven Agenten und ein festes Projekt. Sie erlaubt nur, neue Berichte zu berechnen und zu speichern. Bisherige Berichte können nicht gelesen oder gelöscht werden; Käufe und Abonnements sind nicht erlaubt. „Berichte stoppen“ widerruft den Zugang.

## Pipeline verbinden

Senden Sie POST https://alpnai.com/api/v1/project-reports mit Authorization: Bearer und Ihrem ALPNAI-Schlüssel. Der Inhalt enthält request_id, title und input. input nutzt das runs/config-Format der kostenlosen Werkzeuge. user_id und project werden nicht akzeptiert: Die Freigabe bestimmt das Ziel.

Mit MCP rufen Sie save_project_report mit denselben Argumenten auf. Prüfen Sie result.isError. Bei Erfolg erhalten Sie eine Berichtskennung, saved: true und persistence: computed_summary. Der Kontoinhaber liest den Inhalt in Projects.

Begrenzen Sie jeden Upload auf 1.000 Versuche und 500.000 Bytes, damit beide Übertragungswege unterstützt werden. Nur Messwerte ohne Prompts, Geheimnisse oder personenbezogene Daten senden. Rohversuche werden nicht in der Datenbank gespeichert; aggregierte Ergebnisse, Bezeichnungen und technische Kennungen werden gespeichert.

Formatbeispiel mit zwei synthetischen Versuchen, kein Nachweis für Einsparungen. Messwerte ersetzen und für jeden neuen Bericht eine eigene Kennung erstellen.

```json
{
  "request_id": "e5b67ec8-5d1a-4abe-9e1b-5f358557db82",
  "title": "Evaluation 2026-09-15",
  "input": {
    "runs": [
      {
        "task_id": "synthetic-1",
        "workflow": "support",
        "variant": "baseline",
        "cost_usd": 0.02,
        "success": true,
        "latency_ms": 200
      },
      {
        "task_id": "synthetic-1",
        "workflow": "support",
        "variant": "candidate",
        "cost_usd": 0.01,
        "success": true,
        "latency_ms": 180
      }
    ]
  }
}
```

## Nach Unterbrechungen ohne doppelte Zählung fortsetzen

Vor jedem neuen Bericht eine UUID erstellen und aufbewahren. Nach einer Unterbrechung dieselbe request_id, denselben Titel, dieselben Daten und dieselbe Freigabe verwenden. Der Server gibt dieselbe Kennung mit replayed: true zurück und verbraucht kein weiteres Kontingent. Andere Inhalte mit derselben Kennung werden abgelehnt.

Ein Projektwechsel oder eine neue Freigabe erstellt einen neuen Kennungsraum. Laufende Uploads vorher abschließen. Ein widerrufener Schlüssel funktioniert nicht mehr; nach einem Schlüsselwechsel das Geheimnis in der Pipeline aktualisieren. Keine neuen Kennungen erstellen, um Kontingentfehler zu umgehen.

## Gemeinsames Kontingent, klare Kosten

Automatische und manuelle Speicherungen teilen sich die drei lebenslang kostenlosen Berichte, 100 Berichte je bezahlter Monatsperiode oder 1.200 je bezahlter Jahresperiode. Es gibt keine Mehrverbrauchsabrechnung und keinen automatischen Wechsel zu einem kostenpflichtigen Angebot.

Abonnements kosten monatlich 19 CHF, EUR, USD oder GBP beziehungsweise jährlich 190 in derselben Währung. Der Kontoinhaber wählt und bestätigt das Abonnement auf der Website. Bei ausgeschöpftem Kontingent lehnt die API neue Speicherungen ab; kostenlose Analysen bleiben verfügbar.

## Fehler behandeln

401 agent_key_required: aktiven Schlüssel prüfen. 403 project_access_required oder project_access_revoked: Freigabe durch den Inhaber prüfen. 409 report_limit_reached: Projects-Kontingent prüfen. 409 report_request_conflict: ursprüngliche Parameter verwenden. 400 invalid_report: Datenformat prüfen.

Nach einem Zeitlimit oder einer vorübergehenden Störung dieselbe Kennung wiederverwenden. Ein gelöschter Bericht lässt sich unter derselben Kennung nicht erneut erstellen. Die Projects-Bedingungen beschreiben Speicherung und Abrechnung vollständig.

## Einsatzbereiter Python-Client

Im Repository ALPNAI_AGENT_KEY über Ihre Geheimnisverwaltung bereitstellen und eigene Messdaten verwenden. Eine neue Statusdatei steht für einen neuen Bericht. Nach Unterbrechung genau denselben Befehl wiederholen.

```sh
python3 examples/save_project.py --input private/attempts.json --title "Extraction v2" --state private/extraction-v2-state.json
```

Der Client speichert Kennung und Fingerabdruck vor dem Senden in einer privaten Datei; Weiterleitungen und geänderte Wiederholungsparameter werden abgelehnt. Nach einer Projektfreigabeänderung keine alten Befehle erneut verwenden.

---

[Einen Agenten über MCP verbinden](mcp.md) · [Projects, Zahlungen und Testmodus](payments.md)
