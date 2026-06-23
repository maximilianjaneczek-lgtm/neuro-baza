from __future__ import annotations

import csv
import html
import json
import re
import unicodedata
from pathlib import Path
from typing import Any
from xml.sax.saxutils import escape

from pypdf import PdfReader
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path("/Users/maksymilianjaneczek/Documents/Codex/2026-06-23/po")
WORK = ROOT / "work" / "neuro"
OUT = ROOT / "outputs"
PAGES_JSON = WORK / "pages.json"
EXTERNAL_JSON = WORK / "external_sources.json"
OUT.mkdir(parents=True, exist_ok=True)


CHAPTERS: list[dict[str, Any]] = [
    {
        "id": "badanie",
        "day": 1,
        "title": "Badanie neurologiczne",
        "pages": "6-9",
        "pdf_start": 7,
        "pdf_end": 10,
        "time": "60 min",
        "priority": "A",
        "summary": "Najpierw lokalizacja, potem etiologia. Badanie ma odpowiedzieć: czy problem jest w OUN czy obwodowo, czy dotyczy drogi ruchowej, czucia, móżdżku, pnia, nerwów czaszkowych albo korzeni.",
        "core": [
            "Kolejność: wrażenie ogólne, mowa i chód, objawy oponowe, nerwy czaszkowe, układ ruchu, odruchy, czucie, objawy korzeniowe, móżdżek, testy dodatkowe.",
            "Objawy oponowe: sztywność karku, Kernig, Brudziński, Flatau i Herman. W pytaniu egzaminacyjnym łącz je z zapaleniem opon lub krwotokiem podpajęczynówkowym.",
            "Nerwy czaszkowe ucz się parami funkcji: I węch, II wzrok i dno oka, III-IV-VI ruchy gałek i źrenice, V czucie twarzy i żucie, VII mimika, VIII słuch i równowaga, IX-X gardło i podniebienie, XI SCM/czworoboczny, XII język.",
            "Skala Lovetta: 0 brak skurczu, 1 ślad, 2 ruch w odciążeniu, 3 ruch przeciw grawitacji, 4 ruch przeciw oporowi, 5 norma.",
            "Odruchy: biceps C5-C6, triceps C7, promieniowy C5-C6, kolanowy L3-L4, skokowy S1-S2. Patologiczne: Babiński, Rossolimo, Chaddock, Gordon, Oppenheim.",
            "Móżdżek: ataksja, dysmetria, drżenie zamiarowe, adiadochokineza, oczopląs, mowa skandowana, chód na szerokiej podstawie, hipotonia i odruchy wahadłowe.",
        ],
        "memory": [
            "Różnicuj Romberga: pogorszenie po zamknięciu oczu sugeruje czucie głębokie/przedsionek; móżdżek daje niestabilność także przy oczach otwartych.",
            "Język zbacza w stronę uszkodzenia XII, żuchwa w stronę porażoną V, języczek zwykle w stronę zdrową przy IX/X.",
            "Objaw Lasegue'a to ból po tylnej stronie uda przy unoszeniu wyprostowanej kończyny; Mackiewicz prowokuje ból z przodu uda.",
        ],
        "recall": [
            ["Jak odróżnisz zespół piramidowy od uszkodzenia obwodowego neuronu ruchowego?", "Piramidowy: spastyczność, wygórowane odruchy, objawy patologiczne, niedowład. Obwodowy: wiotkość, zaniki, fascykulacje, osłabione odruchy."],
            ["Jakie trzy próby badają zborność?", "Palec-nos, pięta-kolano oraz szybkie ruchy naprzemienne; do tułowia przydatne siadanie z leżenia bez pomocy rąk."],
            ["Co musi wejść do szybkiego badania nerwów czaszkowych?", "Węch, ostrość/pole widzenia i dno oka, ruchy gałek i źrenice, czucie twarzy, mimika, słuch/równowaga, gardło/podniebienie/głos, barki i język."],
        ],
    },
    {
        "id": "diagnostyka",
        "day": 1,
        "title": "Badania pomocnicze w neurologii",
        "pages": "10-13",
        "pdf_start": 11,
        "pdf_end": 14,
        "time": "50 min",
        "priority": "A",
        "summary": "Najważniejsze jest skojarzenie badania z pytaniem klinicznym: PMR do infekcji, zapaleń, SM i SAH; EEG do padaczki i śpiączki; EMG/ENG do nerwów i mięśni; potencjały do dróg czuciowych i ruchowych.",
        "core": [
            "Punkcja lędźwiowa: zwykle L3-L4, po wykluczeniu wzmożonego ciśnienia śródczaszkowego, zaburzeń krzepnięcia i zakażenia skóry w miejscu wkłucia.",
            "Prawidłowy PMR: wodojasny, ciśnienie ok. 5-18 cm H2O, białko 0,2-0,4 g/l, glukoza 2,2-3,9 mmol/l lub około 65% surowicy, komórki poniżej 5/ul.",
            "Rozszczepienie białkowo-komórkowe: wysokie białko bez istotnej pleocytozy, klasycznie w zapalnej poliradikulopatii.",
            "EEG: alfa 8-13 Hz z tyłu i zanika po otwarciu oczu; beta 14-30 Hz; theta 4-7 Hz; delta 0-3 Hz u czuwającego dorosłego jest patologiczna.",
            "ENG/elektroneurografia: zwolnienie przewodzenia wskazuje na demielinizację, spadek amplitudy na uszkodzenie aksonalne.",
            "EMG: w spoczynku powinna być cisza elektryczna; fascykulacje i fibrylacje sugerują patologię jednostki ruchowej.",
        ],
        "memory": [
            "VEP: fala około 100 ms, wydłużenie latencji sugeruje uszkodzenie drogi wzrokowej.",
            "BAEP: ocena pnia i nerwu VIII, przydatne m.in. w nerwiaku osłonkowym VIII.",
            "SSEP: ocena dróg somatosensorycznych, korzeni, splotów, rdzenia i pnia.",
        ],
        "recall": [
            ["Jakie są przeciwwskazania do punkcji lędźwiowej?", "Wzmożone ciśnienie śródczaszkowe/efekt masy, zaburzenia krzepnięcia oraz proces ropny w okolicy wkłucia."],
            ["Co w PMR sugeruje bakteryjne ZOMR?", "Mętny płyn, wysoka komórkowość z neutrofilami, wysokie białko, obniżona glukoza i często podwyższone mleczany."],
            ["Jak odróżnisz uszkodzenie aksonalne od demielinizacyjnego w ENG?", "Aksonalne obniża amplitudę odpowiedzi, demielinizacyjne zwalnia szybkość przewodzenia i wydłuża latencje."],
        ],
    },
    {
        "id": "zespoly",
        "day": 1,
        "title": "Zespoły neurologiczne i lokalizacja",
        "pages": "14-44",
        "pdf_start": 15,
        "pdf_end": 45,
        "time": "110 min",
        "priority": "A",
        "summary": "To rdzeń egzaminu: objaw ma prowadzić do miejsca uszkodzenia. Ucz się zespołów jako par: objaw dodatni plus lokalizacja.",
        "core": [
            "Zespół piramidowy: niedowład spastyczny, wzmożone napięcie typu scyzorykowego, hiperrefleksja, klonusy, objaw Babińskiego i zanik odruchów powierzchownych.",
            "Zespół pozapiramidowy: zaburzenia ruchu bez typowego niedowładu - hipokinezja, sztywność plastyczna, drżenie spoczynkowe, dystonie, pląsawica, tiki, mioklonie.",
            "Zespół móżdżkowy: ipsilateralna niezborność, dysmetria, drżenie zamiarowe, mowa skandowana, oczopląs, adiadochokineza i chód ataktyczny.",
            "Pień mózgu: myśl o zespołach naprzemiennych - po stronie ogniska objawy nerwu czaszkowego, po stronie przeciwnej objawy piramidowe lub czuciowe.",
            "Wzmożone ciśnienie śródczaszkowe: ból głowy, nudności/wymioty, tarcza zastoinowa, zaburzenia świadomości, porażenie VI i ryzyko wgłobienia.",
            "Płaty: czołowy - osobowość, napęd, ruch i afazja Broki; skroniowy - pamięć, słuch, afazja Wernickego; ciemieniowy - czucie, praksja, schemat ciała; potyliczny - widzenie.",
            "Rdzeń: poprzeczne uszkodzenie daje poziom czucia i niedowład; Brown-Sequard łączy ipsilateralny niedowład i utratę czucia głębokiego z kontralateralną utratą bólu/temperatury.",
        ],
        "memory": [
            "Afazja Broki: rozumienie względnie zachowane, mowa niepłynna. Afazja Wernickego: mowa płynna, ale niezrozumiała i zaburzone rozumienie.",
            "Uszkodzenie neuronu obwodowego daje zaniki i fascykulacje; ośrodkowego - spastyczność i objawy patologiczne.",
            "Zaburzenia korzeniowe są dermatomalne, splotowe obejmują kilka nerwów, nerw obwodowy ma własny obszar czucia i typowy deficyt ruchowy.",
        ],
        "recall": [
            ["Co oznacza zespół naprzemienny?", "Uszkodzenie pnia: po stronie ogniska objawy nerwu czaszkowego, po przeciwnej objawy dróg długich."],
            ["Jak zapamiętać płaty mózgu jednym zdaniem?", "Czołowy wykonuje i hamuje, skroniowy słyszy i pamięta, ciemieniowy czuje i składa ciało/przestrzeń, potyliczny widzi."],
            ["Co jest typowe dla zespołu móżdżkowego?", "Ataksja, dysmetria, drżenie zamiarowe, mowa skandowana, oczopląs, chód na szerokiej podstawie i obniżone napięcie."],
        ],
    },
    {
        "id": "naczyniowe",
        "day": 1,
        "title": "Choroby naczyniowe mózgu i rdzenia",
        "pages": "45-61",
        "pdf_start": 46,
        "pdf_end": 62,
        "time": "100 min",
        "priority": "A",
        "summary": "Udar to nagły deficyt ogniskowy. Najpierw odróżnij niedokrwienie, krwotok, SAH i zakrzepicę żylną, potem dopiero szukaj mechanizmu.",
        "core": [
            "TIA: przemijający epizod ogniskowych objawów niedokrwiennych bez trwałego zawału; traktuj jako alarm udarowy, nie jako 'łagodny incydent'.",
            "Udar niedokrwienny: nagły niedowład, zaburzenia mowy, czucia, widzenia, równowagi; diagnostycznie najpierw obrazowanie, żeby wykluczyć krwotok.",
            "Mechanizmy: miażdżyca dużych tętnic, zator sercowopochodny, choroba małych naczyń, rozwarstwienie, koagulopatie i rzadsze zapalenia/naczyniopatie.",
            "Profilaktyka wtórna: leczenie przyczyny, kontrola RR, lipidów, cukrzycy, rzucenie palenia, leki przeciwpłytkowe lub przeciwkrzepliwe zależnie od mechanizmu.",
            "Krwotok śródmózgowy: częściej ból głowy, wymioty, zaburzenia świadomości i gwałtowne narastanie objawów; typowe tło to nadciśnienie lub angiopatia amyloidowa.",
            "SAH: nagły piorunujący ból głowy, objawy oponowe, nudności/wymioty, możliwa utrata przytomności; klasycznie pęknięcie tętniaka.",
            "Zakrzepica żylna: ból głowy, napady, objawy ogniskowe, obrzęk i krwotoczne zawały; pamiętaj o połogu, antykoncepcji, trombofiliach i infekcjach.",
        ],
        "memory": [
            "Udar tętnicy środkowej mózgu: twarz i kończyna górna, afazja w dominującej półkuli lub zaniedbywanie w niedominującej.",
            "Udar tętnicy przedniej: kończyna dolna, abulia, zaburzenia zachowania i nietrzymanie moczu.",
            "Udar tylnego krążenia: zawroty, ataksja, dyzartria, diplopia, dysfagia, objawy pniowe i zaburzenia świadomości.",
        ],
        "recall": [
            ["Jak klinicznie podejrzysz SAH?", "Nagły 'najgorszy w życiu' ból głowy, objawy oponowe, wymioty, światłowstręt, czasem utrata przytomności."],
            ["Co trzeba wykluczyć przed leczeniem ostrego udaru niedokrwiennego?", "Krwotok i przeciwwskazania do leczenia reperfuzyjnego; pierwszym krokiem jest pilne obrazowanie."],
            ["Jak różni się krwotok od udaru niedokrwiennego?", "Krwotok częściej daje ból głowy, wymioty, szybkie zaburzenia świadomości i obraz krwi w TK; niedokrwienie częściej czysty deficyt ogniskowy."],
        ],
    },
    {
        "id": "infekcje",
        "day": 1,
        "title": "Infekcje OUN",
        "pages": "62-70",
        "pdf_start": 63,
        "pdf_end": 71,
        "time": "65 min",
        "priority": "A",
        "summary": "Największy zysk pamięciowy daje tabela PMR: bakteryjne, wirusowe, gruźlicze/grzybicze. Potem ucz się encefalitis jako zaburzenia świadomości plus objawy ogniskowe/napady.",
        "core": [
            "Ostre bakteryjne ZOMR: gorączka, ból głowy, sztywność karku, zaburzenia świadomości; PMR zwykle neutrofilowy, białko wysokie, glukoza niska.",
            "Wirusowe ZOMR: łagodniejsze, PMR limfocytarny, glukoza zwykle prawidłowa, białko umiarkowanie podwyższone.",
            "Gruźlicze i grzybicze ZOMR: przebieg podostry/przewlekły, limfocyty, wysokie białko i często obniżona glukoza.",
            "Zapalenie mózgu: oprócz objawów oponowych pojawia się zaburzenie świadomości, osobowości, napady, objawy ogniskowe; HSV kojarz z płatem skroniowym.",
            "Ropień mózgu: triada bywa niepełna - ból głowy, gorączka, deficyt ogniskowy; w obrazie efekt masy i wzmacniająca się torebka.",
            "Priony: szybko postępujące otępienie, mioklonie, ataksja, charakterystyczne zmiany EEG/MRI i białko 14-3-3 jako element diagnostyki.",
        ],
        "memory": [
            "Meningitis = opony: ból głowy, gorączka, sztywność karku. Encephalitis = mózg: świadomość, napady, osobowość, ognisko.",
            "Niska glukoza w PMR najbardziej pcha w stronę bakteryjnego, gruźliczego, grzybiczego lub nowotworowego procesu.",
            "Nie czekaj z myśleniem o HSV przy zapaleniu mózgu z objawami skroniowymi.",
        ],
        "recall": [
            ["Jak odróżnisz bakteryjne i wirusowe ZOMR po PMR?", "Bakteryjne: neutrofile, wysokie białko, niska glukoza. Wirusowe: limfocyty, glukoza zwykle prawidłowa, białko umiarkowanie wysokie."],
            ["Co dodaje rozpoznanie zapalenia mózgu ponad ZOMR?", "Zaburzenia świadomości, napady, zmiany zachowania i objawy ogniskowe."],
            ["Z czym kojarzyć CJD?", "Szybko postępujące otępienie, mioklonie, ataksję, zmiany EEG/MRI i biomarkery w PMR."],
        ],
    },
    {
        "id": "demielinizacja",
        "day": 1,
        "title": "Choroby demielinizacyjne",
        "pages": "70-84",
        "pdf_start": 71,
        "pdf_end": 85,
        "time": "90 min",
        "priority": "A",
        "summary": "Klucz to rozproszenie w czasie i przestrzeni. Najwięcej pytań zwykle generuje SM: objawy, MRI, PMR, postacie i leczenie rzutu.",
        "core": [
            "SM: wieloogniskowa demielinizacja OUN, zwykle młodzi dorośli, częściej kobiety; objawy rozsiane w czasie i przestrzeni.",
            "Typowe objawy SM: pozagałkowe zapalenie nerwu wzrokowego, zaburzenia czucia, niedowład, ataksja, diplopia, objaw Lhermitte'a, zaburzenia zwieraczy i zmęczenie.",
            "Diagnostyka SM: MRI mózgu i rdzenia, prążki oligoklonalne w PMR, potencjały wywołane oraz wykluczenie chorób podobnych.",
            "Postacie: rzutowo-remisyjna, wtórnie postępująca, pierwotnie postępująca i postępująco-rzutowa w starszych klasyfikacjach.",
            "Rzut SM: nowe lub nasilone objawy neurologiczne trwające ponad 24 h, bez gorączki i infekcji; leczenie rzutu zwykle wysokodawkowymi steroidami.",
            "NMO/choroba Devica: ciężkie zapalenie nerwu wzrokowego i rdzenia, często rozległe zmiany rdzeniowe; kojarz z przeciwciałami AQP4.",
            "ADEM: zwykle jednofazowe rozsiane zapalenie po infekcji lub szczepieniu, częstsze u dzieci, z encefalopatią.",
            "PML: oportunistyczna infekcja JC u osób z immunosupresją, wieloogniskowe objawy i zmiany istoty białej.",
        ],
        "memory": [
            "SM = czas plus przestrzeń; NMO = wzrok plus długi rdzeń; ADEM = dziecko plus encefalopatia; PML = immunosupresja plus JC.",
            "Objaw Lhermitte'a to prąd wzdłuż kręgosłupa przy zgięciu szyi.",
            "Prążki oligoklonalne wspierają rozpoznanie SM, ale nie zastępują obrazu klinicznego i MRI.",
        ],
        "recall": [
            ["Co znaczy rozsianie w czasie i przestrzeni w SM?", "Różne ogniska OUN oraz epizody/zmiany powstające w różnych momentach."],
            ["Czym NMO różni się od typowego SM?", "Cięższe zajęcie nerwów wzrokowych i rdzenia, często długie zmiany rdzeniowe i związek z AQP4."],
            ["Co to jest rzut SM?", "Nowe lub nasilone objawy neurologiczne trwające ponad 24 godziny, bez infekcji/gorączki jako wyjaśnienia."],
        ],
    },
    {
        "id": "pozapiramidowe",
        "day": 1,
        "title": "Układ pozapiramidowy i zaburzenia ruchowe",
        "pages": "85-99",
        "pdf_start": 86,
        "pdf_end": 100,
        "time": "80 min",
        "priority": "A",
        "summary": "Ucz się po fenotypie ruchu: za mało ruchu, za dużo ruchu, ruch skręcający, ruch nagły, ruch rytmiczny. Parkinsonizm to tylko jeden fragment.",
        "core": [
            "Choroba Parkinsona: bradykinezja plus drżenie spoczynkowe, sztywność lub zaburzenia postawy; często asymetryczny początek.",
            "Objawy niemotoryczne PD: hiposmia, zaparcia, depresja, zaburzenia snu REM, dysautonomia i zaburzenia poznawcze.",
            "Atypowy parkinsonizm: szybka progresja, wczesne upadki, słaba odpowiedź na lewodopę, objawy autonomiczne, spojrzenie pionowe albo wyraźna asymetria korowa.",
            "DLB: otępienie plus parkinsonizm, fluktuacje poznawcze, omamy wzrokowe i nadwrażliwość na neuroleptyki.",
            "MSA: parkinsonizm lub ataksja z nasilonymi objawami autonomicznymi. PSP: wczesne upadki i porażenie spojrzenia pionowego. CBD: asymetryczny zespół korowy i apraksja.",
            "Drżenie samoistne: posturalno-kinetyczne, często rodzinne, poprawa po alkoholu w części przypadków; odróżnij od drżenia spoczynkowego PD.",
            "Huntington: pląsawica, zaburzenia psychiczne i otępienie, dziedziczenie autosomalne dominujące.",
            "Wilson: młody pacjent z zaburzeniami ruchu, psychiatrycznymi lub wątrobowymi; pierścień Kaysera-Fleischera i metabolizm miedzi.",
        ],
        "memory": [
            "PD: 'wolno, sztywno, drży'. ET: 'drży przy działaniu'. Huntington: 'tańczy, zmienia psychikę, dziedziczy AD'.",
            "PSP zapamiętaj przez oczy i upadki; MSA przez autonomię; CBD przez asymetrię i objawy korowe.",
            "Dystonia to utrwalone lub napadowe skręcające skurcze, często zależne od zadania lub pozycji.",
        ],
        "recall": [
            ["Jakie objawy tworzą parkinsonizm?", "Bradykinezja oraz co najmniej jeden z: drżenie spoczynkowe, sztywność, zaburzenia postawy."],
            ["Co sugeruje atypowy parkinsonizm?", "Wczesne upadki, szybki postęp, słaba odpowiedź na lewodopę, ciężka dysautonomia lub zaburzenie spojrzenia pionowego."],
            ["Jak odróżnisz drżenie samoistne od parkinsonowskiego?", "Samoistne jest głównie posturalno-kinetyczne; parkinsonowskie typowo spoczynkowe i z bradykinezją."],
        ],
    },
    {
        "id": "otepienia",
        "day": 2,
        "title": "Otępienia neurozwyrodnieniowe i naczyniowe",
        "pages": "99-107",
        "pdf_start": 100,
        "pdf_end": 108,
        "time": "55 min",
        "priority": "A",
        "summary": "Otępienie to nabyte pogorszenie poznawcze zaburzające funkcjonowanie. Egzaminowo odróżniaj profil pamięciowy, czołowy, lewy-body i naczyniowy.",
        "core": [
            "Choroba Alzheimera: początek zwykle od pamięci epizodycznej, potem język, funkcje wzrokowo-przestrzenne i wykonawcze.",
            "FTD: wczesne zmiany zachowania, odhamowanie, apatia, utrata empatii, stereotypie lub warianty językowe; pamięć może być względnie lepsza na początku.",
            "DLB: fluktuacje poznawcze, omamy wzrokowe, parkinsonizm i zaburzenia snu REM; uwaga na nadwrażliwość na neuroleptyki.",
            "PDD: otępienie rozwija się u chorego z rozpoznaną chorobą Parkinsona, zwykle po okresie objawów ruchowych.",
            "Otępienie naczyniopochodne: związek z udarami lub chorobą małych naczyń, schodkowy lub fluktuujący przebieg, objawy ogniskowe i spowolnienie wykonawcze.",
            "Odwracalne przyczyny zespołów otępiennych do sprawdzenia: depresja, leki, niedoczynność tarczycy, B12, wodogłowie normotensyjne, guzy, infekcje.",
        ],
        "memory": [
            "AD = pamięć; FTD = osobowość/język; DLB = fluktuacje i omamy; naczyniowe = schodki i ogniska.",
            "Wodogłowie normotensyjne: chód, otępienie, nietrzymanie moczu.",
            "Majaczenie jest ostre i fluktuuje z zaburzeniem uwagi; otępienie jest przewlekłe.",
        ],
        "recall": [
            ["Jaka jest triada DLB?", "Fluktuacje poznawcze, omamy wzrokowe i parkinsonizm; często dochodzi zaburzenie snu REM."],
            ["Co przemawia za FTD zamiast AD?", "Wczesne zmiany zachowania, odhamowanie/apatie, stereotypie lub pierwotne zaburzenia języka."],
            ["Jak zapamiętać otępienie naczyniowe?", "Schodkowy przebieg, czynniki naczyniowe, objawy ogniskowe i przewaga zaburzeń wykonawczych."],
        ],
    },
    {
        "id": "bole_zawroty",
        "day": 2,
        "title": "Bóle głowy i zawroty",
        "pages": "107-114",
        "pdf_start": 108,
        "pdf_end": 115,
        "time": "70 min",
        "priority": "A",
        "summary": "Najpierw rozpoznaj czerwone flagi, potem klasyfikuj ból pierwotny. W zawrotach oddziel vertigo obwodowe od centralnego.",
        "core": [
            "Migrena: napadowy, zwykle jednostronny pulsujący ból, nudności, foto-/fonofobia, nasilenie przy aktywności; może być aura.",
            "Napięciowy ból głowy: obustronny, uciskowy, łagodny/umiarkowany, bez typowych nudności i bez nasilania wysiłkiem.",
            "Klasterowy ból głowy: bardzo silny jednostronny ból oczodołowo-skroniowy z objawami autonomicznymi, seriami napadów.",
            "Czerwone flagi: nagły piorunujący początek, nowy ból po 50 r.ż., gorączka/oponowe, deficyt ogniskowy, nowotwór/immunosupresja, ciąża/połóg, ból po urazie.",
            "Vertigo obwodowe: silne wirowanie, nudności, oczopląs zwykle jednokierunkowy, zaburzenia słuchu możliwe, bez innych objawów pniowych.",
            "Vertigo centralne: objawy neurologiczne, ataksja, dyzartria, diplopia, oczopląs pionowy/zmienny lub nieproporcjonalnie ciężki chód.",
            "BPPV: krótkie napady po zmianie pozycji głowy. Meniere: napady vertigo plus fluktuacyjny niedosłuch, szum i pełność ucha.",
        ],
        "memory": [
            "Migrena lubi ciemność; napięciowy ściska; klaster budzi i łzawi.",
            "W zawrotach centralnych szukaj móżdżku i pnia, nie samego błędnika.",
            "Piorunujący ból głowy to SAH, dopóki nie udowodnisz inaczej w materiale egzaminacyjnym.",
        ],
        "recall": [
            ["Jakie są trzy najważniejsze pierwotne bóle głowy?", "Migrena, napięciowy ból głowy i klasterowy ból głowy."],
            ["Co sugeruje centralne zawroty głowy?", "Objawy pniowe/móżdżkowe, ciężka ataksja, dyzartria, diplopia, pionowy lub zmienny oczopląs."],
            ["Czym jest BPPV?", "Krótkie napady zawrotu układowego wywołane zmianą pozycji głowy."],
        ],
    },
    {
        "id": "padaczka",
        "day": 2,
        "title": "Padaczka",
        "pages": "114-119",
        "pdf_start": 115,
        "pdf_end": 120,
        "time": "65 min",
        "priority": "A",
        "summary": "Ucz się sekwencji: napad prowokowany czy nie, ogniskowy czy uogólniony, z zachowaną czy zaburzoną świadomością, jaki zespół i jakie leczenie.",
        "core": [
            "Napad padaczkowy to przemijające objawy wynikające z nadmiernej, synchronicznej czynności neuronów.",
            "Padaczka to skłonność do nawracających nieprowokowanych napadów; pojedynczy napad prowokowany nie musi oznaczać padaczki.",
            "Napady ogniskowe mogą przebiegać bez zaburzeń świadomości lub z zaburzeniami świadomości i mogą wtórnie uogólniać się.",
            "Napady uogólnione: nieświadomości, miokloniczne, toniczne, kloniczne, toniczno-kloniczne, atoniczne.",
            "Diagnostyka: dokładny opis napadu/świadek, EEG, neuroobrazowanie przy podejrzeniu przyczyny strukturalnej, badania metaboliczne i różnicowanie omdleń.",
            "Stan padaczkowy: napad przedłużony lub seria bez odzyskania świadomości; wymaga pilnego leczenia.",
        ],
        "memory": [
            "Ogniskowy zaczyna się w jednej sieci, uogólniony od razu obejmuje obie półkule.",
            "Absence: krótkie wyłączenia, często prowokowane hiperwentylacją, bez splątania ponapadowego.",
            "Po napadzie toniczno-klonicznym oczekuj fazy ponapadowej: senność, splątanie, bóle mięśni, przygryzienie języka.",
        ],
        "recall": [
            ["Jak rozróżnić napad ogniskowy i uogólniony?", "Ogniskowy zaczyna się lokalnie i może dawać aurę/objawy ogniskowe; uogólniony od początku obejmuje obie półkule."],
            ["Co to jest stan padaczkowy?", "Przedłużony napad lub napady bez powrotu świadomości między nimi, stan pilny neurologiczny."],
            ["Jakie są typy napadów uogólnionych?", "Nieświadomości, miokloniczne, toniczne, kloniczne, toniczno-kloniczne i atoniczne."],
        ],
    },
    {
        "id": "guzy_urazy",
        "day": 2,
        "title": "Guzy OUN i urazy czaszkowo-mózgowe",
        "pages": "119-129",
        "pdf_start": 120,
        "pdf_end": 130,
        "time": "70 min",
        "priority": "B",
        "summary": "Guzy dają ognisko, padaczkę i ciasnotę; urazy wymagają rozpoznania krwiaka po czasie narastania objawów i obrazie klinicznym.",
        "core": [
            "Guzy śródczaszkowe: objawy ogólne z ciasnoty, napady padaczkowe, deficyty ogniskowe i zmiany psychiczne zależne od lokalizacji.",
            "Ciasnota śródczaszkowa: ból głowy, wymioty, tarcza zastoinowa, senność, porażenie VI i ryzyko wgłobienia.",
            "Guzy rdzenia/kanału kręgowego: ból korzeniowy, narastający niedowład, zaburzenia czucia z poziomem i zaburzenia zwieraczy.",
            "Przerzuty do OUN są częstsze niż pierwotne guzy u dorosłych; myśl o płucu, piersi, czerniaku, nerce i przewodzie pokarmowym.",
            "Krwiak nadtwardówkowy: często uraz tętnicy oponowej środkowej, możliwy 'jasny okres', szybkie narastanie.",
            "Krwiak podtwardówkowy: uszkodzenie żył pomostowych, częsty u starszych i po alkoholu, może narastać przewlekle.",
            "Wstrząśnienie: przemijające zaburzenia czynności bez trwałego uszkodzenia strukturalnego; stłuczenie i DAI mają cięższy obraz.",
        ],
        "memory": [
            "Nadtwardówkowy = tętnica i jasny okres; podtwardówkowy = żyły i starszy pacjent; podpajęczynówkowy = piorunujący ból.",
            "Guz powoli narasta, udar jest nagły, infekcja zwykle ma gorączkę/stan zapalny - tempo pomaga.",
            "Objawy rdzeniowe plus ból nocny/nowotwór w wywiadzie traktuj jako kompresję do wykluczenia.",
        ],
        "recall": [
            ["Jakie są objawy ciasnoty śródczaszkowej?", "Ból głowy, nudności/wymioty, tarcza zastoinowa, senność, porażenie VI i objawy wgłobienia."],
            ["Jak odróżnić krwiak nadtwardówkowy od podtwardówkowego?", "Nadtwardówkowy zwykle tętniczy i szybki z jasnym okresem; podtwardówkowy żylny, częściej starsi, może być przewlekły."],
            ["Jakie objawy sugerują guz kanału kręgowego?", "Ból korzeniowy, narastający niedowład, poziom czucia i zaburzenia zwieraczy."],
        ],
    },
    {
        "id": "toksyczne_sen",
        "day": 2,
        "title": "Toksyczne uszkodzenia OUN i zaburzenia snu",
        "pages": "129-139",
        "pdf_start": 130,
        "pdf_end": 140,
        "time": "50 min",
        "priority": "B",
        "summary": "Tu liczą się zespoły rozpoznawane po kontekście: ekspozycja, alkohol/leki/narkotyki, zaburzenia świadomości oraz typowe parasomnie i bezsenność.",
        "core": [
            "Zatrucia neurologiczne dają encefalopatię, drgawki, neuropatie, objawy pozapiramidowe, zaburzenia autonomiczne lub śpiączkę - zawsze pytaj o ekspozycję.",
            "Alkohol: ostre zatrucie, zespół abstynencyjny, majaczenie drżenne, encefalopatia Wernickego, zespół Korsakowa, polineuropatia i zwyrodnienie móżdżku.",
            "Encefalopatia Wernickego: zaburzenia świadomości, ataksja, oftalmoplegia; kojarz z niedoborem tiaminy.",
            "Leki i narkotyki: obraz zależy od grupy, ale kluczowe są źrenice, oddech, temperatura, napięcie mięśniowe, drgawki i rytm serca.",
            "Bezsenność: trudność zasypiania, utrzymania snu lub wczesne budzenie z pogorszeniem funkcjonowania.",
            "Narkolepsja: nadmierna senność dzienna, katapleksja, porażenie przysenne i omamy hipnagogiczne/hipnopompiczne.",
            "Zaburzenia snu REM: odgrywanie marzeń sennych, ważne jako objaw prodromalny synukleinopatii.",
        ],
        "memory": [
            "Wernicke: daj tiaminę w głowie przed glukozą w scenariuszach niedożywienia/alkoholu.",
            "REM behavior disorder łączy się z PD, DLB i MSA.",
            "Toksykologia neurologiczna to wzorzec: świadomość + źrenice + oddech + temperatura + ruchy.",
        ],
        "recall": [
            ["Jaka jest triada Wernickego?", "Zaburzenia świadomości, ataksja i oftalmoplegia, choć pełna triada nie zawsze występuje."],
            ["Co sugeruje narkolepsję?", "Napady senności dziennej, katapleksja, porażenie przysenne i omamy okołosnowe."],
            ["Dlaczego zaburzenie zachowania w REM jest ważne neurologicznie?", "Może poprzedzać synukleinopatie, m.in. chorobę Parkinsona, DLB i MSA."],
        ],
    },
    {
        "id": "swiadomosc",
        "day": 2,
        "title": "Zaburzenia świadomości, śpiączka i śmierć mózgu",
        "pages": "139-143",
        "pdf_start": 140,
        "pdf_end": 144,
        "time": "45 min",
        "priority": "A",
        "summary": "Najpierw ABC i przyczyny odwracalne, potem skale i odruchy pniowe. W śmierci mózgu egzamin pyta o brak czynności pnia i warunki rozpoznania.",
        "core": [
            "Świadomość ma komponent przytomności i treści; zaburzenia mogą wynikać z uszkodzenia pnia/układu siatkowatego albo rozlanego uszkodzenia półkul.",
            "Ocena śpiączki: reakcja na bodźce, źrenice, ruchy gałek, odruchy pniowe, tor oddychania, napięcie i objawy ogniskowe.",
            "GCS obejmuje otwieranie oczu, odpowiedź słowną i ruchową; pomaga opisać ciężkość, ale nie zastępuje lokalizacji.",
            "Przyczyny śpiączki: strukturalne, metaboliczne, toksyczne, infekcyjne, napadowe, pourazowe i naczyniowe.",
            "Śmierć mózgu: nieodwracalne ustanie czynności całego mózgu, zwłaszcza pnia, przy spełnieniu warunków i wykluczeniu czynników odwracalnych.",
            "Odruchy pniowe: źreniczny, rogówkowy, oczno-mózgowy/kaloryczny, kaszlowy, wymiotny oraz próba bezdechu w odpowiednim protokole.",
        ],
        "memory": [
            "Śpiączka metaboliczna zwykle jest bardziej symetryczna; ogniskowe objawy i asymetria źrenic pchają w stronę strukturalną.",
            "Przed rozpoznaniem śmierci mózgu trzeba wykluczyć hipotermię, zatrucia, leki depresyjne i zaburzenia metaboliczne.",
            "Pnień mózgu testujesz oczami, źrenicami, rogówką, kaszlem, oddechem.",
        ],
        "recall": [
            ["Jakie elementy obejmuje GCS?", "Otwieranie oczu, odpowiedź słowną i odpowiedź ruchową."],
            ["Co trzeba wykluczyć przed rozpoznaniem śmierci mózgu?", "Stany odwracalne: hipotermię, zatrucia/leki, ciężkie zaburzenia metaboliczne i krążeniowe."],
            ["Co sugeruje strukturalną przyczynę śpiączki?", "Asymetria neurologiczna, ogniskowe objawy, nierówne źrenice, objawy wgłobienia."],
        ],
    },
    {
        "id": "obwodowe",
        "day": 2,
        "title": "Nerwy obwodowe, złącze nerwowo-mięśniowe i mięśnie",
        "pages": "143-154",
        "pdf_start": 144,
        "pdf_end": 155,
        "time": "90 min",
        "priority": "A",
        "summary": "Najpierw ustal poziom: korzeń, splot, nerw, polineuropatia, złącze, mięsień. Potem pytaj o symetrię, czucie, odruchy i męczliwość.",
        "core": [
            "Polineuropatia: zwykle symetryczne, dystalne zaburzenia czucia i osłabienie, często 'skarpetki i rękawiczki', osłabione odruchy.",
            "Neuropatia aksonalna: spadek amplitudy w ENG, często dystalna. Demielinizacyjna: zwolnienie przewodzenia, bloki i wydłużone latencje.",
            "GBS: ostra zapalna poliradikuloneuropatia, wstępujące osłabienie, arefleksja, możliwe zaburzenia autonomiczne i oddechowe, rozszczepienie białkowo-komórkowe w PMR.",
            "CIDP: przewlekły odpowiednik demielinizacyjny z postępem ponad tygodnie/miesiące.",
            "Miastenia: męczliwość, opadanie powiek, diplopia, dyzartria/dysfagia, poprawa po odpoczynku; przeciwciała przeciw AChR lub MuSK.",
            "Lambert-Eaton: osłabienie proksymalne, autonomiczne objawy, poprawa siły po wysiłku, związek z rakiem drobnokomórkowym płuca.",
            "Miopatie: osłabienie proksymalne, odruchy długo zachowane, brak typowych zaburzeń czucia; CK często podwyższone w miopatiach zapalnych/dystrofiach.",
            "Dystrofie mięśniowe: genetyczne, postępujące zaniki i osłabienie; Duchenne ciężki, wczesny, sprzężony z X.",
        ],
        "memory": [
            "Nerw = czucie plus odruchy; mięsień = proksymalne osłabienie bez czucia; złącze = męczliwość.",
            "Miastenia pogarsza się wysiłkiem, Lambert-Eaton może chwilowo poprawiać się po aktywacji.",
            "GBS pilnuje oddechu i autonomii.",
        ],
        "recall": [
            ["Jak odróżnisz miopatię od neuropatii?", "Miopatia: proksymalne osłabienie bez zaburzeń czucia; neuropatia: czucie, odruchy i dystalny rozkład."],
            ["Co jest typowe dla miastenii?", "Męczliwość, ptoza, diplopia, objawy opuszkowe i poprawa po odpoczynku."],
            ["Co w GBS jest groźne życiowo?", "Niewydolność oddechowa i zaburzenia autonomiczne."],
        ],
    },
    {
        "id": "neuron",
        "day": 2,
        "title": "Choroby neuronu ruchowego",
        "pages": "154-156",
        "pdf_start": 155,
        "pdf_end": 157,
        "time": "35 min",
        "priority": "A",
        "summary": "Szukaj połączenia objawów górnego i dolnego neuronu ruchowego bez zaburzeń czucia. To najbardziej egzaminacyjny filtr dla SLA.",
        "core": [
            "SLA/ALS: współistnienie objawów górnego i dolnego neuronu ruchowego w różnych regionach, postęp, brak istotnych zaburzeń czucia.",
            "Objawy górnego neuronu: spastyczność, wygórowane odruchy, Babiński. Objawy dolnego: zaniki, fascykulacje, osłabienie, obniżone odruchy.",
            "Postać opuszkowa: dyzartria, dysfagia, zanik/fascykulacje języka, ryzyko aspiracji.",
            "SMA: genetyczna choroba dolnego neuronu ruchowego z wiotkością i zanikiem mięśni.",
            "Choroba Kennedy'ego/SBMA: sprzężona z X, objawy opuszkowo-rdzeniowe i cechy androgenowe.",
        ],
        "memory": [
            "SLA = ruch bez czucia, UMN plus LMN, postępuje.",
            "Fascykulacje języka i dysfagia każą myśleć o opuszkowym zajęciu neuronu ruchowego.",
            "SMA to dolny neuron, nie mieszany obraz jak SLA.",
        ],
        "recall": [
            ["Jaki zestaw objawów sugeruje SLA?", "Jednoczesne cechy górnego i dolnego neuronu ruchowego, progresja i brak wyraźnych zaburzeń czucia."],
            ["Wymień objawy dolnego neuronu ruchowego.", "Zaniki, fascykulacje, wiotkość/osłabienie i osłabienie odruchów."],
            ["Co oznacza postać opuszkowa?", "Zajęcie mowy, połykania i języka: dyzartria, dysfagia, fascykulacje/zanik języka."],
        ],
    },
    {
        "id": "systemowe_psychiczne",
        "day": 2,
        "title": "Neurologia w chorobach systemowych i zaburzenia psychiczne",
        "pages": "156-164",
        "pdf_start": 157,
        "pdf_end": 165,
        "time": "50 min",
        "priority": "B",
        "summary": "Tu najczęściej chodzi o skojarzenia: choroba ogólnoustrojowa może dawać encefalopatię, neuropatię, miopatię, udary albo napady.",
        "core": [
            "Zaburzenia metaboliczne mogą dawać encefalopatię, śpiączkę, drgawki, mioklonie i neuropatie - zawsze myśl o glukozie, sodzie, nerkach, wątrobie i tarczycy.",
            "Cukrzyca: polineuropatia dystalna, mononeuropatie, radikulopleksopatia, ryzyko udaru i encefalopatii przy zaburzeniach glikemii.",
            "Choroby tarczycy: miopatie, neuropatie, zaburzenia poznawcze i nastroju; niedoczynność może przypominać spowolnienie/otępienie.",
            "Niedobory: B12 daje mielopatię sznurową, neuropatię i zaburzenia poznawcze; tiamina daje Wernickego.",
            "Choroby autoimmunologiczne i nowotwory mogą wywoływać zapalenia naczyń, neuropatie, encefalopatie i zespoły paranowotworowe.",
            "Zaburzenia psychiczne w neurologii: depresja po udarze, apatia i odhamowanie w chorobach czołowych, psychozy w DLB/PD, lęk i depresja w SM.",
        ],
        "memory": [
            "B12 = sznury tylne plus piramidy plus neuropatia.",
            "Neurologiczny objaw u pacjenta z rakiem może być przerzutem, zakrzepicą, lekiem albo paranowotworowy.",
            "Depresja może udawać otępienie, ale też często współistnieje z chorobą neurologiczną.",
        ],
        "recall": [
            ["Jakie badania ogólne warto mieć w głowie przy encefalopatii?", "Glukoza, elektrolity, nerki, wątroba, gazometria, tarczyca, infekcja i toksykologia zależnie od kontekstu."],
            ["Co neurologicznie daje niedobór B12?", "Mielopatię sznurową, neuropatię, zaburzenia poznawcze i niedokrwistość jako trop ogólny."],
            ["Dlaczego nowotwór jest ważny neurologicznie?", "Może dawać przerzuty, zakrzepicę, powikłania leczenia i zespoły paranowotworowe."],
        ],
    },
    {
        "id": "bol_rozwoj",
        "day": 2,
        "title": "Ból, wady rozwoju OUN i neurologia dziecięca",
        "pages": "164-172",
        "pdf_start": 165,
        "pdf_end": 173,
        "time": "60 min",
        "priority": "B",
        "summary": "Końcowe rozdziały ucz jako definicje i rozpoznawanie wzorców: typ bólu, dziedziczenie/wady rozwoju, MPD i stany napadowe u dzieci.",
        "core": [
            "Ból receptorowy/nocyceptywny wynika z pobudzenia receptorów bólowych; neuropatyczny z uszkodzenia układu somatosensorycznego; psychogenny z dominującym mechanizmem psychologicznym.",
            "Ból neuropatyczny: pieczenie, prąd, kłucie, allodynia, hiperalgezja, zaburzenia czucia i możliwy brak proporcji do bodźca.",
            "Leczenie bólu: dobór do mechanizmu - nocyceptywny reaguje na klasyczne analgetyki, neuropatyczny często wymaga leków przeciwpadaczkowych/przeciwdepresyjnych.",
            "Zaburzenia rozwoju OUN: kojarz aberracje chromosomalne, mutacje genowe, dziedziczenie wieloczynnikowe i czynniki środowiskowe w okresie płodowym.",
            "MPD: trwałe, niepostępujące zaburzenie ruchu i postawy wynikające z uszkodzenia rozwijającego się mózgu; objawy zmieniają się wraz z rozwojem dziecka.",
            "Stany napadowe u dzieci: trzeba różnicować padaczkę z omdleniami, napadami afektywnego bezdechu, tikami, parasomniami i migreną.",
        ],
        "memory": [
            "Neuropatyczny ból mówi językiem prądu, palenia i allodynii.",
            "MPD nie jest chorobą postępującą, ale potrzeby dziecka zmieniają się z wiekiem.",
            "U dzieci nie każdy napad jest padaczką; opis świadka jest złotem.",
        ],
        "recall": [
            ["Jak odróżnisz ból neuropatyczny od receptorowego?", "Neuropatyczny ma pieczenie/prąd/allodynię i zaburzenia czucia; receptorowy wiąże się z uszkodzeniem tkanek i zapaleniem."],
            ["Czym jest MPD?", "Trwałym, niepostępującym zaburzeniem ruchu i postawy po uszkodzeniu rozwijającego się mózgu."],
            ["Co różnicować z padaczką u dziecka?", "Omdlenia, napady afektywnego bezdechu, tiki, parasomnie, migrenę i zaburzenia psychogenne."],
        ],
    },
]


PLAN = [
    {
        "day": 1,
        "title": "Dzisiaj od 19:15 - rdzeń, lokalizacja, rzeczy najbardziej pytalne",
        "blocks": [
            "19:15-19:30: otwórz HTML, przejrzyj mapę priorytetów i zaznacz tematy, które brzmią obco.",
            "19:30-20:35: badanie neurologiczne + badania pomocnicze. Po bloku bez patrzenia: nerwy czaszkowe, Lovett, PMR, EEG/ENG/EMG.",
            "20:35-22:00: zespoły neurologiczne. Rysuj lokalizację: kora, pień, rdzeń, korzeń, nerw, mięsień.",
            "22:00-22:15: przerwa bez doczytywania. Mózg też musi mieć miejsce na zapis.",
            "22:15-23:05: udary. Ucz się algorytmami: nagłe ognisko, naczynie, krwotok, SAH, zakrzepica żylna.",
            "23:05-23:50: infekcje OUN i PMR. Tabela bakteryjne/wirusowe/gruźlicze musi wejść z pamięci.",
            "23:50-00:30: SM/NMO/ADEM/PML oraz Parkinsonizmy tylko przez fiszki i pytania kontrolne.",
            "00:30: stop. Jeśli nie zdążysz, nie nadrabiaj kosztem snu - przenieś pozapiramidowe na jutro rano.",
        ],
    },
    {
        "day": 2,
        "title": "Jutro - domknięcie materiału i brutalne odpytywanie",
        "blocks": [
            "08:30-09:00: rozruch - fiszki z priorytetu A, bez czytania rozdziałów.",
            "09:00-10:20: demielinizacja i zaburzenia ruchowe, jeśli nie weszły dzisiaj.",
            "10:20-12:00: otępienia, bóle głowy, zawroty i padaczka. Po każdym temacie test ustny bez patrzenia.",
            "12:00-13:00: guzy, urazy, toksyny, sen. Zapamiętaj tempo narastania objawów.",
            "13:00-14:00: przerwa i lekki powrót do fiszek, nie pełne czytanie.",
            "14:00-14:45: świadomość, śpiączka, śmierć mózgu.",
            "14:45-16:45: nerwy obwodowe, złącze, mięśnie. Różnicuj poziom uszkodzenia.",
            "16:45-17:20: neuron ruchowy, SLA/SMA/Kennedy.",
            "17:20-18:10: systemowe, ból, wady rozwoju, dzieci.",
            "18:30-20:00: pełny test ustny z HTML. Wszystko, co nie wychodzi w 20 sekund, wraca do fiszek.",
            "20:00-21:00: tryb Ostatnia godzina - tylko priorytet A i lista 'muszę umieć'.",
        ],
    },
]


VISUALS: dict[str, dict[str, Any]] = {
    "badanie": {
        "tables": [
            {
                "title": "Lokalizacja po badaniu - szybka tabela",
                "columns": ["Wzorzec", "Najważniejsze objawy", "Co to lokalizuje"],
                "rows": [
                    ["Górny neuron ruchowy", "Spastyczność, hiperrefleksja, Babiński, małe zaniki", "Droga piramidowa w OUN"],
                    ["Dolny neuron ruchowy", "Wiotkość, zaniki, fascykulacje, osłabione odruchy", "Róg przedni, korzeń, nerw"],
                    ["Móżdżek", "Ataksja, dysmetria, drżenie zamiarowe, mowa skandowana", "Półkula/robak móżdżku"],
                    ["Korzeń", "Ból promieniujący, dermatom, odruch segmentalny", "Radikulopatia"],
                    ["Nerw obwodowy", "Deficyt w obszarze nerwu, czucie + ruch", "Mononeuropatia"],
                ],
            },
            {
                "title": "Nerwy czaszkowe - minimum egzaminacyjne",
                "columns": ["NC", "Funkcja", "Objaw uszkodzenia"],
                "rows": [
                    ["I", "Węch", "Anosmia"],
                    ["II", "Wzrok, pole widzenia, dno oka", "Ubytek pola, spadek ostrości, tarcza zastoinowa"],
                    ["III/IV/VI", "Ruchy gałek, źrenice", "Diplopia, ptoza, zez, zaburzenia reakcji źrenic"],
                    ["V", "Czucie twarzy, żucie, rogówkowy", "Ból/czucie twarzy, żuchwa w stronę porażoną"],
                    ["VII", "Mimika, smak 2/3 języka", "Asymetria twarzy, niedomykanie oka"],
                    ["VIII", "Słuch i równowaga", "Niedosłuch, szum, zawroty, oczopląs"],
                    ["IX/X", "Gardło, podniebienie, głos", "Dysfagia, chrypka, języczek w stronę zdrową"],
                    ["XI/XII", "SCM/czworoboczny, język", "Słabe barki/skręt głowy, język w stronę chorą"],
                ],
            },
        ],
        "schemes": [
            ["Niedowład", "sprawdź napięcie i odruchy", "spastyczny = OUN, wiotki = obwód"],
            ["Zaburzenie chodu", "móżdżkowy szeroka podstawa", "parkinsonowski drobne kroki", "czuciowy pogarsza się po zamknięciu oczu"],
        ],
    },
    "diagnostyka": {
        "tables": [
            {
                "title": "PMR - różnicowanie w 30 sekund",
                "columns": ["Stan", "Komórki", "Białko", "Glukoza", "Skojarzenie"],
                "rows": [
                    ["Norma", "<5/ul", "0,2-0,4 g/l", "ok. 65% surowicy", "wodojasny"],
                    ["Bakteryjne ZOMR", "neutrofile", "wysokie", "niskie", "ostry ciężki stan"],
                    ["Wirusowe ZOMR", "limfocyty", "umiarkowanie wysokie", "zwykle norma", "łagodniejsze"],
                    ["Gruźlicze/grzybicze", "limfocyty", "wysokie", "często niskie", "podostre/przewlekłe"],
                    ["GBS", "komórek mało", "wysokie", "norma", "rozszczepienie białkowo-komórkowe"],
                    ["SM", "limfocyty czasem", "zwykle umiarkowane", "norma", "prążki oligoklonalne"],
                    ["SAH", "RBC/ksantochromia", "zmienne", "norma", "gdy TK nie rozstrzyga"],
                ],
            },
            {
                "title": "Badanie pomocnicze - co wybrać",
                "columns": ["Problem", "Badanie", "Po co"],
                "rows": [
                    ["Padaczka/śpiączka", "EEG", "iglice, fale ostre, rytmy patologiczne"],
                    ["Demielinizacja drogi wzrokowej", "VEP", "wydłużenie latencji P100"],
                    ["Nerw VIII/pień", "BAEP", "droga słuchowa i pień"],
                    ["Korzeń/splot/rdzeń", "SSEP", "droga czuciowa"],
                    ["Neuropatia", "ENG", "aksonalna = amplituda, demielinizacja = szybkość"],
                    ["Mięsień/jednostka ruchowa", "EMG", "fibrylacje, fascykulacje, wzorzec miogenny/neurogenny"],
                ],
            },
        ],
        "schemes": [
            ["Podejrzenie ZOMR", "oceń przeciwwskazania do punkcji", "PMR + posiew/PCR", "leczenie empiryczne nie czeka na perfekcyjny wynik"],
            ["Osłabienie kończyn", "ENG/EMG", "amplituda niska = akson", "przewodzenie wolne = mielina"],
        ],
    },
    "zespoly": {
        "tables": [
            {
                "title": "Zespoły neurologiczne - objaw prowadzi do miejsca",
                "columns": ["Zespół", "Objawy kluczowe", "Najważniejsza myśl"],
                "rows": [
                    ["Piramidowy", "spastyczność, hiperrefleksja, Babiński", "droga korowo-rdzeniowa"],
                    ["Pozapiramidowy", "bradykinezja, sztywność, drżenia, pląsawice, dystonie", "jądra podstawy"],
                    ["Móżdżkowy", "dysmetria, ataksja, oczopląs, mowa skandowana", "koordynacja po stronie uszkodzenia"],
                    ["Pniowy naprzemienny", "NC po stronie ogniska + drogi długie po przeciwnej", "pień mózgu"],
                    ["Oponowy", "sztywność karku, Kernig/Brudziński, światłowstręt", "opony: infekcja lub SAH"],
                    ["Ciasnota", "ból głowy, wymioty, tarcza zastoinowa, VI", "wzrost ciśnienia śródczaszkowego"],
                    ["Rdzeniowy", "poziom czucia, niedowład, zwieracze", "rdzeń/ucisk"],
                ],
            },
            {
                "title": "Płaty mózgu - skrót objawów",
                "columns": ["Płat", "Co robi", "Uszkodzenie"],
                "rows": [
                    ["Czołowy", "napęd, osobowość, funkcje wykonawcze, ruch", "odhamowanie/apatie, afazja Broki, niedowład"],
                    ["Skroniowy", "pamięć, słuch, rozumienie mowy", "afazja Wernickego, zaburzenia pamięci, napady skroniowe"],
                    ["Ciemieniowy", "czucie, przestrzeń, schemat ciała", "zaniedbywanie, apraksja, agnozje, zaburzenia czucia"],
                    ["Potyliczny", "widzenie", "ubytki pola, agnozje wzrokowe"],
                ],
            },
        ],
        "schemes": [
            ["Objaw nerwu czaszkowego + niedowład po przeciwnej", "pień mózgu", "myśl: zespół naprzemienny"],
            ["Poziom czucia + zwieracze", "rdzeń", "pilnie różnicuj ucisk, zapalenie, niedokrwienie"],
        ],
    },
    "naczyniowe": {
        "tables": [
            {
                "title": "Udar - różnicowanie typów",
                "columns": ["Typ", "Początek/objawy", "Trop", "Pierwsza myśl"],
                "rows": [
                    ["Niedokrwienny", "nagły deficyt ogniskowy", "afazja/niedowład/hemianopsja", "TK/MRI wyklucz krwotok"],
                    ["TIA", "objawy ustępują", "alarm, nie błahostka", "profilaktyka wtórna"],
                    ["Krwotok śródmózgowy", "nagły deficyt + ból/wymioty/świadomość", "nadciśnienie, amyloid", "krew w TK"],
                    ["SAH", "piorunujący ból głowy, oponowe", "tętniak", "TK, potem PMR/angiografia wg scenariusza"],
                    ["Zakrzepica żylna", "ból głowy, napady, ogniska, obrzęk", "połóg, antykoncepcja, trombofilia", "MR/angio żylne"],
                ],
            },
            {
                "title": "Tętnice mózgowe - skojarzenia",
                "columns": ["Naczynie", "Objawy"],
                "rows": [
                    ["MCA", "twarz i kończyna górna, afazja w dominującej, zaniedbywanie w niedominującej"],
                    ["ACA", "kończyna dolna, abulia, nietrzymanie moczu, zmiany zachowania"],
                    ["PCA", "hemianopsja, objawy wzrokowe, możliwe zaburzenia pamięci"],
                    ["Krążenie tylne", "zawroty, ataksja, diplopia, dyzartria, dysfagia, zaburzenia świadomości"],
                    ["Lakunarny", "czysty niedowład/czucie, ataksja-hemipareza, dyzartria-niezgrabna ręka"],
                ],
            },
        ],
        "schemes": [
            ["Nagły deficyt ogniskowy", "TK bez kontrastu", "krew = krwotok", "brak krwi + okno = myśl reperfuzja"],
            ["Najgorszy ból głowy w życiu", "SAH do wykluczenia", "objawy oponowe wzmacniają trop"],
        ],
    },
    "infekcje": {
        "tables": [
            {
                "title": "ZOMR i zapalenie mózgu - co odróżnia",
                "columns": ["Rozpoznanie", "Objawy", "PMR / trop"],
                "rows": [
                    ["Bakteryjne ZOMR", "gorączka, ból głowy, oponowe, ciężki stan", "neutrofile, białko wysokie, glukoza niska"],
                    ["Wirusowe ZOMR", "oponowe, zwykle łagodniej", "limfocyty, glukoza zwykle prawidłowa"],
                    ["Encephalitis", "świadomość, napady, zachowanie, ogniskowe", "HSV lub inne wirusy, MRI/EEG/PCR"],
                    ["Ropień", "ból głowy, gorączka, ognisko, efekt masy", "obrazowanie; punkcja często ryzykowna"],
                    ["Priony", "szybkie otępienie, mioklonie, ataksja", "EEG/MRI, 14-3-3 jako trop"],
                ],
            }
        ],
        "schemes": [
            ["Oponowe bez zaburzeń świadomości", "myśl ZOMR", "PMR różnicuje bakteryjne/wirusowe/TB"],
            ["Oponowe + świadomość/napady/osobowość", "myśl zapalenie mózgu", "HSV lubi skronie"],
        ],
    },
    "demielinizacja": {
        "tables": [
            {
                "title": "Demielinizacja - cztery najważniejsze jednostki",
                "columns": ["Jednostka", "Klucz", "Diagnostyczny skrót"],
                "rows": [
                    ["SM", "rozsianie w czasie i przestrzeni", "MRI + PMR prążki oligoklonalne + wykluczenia"],
                    ["NMO/Devic", "ciężki nerw wzrokowy + długi rdzeń", "AQP4, rozległe LETM"],
                    ["ADEM", "dziecko/młody, po infekcji, encefalopatia", "często jednofazowe"],
                    ["PML", "immunosupresja, JC, wieloogniskowa istota biała", "postępujące objawy bez typowego rzutu"],
                ],
            },
            {
                "title": "SM - najczęstsze haczyki",
                "columns": ["Hasło", "Zapamiętaj"],
                "rows": [
                    ["Rzut", "nowe/nasilone objawy >24 h, bez infekcji/gorączki"],
                    ["Objawy", "PZNW, czucie, niedowład, ataksja, diplopia, Lhermitte, zwieracze"],
                    ["Postacie", "RRMS, SPMS, PPMS; myśl o progresji i rzutach"],
                    ["Leczenie rzutu", "wysokodawkowe steroidy w typowym schemacie egzaminacyjnym"],
                ],
            },
        ],
        "schemes": [
            ["Młoda osoba + epizody neurologiczne w różnych miejscach", "SM", "MRI + PMR"],
            ["Obustronny/ciężki wzrok + długi rdzeń", "NMO bardziej niż SM"],
        ],
    },
    "pozapiramidowe": {
        "tables": [
            {
                "title": "Parkinsonizmy - tabela różnicowa",
                "columns": ["Jednostka", "Najważniejszy wyróżnik", "Pułapka"],
                "rows": [
                    ["PD", "asymetryczny początek, bradykinezja, dobra odpowiedź na L-dopę", "objawy niemotoryczne mogą wyprzedzać ruchowe"],
                    ["DLB", "otępienie, fluktuacje, omamy, parkinsonizm", "nadwrażliwość na neuroleptyki"],
                    ["MSA", "parkinsonizm/ataksja + ciężka dysautonomia", "słaba odpowiedź na L-dopę"],
                    ["PSP", "wczesne upadki, porażenie spojrzenia pionowego", "często osiowa sztywność"],
                    ["CBD", "asymetria, apraksja, objawy korowe", "kończyna obca"],
                    ["Wtórny", "leki, toksyny, naczyniowy", "zawsze pytaj o neuroleptyki/metoklopramid"],
                ],
            },
            {
                "title": "Zaburzenia ruchowe - po wyglądzie ruchu",
                "columns": ["Ruch", "Jak wygląda", "Jednostki"],
                "rows": [
                    ["Drżenie spoczynkowe", "w spoczynku, maleje przy ruchu", "PD"],
                    ["Drżenie kinetyczne/posturalne", "przy działaniu lub utrzymaniu pozycji", "drżenie samoistne"],
                    ["Pląsawica", "nieregularne, płynne, 'taneczne'", "Huntington, Sydenham"],
                    ["Dystonia", "skręcające skurcze i postawy", "ogniskowe, DYT, wtórne"],
                    ["Mioklonie", "nagłe krótkie zrywania", "padaczka, metaboliczne, neurodegeneracyjne"],
                    ["Tiki", "powtarzalne, z przymusem, częściowo hamowalne", "Tourette i tiki przewlekłe"],
                ],
            },
        ],
        "schemes": [
            ["Bradykinezja + drżenie/sztywność", "parkinsonizm", "szukaj czerwonych flag atypii"],
            ["Młody + ruchy + wątroba/psychiatria", "Wilson", "miedź, ceruloplazmina, pierścień KF"],
        ],
    },
    "otepienia": {
        "tables": [
            {
                "title": "Otępienia - profil pomaga rozpoznać",
                "columns": ["Typ", "Początek/profil", "Haczyk"],
                "rows": [
                    ["Alzheimer", "pamięć epizodyczna, potem język/przestrzeń", "najczęstsze"],
                    ["FTD", "zachowanie, odhamowanie/apatie lub język", "pamięć może długo nie dominować"],
                    ["DLB", "fluktuacje, omamy wzrokowe, parkinsonizm", "neuroleptyki mogą szkodzić"],
                    ["PDD", "otępienie po rozpoznanej PD", "kolejność czasowa"],
                    ["Naczyniowe", "schodkowo, ogniska, funkcje wykonawcze", "czynniki naczyniowe"],
                    ["Odwracalne", "depresja, leki, B12, tarczyca, NPH", "zawsze sprawdź tropy"],
                ],
            }
        ],
        "schemes": [
            ["Otępienie + omamy/fluktuacje", "DLB", "uważaj na neuroleptyki"],
            ["Chód + otępienie + nietrzymanie", "wodogłowie normotensyjne"],
        ],
    },
    "bole_zawroty": {
        "tables": [
            {
                "title": "Bóle głowy - rozpoznawanie po opisie",
                "columns": ["Ból", "Opis", "Co pamiętać"],
                "rows": [
                    ["Migrena", "pulsujący, nudności, foto/fonofobia, wysiłek nasila", "może być aura"],
                    ["Napięciowy", "obustronny uciskowy, łagodny/umiarkowany", "bez typowych nudności"],
                    ["Klasterowy", "silny oczodołowo-skroniowy + autonomiczne", "serie napadów"],
                    ["SAH", "piorunujący najgorszy w życiu", "czerwona flaga"],
                    ["Wtórny groźny", "nowy po 50, gorączka, deficyt, nowotwór, ciąża", "diagnostyka, nie tylko leki"],
                ],
            },
            {
                "title": "Zawroty - obwodowe vs centralne",
                "columns": ["Cecha", "Obwodowe", "Centralne"],
                "rows": [
                    ["Nasilenie", "często bardzo silne nudności", "czasem mniej spektakularne, ale groźne"],
                    ["Oczopląs", "zwykle jednokierunkowy", "pionowy/zmienny/kierunkowo zależny"],
                    ["Objawy neurologiczne", "brak pniowych", "diplopia, dyzartria, ataksja, niedowład"],
                    ["Chód", "może być chwiejny", "ciężka ataksja alarmuje"],
                    ["Przykłady", "BPPV, Meniere, neuritis", "udar pnia/móżdżku, SM, guz"],
                ],
            },
        ],
        "schemes": [
            ["Ból piorunujący", "SAH do wykluczenia"],
            ["Zawroty + objawy pniowe/móżdżkowe", "centralne", "traktuj jak neurologiczne alarmowe"],
        ],
    },
    "padaczka": {
        "tables": [
            {
                "title": "Napady padaczkowe - klasyfikuj prosto",
                "columns": ["Pytanie", "Odpowiedź", "Przykład"],
                "rows": [
                    ["Prowokowany?", "tak = nie musi być padaczka", "hipoglikemia, alkohol, gorączka"],
                    ["Ogniskowy?", "początek w jednej sieci", "aura, objaw ruchowy/czuciowy"],
                    ["Świadomość?", "zachowana lub zaburzona", "ogniskowy z zaburzeniem świadomości"],
                    ["Uogólniony?", "od początku obie półkule", "absence, toniczno-kloniczny, miokloniczny"],
                    ["Przedłużony?", "stan padaczkowy", "pilne leczenie"],
                ],
            }
        ],
        "schemes": [
            ["Napad", "czy prowokowany?", "czy ogniskowy?", "czy świadomość zaburzona?", "czy stan padaczkowy?"],
            ["Krótkie wyłączenia u dziecka", "absence", "hiperwentylacja może prowokować"],
        ],
    },
    "guzy_urazy": {
        "tables": [
            {
                "title": "Urazy - krwiaki w tabeli",
                "columns": ["Zmiana", "Mechanizm", "Klinika"],
                "rows": [
                    ["Nadtwardówkowy", "tętnica oponowa środkowa", "jasny okres, szybkie pogorszenie"],
                    ["Podtwardówkowy", "żyły pomostowe", "starsi/alkohol, może przewlekły"],
                    ["Podpajęczynówkowy", "krew w PMR/przestrzeni podpajęczynówkowej", "ból piorunujący, oponowe"],
                    ["Stłuczenie", "uszkodzenie miąższu", "ognisko, obrzęk, napady"],
                    ["DAI", "siły ścinające", "ciężka śpiączka po urazie"],
                ],
            },
            {
                "title": "Guzy - triada myślenia",
                "columns": ["Objaw", "Co oznacza"],
                "rows": [
                    ["Ciasnota", "ból głowy, wymioty, tarcza zastoinowa, VI"],
                    ["Ognisko", "lokalizacja guza po objawach"],
                    ["Napady", "częsty początek guzów korowych"],
                    ["Rdzeń/kanał", "ból korzeniowy, poziom czucia, zwieracze"],
                ],
            },
        ],
        "schemes": [
            ["Narastające tygodniami ognisko + napady", "guz bardziej niż udar"],
            ["Uraz + jasny okres", "krwiak nadtwardówkowy"],
        ],
    },
    "toksyczne_sen": {
        "tables": [
            {
                "title": "Toksyczne i alkoholowe - skojarzenia",
                "columns": ["Stan", "Najważniejsze objawy", "Zapamiętaj"],
                "rows": [
                    ["Ostre zatrucie", "świadomość, oddech, źrenice, temperatura", "schemat toksydromu"],
                    ["Abstynencja", "drżenie, pobudzenie, napady, majaczenie", "czas po odstawieniu"],
                    ["Wernicke", "świadomość, ataksja, oftalmoplegia", "tiamina"],
                    ["Korsakow", "pamięć, konfabulacje", "następstwo niedoboru tiaminy"],
                    ["REM behavior disorder", "odgrywanie snów", "prodrom synukleinopatii"],
                    ["Narkolepsja", "senność, katapleksja, porażenie przysenne", "napadowa senność dzienna"],
                ],
            }
        ],
        "schemes": [
            ["Splątany pacjent", "glukoza/Na/wątroba/nerki/toksyny", "nie zakładaj od razu psychiatrii"],
            ["Alkohol + ataksja + oczy + świadomość", "Wernicke"],
        ],
    },
    "swiadomosc": {
        "tables": [
            {
                "title": "Śpiączka - strukturalna czy metaboliczna",
                "columns": ["Cecha", "Strukturalna", "Metaboliczna/toksyczna"],
                "rows": [
                    ["Początek", "często nagły/ogniskowy", "często rozlany/fluktuujący"],
                    ["Źrenice", "asymetria alarmuje", "często symetryczne"],
                    ["Objawy ogniskowe", "częste", "mniej typowe"],
                    ["Oddech/odruchy pniowe", "lokalizują pień/wgłobienie", "mogą być uogólnione zaburzenia"],
                    ["Pierwsze badania", "TK/MRI gdy ognisko", "glukoza, elektrolity, gazometria, toksyny"],
                ],
            },
            {
                "title": "Śmierć mózgu - warunki w głowie",
                "columns": ["Krok", "Sens"],
                "rows": [
                    ["Ustal przyczynę", "nieodwracalne uszkodzenie mózgu"],
                    ["Wyklucz odwracalne", "hipotermia, leki, zatrucia, metaboliczne"],
                    ["Brak odruchów pniowych", "źreniczny, rogówkowy, oczno-mózgowy/kaloryczny, kaszlowy"],
                    ["Bezdech", "próba w protokole"],
                ],
            },
        ],
        "schemes": [
            ["Śpiączka + asymetria źrenic/ognisko", "pilnie strukturalna"],
            ["Rozpoznanie śmierci mózgu", "najpierw wyklucz odwracalne"],
        ],
    },
    "obwodowe": {
        "tables": [
            {
                "title": "Poziom uszkodzenia - nerw, złącze, mięsień",
                "columns": ["Poziom", "Objawy", "Badania/trop"],
                "rows": [
                    ["Polineuropatia", "dystalnie, symetrycznie, czucie, odruchy", "ENG; cukrzyca, toksyny, GBS"],
                    ["Korzeń", "ból promieniujący, dermatom, odruch segmentalny", "MRI/EMG"],
                    ["Złącze", "męczliwość, oczy/opuszka", "miastenia, LEMS"],
                    ["Mięsień", "proksymalne osłabienie, czucie ok", "CK, EMG, biopsja"],
                    ["Neuron ruchowy", "ruch bez czucia", "UMN/LMN, EMG"],
                ],
            },
            {
                "title": "Miastenia vs Lambert-Eaton",
                "columns": ["Cecha", "Miastenia", "Lambert-Eaton"],
                "rows": [
                    ["Mechanizm", "postsynaptyczne AChR/MuSK", "presynaptyczne kanały Ca"],
                    ["Wysiłek", "pogarsza", "może poprawiać chwilowo"],
                    ["Oczy", "częste ptoza/diplopia", "mniej dominujące"],
                    ["Autonomia", "mniej", "częsta suchość, dysautonomia"],
                    ["Nowotwór", "grasica", "rak drobnokomórkowy płuca"],
                ],
            },
            {
                "title": "GBS/CIDP - szybkie różnicowanie",
                "columns": ["Cecha", "GBS", "CIDP"],
                "rows": [
                    ["Czas", "ostra, dni-tygodnie", "przewlekła, >8 tygodni"],
                    ["Objawy", "wstępujące osłabienie, arefleksja", "postępujące/nawrotowe osłabienie"],
                    ["Ryzyko", "oddech i autonomia", "niepełnosprawność przewlekła"],
                    ["PMR", "rozszczepienie białkowo-komórkowe", "podobnie możliwe"],
                ],
            },
        ],
        "schemes": [
            ["Osłabienie + czucie/odruchy", "neuropatia"],
            ["Osłabienie zmienne w ciągu dnia + ptoza", "miastenia"],
            ["Osłabienie proksymalne bez czucia", "miopatia"],
        ],
    },
    "neuron": {
        "tables": [
            {
                "title": "Neuron ruchowy - UMN i LMN",
                "columns": ["Element", "Objawy"],
                "rows": [
                    ["UMN", "spastyczność, hiperrefleksja, Babiński"],
                    ["LMN", "zaniki, fascykulacje, wiotkość, osłabione odruchy"],
                    ["SLA", "UMN + LMN, progresja, brak istotnych zaburzeń czucia"],
                    ["Postać opuszkowa", "dyzartria, dysfagia, język"],
                    ["SMA", "dolny neuron, genetyczna, wiotkość"],
                ],
            }
        ],
        "schemes": [
            ["Ruch bez czucia + UMN i LMN", "SLA"],
            ["Fascykulacje języka + dysfagia", "zajęcie opuszkowe"],
        ],
    },
    "systemowe_psychiczne": {
        "tables": [
            {
                "title": "Systemowe przyczyny neurologiczne",
                "columns": ["Trop", "Co może dać"],
                "rows": [
                    ["Glukoza/Na/Ca", "splątanie, napady, śpiączka"],
                    ["Nerki/wątroba", "encefalopatia, mioklonie, neuropatie"],
                    ["Tarczyca", "spowolnienie, miopatia, neuropatia, nastrój"],
                    ["B12", "mielopatia sznurowa, neuropatia, poznawcze"],
                    ["Nowotwór", "przerzuty, zakrzepica, leki, paranowotworowe"],
                    ["Autoimmunologia", "zapalenie naczyń, neuropatie, encefalopatie"],
                ],
            }
        ],
        "schemes": [
            ["Encefalopatia", "glukoza, elektrolity, nerki, wątroba, tarczyca, toksyny"],
            ["Objawy neurologiczne + rak", "przerzut? leczenie? zakrzepica? paranowotworowe?"],
        ],
    },
    "bol_rozwoj": {
        "tables": [
            {
                "title": "Ból - mechanizm decyduje o leczeniu",
                "columns": ["Typ", "Opis", "Skojarzenie"],
                "rows": [
                    ["Nocyceptywny", "tkanki, zapalenie, uraz", "klasyczne analgetyki"],
                    ["Neuropatyczny", "pieczenie, prąd, allodynia, zaburzenia czucia", "leki przeciwpadaczkowe/przeciwdepresyjne"],
                    ["Psychogenny", "dominują czynniki psychiczne", "ocena całościowa"],
                    ["MPD", "niepostępujące uszkodzenie rozwijającego mózgu", "objawy zmieniają się z rozwojem"],
                    ["Stany napadowe dzieci", "nie każdy napad = padaczka", "świadek i różnicowanie"],
                ],
            }
        ],
        "schemes": [
            ["Palenie/prąd/allodynia", "ból neuropatyczny"],
            ["Dziecko z napadem", "padaczka vs omdlenie vs afektywny bezdech vs parasomnia/tik"],
        ],
    },
}


BRAIN_CENTERS: list[dict[str, Any]] = [
    {
        "id": "frontal",
        "icon": "target",
        "name": "Płat czołowy",
        "short": "wykonuje, hamuje, planuje",
        "functions": ["funkcje wykonawcze", "osobowość i napęd", "kora ruchowa", "Broca w półkuli dominującej"],
        "lesion": "odhamowanie lub apatia, niedowład, afazja Broki, perseweracje",
        "mnemo": "CZOŁO = cel, czyn, cenzura zachowania.",
    },
    {
        "id": "parietal",
        "icon": "hand",
        "name": "Płat ciemieniowy",
        "short": "czuje i składa przestrzeń",
        "functions": ["czucie somatyczne", "schemat ciała", "orientacja przestrzenna", "praksja"],
        "lesion": "zaburzenia czucia, zaniedbywanie, apraksja, agnozja, zespół Gerstmanna",
        "mnemo": "CIEMIĘ = czucie i ciało w przestrzeni.",
    },
    {
        "id": "temporal",
        "icon": "ear",
        "name": "Płat skroniowy",
        "short": "słyszy, pamięta, rozumie",
        "functions": ["słuch", "pamięć", "rozumienie mowy Wernickego", "emocje przez połączenia limbiczne"],
        "lesion": "afazja Wernickego, zaburzenia pamięci, napady skroniowe, objawy węchowe",
        "mnemo": "SKROŃ = słowo, słuch, wspomnienie.",
    },
    {
        "id": "occipital",
        "icon": "eye",
        "name": "Płat potyliczny",
        "short": "widzi",
        "functions": ["kora wzrokowa", "analiza bodźców wzrokowych", "pole widzenia"],
        "lesion": "hemianopsja, ślepota korowa, agnozje wzrokowe",
        "mnemo": "POTYLICA = patrzenie.",
    },
    {
        "id": "broca",
        "icon": "speech",
        "name": "Ośrodek Broki",
        "short": "produkcja mowy",
        "functions": ["mowa ruchowa", "programowanie wypowiedzi"],
        "lesion": "mowa niepłynna, rozumienie względnie zachowane, chory wie, że mówi źle",
        "mnemo": "Broca = brak płynności.",
    },
    {
        "id": "wernicke",
        "icon": "message",
        "name": "Ośrodek Wernickego",
        "short": "rozumienie mowy",
        "functions": ["rozumienie słów", "semantyka", "kontrola sensu wypowiedzi"],
        "lesion": "mowa płynna, ale bez sensu; zaburzone rozumienie",
        "mnemo": "Wernicke = wypowiedź płynie, sens tonie.",
    },
    {
        "id": "basal",
        "icon": "activity",
        "name": "Jądra podstawy",
        "short": "dobierają ruch",
        "functions": ["inicjacja i hamowanie ruchu", "nawyki ruchowe", "napięcie mięśniowe"],
        "lesion": "parkinsonizm, pląsawica, dystonia, tiki, ruchy mimowolne",
        "mnemo": "Jądra podstawy = selektor ruchu.",
    },
    {
        "id": "cerebellum",
        "icon": "balance",
        "name": "Móżdżek",
        "short": "koordynuje i koryguje",
        "functions": ["koordynacja", "równowaga", "precyzja", "uczenie ruchowe"],
        "lesion": "ataksja, dysmetria, drżenie zamiarowe, oczopląs, mowa skandowana",
        "mnemo": "Móżdżek = metronom ruchu.",
    },
    {
        "id": "brainstem",
        "icon": "zap",
        "name": "Pień mózgu",
        "short": "drogi, nerwy, życie",
        "functions": ["nerwy czaszkowe", "drogi długie", "oddech i krążenie", "przytomność"],
        "lesion": "zespoły naprzemienne, dysfagia, diplopia, zaburzenia świadomości, niewydolność oddechowa",
        "mnemo": "Pień = przewody + przeżycie.",
    },
    {
        "id": "thalamus",
        "icon": "filter",
        "name": "Wzgórze",
        "short": "przekaźnik czucia",
        "functions": ["przełączanie czucia", "uwaga", "czuwanie", "integracja korowa"],
        "lesion": "zaburzenia czucia, ból wzgórzowy, zaburzenia świadomości",
        "mnemo": "Wzgórze = dworzec czuciowy.",
    },
    {
        "id": "hypothalamus",
        "icon": "thermo",
        "name": "Podwzgórze",
        "short": "homeostaza",
        "functions": ["temperatura", "głód i pragnienie", "autonomia", "oś hormonalna"],
        "lesion": "zaburzenia temperatury, łaknienia, pragnienia, snu, autonomii i hormonów",
        "mnemo": "Podwzgórze = panel sterowania ciałem.",
    },
    {
        "id": "hippocampus",
        "icon": "book",
        "name": "Hipokamp",
        "short": "nowe wspomnienia",
        "functions": ["pamięć epizodyczna", "konsolidacja", "orientacja"],
        "lesion": "amnezja następcza, początek profilu alzheimerowskiego, napady skroniowe",
        "mnemo": "Hipokamp zapisuje nowe pliki.",
    },
    {
        "id": "amygdala",
        "icon": "alert",
        "name": "Ciało migdałowate",
        "short": "emocje i alarm",
        "functions": ["lęk", "reakcje emocjonalne", "nadawanie znaczenia bodźcom"],
        "lesion": "spłycenie reakcji emocjonalnych lub napady z lękiem/autonomią",
        "mnemo": "Migdał = alarm emocjonalny.",
    },
]


KEYWORDS = [
    "objaw",
    "rozpozn",
    "diagnost",
    "leczen",
    "różnic",
    "roznic",
    "PMR",
    "EEG",
    "EMG",
    "ENG",
    "MRI",
    "TK",
    "udar",
    "niedokr",
    "krwotok",
    "zesp",
    "uszkod",
    "prawid",
    "nieprawid",
    "napad",
    "otęp",
    "ból",
    "czuc",
    "niedow",
    "poraż",
    "ataks",
    "drż",
    "mięś",
    "nerw",
    "rdze",
    "gluko",
    "biał",
    "komór",
    "przeciw",
    "charakterystycz",
]


def normalize_text(value: str) -> str:
    value = unicodedata.normalize("NFC", value)
    value = value.replace("\u2013", "-").replace("\u2014", "-").replace("\u2212", "-")
    value = value.replace("\u2022", "-").replace("\u2756", "-").replace("\u25aa", "-")
    value = value.replace("\u25a1", "-").replace("\u25ab", "-").replace("\u25cf", "-")
    value = value.replace("\u2794", "->").replace("\u27a2", "-").replace("\u2192", "->")
    value = value.replace("\u23af", "-")
    value = re.sub(r"[\ue000-\uf8ff]", " ", value)
    value = re.sub(r"[➢▪◦●■□]", "-", value)
    value = re.sub(r"[ \t]+", " ", value)
    return value.strip()


def load_pages() -> list[dict[str, Any]]:
    return json.loads(PAGES_JSON.read_text(encoding="utf-8"))


def page_text(pages: list[dict[str, Any]], start: int, end: int) -> str:
    chunks = []
    for page in pages:
        number = int(page["page"])
        if start <= number <= end:
            chunks.append(str(page["text"]))
    return "\n".join(chunks)


def clean_candidates(text: str) -> list[str]:
    out: list[str] = []
    current = ""
    for raw in text.splitlines():
        line = normalize_text(raw)
        if not line:
            continue
        if re.match(r"Neurologia .* Natalia Rachfalska \d+", line):
            continue
        if line in {"SKRYPT DO EGZAMINU", "NEUROLOGIA"}:
            continue
        line = re.sub(r"^[\-–—]\s*", "", line)
        line = re.sub(r"^[a-z]\)\s*", "", line)
        line = re.sub(r"^\d+\.\s*", "", line)
        line = normalize_text(line)
        if not line or len(line) < 16:
            continue
        starts_new = bool(re.match(r"^([A-ZŁŚŻŹĆŃÓ]|[IVX]+\.)", line)) or ":" in line[:55]
        if current and not starts_new and not current.endswith((".", ";", ":", "?", "!")):
            current = normalize_text(current + " " + line)
        else:
            if current:
                out.append(current)
            current = line
    if current:
        out.append(current)

    cleaned: list[str] = []
    seen: set[str] = set()
    for item in out:
        item = re.sub(r"\s+", " ", item)
        item = re.sub(r"([a-ząćęłńóśźż])- ([a-ząćęłńóśźż])", r"\1\2", item)
        if len(item) > 260:
            item = item[:257].rsplit(" ", 1)[0] + "..."
        key = re.sub(r"\W+", "", item.lower())[:100]
        if key and key not in seen:
            seen.add(key)
            cleaned.append(item)
    return cleaned


def score_candidate(item: str) -> int:
    lowered = item.lower()
    score = 0
    for keyword in KEYWORDS:
        if keyword.lower() in lowered:
            score += 4
    if re.search(r"\d", item):
        score += 2
    if ":" in item[:80]:
        score += 2
    if re.search(r"\b[A-ZŁŚŻŹĆŃÓ]{2,}\b", item):
        score += 2
    if len(item) < 45:
        score -= 1
    if len(item) > 220:
        score -= 1
    return score


def source_digest(
    chapter: dict[str, Any],
    pages: list[dict[str, Any]],
    limit: int,
    min_score: int = 4,
) -> list[str]:
    text = page_text(pages, int(chapter["pdf_start"]), int(chapter["pdf_end"]))
    candidates = clean_candidates(text)
    ranked = sorted(enumerate(candidates), key=lambda x: (-score_candidate(x[1]), x[0]))
    selected: list[str] = []
    seen_roots: set[str] = set()
    for _, item in ranked:
        if score_candidate(item) < min_score:
            continue
        root = re.sub(r"\W+", "", item.lower())[:70]
        if root in seen_roots:
            continue
        seen_roots.add(root)
        selected.append(item)
        if len(selected) >= limit:
            break
    selected.sort(key=lambda line: candidates.index(line) if line in candidates else 9999)
    return selected


def load_external_bundle() -> dict[str, Any]:
    if not EXTERNAL_JSON.exists():
        return {"questions": [], "sources": [], "stats": {}}
    return json.loads(EXTERNAL_JSON.read_text(encoding="utf-8"))


def question_prompt(question: dict[str, Any]) -> str:
    options = question.get("options", [])
    option_lines = []
    for index, option in enumerate(options):
        label = chr(ord("A") + index)
        option_lines.append(f"{label}. {option['text']}")
    return question["stem"] + ("\n" + "\n".join(option_lines) if option_lines else "")


def question_answer(question: dict[str, Any]) -> str:
    answer = question.get("answer") or "Brak odpowiedzi w źródle"
    letter = question.get("answer_letter") or "?"
    source = question.get("source", "baza pytań")
    number = question.get("number", "?")
    return f"{letter}. {answer} ({source}, pyt. {number})"


def questions_by_topic(external: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for question in external.get("questions", []):
        grouped.setdefault(question.get("topic", "zespoly"), []).append(question)
    return grouped


def sources_by_topic(external: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for source in external.get("sources", []):
        grouped.setdefault(source.get("topic", "zespoly"), []).append(source)
    return grouped


def build_cards(chapters: list[dict[str, Any]]) -> list[dict[str, str]]:
    cards: list[dict[str, str]] = []
    for chapter in chapters:
        title = chapter["title"]
        for question in chapter.get("exam_questions", []):
            cards.append(
                {
                    "chapter": title,
                    "q": question_prompt(question),
                    "a": question_answer(question),
                }
            )
        for bullet in chapter["core"][:5] + chapter["memory"]:
            topic = bullet.split(":")[0]
            topic = re.sub(r"\s+", " ", topic).strip()
            if len(topic) > 80 or len(topic) < 8:
                topic = "ten punkt"
            cards.append(
                {
                    "chapter": title,
                    "q": f"{title}: co trzeba pamiętać o: {topic}?",
                    "a": bullet,
                }
            )
        for item in chapter.get("digest_html", [])[:6]:
            if not (45 <= len(item) <= 230):
                continue
            if ":" in item[:90]:
                topic, answer = item.split(":", 1)
                question = f"{title}: co pamiętasz o: {topic.strip()}?"
                answer = answer.strip() or item
            else:
                cue = item[:72].rsplit(" ", 1)[0]
                question = f"{title}: odtwórz fakt ze skryptu zaczynający się od: {cue}..."
                answer = item
            cards.append({"chapter": title, "q": question, "a": answer})
    return cards


def build_quiz(chapters: list[dict[str, Any]]) -> list[dict[str, str]]:
    quiz: list[dict[str, Any]] = []
    for chapter in chapters:
        for question in chapter.get("exam_questions", []):
            item = dict(question)
            item["chapter"] = chapter["title"]
            item["q"] = question["stem"]
            item["a"] = question_answer(question)
            quiz.append(item)
    return quiz


def register_fonts() -> tuple[str, str]:
    regular_candidates = [
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/Library/Fonts/Arial.ttf",
        "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
    ]
    bold_candidates = [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        "/Library/Fonts/Arial Bold.ttf",
    ]
    regular = next((p for p in regular_candidates if Path(p).exists()), None)
    bold = next((p for p in bold_candidates if Path(p).exists()), None)
    if regular:
        pdfmetrics.registerFont(TTFont("StudyRegular", regular))
    if bold:
        pdfmetrics.registerFont(TTFont("StudyBold", bold))
    return ("StudyRegular" if regular else "Helvetica", "StudyBold" if bold else "Helvetica-Bold")


def make_styles(font_name: str, bold_name: str) -> dict[str, ParagraphStyle]:
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "title",
            parent=base["Title"],
            fontName=bold_name,
            fontSize=24,
            leading=28,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#16324F"),
            spaceAfter=12,
        ),
        "subtitle": ParagraphStyle(
            "subtitle",
            parent=base["Normal"],
            fontName=font_name,
            fontSize=10,
            leading=14,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#44546A"),
            spaceAfter=16,
        ),
        "h1": ParagraphStyle(
            "h1",
            parent=base["Heading1"],
            fontName=bold_name,
            fontSize=15,
            leading=18,
            textColor=colors.HexColor("#16324F"),
            spaceBefore=10,
            spaceAfter=6,
        ),
        "h2": ParagraphStyle(
            "h2",
            parent=base["Heading2"],
            fontName=bold_name,
            fontSize=11,
            leading=14,
            textColor=colors.HexColor("#0E6B67"),
            spaceBefore=6,
            spaceAfter=4,
        ),
        "body": ParagraphStyle(
            "body",
            parent=base["Normal"],
            fontName=font_name,
            fontSize=8.6,
            leading=11,
            textColor=colors.HexColor("#202B33"),
            spaceAfter=4,
        ),
        "small": ParagraphStyle(
            "small",
            parent=base["Normal"],
            fontName=font_name,
            fontSize=7.6,
            leading=9.6,
            textColor=colors.HexColor("#44546A"),
            spaceAfter=3,
        ),
        "bullet": ParagraphStyle(
            "bullet",
            parent=base["Normal"],
            fontName=font_name,
            fontSize=8.1,
            leading=10.2,
            leftIndent=10,
            firstLineIndent=-6,
            spaceAfter=2.5,
            textColor=colors.HexColor("#1E2933"),
        ),
        "question": ParagraphStyle(
            "question",
            parent=base["Normal"],
            fontName=font_name,
            fontSize=8.0,
            leading=10,
            leftIndent=8,
            firstLineIndent=-6,
            textColor=colors.HexColor("#374151"),
            spaceAfter=2,
        ),
        "cell": ParagraphStyle(
            "cell",
            parent=base["Normal"],
            fontName=font_name,
            fontSize=7.1,
            leading=8.4,
            textColor=colors.HexColor("#243447"),
        ),
        "cell_head": ParagraphStyle(
            "cell_head",
            parent=base["Normal"],
            fontName=bold_name,
            fontSize=7.2,
            leading=8.5,
            textColor=colors.white,
        ),
        "memo": ParagraphStyle(
            "memo",
            parent=base["Normal"],
            fontName=font_name,
            fontSize=7.8,
            leading=9.4,
            leftIndent=0,
            textColor=colors.HexColor("#243447"),
            spaceAfter=2,
        ),
    }


def para(text: str, style: ParagraphStyle) -> Paragraph:
    safe = escape(normalize_text(text))
    safe = safe.replace("&lt;b&gt;", "<b>").replace("&lt;/b&gt;", "</b>")
    return Paragraph(safe, style)


def bullet(text: str, style: ParagraphStyle) -> Paragraph:
    return Paragraph(escape(normalize_text(text)), style, bulletText="-")


def pdf_table_from_visual(
    visual_table: dict[str, Any],
    styles: dict[str, ParagraphStyle],
    font_name: str,
    bold_name: str,
) -> list[Any]:
    columns = visual_table["columns"]
    rows = visual_table["rows"]
    col_width = 16.2 * cm / len(columns)
    data = [[para(str(col), styles["cell_head"]) for col in columns]]
    for row in rows:
        data.append([para(str(cell), styles["cell"]) for cell in row])
    table = Table(data, colWidths=[col_width] * len(columns), repeatRows=1)
    table.setStyle(
        TableStyle(
            [
                ("FONTNAME", (0, 0), (-1, -1), font_name),
                ("FONTNAME", (0, 0), (-1, 0), bold_name),
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#16324F")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F7FAFC")]),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#CDD6E1")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ]
        )
    )
    return [para(f"TABELA - {visual_table['title']}", styles["h2"]), table, Spacer(1, 5)]


def pdf_schemes(
    schemes: list[list[str]],
    styles: dict[str, ParagraphStyle],
    font_name: str,
    bold_name: str,
) -> list[Any]:
    if not schemes:
        return []
    flowables: list[Any] = [para("SCHEMAT - jak myśleć na pytaniu", styles["h2"])]
    for scheme in schemes:
        cells = []
        for index, step in enumerate(scheme, start=1):
            label = f"<b>{index}</b> {escape(normalize_text(step))}"
            cells.append(Paragraph(label, styles["memo"]))
        table = Table([cells], colWidths=[16.2 * cm / len(cells)] * len(cells))
        table.setStyle(
            TableStyle(
                [
                    ("FONTNAME", (0, 0), (-1, -1), font_name),
                    ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F3F7F6")),
                    ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#B8D8D4")),
                    ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#D8E7E4")),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 5),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                    ("TOPPADDING", (0, 0), (-1, -1), 5),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ]
            )
        )
        flowables.extend([table, Spacer(1, 4)])
    return flowables


def pdf_mnemo(items: list[str], styles: dict[str, ParagraphStyle]) -> list[Any]:
    if not items:
        return []
    flowables: list[Any] = [para("MNEMO - zaczepki pamięciowe", styles["h2"])]
    for item in items:
        flowables.append(Paragraph(f"<b>MEMO</b> {escape(normalize_text(item))}", styles["memo"]))
    return flowables


def pdf_exam_questions(questions: list[dict[str, Any]], styles: dict[str, ParagraphStyle], limit: int = 7) -> list[Any]:
    if not questions:
        return []
    flowables: list[Any] = [para("BAZA PYTAŃ - z klucza egzaminacyjnego", styles["h2"])]
    for question in questions[:limit]:
        options = []
        for index, option in enumerate(question.get("options", [])):
            label = chr(ord("A") + index)
            text = normalize_text(option["text"])
            if option.get("correct"):
                options.append(f"<b>{label}. {escape(text)}</b>")
            else:
                options.append(f"{label}. {escape(text)}")
        source = f"{question.get('source', 'baza')}, pyt. {question.get('number', '?')}"
        body = f"<b>?</b> {escape(normalize_text(question['stem']))}<br/>" + "<br/>".join(options)
        body += f"<br/><font color='#0E6B67'><b>Odp.: {escape(question_answer(question))}</b></font>"
        body += f"<br/><font color='#6B7280'>{escape(source)}</font>"
        flowables.append(Paragraph(body, styles["question"]))
    if len(questions) > limit:
        flowables.append(para(f"W HTML jest pełna pula tego działu: {len(questions)} pytań.", styles["small"]))
    return flowables


def pdf_source_updates(sources: list[dict[str, Any]], styles: dict[str, ParagraphStyle], per_source: int = 4) -> list[Any]:
    if not sources:
        return []
    flowables: list[Any] = [para("AKTUALIZACJA Z PREZENTACJI", styles["h2"])]
    for source in sources:
        flowables.append(Paragraph(f"<b>{escape(source['file'])}</b>", styles["memo"]))
        for point in source.get("key_points", [])[:per_source]:
            flowables.append(bullet(point, styles["small"]))
    return flowables


def pdf_brain_centers(
    styles: dict[str, ParagraphStyle],
    font_name: str,
    bold_name: str,
) -> list[Any]:
    rows = [["Ośrodek", "Za co odpowiada", "Uszkodzenie", "MNEMO"]]
    for center in BRAIN_CENTERS:
        rows.append(
            [
                center["name"],
                "; ".join(center["functions"]),
                center["lesion"],
                center["mnemo"],
            ]
        )
    data = [[para(str(cell), styles["cell_head"]) for cell in rows[0]]]
    for row in rows[1:]:
        data.append([para(str(cell), styles["cell"]) for cell in row])
    table = Table(data, colWidths=[3.1 * cm, 4.8 * cm, 5.4 * cm, 2.9 * cm], repeatRows=1)
    table.setStyle(
        TableStyle(
            [
                ("FONTNAME", (0, 0), (-1, -1), font_name),
                ("FONTNAME", (0, 0), (-1, 0), bold_name),
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#16324F")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F7FAFC")]),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#CDD6E1")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ]
        )
    )
    flowables: list[Any] = [
        para("Mapa mózgu i ośrodki", styles["h1"]),
        para(
            "Używaj tej strony jak ściągi lokalizacyjnej: objaw -> ośrodek -> typowe uszkodzenie. Ikony i mnemotechniki są rozwinięte w zakładce Mózg w HTML.",
            styles["body"],
        ),
        table,
    ]
    return flowables


def footer(canvas, doc) -> None:  # type: ignore[no-untyped-def]
    canvas.saveState()
    canvas.setFont("StudyRegular" if "StudyRegular" in pdfmetrics.getRegisteredFontNames() else "Helvetica", 7)
    canvas.setFillColor(colors.HexColor("#6B7280"))
    canvas.drawString(1.4 * cm, 0.8 * cm, "NeuroSprint 48h - kondensat do nauki z pliku NASIOSKRYPT-NEUROLOGIA")
    canvas.drawRightString(A4[0] - 1.4 * cm, 0.8 * cm, f"str. {doc.page}")
    canvas.restoreState()


def build_pdf(chapters: list[dict[str, Any]], cards: list[dict[str, str]]) -> Path:
    font_name, bold_name = register_fonts()
    styles = make_styles(font_name, bold_name)
    path = OUT / "neuro_sprint_48h.pdf"
    doc = SimpleDocTemplate(
        str(path),
        pagesize=A4,
        rightMargin=1.25 * cm,
        leftMargin=1.25 * cm,
        topMargin=1.15 * cm,
        bottomMargin=1.25 * cm,
        title="NeuroSprint 48h",
        author="Codex",
    )
    story: list[Any] = []
    story.append(para("NeuroSprint 48h", styles["title"]))
    story.append(
        para(
            "Wersja rozszerzona do limitu 60 stron: materiał do opanowania neurologii od 19:15 dzisiaj do jutra wieczorem. Przygotowane do nauki egzaminacyjnej z przesłanego PDF-u, nie jako aktualna instrukcja leczenia pacjentów.",
            styles["subtitle"],
        )
    )
    meta_table = [
        ["Start", "Dzisiaj 19:15. Czas ucieka, więc priorytet A idzie przed perfekcyjnym doczytywaniem szczegółów."],
        ["Priorytet A", "Naucz się aktywnie: objaw -> lokalizacja -> diagnostyka -> leczenie/ryzyko."],
        ["Priorytet B", "Przejdź po rdzeniu i fiszkach; szczegóły tylko jeśli zostanie czas."],
        ["Metoda", "Po każdym rozdziale zamknij PDF i odpowiedz na pytania kontrolne z pamięci."],
    ]
    table = Table(meta_table, colWidths=[3.2 * cm, 13.0 * cm])
    table.setStyle(
        TableStyle(
            [
                ("FONTNAME", (0, 0), (-1, -1), font_name),
                ("FONTNAME", (0, 0), (0, -1), bold_name),
                ("FONTSIZE", (0, 0), (-1, -1), 8.2),
                ("LEADING", (0, 0), (-1, -1), 10),
                ("TEXTCOLOR", (0, 0), (0, -1), colors.HexColor("#0E6B67")),
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F3F7F6")),
                ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#B8D8D4")),
                ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#D8E7E4")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    story.append(table)
    story.append(Spacer(1, 8))
    story.append(para("Plan 2-dniowy", styles["h1"]))
    for day in PLAN:
        story.append(para(day["title"], styles["h2"]))
        for block in day["blocks"]:
            story.append(bullet(block, styles["bullet"]))
    story.append(para("Mapa priorytetów", styles["h1"]))
    priority_rows = [["Dzień", "Priorytet", "Rozdział", "Czas"]]
    for chapter in chapters:
        priority_rows.append([str(chapter["day"]), chapter["priority"], chapter["title"], chapter["time"]])
    priority_table = Table(priority_rows, colWidths=[1.3 * cm, 1.9 * cm, 11.2 * cm, 2.0 * cm], repeatRows=1)
    priority_table.setStyle(
        TableStyle(
            [
                ("FONTNAME", (0, 0), (-1, -1), font_name),
                ("FONTNAME", (0, 0), (-1, 0), bold_name),
                ("FONTSIZE", (0, 0), (-1, -1), 7.6),
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#16324F")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#D1D5DB")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ]
        )
    )
    story.append(priority_table)
    story.append(PageBreak())
    story.extend(pdf_brain_centers(styles, font_name, bold_name))
    story.append(PageBreak())

    for index, chapter in enumerate(chapters, start=1):
        block: list[Any] = []
        block.append(
            para(
                f"{index}. {chapter['title']} <b>({chapter['pages']})</b> - priorytet {chapter['priority']}",
                styles["h1"],
            )
        )
        block.append(para(chapter["summary"], styles["body"]))
        visual = chapter.get("visuals", {})
        if visual.get("tables"):
            for visual_table in visual["tables"]:
                block.extend(pdf_table_from_visual(visual_table, styles, font_name, bold_name))
        if visual.get("schemes"):
            block.extend(pdf_schemes(visual["schemes"], styles, font_name, bold_name))
        block.extend(pdf_mnemo(chapter["memory"], styles))
        block.extend(pdf_exam_questions(chapter.get("exam_questions", []), styles))
        block.extend(pdf_source_updates(chapter.get("source_updates", []), styles))
        block.append(para("Sedno", styles["h2"]))
        for item in chapter["core"]:
            block.append(bullet(item, styles["bullet"]))
        if chapter.get("digest_pdf"):
            block.append(para("Warstwa 2 - kondensat ze skryptu", styles["h2"]))
            for item in chapter["digest_pdf"]:
                block.append(bullet(item, styles["small"]))
        story.extend(block)
        if index in {6, 12, 18}:
            story.append(PageBreak())

    story.append(PageBreak())
    story.append(para("Ostatnia godzina przed snem / egzaminem", styles["h1"]))
    final_rules = [
        "Przejdź tylko pytania kontrolne. Jeśli odpowiedź nie wychodzi w 20 sekund, oznacz rozdział jako słaby.",
        "Powiedz na głos trzy różnicowania: udar vs guz vs infekcja; OUN vs obwód vs mięsień; migrena vs SAH vs zapalenie opon.",
        "Zrób 30 fiszek: najpierw nieumiane, potem losowe. Nie doczytuj całych rozdziałów, jeśli problemem jest tylko jedno hasło.",
        "Na koniec wróć do PMR, nerwów czaszkowych, zespołów pniowych, SM, parkinsonizmów, padaczki, GBS/miastenii/SLA.",
    ]
    for item in final_rules:
        story.append(bullet(item, styles["bullet"]))
    story.append(para("Szybka lista 'muszę umieć'", styles["h2"]))
    must = [
        "Nerwy czaszkowe i ich deficyty.",
        "Piramidowy, móżdżkowy, pozapiramidowy, rdzeniowy, korzeniowy i obwodowy wzorzec objawów.",
        "PMR: bakteryjny, wirusowy, gruźliczy/grzybiczy, SAH, SM/GBS.",
        "Udar: objawy, naczynia, różnicowanie krwotoku, SAH i zakrzepicy żylnej.",
        "SM/NMO/ADEM/PML.",
        "PD, DLB, MSA, PSP, CBD, Huntington, Wilson.",
        "AD, FTD, DLB/PDD, naczyniowe.",
        "Migrena, napięciowy, klasterowy; centralne vs obwodowe zawroty.",
        "Napady ogniskowe/uogólnione i stan padaczkowy.",
        "GBS, CIDP, miastenia, Lambert-Eaton, miopatie, SLA.",
    ]
    for item in must:
        story.append(bullet(item, styles["bullet"]))
    story.append(Spacer(1, 8))
    story.append(para(f"W narzędziu HTML znajduje się {len(cards)} fiszek i test ustny z {len(build_quiz(chapters))} pytaniami. PDF jest wersją rozszerzoną, ale nadal ma mniej niż 60 stron.", styles["small"]))

    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    return path


def build_html(chapters: list[dict[str, Any]], cards: list[dict[str, str]], quiz: list[dict[str, str]]) -> Path:
    data = {
        "chapters": chapters,
        "cards": cards,
        "quiz": quiz,
        "plan": PLAN,
        "brain": BRAIN_CENTERS,
    }
    payload = json.dumps(data, ensure_ascii=False)
    path = OUT / "neuro_sprint_48h.html"
    css = """
:root {
  color-scheme: light;
  --ink: #17212b;
  --muted: #667085;
  --line: #d8dee7;
  --bg: #f5f7f8;
  --panel: #ffffff;
  --teal: #0e6b67;
  --blue: #16324f;
  --coral: #c84f4a;
  --amber: #a66a00;
  --green: #26734d;
  --shadow: 0 8px 24px rgba(22, 50, 79, 0.08);
}
* { box-sizing: border-box; }
html, body { margin: 0; min-height: 100%; }
body {
  font-family: Arial, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  background:
    linear-gradient(135deg, rgba(14, 107, 103, 0.09), rgba(255,255,255,0) 34%),
    linear-gradient(180deg, #f7f8f4 0%, #eef3f5 54%, #f8f7f2 100%);
  color: var(--ink);
  font-size: 15px;
}
button, input {
  font: inherit;
}
.app {
  display: grid;
  grid-template-columns: 320px minmax(0, 1fr);
  min-height: 100vh;
}
.side {
  background:
    linear-gradient(180deg, #f8fbfa 0%, #eef3f2 100%);
  border-right: 1px solid var(--line);
  padding: 18px 14px;
  position: sticky;
  top: 0;
  height: 100vh;
  overflow: auto;
}
.brand {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 14px;
  padding: 10px;
  border: 1px solid rgba(14, 107, 103, 0.16);
  border-radius: 8px;
  background: rgba(255,255,255,0.72);
}
.brand-mark {
  width: 34px;
  height: 34px;
  border-radius: 8px;
  background: conic-gradient(from 220deg, var(--teal), #315f9b, var(--coral), #d9a441, var(--teal));
  box-shadow: inset 0 0 0 2px rgba(255,255,255,0.75);
}
h1, h2, h3 { margin: 0; letter-spacing: 0; }
.brand h1 {
  font-size: 20px;
  line-height: 1.1;
}
.brand small {
  color: var(--muted);
  font-weight: 700;
}
.search {
  width: 100%;
  border: 1px solid var(--line);
  border-radius: 6px;
  padding: 10px 11px;
  background: #fff;
  margin: 8px 0 12px;
}
.tabs, .tools {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
  margin-bottom: 12px;
}
.filters {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 5px;
  margin: 0 0 12px;
}
.tab, .tool-btn, .chapter-btn, .primary {
  border: 1px solid var(--line);
  background: #fff;
  color: var(--ink);
  border-radius: 6px;
  padding: 8px 10px;
  cursor: pointer;
  text-decoration: none;
  transition: transform 140ms ease, border-color 140ms ease, background 140ms ease, color 140ms ease;
}
.tab:hover, .tool-btn:hover, .chapter-btn:hover, .primary:hover {
  transform: translateY(-1px);
  border-color: rgba(14, 107, 103, 0.42);
}
.tab.active, .chapter-btn.active, .primary {
  background: var(--blue);
  color: #fff;
  border-color: var(--blue);
}
.tool-btn.done {
  border-color: rgba(38, 115, 77, 0.35);
  color: var(--green);
}
.filter {
  border: 1px solid var(--line);
  background: rgba(255,255,255,0.72);
  border-radius: 6px;
  padding: 7px 5px;
  color: #344054;
  cursor: pointer;
  font-size: 12px;
  font-weight: 700;
}
.filter.active {
  background: var(--teal);
  border-color: var(--teal);
  color: #fff;
}
.progress {
  height: 8px;
  border-radius: 999px;
  background: #dfe7e6;
  overflow: hidden;
  margin: 8px 0 14px;
}
.progress > span {
  display: block;
  height: 100%;
  width: 0%;
  background: linear-gradient(90deg, var(--teal), var(--green));
}
.chapter-list {
  display: grid;
  gap: 7px;
}
.chapter-btn {
  width: 100%;
  text-align: left;
  display: grid;
  grid-template-columns: 22px 1fr auto;
  gap: 8px;
  align-items: center;
  min-height: 42px;
  border-left: 4px solid transparent;
  box-shadow: 0 2px 10px rgba(22, 50, 79, 0.04);
}
.chapter-btn:has(.badge.a) {
  border-left-color: var(--coral);
}
.chapter-btn:has(.badge.b) {
  border-left-color: var(--amber);
}
.chapter-btn .check {
  width: 18px;
  height: 18px;
  border: 1px solid #9aa8b5;
  border-radius: 4px;
  display: inline-grid;
  place-items: center;
  color: #fff;
  font-size: 12px;
}
.chapter-btn.complete .check {
  background: var(--green);
  border-color: var(--green);
}
.chapter-btn strong {
  font-size: 13px;
  line-height: 1.2;
}
.badge {
  font-size: 11px;
  font-weight: 700;
  border-radius: 4px;
  padding: 3px 5px;
  color: #fff;
}
.badge.a { background: var(--coral); }
.badge.b { background: var(--amber); }
.main {
  padding: 22px;
  overflow: auto;
}
.topbar {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: center;
  margin-bottom: 16px;
  color: #fff;
  background:
    linear-gradient(135deg, rgba(22,50,79,0.98) 0%, rgba(14,107,103,0.96) 62%, rgba(200,79,74,0.92) 100%);
  border-radius: 8px;
  padding: 18px;
  box-shadow: 0 14px 32px rgba(22, 50, 79, 0.18);
}
.topbar h2 {
  font-size: 24px;
}
.topbar .meta {
  color: rgba(255,255,255,0.78);
  font-size: 13px;
}
.topbar .tool-btn {
  background: rgba(255,255,255,0.12);
  color: #fff;
  border-color: rgba(255,255,255,0.28);
}
.status-panel {
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: 10px;
  margin-bottom: 14px;
}
.metric {
  background: rgba(255,255,255,0.78);
  border: 1px solid rgba(216, 222, 231, 0.95);
  border-radius: 8px;
  padding: 12px;
  box-shadow: var(--shadow);
  min-height: 78px;
}
.metric span {
  color: var(--muted);
  font-size: 12px;
  font-weight: 700;
  text-transform: uppercase;
}
.metric strong {
  display: block;
  font-size: 24px;
  margin-top: 5px;
  color: var(--blue);
}
.metric em {
  display: block;
  color: var(--muted);
  font-style: normal;
  font-size: 12px;
  margin-top: 3px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.view {
  display: none;
}
.view.active {
  display: block;
}
.panel {
  background: var(--panel);
  border: 1px solid var(--line);
  border-radius: 8px;
  box-shadow: var(--shadow);
  padding: 16px;
  margin-bottom: 14px;
  position: relative;
}
.chapter-head {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: flex-start;
  border-bottom: 1px solid var(--line);
  padding-bottom: 12px;
  margin-bottom: 12px;
}
.chapter-head h2 {
  font-size: 26px;
  line-height: 1.1;
}
.chapter-head p {
  margin: 8px 0 0;
  color: var(--muted);
  line-height: 1.45;
}
.pill-row {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}
.pill {
  border: 1px solid var(--line);
  border-radius: 999px;
  padding: 5px 8px;
  font-size: 12px;
  background: #f8fafc;
  color: #314154;
  white-space: nowrap;
}
.grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px;
}
.quick-grid {
  display: grid;
  grid-template-columns: minmax(0, 1.25fr) minmax(280px, 0.75fr);
  gap: 14px;
  margin-bottom: 14px;
}
.visual-stack {
  display: grid;
  gap: 12px;
}
.visual-card {
  border: 1px solid var(--line);
  border-radius: 8px;
  overflow: hidden;
  background: #fff;
}
.visual-card header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 12px;
  background: #f3f7f6;
  border-bottom: 1px solid var(--line);
  font-weight: 800;
  color: var(--blue);
}
.icon {
  width: 18px;
  height: 18px;
  display: inline-block;
  flex: 0 0 18px;
}
.icon svg {
  width: 18px;
  height: 18px;
  stroke: currentColor;
  fill: none;
  stroke-width: 2.2;
  stroke-linecap: round;
  stroke-linejoin: round;
}
.visual-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
}
.visual-table th,
.visual-table td {
  text-align: left;
  vertical-align: top;
  border-bottom: 1px solid #e7edf2;
  padding: 8px 9px;
  line-height: 1.32;
}
.visual-table th {
  color: #fff;
  background: var(--blue);
  font-size: 12px;
}
.visual-table tr:last-child td {
  border-bottom: 0;
}
.flow-list {
  display: grid;
  gap: 8px;
  padding: 12px;
}
.flow {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  align-items: center;
}
.flow-step {
  border: 1px solid #cdd8df;
  background: #fbfcfd;
  border-radius: 6px;
  padding: 7px 9px;
  line-height: 1.25;
  font-size: 13px;
}
.flow-arrow {
  color: var(--teal);
  font-weight: 900;
}
.memo-list {
  display: grid;
  gap: 8px;
  padding: 12px;
}
.memo {
  display: grid;
  grid-template-columns: 22px 1fr;
  gap: 8px;
  align-items: start;
  border: 1px solid #e3e9ef;
  background: #fbfcfd;
  border-radius: 7px;
  padding: 8px;
  line-height: 1.35;
}
.memo .tag {
  width: 22px;
  height: 22px;
  border-radius: 6px;
  display: inline-grid;
  place-items: center;
  background: var(--teal);
  color: #fff;
}
.section h3 {
  font-size: 15px;
  margin-bottom: 8px;
  color: var(--teal);
  display: inline-block;
  border-bottom: 2px solid rgba(14,107,103,0.22);
  padding-bottom: 3px;
}
ul {
  margin: 0;
  padding-left: 18px;
}
li {
  margin: 0 0 7px;
  line-height: 1.42;
}
.qa {
  display: grid;
  gap: 8px;
}
.qa details {
  border: 1px solid var(--line);
  border-radius: 6px;
  background: #fbfcfd;
  padding: 9px 10px;
}
.qa summary {
  cursor: pointer;
  font-weight: 700;
}
.qa p {
  color: var(--muted);
  margin: 7px 0 0;
  line-height: 1.45;
}
.exam-list {
  display: grid;
  gap: 10px;
}
.exam-card {
  border: 1px solid var(--line);
  border-radius: 8px;
  background: #fbfcfd;
  padding: 11px;
}
.exam-card strong {
  display: block;
  line-height: 1.35;
  margin-bottom: 8px;
}
.option-list {
  display: grid;
  gap: 5px;
  margin: 8px 0;
}
.option {
  display: grid;
  grid-template-columns: 24px 1fr;
  gap: 7px;
  border: 1px solid #e1e8ee;
  border-radius: 6px;
  padding: 7px;
  background: #fff;
  line-height: 1.3;
}
.option.correct {
  border-color: rgba(38, 115, 77, 0.38);
  background: #f0f8f4;
}
.option b {
  color: var(--blue);
}
.source-note {
  color: var(--muted);
  font-size: 12px;
  margin-top: 6px;
}
.source-grid {
  display: grid;
  gap: 10px;
}
.source-box {
  border: 1px solid var(--line);
  border-radius: 8px;
  padding: 10px;
  background: #fbfcfd;
}
.source-box h4 {
  margin: 0 0 7px;
  color: var(--blue);
  font-size: 14px;
}
.brain-layout {
  display: grid;
  grid-template-columns: minmax(320px, 0.9fr) minmax(0, 1.1fr);
  gap: 14px;
}
.brain-map {
  position: sticky;
  top: 18px;
  align-self: start;
  border: 1px solid var(--line);
  border-radius: 8px;
  background: #fbfcfd;
  padding: 14px;
}
.brain-svg {
  width: 100%;
  max-height: 360px;
}
.brain-region {
  cursor: pointer;
  transition: opacity 140ms ease, transform 140ms ease;
}
.brain-region:hover {
  opacity: 0.82;
}
.brain-region.active path,
.brain-region.active ellipse,
.brain-region.active rect {
  stroke: var(--coral);
  stroke-width: 3;
}
.brain-legend {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 6px;
  margin-top: 10px;
}
.legend-btn {
  border: 1px solid var(--line);
  background: #fff;
  border-radius: 6px;
  padding: 7px 8px;
  text-align: left;
  font-size: 12px;
  cursor: pointer;
}
.legend-btn.active {
  border-color: var(--coral);
  background: #fff6f5;
  color: var(--blue);
  font-weight: 800;
}
.center-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
}
.center-card {
  border: 1px solid var(--line);
  border-radius: 8px;
  background: #fff;
  padding: 11px;
  box-shadow: 0 4px 14px rgba(22, 50, 79, 0.05);
}
.center-card.active {
  border-color: var(--coral);
  box-shadow: 0 8px 22px rgba(200, 79, 74, 0.12);
}
.center-card h3 {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0 0 4px;
  color: var(--blue);
  border: 0;
  padding: 0;
}
.center-card .short {
  color: var(--teal);
  font-weight: 800;
  margin-bottom: 8px;
}
.center-card dl {
  margin: 0;
  display: grid;
  gap: 7px;
}
.center-card dt {
  font-size: 12px;
  font-weight: 900;
  color: var(--muted);
  text-transform: uppercase;
}
.center-card dd {
  margin: 0;
  line-height: 1.35;
}
.mnemo-chip {
  display: inline-block;
  margin-top: 7px;
  border-radius: 6px;
  background: #f3f7f6;
  color: var(--teal);
  padding: 6px 8px;
  font-weight: 800;
}
.plan-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px;
}
.block {
  border-left: 4px solid var(--teal);
  background: #fbfcfd;
  padding: 10px 12px;
  margin: 8px 0;
  border-radius: 0 6px 6px 0;
}
.flash {
  min-height: 260px;
  display: grid;
  place-items: center;
  text-align: center;
  padding: 22px;
  overflow: hidden;
}
.flash::before {
  content: "";
  position: absolute;
  inset: 0 0 auto 0;
  height: 5px;
  background: linear-gradient(90deg, var(--coral), #d9a441, var(--teal), #315f9b);
}
.flash h3 {
  font-size: 22px;
  line-height: 1.25;
  max-width: 760px;
}
.flash p {
  color: var(--muted);
  font-size: 18px;
  line-height: 1.45;
  max-width: 760px;
}
.answer {
  display: none;
}
.answer.show {
  display: block;
}
.quiz-item {
  border-top: 1px solid var(--line);
  padding: 12px 0;
}
.quiz-item:first-child { border-top: 0; }
.quiz-item strong {
  display: block;
  margin-bottom: 6px;
}
.quiz-item details {
  margin-top: 6px;
}
.empty {
  color: var(--muted);
  padding: 24px;
  text-align: center;
}
@media (max-width: 920px) {
  .app { grid-template-columns: 1fr; }
  .side { position: relative; height: auto; }
  .main { padding: 14px; }
  .grid, .plan-grid, .quick-grid, .brain-layout, .center-grid { grid-template-columns: 1fr; }
  .brain-map { position: relative; top: auto; }
  .status-panel { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .chapter-list { max-height: 310px; overflow: auto; padding-right: 2px; }
  .chapter-head { display: block; }
  .topbar { display: block; }
}
@media (max-width: 560px) {
  .status-panel { grid-template-columns: 1fr; }
  .filters { grid-template-columns: repeat(2, 1fr); }
}
@media print {
  body { background: #fff; }
  .side, .topbar, .tools, .tabs { display: none !important; }
  .app { display: block; }
  .main { padding: 0; }
  .view { display: block !important; }
  #flashView, #quizView, #planView { display: none !important; }
  .panel { box-shadow: none; break-inside: avoid; border-color: #bbb; }
}
"""
    js = """
const data = DATA_PLACEHOLDER;
const storeKey = "neuroSprint48h";
let state = JSON.parse(localStorage.getItem(storeKey) || '{"done":{},"cardIndex":0,"known":{},"view":"learn","chapter":null,"filter":"all","panic":false}');
if (!state.chapter) state.chapter = data.chapters[0].id;
if (!state.brainCenter) state.brainCenter = "frontal";
if (!state.sprintStart) {
  const now = new Date();
  const start = new Date(now);
  start.setHours(19, 15, 0, 0);
  if (now.getTime() < start.getTime() - 12 * 3600000) start.setDate(start.getDate() - 1);
  const deadline = new Date(start);
  deadline.setDate(start.getDate() + 1);
  deadline.setHours(21, 0, 0, 0);
  state.sprintStart = start.toISOString();
  state.sprintDeadline = deadline.toISOString();
}
function save(){ localStorage.setItem(storeKey, JSON.stringify(state)); }
function byId(id){ return document.getElementById(id); }
function setView(view){
  state.view = view; save();
  document.querySelectorAll(".tab").forEach(b => b.classList.toggle("active", b.dataset.view === view));
  document.querySelectorAll(".view").forEach(v => v.classList.toggle("active", v.id === view + "View"));
  render();
}
function setFilter(filter){
  state.filter = filter; save(); renderSidebar();
}
function setChapter(id){ state.chapter = id; save(); render(); }
function setBrainCenter(id){ state.brainCenter = id; save(); renderBrain(); }
function toggleDone(id){ state.done[id] = !state.done[id]; save(); render(); }
function progress(){
  const done = data.chapters.filter(c => state.done[c.id]).length;
  return Math.round(done / data.chapters.length * 100);
}
function sprintClock(){
  const deadline = new Date(state.sprintDeadline);
  const diff = deadline.getTime() - Date.now();
  if (diff <= 0) return { short: "Finał", label: "uruchom Ostatnią godzinę" };
  const hours = Math.floor(diff / 3600000);
  const minutes = Math.floor((diff % 3600000) / 60000);
  return { short: `${hours}h ${String(minutes).padStart(2, "0")}m`, label: "do deadline 21:00" };
}
function updateClockOnly(){
  const clock = sprintClock();
  const clockText = byId("clockText");
  if (clockText) clockText.textContent = `start 19:15 • ${clock.short} ${clock.label}`;
  const clockShort = byId("clockShort");
  const clockLabel = byId("clockLabel");
  if (clockShort) clockShort.textContent = clock.short;
  if (clockLabel) clockLabel.textContent = clock.label;
}
function priorityChapters(priority){
  return data.chapters.filter(c => c.priority === priority);
}
function renderStatus(){
  const doneCount = data.chapters.filter(c => state.done[c.id]).length;
  const knownCount = data.cards.filter(c => state.known[c.q] > 0).length;
  const aDone = priorityChapters("A").filter(c => state.done[c.id]).length;
  const next = data.chapters.find(c => !state.done[c.id] && c.priority === "A") || data.chapters.find(c => !state.done[c.id]) || data.chapters[0];
  const clock = sprintClock();
  byId("statusPanel").innerHTML = `
    <div class="metric"><span>Rozdziały</span><strong>${doneCount}/${data.chapters.length}</strong><em>postęp całego sprintu</em></div>
    <div class="metric"><span>Priorytet A</span><strong>${aDone}/${priorityChapters("A").length}</strong><em>największy zwrot z nauki</em></div>
    <div class="metric"><span>Fiszki</span><strong>${knownCount}/${data.cards.length}</strong><em>oznaczone jako umiane</em></div>
    <div class="metric"><span>Następny ruch</span><strong>${escapeHtml(next.priority)}</strong><em>${escapeHtml(next.title)}</em></div>
    <div class="metric"><span>Zegar</span><strong id="clockShort">${escapeHtml(clock.short)}</strong><em id="clockLabel">${escapeHtml(clock.label)}</em></div>`;
  updateClockOnly();
}
function chapterButton(ch){
  const complete = !!state.done[ch.id];
  return `<button class="chapter-btn ${state.chapter===ch.id?'active':''} ${complete?'complete':''}" onclick="setChapter('${ch.id}')">
    <span class="check">${complete?'✓':''}</span>
    <strong>${escapeHtml(ch.title)}</strong>
    <span class="badge ${ch.priority.toLowerCase()}">${ch.priority}</span>
  </button>`;
}
function renderSidebar(){
  const q = byId("search").value.trim().toLowerCase();
  const chapters = data.chapters.filter(ch => {
    const textMatch = !q || JSON.stringify(ch).toLowerCase().includes(q);
    const filterMatch = state.filter === "all" || ch.priority === state.filter || String(ch.day) === state.filter;
    return textMatch && filterMatch;
  });
  byId("progressText").textContent = `${progress()}%`;
  byId("progressBar").style.width = progress() + "%";
  document.querySelectorAll(".filter").forEach(btn => btn.classList.toggle("active", btn.dataset.filter === state.filter));
  byId("chapterList").innerHTML = chapters.map(chapterButton).join("") || `<div class="empty">Brak wyników</div>`;
}
function iconSvg(name){
  const icons = {
    table: '<svg viewBox="0 0 24 24"><path d="M4 5h16v14H4z"/><path d="M4 10h16"/><path d="M10 5v14"/></svg>',
    flow: '<svg viewBox="0 0 24 24"><path d="M4 7h10"/><path d="M14 7l-3-3"/><path d="M14 7l-3 3"/><path d="M10 17h10"/><path d="M20 17l-3-3"/><path d="M20 17l-3 3"/><path d="M4 17h2"/></svg>',
    memo: '<svg viewBox="0 0 24 24"><path d="M9 18h6"/><path d="M10 22h4"/><path d="M8 14a6 6 0 1 1 8 0c-.8.7-1.2 1.5-1.2 2.5H9.2c0-1-.4-1.8-1.2-2.5z"/></svg>',
    core: '<svg viewBox="0 0 24 24"><path d="M12 3v18"/><path d="M5 8h14"/><path d="M5 16h14"/></svg>',
    question: '<svg viewBox="0 0 24 24"><path d="M9.1 9a3 3 0 1 1 5.8 1c-.5 1.1-1.7 1.5-2.3 2.4-.4.5-.5 1-.5 1.6"/><path d="M12 18h.01"/><path d="M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0z"/></svg>',
    target: '<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="8"/><circle cx="12" cy="12" r="3"/><path d="M12 2v4"/><path d="M12 18v4"/><path d="M2 12h4"/><path d="M18 12h4"/></svg>',
    hand: '<svg viewBox="0 0 24 24"><path d="M8 11V5a2 2 0 0 1 4 0v6"/><path d="M12 10V4a2 2 0 0 1 4 0v8"/><path d="M16 11V6a2 2 0 0 1 4 0v8c0 5-3 8-8 8-3 0-5-1-7-4l-2-3a2 2 0 0 1 3-2l2 2"/></svg>',
    ear: '<svg viewBox="0 0 24 24"><path d="M6 8a6 6 0 1 1 11 3c-1 2-3 3-3 6a3 3 0 0 1-6 0"/><path d="M10 8a2 2 0 1 1 4 1c-.6 1-1.5 1.4-1.8 2.4"/></svg>',
    eye: '<svg viewBox="0 0 24 24"><path d="M2 12s4-7 10-7 10 7 10 7-4 7-10 7S2 12 2 12z"/><circle cx="12" cy="12" r="3"/></svg>',
    speech: '<svg viewBox="0 0 24 24"><path d="M4 5h16v10H8l-4 4z"/><path d="M8 9h8"/><path d="M8 12h5"/></svg>',
    message: '<svg viewBox="0 0 24 24"><path d="M21 15a4 4 0 0 1-4 4H8l-5 3V7a4 4 0 0 1 4-4h10a4 4 0 0 1 4 4z"/><path d="M8 9h8"/><path d="M8 13h6"/></svg>',
    activity: '<svg viewBox="0 0 24 24"><path d="M3 12h4l3-8 4 16 3-8h4"/></svg>',
    balance: '<svg viewBox="0 0 24 24"><path d="M12 3v18"/><path d="M5 7h14"/><path d="M6 7l-3 6h6z"/><path d="M18 7l-3 6h6z"/></svg>',
    zap: '<svg viewBox="0 0 24 24"><path d="M13 2L4 14h7l-1 8 10-13h-7z"/></svg>',
    filter: '<svg viewBox="0 0 24 24"><path d="M4 5h16l-6 7v5l-4 2v-7z"/></svg>',
    thermo: '<svg viewBox="0 0 24 24"><path d="M14 14.8V5a2 2 0 0 0-4 0v9.8a4 4 0 1 0 4 0z"/><path d="M12 9v7"/></svg>',
    book: '<svg viewBox="0 0 24 24"><path d="M4 5a3 3 0 0 1 3-3h13v17H7a3 3 0 0 0-3 3z"/><path d="M8 6h8"/></svg>',
    alert: '<svg viewBox="0 0 24 24"><path d="M12 3l10 18H2z"/><path d="M12 9v5"/><path d="M12 18h.01"/></svg>'
  };
  return `<span class="icon" aria-hidden="true">${icons[name] || icons.core}</span>`;
}
function renderVisuals(ch){
  const visuals = ch.visuals || { tables: [], schemes: [] };
  const tables = (visuals.tables || []).map(t => `<div class="visual-card">
    <header>${iconSvg('table')}<span>${escapeHtml(t.title)}</span></header>
    <table class="visual-table">
      <thead><tr>${t.columns.map(c => `<th>${escapeHtml(c)}</th>`).join("")}</tr></thead>
      <tbody>${t.rows.map(row => `<tr>${row.map(cell => `<td>${escapeHtml(cell)}</td>`).join("")}</tr>`).join("")}</tbody>
    </table>
  </div>`).join("");
  const schemes = (visuals.schemes || []).length ? `<div class="visual-card">
    <header>${iconSvg('flow')}<span>Schematy decyzyjne</span></header>
    <div class="flow-list">${visuals.schemes.map(steps => `<div class="flow">${steps.map((step, idx) => `${idx ? '<span class="flow-arrow">→</span>' : ''}<span class="flow-step">${escapeHtml(step)}</span>`).join("")}</div>`).join("")}</div>
  </div>` : "";
  return tables + schemes;
}
function renderMemos(ch){
  return `<div class="visual-card">
    <header>${iconSvg('memo')}<span>Mnemotechniki</span></header>
    <div class="memo-list">${ch.memory.map(m => `<div class="memo"><span class="tag">${iconSvg('memo')}</span><span>${escapeHtml(m)}</span></div>`).join("")}</div>
  </div>`;
}
function renderExamQuestions(ch, limit = 999){
  const questions = ch.exam_questions || [];
  if (!questions.length) return `<div class="empty">Brak pytań z bazy przypisanych do tego działu.</div>`;
  return `<div class="exam-list">${questions.slice(0, limit).map(q => {
    const options = (q.options || []).map((opt, idx) => {
      const label = String.fromCharCode(65 + idx);
      return `<div class="option ${opt.correct ? 'correct' : ''}"><b>${label}</b><span>${escapeHtml(opt.text)}</span></div>`;
    }).join("");
    return `<article class="exam-card">
      <strong>${escapeHtml(q.stem)}</strong>
      <div class="option-list">${options}</div>
      <details><summary>Odpowiedź</summary><p>${escapeHtml(q.answer_letter || "?")}. ${escapeHtml(q.answer || "")}</p></details>
      <div class="source-note">${escapeHtml(q.source || "baza pytań")} • pyt. ${escapeHtml(q.number || "")}</div>
    </article>`;
  }).join("")}</div>`;
}
function renderSourceUpdates(ch){
  const sources = ch.source_updates || [];
  if (!sources.length) return "";
  return `<section class="panel section">
    <h3>${iconSvg('core')} Aktualizacja z prezentacji</h3>
    <div class="source-grid">${sources.map(source => `<div class="source-box">
      <h4>${escapeHtml(source.file)}</h4>
      <ul>${(source.key_points || []).slice(0, 12).map(point => `<li>${escapeHtml(point)}</li>`).join("")}</ul>
    </div>`).join("")}</div>
  </section>`;
}
function renderChapter(){
  const ch = data.chapters.find(c => c.id === state.chapter) || data.chapters[0];
  const digest = (ch.digest_html || []).map(x => `<li>${escapeHtml(x)}</li>`).join("");
  byId("learnView").innerHTML = `<article class="panel">
    <div class="chapter-head">
      <div>
        <h2>${escapeHtml(ch.title)}</h2>
        <p>${escapeHtml(ch.summary)}</p>
      </div>
      <div class="pill-row">
        <span class="pill">dzień ${ch.day}</span>
        <span class="pill">str. ${escapeHtml(ch.pages)}</span>
        <span class="pill">priorytet ${ch.priority}</span>
        <span class="pill">${escapeHtml(ch.time)}</span>
      </div>
    </div>
    <div class="tools">
      <button class="tool-btn ${state.done[ch.id]?'done':''}" onclick="toggleDone('${ch.id}')" title="Oznacz rozdział jako przerobiony">${state.done[ch.id]?'✓ Zrobione':'□ Do zrobienia'}</button>
      <button class="tool-btn" onclick="state.cardIndex = firstCardFor('${escapeJs(ch.title)}'); setView('flash')" title="Przejdź do fiszek z rozdziału">↻ Fiszki</button>
      <a class="tool-btn" href="./neuro_sprint_48h.pdf" title="Otwórz PDF">PDF</a>
    </div>
    <div class="quick-grid">
      <div class="visual-stack">${renderVisuals(ch)}</div>
      <div class="visual-stack">${renderMemos(ch)}</div>
    </div>
    <div class="grid">
      <section class="section">
        <h3>${iconSvg('core')} Sedno</h3>
        <ul>${ch.core.map(x => `<li>${escapeHtml(x)}</li>`).join("")}</ul>
      </section>
      <section class="section">
        <h3>${iconSvg('question')} Baza pytań</h3>
        ${renderExamQuestions(ch, 5)}
      </section>
    </div>
  </article>
  ${renderSourceUpdates(ch)}
  <section class="panel section">
    <h3>${iconSvg('question')} Pełna baza pytań działu</h3>
    ${renderExamQuestions(ch)}
  </section>
  <section class="panel section">
    <h3>Warstwa 2 - kondensat ze skryptu</h3>
    <ul>${digest}</ul>
  </section>`;
}
function firstCardFor(chapterTitle){
  const i = data.cards.findIndex(c => c.chapter === chapterTitle);
  return i >= 0 ? i : 0;
}
function renderPlan(){
  byId("planView").innerHTML = `<div class="plan-grid">${data.plan.map(day => `<section class="panel">
    <h2>${escapeHtml(day.title)}</h2>
    ${day.blocks.map(b => `<div class="block">${escapeHtml(b)}</div>`).join("")}
  </section>`).join("")}</div>
  <section class="panel section"><h3>Lista rozdziałów</h3><ul>${data.chapters.map(ch => `<li><b>Dzień ${ch.day}</b>: ${escapeHtml(ch.title)} - ${escapeHtml(ch.time)} (${ch.priority})</li>`).join("")}</ul></section>`;
}
function renderFlash(){
  const card = data.cards[state.cardIndex % data.cards.length];
  byId("flashView").innerHTML = `<section class="panel flash">
    <div>
      <div class="pill-row" style="justify-content:center"><span class="pill">${escapeHtml(card.chapter)}</span><span class="pill">${state.cardIndex+1}/${data.cards.length}</span></div>
      <h3>${escapeHtml(card.q)}</h3>
      <p class="answer" id="answer">${escapeHtml(card.a)}</p>
      <div class="tools" style="justify-content:center">
        <button class="primary" onclick="byId('answer').classList.add('show')">Pokaż</button>
        <button class="tool-btn" onclick="markCard(false)">Powtórz</button>
        <button class="tool-btn" onclick="markCard(true)">Umiem</button>
        <button class="tool-btn" onclick="nextCard()">Dalej</button>
      </div>
    </div>
  </section>`;
}
function markCard(ok){
  const card = data.cards[state.cardIndex % data.cards.length];
  state.known[card.q] = ok ? (state.known[card.q] || 0) + 1 : 0;
  nextCard();
}
function nextCard(){
  const weak = data.cards.findIndex((c, i) => i > state.cardIndex && !state.known[c.q]);
  state.cardIndex = weak >= 0 ? weak : (state.cardIndex + 1) % data.cards.length;
  save(); renderFlash();
}
function renderBrain(){
  const selected = data.brain.find(c => c.id === state.brainCenter) || data.brain[0];
  const active = id => state.brainCenter === id ? 'active' : '';
  const cards = data.brain.map(center => `<article class="center-card ${active(center.id)}" onclick="setBrainCenter('${center.id}')">
    <h3>${iconSvg(center.icon)} ${escapeHtml(center.name)}</h3>
    <div class="short">${escapeHtml(center.short)}</div>
    <dl>
      <dt>Odpowiada za</dt>
      <dd>${center.functions.map(escapeHtml).join(", ")}</dd>
      <dt>Uszkodzenie daje</dt>
      <dd>${escapeHtml(center.lesion)}</dd>
    </dl>
    <span class="mnemo-chip">${escapeHtml(center.mnemo)}</span>
  </article>`).join("");
  const legend = data.brain.map(center => `<button class="legend-btn ${active(center.id)}" onclick="setBrainCenter('${center.id}')">${escapeHtml(center.name)}</button>`).join("");
  byId("brainView").innerHTML = `<section class="panel">
    <div class="chapter-head">
      <div>
        <h2>Mapa mózgu i ośrodków</h2>
        <p>Ucz się tego jak lokalizatora: objaw z pytania prowadzi do płata, ośrodka albo struktury podkorowej.</p>
      </div>
      <div class="pill-row"><span class="pill">objaw → lokalizacja</span><span class="pill">ikonki + mnemo</span></div>
    </div>
    <div class="brain-layout">
      <aside class="brain-map">
        <svg class="brain-svg" viewBox="0 0 520 340" role="img" aria-label="Schemat mózgu z płatami i strukturami">
          <g class="brain-region ${active('frontal')}" onclick="setBrainCenter('frontal')">
            <path d="M116 140 C105 75 155 42 222 48 L238 150 L190 198 C150 202 124 183 116 140Z" fill="#d9655d" stroke="#ffffff" stroke-width="2"/>
          </g>
          <g class="brain-region ${active('parietal')}" onclick="setBrainCenter('parietal')">
            <path d="M222 48 C292 37 358 72 378 130 L305 181 L238 150Z" fill="#3c7f78" stroke="#ffffff" stroke-width="2"/>
          </g>
          <g class="brain-region ${active('temporal')}" onclick="setBrainCenter('temporal')">
            <path d="M190 198 L305 181 L356 232 C320 270 250 278 197 244 C176 231 174 211 190 198Z" fill="#d7a33f" stroke="#ffffff" stroke-width="2"/>
          </g>
          <g class="brain-region ${active('occipital')}" onclick="setBrainCenter('occipital')">
            <path d="M378 130 C426 145 438 199 410 232 C397 248 377 251 356 232 L305 181Z" fill="#4869a8" stroke="#ffffff" stroke-width="2"/>
          </g>
          <g class="brain-region ${active('basal')}" onclick="setBrainCenter('basal')">
            <ellipse cx="270" cy="165" rx="42" ry="25" fill="#8b5fbf" stroke="#ffffff" stroke-width="2"/>
          </g>
          <g class="brain-region ${active('thalamus')}" onclick="setBrainCenter('thalamus')">
            <ellipse cx="305" cy="154" rx="28" ry="18" fill="#6d7d8b" stroke="#ffffff" stroke-width="2"/>
          </g>
          <g class="brain-region ${active('hypothalamus')}" onclick="setBrainCenter('hypothalamus')">
            <ellipse cx="304" cy="188" rx="22" ry="13" fill="#66a36f" stroke="#ffffff" stroke-width="2"/>
          </g>
          <g class="brain-region ${active('hippocampus')}" onclick="setBrainCenter('hippocampus')">
            <path d="M247 213 C275 198 316 204 335 223 C309 230 277 235 247 226Z" fill="#b85f8a" stroke="#ffffff" stroke-width="2"/>
          </g>
          <g class="brain-region ${active('amygdala')}" onclick="setBrainCenter('amygdala')">
            <ellipse cx="230" cy="222" rx="18" ry="13" fill="#cf6f38" stroke="#ffffff" stroke-width="2"/>
          </g>
          <g class="brain-region ${active('cerebellum')}" onclick="setBrainCenter('cerebellum')">
            <ellipse cx="377" cy="267" rx="67" ry="38" fill="#0e8a9a" stroke="#ffffff" stroke-width="2"/>
            <path d="M330 260 C360 248 395 248 425 260" stroke="#ffffff" stroke-width="2"/>
            <path d="M330 276 C360 286 395 286 425 276" stroke="#ffffff" stroke-width="2"/>
          </g>
          <g class="brain-region ${active('brainstem')}" onclick="setBrainCenter('brainstem')">
            <path d="M316 232 C330 244 336 262 331 291 L310 321 L292 321 L302 288 C306 266 302 249 292 235Z" fill="#7b8a3d" stroke="#ffffff" stroke-width="2"/>
          </g>
          <g class="brain-region ${active('broca')}" onclick="setBrainCenter('broca')">
            <circle cx="172" cy="178" r="13" fill="#ffffff" stroke="#16324f" stroke-width="3"/>
            <text x="172" y="182" text-anchor="middle" font-size="11" font-weight="800" fill="#16324f">B</text>
          </g>
          <g class="brain-region ${active('wernicke')}" onclick="setBrainCenter('wernicke')">
            <circle cx="323" cy="205" r="13" fill="#ffffff" stroke="#16324f" stroke-width="3"/>
            <text x="323" y="209" text-anchor="middle" font-size="11" font-weight="800" fill="#16324f">W</text>
          </g>
        </svg>
        <div class="brain-legend">${legend}</div>
      </aside>
      <div>
        <section class="visual-card" style="margin-bottom:12px">
          <header>${iconSvg(selected.icon)}<span>${escapeHtml(selected.name)}: ${escapeHtml(selected.short)}</span></header>
          <div class="memo-list">
            <div class="memo"><span class="tag">${iconSvg('core')}</span><span><b>Funkcje:</b> ${selected.functions.map(escapeHtml).join(", ")}</span></div>
            <div class="memo"><span class="tag">${iconSvg('alert')}</span><span><b>Uszkodzenie:</b> ${escapeHtml(selected.lesion)}</span></div>
            <div class="memo"><span class="tag">${iconSvg('memo')}</span><span><b>MNEMO:</b> ${escapeHtml(selected.mnemo)}</span></div>
          </div>
        </section>
        <div class="center-grid">${cards}</div>
      </div>
    </div>
  </section>`;
}
function renderQuiz(){
  const items = state.panic ? data.quiz.filter(item => {
    const ch = data.chapters.find(c => c.title === item.chapter);
    return ch && ch.priority === "A";
  }) : data.quiz;
  byId("quizView").innerHTML = `<section class="panel"><h2>${state.panic ? "Ostatnia godzina" : "Test ustny"}</h2>
    <div class="tools"><button class="tool-btn" onclick="state.panic=${state.panic ? "false" : "true"}; save(); renderQuiz()">${state.panic ? "Pełny test" : "Tylko priorytet A"}</button></div>
    <div class="exam-list">${items.map((item, idx) => {
      const options = (item.options || []).map((opt, optIdx) => {
        const label = String.fromCharCode(65 + optIdx);
        return `<div class="option ${opt.correct ? 'correct' : ''}"><b>${label}</b><span>${escapeHtml(opt.text)}</span></div>`;
      }).join("");
      return `<div class="exam-card">
        <strong>${idx+1}. ${escapeHtml(item.q)}</strong>
        <span class="pill">${escapeHtml(item.chapter)}</span>
        <div class="option-list">${options}</div>
        <details><summary>Odpowiedź</summary><p>${escapeHtml(item.a)}</p></details>
        <div class="source-note">${escapeHtml(item.source || "baza")} • pyt. ${escapeHtml(item.number || "")}</div>
      </div>`;
    }).join("")}</div>
  </section>`;
}
function render(){
  renderSidebar();
  renderStatus();
  if (state.view === "learn") renderChapter();
  if (state.view === "plan") renderPlan();
  if (state.view === "flash") renderFlash();
  if (state.view === "quiz") renderQuiz();
  if (state.view === "brain") renderBrain();
}
setInterval(updateClockOnly, 15000);
function panicMode(){
  state.panic = true;
  state.view = "quiz";
  save();
  setView("quiz");
}
function escapeHtml(str){
  return String(str).replace(/[&<>"']/g, s => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[s]));
}
function escapeJs(str){ return String(str).replace(/'/g, "\\\\'"); }
document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll(".tab").forEach(btn => btn.addEventListener("click", () => setView(btn.dataset.view)));
  byId("search").addEventListener("input", renderSidebar);
  setView(state.view || "learn");
});
"""
    page = f"""<!doctype html>
<html lang="pl">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>NeuroSprint 48h</title>
  <style>{css}</style>
</head>
<body>
  <div class="app">
    <aside class="side">
      <div class="brand">
        <div class="brand-mark" aria-hidden="true"></div>
        <div><h1>NeuroSprint 48h</h1><small><span id="progressText">0%</span> materiału</small></div>
      </div>
      <div class="progress"><span id="progressBar"></span></div>
      <div class="tabs">
        <button class="tab" data-view="learn">Nauka</button>
        <button class="tab" data-view="plan">Plan</button>
        <button class="tab" data-view="flash">Fiszki</button>
        <button class="tab" data-view="quiz">Test</button>
        <button class="tab" data-view="brain">Mózg</button>
      </div>
      <input id="search" class="search" type="search" placeholder="Szukaj tematu">
      <div class="filters">
        <button class="filter" data-filter="all" onclick="setFilter('all')">All</button>
        <button class="filter" data-filter="A" onclick="setFilter('A')">A</button>
        <button class="filter" data-filter="1" onclick="setFilter('1')">Dziś</button>
        <button class="filter" data-filter="2" onclick="setFilter('2')">Jutro</button>
      </div>
      <div id="chapterList" class="chapter-list"></div>
    </aside>
    <main class="main">
      <div class="topbar">
        <div>
          <h2>Neurologia - kondensat</h2>
          <div class="meta">Materiał z PDF-u: NASIOSKRYPT-NEUROLOGIA • <span id="clockText">start 19:15</span></div>
        </div>
        <div class="tools">
          <a class="tool-btn" href="./neuro_sprint_48h.pdf">PDF</a>
          <a class="tool-btn" href="./neuro_fiszki_anki.csv">CSV</a>
          <button class="tool-btn" onclick="panicMode()">Ostatnia godzina</button>
          <button class="tool-btn" onclick="window.print()">Druk</button>
        </div>
      </div>
      <section id="statusPanel" class="status-panel"></section>
      <div id="learnView" class="view"></div>
      <div id="planView" class="view"></div>
      <div id="flashView" class="view"></div>
      <div id="quizView" class="view"></div>
      <div id="brainView" class="view"></div>
    </main>
  </div>
  <script>{js.replace("DATA_PLACEHOLDER", payload)}</script>
</body>
</html>
"""
    path.write_text(page, encoding="utf-8")
    return path


def build_csv(cards: list[dict[str, str]]) -> Path:
    path = OUT / "neuro_fiszki_anki.csv"
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, delimiter=";")
        writer.writerow(["Pytanie", "Odpowiedź", "Rozdział"])
        for card in cards:
            writer.writerow([card["q"], card["a"], card["chapter"]])
    return path


def main() -> None:
    pages = load_pages()
    external = load_external_bundle()
    grouped_questions = questions_by_topic(external)
    grouped_sources = sources_by_topic(external)
    chapters = json.loads(json.dumps(CHAPTERS, ensure_ascii=False))
    for chapter in chapters:
        chapter["visuals"] = VISUALS.get(chapter["id"], {"tables": [], "schemes": []})
        chapter["exam_questions"] = grouped_questions.get(chapter["id"], [])
        chapter["source_updates"] = grouped_sources.get(chapter["id"], [])
        chapter["digest_html"] = source_digest(chapter, pages, 125 if chapter["priority"] == "A" else 80, min_score=3)
        chapter["digest_pdf"] = source_digest(chapter, pages, 34 if chapter["priority"] == "A" else 22, min_score=3)
    cards = build_cards(chapters)
    quiz = build_quiz(chapters)
    pdf = build_pdf(chapters, cards)
    html_path = build_html(chapters, cards, quiz)
    csv_path = build_csv(cards)
    page_count = len(PdfReader(str(pdf)).pages)
    print(f"PDF: {pdf} ({page_count} pages)")
    print(f"HTML: {html_path}")
    print(f"CSV: {csv_path} ({len(cards)} cards)")
    if page_count > 60:
        raise SystemExit(f"PDF exceeds 60 pages: {page_count}")


if __name__ == "__main__":
    main()
