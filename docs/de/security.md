# Daten und Zugänge

Bereiten Sie minimale Aufzeichnungen vor und wählen Sie den Berechnungsort.

[Dokumentationsbibliothek](README.md) · [Dokumentation auf der Website](https://alpnai.com/de/docs)

[Français](../fr/security.md) · [English](../en/security.md) · [Deutsch](../de/security.md)

## Berechnung im Browser

Lokale Werkzeuge rechnen mit den in die Seite geladenen Aufzeichnungen. Deren Inhalt wird dafür nicht an die API gesendet. HTML- und JSON-Exporte entstehen auf Ihrem Gerät.

Die Seite kann Ressourcen laden und mit Ihrer Zustimmung Nutzungsschritte messen. Lokale Berechnung bedeutet nicht, dass die gesamte Website offline funktioniert.

## Berechnung über API oder MCP

Bei API oder MCP werden Aufzeichnungen zur Berechnung an den Server übertragen. Sie werden nicht in der Audit-Anwendungsdatenbank gespeichert. Kontodaten, gehashte Schlüssel und Pilotbelege werden getrennt behandelt.

Ihre Infrastruktur und der Hoster können technische Protokolle erzeugen. Senden Sie deshalb nur erforderliche Berechnungsdaten, auch bei persisted:false.

## Was in die Aufzeichnungen gehört

Verwenden Sie neutrale Kennungen wie task-001. Übermitteln Sie Kosten, Variante, Erfolg und Dauer. Kundennamen, E-Mails, Dokumente, Prompts und ausführliche Antworten bleiben in Ihrer Umgebung.

Die Vertragsfelder sind strikt festgelegt. Speichern Sie keine Geheimnisse in task_id oder workflow; Textfelder sind kein beliebiger Datenspeicher.

## Schlüssel schützen und ersetzen

Ein aktiver Schlüssel ermöglicht die autorisierten Aufrufe seines Kontos. Bewahren Sie ihn serverseitig oder lokal auf, nicht in öffentlichen Repositories oder an Besucher verteiltem Seitencode.

Ein verlorener Schlüssel kann über den vorgesehenen Ablauf ersetzt werden. Der alte wird widerrufen; verbrauchtes Testbudget bleibt erhalten. Das Audit benötigt weder MetaMask-Passwort noch privaten Schlüssel oder Wiederherstellungsphrase.

---

[Zurück: Zahlungen und Testmodus](payments.md)
