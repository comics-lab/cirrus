#!/usr/bin/env python3
from __future__ import annotations

import os
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET


BOOKS = [
    {
        "path": "/mnt/phoenix/media/incoming/jdownloader/DC Finest - Batman - A Death in the Family (TPB) (2026) –/DC Finest - Batman - A Death in the Family (2026) (hybrid) (Marika-Empire).cbz",
        "series": "DC Finest: Batman: A Death in the Family",
        "title": "Batman A Death in the Family",
        "number": "1",
        "volume": "2026",
        "year": "2026",
        "month": "4",
        "publisher": "DC Comics",
        "format": "Trade Paper Back",
        "page_count": "641",
        "series_group": "Batman Trades",
        "summary": (
            "Death comes to us all, now in DC Finest!\n"
            "In 1988 the pop culture world was rocked when comics readers were given the "
            "opportunity to decide the outcome of one of the medium's most controversial "
            "quandaries: Should the Boy Wonder die?\n"
            "When Jason Todd's impulsive nature clashes with the Dark Knight's methodical "
            "approach to crime-fighting yet again, Jason takes off on his own in search of his "
            "birth mother. Meanwhile, Batman's latest case leads him to the Middle East, hot on "
            "the trail of the Joker, whois brokering the sale of a nuclear device to terrorists! "
            "Realizing that they must work together to prevent a global disaster and find Jason's "
            "long-lost mother, Batman and Robin reunite in time to thwart the Clown Prince of "
            "Crime. However, this setback sets in motion a far more sinister plot that ultimately "
            "leads to betrayal and a deadly date with a crowbar...\n"
            "The decision to kill off the second Robin drew polarized opinions from fans and "
            "critics and remains one of the most controversial story arcs in the history of the "
            "Caped Crusader. Would the Dark Knight slip into the darkness of the abyss without a "
            "Boy Wonder to hold him back? And would fans ever accept another wayward youth "
            "stepping into the role of Robin?\n"
            "Collects Batman #423-429, Batman Annual #12, Batman: The Cult #1-4, Detective "
            "Comics #590-595, Detective Comics Annual #1"
        ),
        "notes": (
            "[ISBN9781799508571] [GCDISS2829748] Local library metadata build from existing "
            "collection metadata, GCD issue data, and Penguin Random House catalog data; no "
            "ComicVine id attached."
        ),
        "web": "https://prhcomics.com/book/?isbn=9781799508571",
        "isbn": "9781799508571",
        "gcd": "2829748",
        "source": "PRH + GCD",
        "scan_information": "Marika-Empire",
        "tags": "CVDBSKIP, HYBRID, ISBN",
    },
    {
        "path": "/mnt/phoenix/media/incoming/jdownloader/DC/DC Finest - Justice League of America - Starro the Conqueror (TPB) (2026) –/DC Finest - Justice League of America - Starro the Conqueror v01 (2026) (hybrid) (Marika-Empire).cbz",
        "series": "DC Finest: Justice League of America - Starro the Conqueror",
        "title": "Starro the Conqueror",
        "number": "1",
        "volume": "2026",
        "year": "2026",
        "month": "3",
        "publisher": "DC Comics",
        "format": "Trade Paper Back",
        "page_count": "626",
        "series_group": "Justice League Trades",
        "summary": (
            "Six heroes. One star-shaped alien menace. This is how legends are made.\n"
            "When an alien being with cosmic powers attacks Earth, a new era of heroism is born. "
            "Starro the Conqueror forces the DC Universe's greatest champions to unite-launching "
            "the first Justice League and sparking a legacy of team-based storytelling still "
            "going strong today.\n"
            "Packed with battles against villains like Despero, Felix Faust, and Kanjar Ro, this "
            "collection showcases the early years of the JLA: wild sci-fi plots, impossible odds, "
            "and the birth of super-team chemistry. It's the origin story for the world's greatest "
            "heroes, told with the imagination and excitement of comics' most influential era.\n"
            "Brings together The Brave and the Bold #28-30, Justice League of America #1-19, and "
            "Mystery in Space #75."
        ),
        "notes": (
            "[ISBN9781799507734] [GCD2825349] Local library metadata build from existing "
            "collection metadata, GCD issue data, and Penguin Random House catalog data; no "
            "ComicVine id attached."
        ),
        "web": "https://prhcomics.com/book/?isbn=9781799507734",
        "isbn": "9781799507734",
        "gcd": "2825349",
        "source": "PRH + GCD",
        "scan_information": "Marika-Empire",
        "tags": "CVDBSKIP, HYBRID, ISBN",
    },
    {
        "path": "/mnt/phoenix/media/incoming/jdownloader/DC/DC Finest - Justice Society of America - The Plunder of the Psycho-Pirate (TPB) (2025) –/DC Finest - Justice Society of America - The Plunder of the Psycho-Pirate v01 (2025) (hybrid) (Marika-Empire).cbz",
        "series": "DC Finest: Justice Society of America: The Plunder of the Psycho-Pirate",
        "title": "The Plunder of the Psycho-Pirate",
        "number": "1",
        "volume": "2025",
        "year": "2025",
        "month": "8",
        "publisher": "DC Comics",
        "format": "Trade Paper Back",
        "page_count": "608",
        "series_group": "Justice Society Trades",
        "summary": (
            "A Golden Age classic starring the Justice Society of America, collected for today's "
            "readers! Experience a pivotal story arc in JSA history featuring the Psycho-Pirate!\n"
            "DC Finest continues, a major publishing initiative presenting comprehensive "
            "collections of the most in-demand and celebrated periods in DC Comics history, "
            "spanning genres, characters, and eras!\n"
            "Written by Golden Age all-star, Gardner Fox, the Justice Society encounters a "
            "powerful new foe with the ability to manipulate their emotions! Will the "
            "Psycho-Pirate prove too much for the team to handle?\n"
            "This volume collects All-Star Comics #13-24."
        ),
        "notes": (
            "[ISBN9781799502074] [GCD2755359] Local library metadata build from existing "
            "collection metadata, GCD issue data, and Penguin Random House catalog data; no "
            "ComicVine id attached."
        ),
        "web": "https://www.penguinrandomhouseretail.com/book/?isbn=9781799502074",
        "isbn": "9781799502074",
        "gcd": "2755359",
        "source": "PRH + GCD",
        "scan_information": "Marika-Empire",
        "tags": "CVDBSKIP, HYBRID, ISBN",
    },
]


def add(parent: ET.Element, tag: str, value: str | None) -> None:
    if value is None or value == "":
        return
    ET.SubElement(parent, tag).text = value


def build_comicinfo(book: dict) -> bytes:
    root = ET.Element("ComicInfo")
    add(root, "Title", book["title"])
    add(root, "Series", book["series"])
    add(root, "Number", book["number"])
    add(root, "Volume", book["volume"])
    add(root, "SeriesGroup", book["series_group"])
    add(root, "Summary", book["summary"])
    add(root, "Notes", book["notes"])
    add(root, "Web", book["web"])
    add(root, "Year", book["year"])
    add(root, "Month", book["month"])
    add(root, "Publisher", book["publisher"])
    add(root, "PageCount", book["page_count"])
    add(root, "Format", book["format"])
    add(root, "ScanInformation", book["scan_information"])
    add(root, "Tags", book["tags"])
    return ET.tostring(root, encoding="utf-8", xml_declaration=True)


def build_metroninfo(book: dict) -> bytes:
    root = ET.Element("MetronInfo")
    add(root, "Series", book["series"])
    add(root, "Title", book["title"])
    add(root, "Number", book["number"])
    add(root, "Volume", book["volume"])
    add(root, "Publisher", book["publisher"])
    add(root, "CoverDate", f"{book['year']}-{int(book['month']):02d}-01")
    add(root, "Format", book["format"])
    add(root, "Summary", book["summary"])
    add(root, "ISBN", book["isbn"])
    add(root, "Database", "GCD")
    add(root, "DatabaseId", book["gcd"])
    add(root, "Source", book["source"])
    add(root, "Notes", book["notes"])
    add(root, "Web", book["web"])
    return ET.tostring(root, encoding="utf-8", xml_declaration=True)


def rewrite_archive(cbz_path: Path, comicinfo_xml: bytes, metroninfo_xml: bytes) -> None:
    tmp_path = cbz_path.with_suffix(".tmp.cbz")
    with zipfile.ZipFile(cbz_path, "r") as zin, zipfile.ZipFile(
        tmp_path, "w", compression=zipfile.ZIP_DEFLATED
    ) as zout:
        for item in zin.infolist():
            lower_name = item.filename.lower()
            if lower_name in {"comicinfo.xml", "metroninfo.xml", "metroninfo.cml"}:
                continue
            zout.writestr(item, zin.read(item.filename))
        zout.writestr("ComicInfo.xml", comicinfo_xml)
        zout.writestr("MetronInfo.xml", metroninfo_xml)
    os.replace(tmp_path, cbz_path)


def main() -> int:
    for book in BOOKS:
        cbz_path = Path(book["path"])
        comicinfo = build_comicinfo(book)
        metroninfo = build_metroninfo(book)
        rewrite_archive(cbz_path, comicinfo, metroninfo)
        print(f"updated {cbz_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
