# ALPNAI Projects — Entscheidungen über Agenten dokumentieren

Stand: 14. September 2026.

Vergleichen Sie Kosten, Erfolgsquote und Latenz zweier Versionen, bevor Sie eine davon auswählen. Projects speichert aggregierte Ergebnisse von **Spend Proof, Latency Lab und Quality Gate** in Ihrem privaten Konto, mit JSON-Downloads und druckbaren Berichten. Ihre Messwerte bestimmen das Ergebnis; eine Hochrechnung garantiert keine Einsparung.

[Projects öffnen](https://alpnai.com/projects) · [Bedingungen](https://alpnai.com/de/legal/projects) · [Datenschutz](https://alpnai.com/de/legal/privacy)

[Dokumentationsbibliothek](README.md) · [ALPNAI](https://alpnai.com/de/docs)

[Français](../fr/projects.md) · [English](../en/projects.md) · [Deutsch](../de/projects.md)

## Zugang und Angebote

Melden Sie sich mit ChatGPT an. Projects ist dem authentifizierten Kontoinhaber vorbehalten; ein Agenten-API-Schlüssel öffnet weder dessen Berichte noch die Abrechnung. Keine Krypto-Wallet erforderlich.

| Angebot | Preis | Neu gespeicherte Berichte |
|---|---|---|
| Kostenloser Zugang | Ohne Karte | 3 für die Lebensdauer des Kontos |
| Monatlich | 19 CHF, 19 EUR, 19 USD oder 19 GBP pro Monat | 100 je bezahlter Monatsperiode |
| Jährlich | 190 CHF, 190 EUR, 190 USD oder 190 GBP pro Jahr | 1.200 je bezahlter Jahresperiode |

Projects unterstützt 10 Projekte und höchstens 2.400 gespeicherte Berichte. Löschen stellt kein Kontingent wieder her; es gibt keine Mehrverbrauchsabrechnung. CHF, EUR, USD und GBP sind getrennte feste lokale Preise ohne Währungsumrechnung. Stripe zeigt vor Bestätigung den Gesamtpreis einschließlich Steuern. Die Verfügbarkeit von Abonnements wird in Projects angezeigt.

## Mit eigenen Messwerten beginnen

1. Anmelden, Projekt und Version benennen und JSON-Messwerte aus dem [Spend-Proof-Leitfaden](spend-proof.md) importieren.
2. **Berechnen und speichern** wählen. Beim Speichern werden Messwerte zur Berechnung an ALPNAI übertragen. Die Datenbank speichert aggregierte Ergebnisse und Bezeichnungen, keine Rohversuche oder Prompts. Keine Geheimnisse oder Personenkennungen aufnehmen.
3. Eine weitere Version speichern, bis zu zwei Berichte auswählen und vergleichen. JSON-Details oder einen druckbaren Bericht herunterladen.

## Abonnement und Rechnungen

Währung und Zeitraum wählen, Projects-Bedingungen akzeptieren und über Stripe bezahlen. Kostenloser Zugang wird nicht automatisch kostenpflichtig. Bezahlter Zugang beginnt nach bestätigter Zahlung; die Rückkehr von Stripe allein ist kein Zahlungsnachweis. Unter **Abonnement und Rechnungen** können Sie die Abrechnung verwalten und die nächste Verlängerung stoppen. Fehlgeschlagene Zahlungen gewähren keine neue Periode. Bestehende Berichte bleiben nach Ablauf herunterladbar.

API-/MCP-Käufe dieses Kits bleiben **ausschließlich in der Sandbox**. Projects-Abonnements sind ein separater Webdienst; das Kit schließt oder verlängert sie nicht und überträgt keine Kryptowährung.

Kontakt: [frederic@alpnor.com](mailto:frederic@alpnor.com).

## Berichte automatisch zustellen

Eine Agentur mit mehreren Agenten muss Ergebnisse zusammenführen. Ergänzen Sie Ihre eigene Pipeline um einen ALPNAI-Aufruf: Der Server berechnet Kosten, Latenz und Qualitätsprüfungen und speichert das Ergebnis in Projects.

save_project_report berechnet und speichert einen Bericht im ausdrücklich vom Inhaber freigegebenen Projekt mit dem bestehenden Projects-Kontingent. Es benötigt request_id, title und input. Anleitung: https://alpnai.com/de/docs/projects-automation.

Automatische und manuelle Speicherungen teilen sich die drei lebenslang kostenlosen Berichte, 100 Berichte je bezahlter Monatsperiode oder 1.200 je bezahlter Jahresperiode. Es gibt keine Mehrverbrauchsabrechnung und keinen automatischen Wechsel zu einem kostenpflichtigen Angebot.

---

[Ihr erstes Audit](quickstart.md) · [Spend Proof: Kosten pro Erfolg](spend-proof.md)
