from __future__ import annotations

import random

from .layouts import HEADINGS

VARIANTS: dict[str, dict[str, tuple[str, ...]]] = {
    "en": {
        "objective": ("Objectives and investment policy", "Investment objective", "What is this product?", "Objectives"),
        "risk": ("Risk indicator", "Summary risk indicator", "Risk and reward profile", "Risk profile"),
        "costs": ("What are the costs?", "Charges", "Costs and charges", "What will this investment cost?"),
        "holding": ("How long should I hold it?", "Recommended holding period", "Investment horizon"),
        "practical": ("Practical information", "Other relevant information", "Further information"),
        "manufacturer": ("Manufacturer", "Management company", "PRIIP manufacturer", "Fund manager"),
        "isin": ("ISIN", "ISIN code", "Share class ISIN", "Identifier"),
        "currency": ("Currency", "Share class currency", "Base currency", "Fund currency"),
        "benchmark": ("Benchmark", "Reference index", "Comparator benchmark", "Index"),
        "domicile": ("Domicile", "Country of domicile", "Fund domicile", "Registered in"),
        "rhp": ("Recommended holding period", "Recommended minimum holding period", "Suggested holding period"),
        "ongoing": ("Ongoing charges", "Ongoing costs", "Ongoing charges figure", "Running costs"),
        "entry": ("Entry costs", "Entry charge", "Subscription fee", "Initial charge"),
        "exit": ("Exit costs", "Exit charge", "Redemption fee", "Deferred charge"),
        "transaction": ("Transaction costs", "Portfolio transaction costs", "Trading costs"),
        "performance_fee": ("Performance fee", "Performance-related fee", "Incentive fee"),
    },
    "de": {
        "objective": ("Ziele und Anlagepolitik", "Anlageziel", "Um welche Art von Produkt handelt es sich?", "Ziele"),
        "risk": ("Risikoindikator", "Gesamtrisikoindikator", "Risiko- und Ertragsprofil", "Risikoprofil"),
        "costs": ("Welche Kosten entstehen?", "Kosten", "Kosten und Gebühren", "Gebühren"),
        "holding": ("Wie lange sollte ich die Anlage halten?", "Empfohlene Haltedauer", "Anlagehorizont"),
        "practical": ("Praktische Informationen", "Weitere Informationen", "Sonstige Informationen"),
        "manufacturer": ("Hersteller", "Verwaltungsgesellschaft", "Fondsgesellschaft", "Anbieter"),
        "isin": ("ISIN", "ISIN-Code", "Wertpapierkennung", "Kennung"),
        "currency": ("Währung", "Fondswährung", "Anteilklassenwährung", "Basiswährung"),
        "benchmark": ("Referenzwert", "Vergleichsindex", "Benchmark", "Index"),
        "domicile": ("Sitz", "Fondsdomizil", "Sitzland", "Registriert in"),
        "rhp": ("Empfohlene Haltedauer", "Empfohlene Mindesthaltedauer", "Vorgeschlagene Haltedauer"),
        "ongoing": ("Laufende Kosten", "Laufende Gebühren", "Laufende Kosten des Fonds", "Verwaltungskosten"),
        "entry": ("Einstiegskosten", "Ausgabeaufschlag", "Zeichnungsgebühr", "Anfangsgebühr"),
        "exit": ("Ausstiegskosten", "Rücknahmeabschlag", "Rückgabegebühr"),
        "transaction": ("Transaktionskosten", "Portfoliotransaktionskosten", "Handelskosten"),
        "performance_fee": ("Erfolgsabhängige Gebühr", "Performancegebühr", "Erfolgsbeteiligung"),
    },
    "fr": {
        "objective": ("Objectifs et politique d'investissement", "Objectif d'investissement", "En quoi consiste ce produit ?", "Objectifs"),
        "risk": ("Indicateur de risque", "Indicateur synthetique de risque", "Profil de risque et de rendement", "Profil de risque"),
        "costs": ("Que va me couter cet investissement ?", "Frais", "Couts et frais", "Ce que cet investissement vous coutera"),
        "holding": ("Combien de temps dois-je le conserver ?", "Periode de detention recommandee", "Horizon d'investissement"),
        "practical": ("Informations pratiques", "Autres informations", "Informations complementaires"),
        "manufacturer": ("Initiateur", "Societe de gestion", "Gestionnaire du fonds", "Promoteur"),
        "isin": ("ISIN", "Code ISIN", "Identifiant", "Code valeur"),
        "currency": ("Devise", "Devise du fonds", "Devise de la part", "Devise de reference"),
        "benchmark": ("Indice de reference", "Reference", "Benchmark", "Indice"),
        "domicile": ("Domiciliation", "Pays de domiciliation", "Domicile du fonds", "Enregistre en"),
        "rhp": ("Periode de detention recommandee", "Duree de detention recommandee", "Duree minimale recommandee"),
        "ongoing": ("Frais courants", "Couts recurrents", "Frais de gestion courants", "Charges courantes"),
        "entry": ("Couts d'entree", "Frais d'entree", "Commission de souscription", "Droit d'entree"),
        "exit": ("Couts de sortie", "Frais de sortie", "Commission de rachat"),
        "transaction": ("Couts de transaction", "Frais de transaction du portefeuille", "Couts de negociation"),
        "performance_fee": ("Commission de performance", "Commission de surperformance", "Frais lies a la performance"),
    },
    "nl": {
        "objective": ("Doelstellingen en beleggingsbeleid", "Beleggingsdoelstelling", "Wat is dit voor een product?", "Doelstellingen"),
        "risk": ("Risico-indicator", "Samenvattende risico-indicator", "Risico- en opbrengstprofiel", "Risicoprofiel"),
        "costs": ("Wat zijn de kosten?", "Kosten", "Kosten en vergoedingen", "Vergoedingen"),
        "holding": ("Hoe lang moet ik het aanhouden?", "Aanbevolen periode van bezit", "Beleggingshorizon"),
        "practical": ("Praktische informatie", "Overige informatie", "Aanvullende informatie"),
        "manufacturer": ("Ontwikkelaar", "Beheermaatschappij", "Fondsbeheerder", "Aanbieder"),
        "isin": ("ISIN", "ISIN-code", "Identificatie", "Fondscode"),
        "currency": ("Valuta", "Fondsvaluta", "Valuta van de aandelenklasse", "Basisvaluta"),
        "benchmark": ("Benchmark", "Referentie-index", "Vergelijkingsmaatstaf", "Index"),
        "domicile": ("Vestigingsplaats", "Land van vestiging", "Fondsdomicilie", "Geregistreerd in"),
        "rhp": ("Aanbevolen periode van bezit", "Aanbevolen minimale periode van bezit", "Voorgestelde beleggingsduur"),
        "ongoing": ("Lopende kosten", "Doorlopende kosten", "Lopende kosten van het fonds", "Beheerkosten"),
        "entry": ("Instapkosten", "Instapvergoeding", "Inschrijvingskosten", "Aankoopkosten"),
        "exit": ("Uitstapkosten", "Uitstapvergoeding", "Terugbetalingskosten"),
        "transaction": ("Transactiekosten", "Portefeuilletransactiekosten", "Handelskosten"),
        "performance_fee": ("Prestatievergoeding", "Prestatieafhankelijke vergoeding", "Resultaatvergoeding"),
    },
}


KNOWN = {
    language: {key: options[:-1] for key, options in variants.items()}
    for language, variants in VARIANTS.items()
}

HELD_OUT = {
    language: {key: options[-1:] for key, options in variants.items()}
    for language, variants in VARIANTS.items()
}

POOLS = {"known": KNOWN, "held_out": HELD_OUT, "all": VARIANTS}


def build_labels(language: str, rng: random.Random, vocabulary: str = "known") -> dict[str, str]:
    labels = dict(HEADINGS[language])
    for key, options in POOLS[vocabulary][language].items():
        labels[key] = rng.choice(options)
    return labels


def all_labels_for(key: str, vocabulary: str = "known") -> set[str]:
    pool = POOLS[vocabulary]
    found: set[str] = set()
    for language, variants in pool.items():
        found.update(variants.get(key, ()))
        if vocabulary != "held_out":
            found.add(HEADINGS[language][key])
    return found
