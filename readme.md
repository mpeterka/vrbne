# Provoz na USD České Vrbné - kalendář
*Voda pro potřeby tréninků a rekreačního ježdění se pouští od 1. dubna do 31. října.*

Jen malé udělátko, které z tabulky na http://itdev.cz/SlalomCourse/OpeningTimes.aspx 
vyrobí icalendar pro zobrazení v kalendáři.


Běží jako AWS Lambda

## Deploy
(Node.js serverless)
`sls deploy --aws-profile martin.peterka`

## endpoints
* GET - https://dmaz11xve5.execute-api.eu-central-1.amazonaws.com/dev/icalendar

## Návod
* [Google Kalendář](/doc/google.md)
* ~~[Microsoft Outlook](/doc/outlook.md)~~ 
  * nefunguje správně - chybí dořešit časová pásma!

## Kontakt
* martin.peterka@gmail.com

# Ostatní
* http://jakoubek.cz/usd
* https://raftingcb.cz
* https://www.slalom.cz
