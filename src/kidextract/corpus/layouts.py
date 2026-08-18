from __future__ import annotations

from dataclasses import dataclass

HEADINGS = {
    "en": {
        "title_kid": "KEY INFORMATION DOCUMENT",
        "title_kiid": "KEY INVESTOR INFORMATION",
        "purpose": "Purpose",
        "purpose_body": (
            "This document provides you with key information about this investment product. "
            "It is not marketing material."
        ),
        "product": "What is this product?",
        "objective": "Objectives and investment policy",
        "risk": "Risk indicator",
        "scenarios": "Performance scenarios",
        "costs": "What are the costs?",
        "holding": "How long should I hold it and can I take money out early?",
        "practical": "Practical information",
        "manufacturer": "Manufacturer",
        "isin": "ISIN",
        "currency": "Currency",
        "benchmark": "Benchmark",
        "domicile": "Domicile",
        "rhp": "Recommended holding period",
        "ongoing": "Ongoing charges",
        "entry": "Entry costs",
        "exit": "Exit costs",
        "transaction": "Transaction costs",
        "performance_fee": "Performance fee",
        "lower_risk": "Lower risk",
        "higher_risk": "Higher risk",
        "years": "years",
        "stress": "Stress",
        "unfavourable": "Unfavourable",
        "moderate": "Moderate",
        "favourable": "Favourable",
        "scenario_intro": "What you might get back after costs on an investment of 10,000",
    },
    "de": {
        "title_kid": "BASISINFORMATIONSBLATT",
        "title_kiid": "WESENTLICHE ANLEGERINFORMATIONEN",
        "purpose": "Zweck",
        "purpose_body": (
            "Dieses Informationsblatt stellt Ihnen wesentliche Informationen über dieses "
            "Anlageprodukt zur Verfügung. Es handelt sich nicht um Werbematerial."
        ),
        "product": "Um welche Art von Produkt handelt es sich?",
        "objective": "Ziele und Anlagepolitik",
        "risk": "Risikoindikator",
        "scenarios": "Performance-Szenarien",
        "costs": "Welche Kosten entstehen?",
        "holding": "Wie lange sollte ich die Anlage halten?",
        "practical": "Praktische Informationen",
        "manufacturer": "Hersteller",
        "isin": "ISIN",
        "currency": "Währung",
        "benchmark": "Referenzwert",
        "domicile": "Sitz",
        "rhp": "Empfohlene Haltedauer",
        "ongoing": "Laufende Kosten",
        "entry": "Einstiegskosten",
        "exit": "Ausstiegskosten",
        "transaction": "Transaktionskosten",
        "performance_fee": "Erfolgsabhängige Gebühr",
        "lower_risk": "Geringeres Risiko",
        "higher_risk": "Höheres Risiko",
        "years": "Jahre",
        "stress": "Stressszenario",
        "unfavourable": "Pessimistisches Szenario",
        "moderate": "Mittleres Szenario",
        "favourable": "Optimistisches Szenario",
        "scenario_intro": "Was Sie nach Kosten bei einer Anlage von 10.000 zurückerhalten könnten",
    },
    "fr": {
        "title_kid": "DOCUMENT D'INFORMATIONS CLES",
        "title_kiid": "INFORMATIONS CLES POUR L'INVESTISSEUR",
        "purpose": "Objet",
        "purpose_body": (
            "Le présent document contient des informations essentielles sur ce produit "
            "d'investissement. Il ne s'agit pas d'un document promotionnel."
        ),
        "product": "En quoi consiste ce produit ?",
        "objective": "Objectifs et politique d'investissement",
        "risk": "Indicateur de risque",
        "scenarios": "Scénarios de performance",
        "costs": "Que va me coûter cet investissement ?",
        "holding": "Combien de temps dois-je le conserver ?",
        "practical": "Informations pratiques",
        "manufacturer": "Initiateur",
        "isin": "ISIN",
        "currency": "Devise",
        "benchmark": "Indice de référence",
        "domicile": "Domiciliation",
        "rhp": "Période de détention recommandée",
        "ongoing": "Frais courants",
        "entry": "Coûts d'entrée",
        "exit": "Coûts de sortie",
        "transaction": "Coûts de transaction",
        "performance_fee": "Commission de performance",
        "lower_risk": "Risque plus faible",
        "higher_risk": "Risque plus élevé",
        "years": "ans",
        "stress": "Tensions",
        "unfavourable": "Défavorable",
        "moderate": "Intermédiaire",
        "favourable": "Favorable",
        "scenario_intro": "Ce que vous pourriez obtenir après déduction des coûts pour un investissement de 10 000",
    },
    "nl": {
        "title_kid": "ESSENTIELE-INFORMATIEDOCUMENT",
        "title_kiid": "ESSENTIELE BELEGGERSINFORMATIE",
        "purpose": "Doel",
        "purpose_body": (
            "Dit document geeft u belangrijke informatie over dit beleggingsproduct. "
            "Het is geen marketingmateriaal."
        ),
        "product": "Wat is dit voor een product?",
        "objective": "Doelstellingen en beleggingsbeleid",
        "risk": "Risico-indicator",
        "scenarios": "Prestatiescenario's",
        "costs": "Wat zijn de kosten?",
        "holding": "Hoe lang moet ik het aanhouden?",
        "practical": "Praktische informatie",
        "manufacturer": "Ontwikkelaar",
        "isin": "ISIN",
        "currency": "Valuta",
        "benchmark": "Benchmark",
        "domicile": "Vestigingsplaats",
        "rhp": "Aanbevolen periode van bezit",
        "ongoing": "Lopende kosten",
        "entry": "Instapkosten",
        "exit": "Uitstapkosten",
        "transaction": "Transactiekosten",
        "performance_fee": "Prestatievergoeding",
        "lower_risk": "Lager risico",
        "higher_risk": "Hoger risico",
        "years": "jaar",
        "stress": "Stressscenario",
        "unfavourable": "Ongunstig",
        "moderate": "Gematigd",
        "favourable": "Gunstig",
        "scenario_intro": "Wat u na kosten kunt terugkrijgen bij een inleg van 10.000",
    },
}

SECTIONS = ("header", "objective", "risk", "scenarios", "costs", "holding", "practical")


@dataclass(frozen=True)
class Layout:
    name: str
    doc_type: str
    language: str
    charge_style: str
    risk_style: str
    number_style: str
    heading_case: str
    key_separator: str
    section_order: tuple[str, ...] = SECTIONS
    scenario_style: str = "table"

    @property
    def words(self) -> dict[str, str]:
        return HEADINGS[self.language]

    @property
    def sections(self) -> tuple[str, ...]:
        if self.doc_type == "kiid":
            return tuple(name for name in self.section_order if name != "scenarios")
        return self.section_order


LAYOUTS = (
    Layout("lux-standard", "kid", "en", "table", "scale", "dot", "title", ":"),
    Layout("lux-prose", "kid", "en", "prose", "sentence", "dot", "upper", ":"),
    Layout("dublin-etf", "kid", "en", "bullets", "outof", "dot", "title", " -"),
    Layout("frankfurt-retail", "kid", "de", "table", "scale", "comma", "upper", ":"),
    Layout("frankfurt-compact", "kiid", "de", "prose", "sentence", "comma", "title", ":"),
    Layout("paris-standard", "kid", "fr", "table", "scale", "comma", "title", " :"),
    Layout("paris-legacy", "kiid", "fr", "prose", "outof", "comma", "upper", " :"),
    Layout("amsterdam-standard", "kid", "nl", "table", "scale", "comma", "title", ":"),
    Layout("amsterdam-bullets", "kid", "nl", "bullets", "sentence", "comma", "title", " |"),
    Layout("institutional-bps", "kid", "en", "table", "outof", "bps", "upper", ":"),
    Layout(
        "legacy-kiid-en", "kiid", "en", "prose", "scale", "dot", "title", ":",
        section_order=("header", "objective", "risk", "costs", "practical"),
    ),
    Layout(
        "reordered-kid", "kid", "en", "table", "scale", "dot", "title", ":",
        section_order=("header", "risk", "costs", "objective", "scenarios", "holding", "practical"),
        scenario_style="prose",
    ),
)

LAYOUTS_BY_NAME = {layout.name: layout for layout in LAYOUTS}
