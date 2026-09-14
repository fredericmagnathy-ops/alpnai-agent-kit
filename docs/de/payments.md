# Zahlungen und Testmodus

Unterscheiden Sie kostenlose Audits, simulierte Käufe und x402-Zahlungen in der Validierung.

## Was heute genutzt werden kann

Spend Proof und lokale Berechnungen erfordern keine Zahlung. Im Evidence-Piloten lassen sich Käufe mit Schlüssel und fiktivem Budget testen.

Eine x402-Integration mit PayAI wird für USDC auf Base vorbereitet; der Mainnet-Zahlungsablauf wird noch validiert. Vorhandener Code belegt weder einen echten Verkauf noch einen vollständig ausgeführten Zahlungsvorgang.

## Ohne Geldtransfer testen

Die Anfrage ruft eine vorhandene Route im Sandbox-Modus auf. Der Beleg enthält settled:false, real_revenue_usdc:0 und einen simulierten Preis. Eine Wallet-Verbindung ist nicht nötig.

Wiederholen Sie dieselbe Anfrage mit derselben Idempotency-Key für denselben Kauf. Andere Parameter mit dieser Kennung führen zu einem Konflikt. Nutzen Sie für eine neue Bestellung eine neue Kennung.

```bash
curl --fail-with-body --silent --show-error \
  'https://alpnai.com/api/v1/snapshot' \
  --header "Authorization: Bearer ${ALPNAI_AGENT_KEY}" \
  --header 'X-ALPNAI-Mode: sandbox' \
  --header 'Idempotency-Key: docs_demo_20260914_001'
```

## Den geplanten x402-Ablauf verstehen

Vor einer 402-Anforderung verlangt der vorbereitete Ablauf ein gültiges Profil und eine Rechnungsprüfung zu den akzeptierten Bedingungen. Das Angebot hält dann den Gesamtbetrag und die verwendeten Angaben fest. Ein Profil ist keine Steuerprüfung; ein Verfahren zur Erteilung der Freigabe ist noch nicht eröffnet.

Der Server erstellt eine Bestellung und übermittelt Zahlungsbedingungen mit einer 402-Antwort. Ein autorisierter Käuferagent kann die passende Autorisierung erstellen. Vor der Abwicklung prüft der Dienst Betrag, Netzwerk, Empfänger und Auftrag.

Der Facilitator unterstützt Prüfung und Abwicklung. pending oder unknown erfordert die Prüfung der ursprünglichen Bestellung und darf keine neue automatische Ausgabe auslösen.

## Bestellung und Beleg wiederfinden

Eine ausstehende Bestellung behält dieselbe Kennung. Der Abgleich sucht in finalisierten Blöcken nach Zahlungsnachweisen, in begrenzten Abschnitten mit gespeichertem Fortschritt. Ein Ausfall oder eine Verzögerung löst niemals einen weiteren Zahlungsversuch aus.

Eine vor jedem Zahlungsversuch aufgegebene Reservierung wird nach Ablauf des Angebots freigegeben. Sobald ein Versuch begonnen hat, bleibt sie in Prüfung: Zeitablauf allein gibt das Budget nicht frei.

Nach der Bestätigung kann der Inhaber Beleg und Ergebnis im Kundenbereich abrufen. Die Umsatzanzeige zählt nur bestätigte USDC-Zahlungen auf Base; Sandbox-Käufe und Testnetz-Zahlungen sind ausgeschlossen.

## Einen bestätigten Beleg drucken

Im Kundenbereich bietet eine bestätigte Bestellung „Beleg und Ergebnis“ als JSON-Datei und „Druckbarer Beleg“ als lesbare Seite. Öffnen Sie die Seite und nutzen Sie die Druckfunktion Ihres Browsers zum Drucken oder Speichern als PDF.

Der Beleg behält die Angaben und Beträge des zugehörigen Angebots bei, auch nach Profiländerungen. Er zeigt die in UTC erfasste Bestätigung, die Transaktion und Dokument-Hashes. Eine ältere Bestellung ohne festgehaltene Rechnungsangaben bleibt ein minimaler Beleg. Das Dokument ersetzt keine Steuerrechnung.

Nur das zugehörige Konto kann dieses private Dokument öffnen. Für unbestätigte Bestellungen wird kein druckbarer Beleg erstellt. Die Ansicht kontaktiert keinen Zahlungsdienst und löst keine Zahlung aus. Echte Käufe bleiben deaktiviert.

```http
GET /api/account/orders/{order_id}/receipt?lang=de
```

## Von der Wallet zur Bank

Vorgesehen ist USDC auf Base an die über MetaMask zugängliche Wallet des Anbieters. Für den anschließenden Umtausch in CHF oder EUR und die Banküberweisung ist ein gesonderter Dienstleister zuständig.

Dieser Ablauf setzt Coinbase Business nicht voraus. Der Umtauschdienstleister muss Tätigkeit und Bankkonto akzeptieren; seine Kurse, Gebühren und Fristen gelten. Der Kunde kauft eine Dienstleistung, keine Anlage, Rendite oder IPO-Zuteilung.

[ALPNAI documentation](https://alpnai.com/de/docs/payments)
