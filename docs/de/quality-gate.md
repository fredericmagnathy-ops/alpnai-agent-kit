# Quality Gate: vor Änderungen vergleichen

Prüfen Sie Erfolg, Kosten und Latenz, bevor Sie eine Variante übernehmen.

[Dokumentationsbibliothek](README.md) · [Dokumentation auf der Website](https://alpnai.com/de/docs)

[Français](../fr/quality-gate.md) · [English](../en/quality-gate.md) · [Deutsch](../de/quality-gate.md)

## Schwellen festlegen

Standardmäßig benötigt jede Version mindestens 30 unterschiedliche Aufgaben. Die Variante muss mindestens 95 % davon erfolgreich lösen und darf gegenüber der Referenz höchstens 2 Prozentpunkte verlieren.

Fügen Sie dieses Objekt unter config in die Datendatei ein. maxP95LatencyMs und monthlyTasks sind optional; die übrigen Werte entsprechen den Standards.

```json
{
  "minSamples": 30,
  "minSuccessRate": 0.95,
  "maxSuccessRateDrop": 0.02,
  "maxP95LatencyMs": 3000,
  "monthlyTasks": 10000
}
```

## Prüfungen lesen

both_variants prüft das Vorliegen beider Versionen. minimum_distinct_tasks_per_variant prüft die Mindeststichprobe. same_task_set verlangt exakt übereinstimmende Kennungen.

observed_success_rate prüft Erfolgsgrenzen, recorded_latency die angeforderte Zeitgrenze und lower_cost_per_successful_task strikt niedrigere Kosten pro Erfolg. pass heißt erfüllt, fail nicht erfüllt, unknown unbestimmt und not_requested nicht angefordert.

## Mit der Entscheidung arbeiten

missing_comparison: fehlende Version ergänzen. collect_more_data: Stichprobe oder Aufgabenabgleich vervollständigen. quality_regression: Fehler anhand Ihrer Kriterien untersuchen.

latency_data_required: Dauern ergänzen. latency_regression: Zeitgrenze überschritten. no_economic_advantage: keine geringeren Kosten pro Erfolg. candidate_for_controlled_trial: begrenzten Versuch vorbereiten.

## Einen kontrollierten Versuch vorbereiten

Bewahren Sie Daten, Konfiguration und Bericht auf. Dokumentieren Sie Änderungen, Erfolgskriterien und fehlende Kosten. Legen Sie danach eine begrenzte Testgruppe und Versuchsdauer fest.

Der Bericht enthält automatic_deployment_authorized:false. Eine bestandene Prüfung löst weder Modellwechsel noch Kauf oder Produktivsetzung aus.

## Was Schwellen nicht beweisen

Diese Prüfungen nutzen beobachtete Raten. Die 95-%-Wilson-Intervalle sind beschreibend und setzen unabhängige Aufgaben voraus. Sie belegen weder Kausalität noch eine statistisch gesicherte Verbesserung.

experimental_bias_control bleibt unknown: Gemeinsame Kennungen beweisen keine Randomisierung. Erfolgskriterien und Repräsentativität müssen separat bewertet werden.

---

[Zurück: Latency Lab: Zeiten und Wiederholungen](latency.md) · [Weiter: Berichte und Exporte](reports.md)
