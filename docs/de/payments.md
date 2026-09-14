# Zahlungen und Testmodus

Unterscheiden Sie kostenlose Audits, simulierte Käufe und x402-Zahlungen in der Validierung.

[Dokumentationsbibliothek](README.md) · [Dokumentation auf der Website](https://alpnai.com/de/docs)

[Français](../fr/payments.md) · [English](../en/payments.md) · [Deutsch](../de/payments.md)

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

Der Server erstellt eine Bestellung und übermittelt Zahlungsbedingungen mit einer 402-Antwort. Ein autorisierter Käuferagent kann die passende Autorisierung erstellen. Vor der Abwicklung prüft der Dienst Betrag, Netzwerk, Empfänger und Auftrag.

Der Facilitator unterstützt Prüfung und Abwicklung. pending oder unknown erfordert die Prüfung der ursprünglichen Bestellung und darf keine neue automatische Ausgabe auslösen.

## Von der Wallet zur Bank

Vorgesehen ist USDC auf Base an die über MetaMask zugängliche Wallet des Anbieters. Für den anschließenden Umtausch in CHF oder EUR und die Banküberweisung ist ein gesonderter Dienstleister zuständig.

Dieser Ablauf setzt Coinbase Business nicht voraus. Der Umtauschdienstleister muss Tätigkeit und Bankkonto akzeptieren; seine Kurse, Gebühren und Fristen gelten. Der Kunde kauft eine Dienstleistung, keine Anlage, Rendite oder IPO-Zuteilung.

---

[Zurück: Einen Agenten über MCP verbinden](mcp.md) · [Weiter: Daten und Zugänge](security.md)
