from __future__ import annotations

import random

OPENINGS = {
    "en": (
        "The Fund aims to achieve long-term capital growth by investing",
        "The objective of the Fund is to provide a total return by investing",
        "The Fund seeks to outperform its benchmark over the recommended holding period by investing",
        "This Fund is actively managed and invests",
    ),
    "de": (
        "Der Fonds strebt langfristiges Kapitalwachstum an und investiert",
        "Ziel des Fonds ist die Erwirtschaftung einer Gesamtrendite durch Anlagen",
        "Der Fonds strebt an, seinen Referenzwert zu übertreffen, und investiert",
        "Dieser Fonds wird aktiv verwaltet und investiert",
    ),
    "fr": (
        "Le Fonds vise une croissance du capital à long terme en investissant",
        "L'objectif du Fonds est de générer un rendement total en investissant",
        "Le Fonds cherche à surperformer son indice de référence en investissant",
        "Ce Fonds est géré activement et investit",
    ),
    "nl": (
        "Het Fonds streeft naar vermogensgroei op lange termijn door te beleggen",
        "Het doel van het Fonds is een totaalrendement te behalen door te beleggen",
        "Het Fonds streeft ernaar zijn benchmark te overtreffen door te beleggen",
        "Dit Fonds wordt actief beheerd en belegt",
    ),
}

HOLDINGS = {
    "Global Equity": {
        "en": "in a diversified portfolio of equities of companies worldwide",
        "de": "in ein diversifiziertes Portfolio von Aktien weltweiter Unternehmen",
        "fr": "dans un portefeuille diversifié d'actions de sociétés du monde entier",
        "nl": "in een gespreide portefeuille van aandelen van ondernemingen wereldwijd",
    },
    "European Equity": {
        "en": "primarily in equities of companies domiciled in Europe",
        "de": "überwiegend in Aktien von Unternehmen mit Sitz in Europa",
        "fr": "principalement dans des actions de sociétés domiciliées en Europe",
        "nl": "voornamelijk in aandelen van in Europa gevestigde ondernemingen",
    },
    "Emerging Markets Equity": {
        "en": "in equities of companies located in emerging market countries",
        "de": "in Aktien von Unternehmen aus Schwellenländern",
        "fr": "dans des actions de sociétés situées dans les pays émergents",
        "nl": "in aandelen van ondernemingen in opkomende markten",
    },
    "Euro Government Bond": {
        "en": "in bonds issued by euro area governments",
        "de": "in Anleihen von Staaten des Euroraums",
        "fr": "dans des obligations émises par des États de la zone euro",
        "nl": "in obligaties uitgegeven door overheden in de eurozone",
    },
    "Euro Corporate Bond": {
        "en": "in investment grade bonds issued by companies in the euro area",
        "de": "in Investment-Grade-Anleihen von Unternehmen im Euroraum",
        "fr": "dans des obligations investment grade émises par des sociétés de la zone euro",
        "nl": "in investment grade obligaties van ondernemingen in de eurozone",
    },
    "Global High Yield": {
        "en": "in sub-investment grade corporate bonds issued worldwide",
        "de": "in Unternehmensanleihen unterhalb von Investment Grade weltweit",
        "fr": "dans des obligations d'entreprises à haut rendement dans le monde entier",
        "nl": "in bedrijfsobligaties met een rating onder investment grade wereldwijd",
    },
    "Sustainable Global Equity": {
        "en": "in equities of companies worldwide that meet the Fund's sustainability criteria",
        "de": "in Aktien weltweiter Unternehmen, die die Nachhaltigkeitskriterien des Fonds erfüllen",
        "fr": "dans des actions de sociétés répondant aux critères de durabilité du Fonds",
        "nl": "in aandelen van ondernemingen die voldoen aan de duurzaamheidscriteria van het Fonds",
    },
    "Multi-Asset Balanced": {
        "en": "across equities, bonds and money market instruments",
        "de": "in Aktien, Anleihen und Geldmarktinstrumente",
        "fr": "en actions, obligations et instruments du marché monétaire",
        "nl": "in aandelen, obligaties en geldmarktinstrumenten",
    },
    "Short Duration Bond": {
        "en": "in bonds with a residual maturity of less than three years",
        "de": "in Anleihen mit einer Restlaufzeit von weniger als drei Jahren",
        "fr": "dans des obligations dont la maturité résiduelle est inférieure à trois ans",
        "nl": "in obligaties met een resterende looptijd van minder dan drie jaar",
    },
    "Technology Equity": {
        "en": "in equities of companies active in the information technology sector",
        "de": "in Aktien von Unternehmen aus dem Informationstechnologiesektor",
        "fr": "dans des actions de sociétés du secteur des technologies de l'information",
        "nl": "in aandelen van ondernemingen in de informatietechnologiesector",
    },
    "Real Estate Equity": {
        "en": "in listed real estate companies and REITs in developed Europe",
        "de": "in börsennotierte Immobiliengesellschaften und REITs in Europa",
        "fr": "dans des sociétés immobilières cotées et des REIT en Europe développée",
        "nl": "in beursgenoteerde vastgoedondernemingen en REIT's in ontwikkeld Europa",
    },
    "Money Market": {
        "en": "in high quality short-term money market instruments",
        "de": "in kurzfristige Geldmarktinstrumente hoher Qualität",
        "fr": "dans des instruments du marché monétaire de haute qualité à court terme",
        "nl": "in kortlopende geldmarktinstrumenten van hoge kwaliteit",
    },
}

CLOSINGS = {
    "en": (
        "The Fund is managed with reference to the {benchmark} index.",
        "Performance is compared against the {benchmark}.",
        "The Fund does not track any index.",
        "",
    ),
    "de": (
        "Der Fonds wird unter Bezugnahme auf den Index {benchmark} verwaltet.",
        "Die Wertentwicklung wird mit {benchmark} verglichen.",
        "Der Fonds bildet keinen Index nach.",
        "",
    ),
    "fr": (
        "Le Fonds est géré en référence à l'indice {benchmark}.",
        "La performance est comparée à {benchmark}.",
        "Le Fonds ne réplique aucun indice.",
        "",
    ),
    "nl": (
        "Het Fonds wordt beheerd met {benchmark} als referentie-index.",
        "De prestaties worden vergeleken met {benchmark}.",
        "Het Fonds volgt geen index.",
        "",
    ),
}


def objective_text(strategy: str, benchmark: str, language: str, rng: random.Random) -> str:
    opening = rng.choice(OPENINGS[language])
    holding = HOLDINGS[strategy][language]
    closing = rng.choice(CLOSINGS[language]).format(benchmark=benchmark)
    sentence = f"{opening} {holding}."
    return f"{sentence} {closing}".strip() if closing else sentence
