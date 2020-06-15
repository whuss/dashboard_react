# Szenarien:

## Keine weitere Verwendung mit Reprolight Projektende

    - Keine Weiterentwicklung am PTL Sourcecode
    - Monitoring der existierenden PTLs und notwendige Wartung im Projektzeitraum
    - Abschaltung der Datenaufzeichnung mit Projektende
    - Umstellung der Reprolight Web-App auf ein fixes Analyse Zeitintervall

## Verwendung der PTL für weitere Projekte ohne Softwareänderungen an PTL Code

    - Derzeitige Datenbank Performanz ungeeignet für Langzeit Datenaufzeichnung.
    - Für Projekt die auf ein paar Monate begrenzt sind, Möglichkeit mit neuer
      Datenbank zu beginnen. (Aufwände: Konfigurierbarkeit der Datenbank URL im
      PTL Code und in der Web-App)
    - Minimale Wartung des PTL Codes. Behebung von Abstürzen etc.

## PTL Code als Basis für weitere Forschungsprojekte

    - PTL Code soll flexibel mit weiteren Modulen erweiterbar sein:
      (Tageszeitabhängige Steuerung, Biodynamik, Gesichtserkennung, Blinkerkennung, etc.)
    - Konsolidierung der aktuellen Funktionalität: Erstellung von automatisierten
      Tests um die Korrektheit von bereits implemtierter Funktionalität zu gewährleisten.
    - Langzeitwartbarkeit des Sourcecodes
    - Updates für Grundlegende Komponeten:
        - Jetson Nano: Betriebsystem
        - Tensorflow
        - Datenbanklayer
    - Evaluierung der aktuellen Softwarearchitektur:
        Threads, vs Async/Await
    - Anpassungen der Datenbank Infrastruktur um Langzeit Datenaufzeichnung zu ermöglichen.
    - Anpassungen der Web-App für Datenauswertungen

## PTL als proof of Concept

    - Stabiles Featureset, dafür höhere Qualität
    - Verbesserung der Systemstabilität (Abstürze)
    - Blickrichtungserkennung:
      (Performanz Probleme, Lange Startup Zeit, Verbesserung der Detektionsrate unter realen Bedingungen)
    - Präsenzdetektion:
      Tiefendetektion derzeit am Limit der Kameraempfindlichkeit,
      
## PTL als vermarktbares Produkt

    Unmöglich mit Bartenbach Ressourcen.


