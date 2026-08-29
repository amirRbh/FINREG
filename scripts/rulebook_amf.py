"""Règles de doctrine AMF du Rulebook V0.

Domaine où la confiance dans les références est la plus faible : la doctrine AMF
est identifiée par des cotes de position-recommandation dont le détail n'a pas pu
être vérifié. Ces règles sont volontairement peu nombreuses et rédigées au niveau
du document, sans citation de paragraphe.
"""

from __future__ import annotations

DOC = "https://www.amf-france.org/fr/reglementation/doctrine/doc-2020-03"
RG = "https://www.amf-france.org/fr/reglementation/reglement-general"

TEXTE = "Position-recommandation AMF DOC-2020-03"
REGIME = "AMF_DOC_2020_03"

def _d(**kw):
    base = dict(text=TEXTE, url=DOC, regime=REGIME, valid_from="2020-03-11",
                article="Position-recommandation DOC-2020-03")
    base.update(kw)
    return base

REGLES = [
    _d(
        id="AMF-R-001", subdomain="Approche significativement engageante", rule_type="THRESHOLD",
        title="Condition d'une communication centrale sur les critères extra-financiers",
        statement=(
            "La position-recommandation AMF DOC-2020-03 subordonne la possibilité pour un "
            "placement collectif de communiquer de manière centrale sur la prise en compte "
            "de critères extra-financiers au caractère significativement engageant de "
            "l'approche mise en œuvre."
        ),
        operational_rule=(
            "La communication commerciale est graduée selon l'engagement réel : un produit "
            "dont l'approche n'est pas significativement engageante ne peut pas faire de "
            "l'extra-financier un axe central de communication."
        ),
        common_confusions=[
            "déduire de la classification article 8 SFDR le droit de communiquer de manière centrale",
            "citer un seuil chiffré sans le rattacher au document de doctrine",
            "confondre doctrine AMF et obligation SFDR",
        ],
        priority="CRITICAL",
        traps=["CROSS_REGULATORY_CONFLATION", "FALSE_THRESHOLD", "CAUSAL_INFERENCE"],
        families=["qualification", "false_premise", "cross_regulatory", "abstention"],
        related=["SFDR-R-008", "AMF-R-002"], exceptions_status="unknown",
        negative_claims=[dict(
            claim="Le règlement SFDR imposerait lui-même les conditions de communication commerciale applicables en France.",
            note="Ces conditions relèvent de la doctrine AMF ; SFDR régit l'information réglementaire.",
        )],
    ),
    _d(
        id="AMF-R-002", subdomain="Communication", rule_type="OBLIGATION",
        title="Proportionnalité de la communication extra-financière",
        statement=(
            "La position-recommandation AMF DOC-2020-03 distingue plusieurs niveaux de "
            "communication sur la prise en compte de critères extra-financiers, du niveau "
            "central au niveau réduit, selon le degré d'engagement du produit."
        ),
        operational_rule=(
            "Le niveau de communication autorisé se déduit du degré d'engagement, non de "
            "l'intention commerciale."
        ),
        common_confusions=[
            "traiter tous les produits intégrant des critères ESG de la même façon en communication",
        ],
        priority="HIGH",
        traps=["OVERGENERALIZATION", "CAUSAL_INFERENCE", "CONCEPT_CONFLATION"],
        families=["qualification", "true_premise_adversarial"],
        related=["AMF-R-001", "SFDR-R-013"], exceptions_status="unknown",
    ),
    _d(
        id="AMF-R-003", subdomain="Dénomination", rule_type="OBLIGATION",
        title="Cohérence de la dénomination du produit avec son approche",
        statement=(
            "La position-recommandation AMF DOC-2020-03 traite de la cohérence entre la "
            "dénomination d'un placement collectif faisant référence à des considérations "
            "extra-financières et la réalité de l'approche mise en œuvre."
        ),
        operational_rule=(
            "Le nom du produit engage : une dénomination à connotation durable appelle une "
            "approche correspondante démontrable."
        ),
        common_confusions=[
            "croire que la dénomination relève de la seule liberté commerciale",
        ],
        priority="HIGH",
        traps=["CAUSAL_INFERENCE", "SCOPE_CONFUSION"],
        families=["qualification", "false_premise"],
        related=["AMF-R-001"], exceptions_status="unknown",
    ),
    _d(
        id="AMF-R-004", subdomain="Articulation avec SFDR", rule_type="SCOPE",
        title="Articulation entre doctrine AMF et règlement SFDR",
        statement=(
            "La doctrine AMF relative aux informations extra-financières des placements "
            "collectifs s'applique en complément du règlement (UE) 2019/2088, qui régit "
            "l'information réglementaire, la doctrine portant sur la communication."
        ),
        operational_rule=(
            "Deux corps de règles distincts et cumulatifs : la conformité SFDR ne vaut pas "
            "conformité à la doctrine AMF, et réciproquement."
        ),
        common_confusions=[
            "déduire de la conformité SFDR la conformité à la doctrine AMF",
            "opposer les deux corps de règles au lieu de les cumuler",
        ],
        priority="CRITICAL",
        traps=["CROSS_REGULATORY_CONFLATION", "SCOPE_CONFUSION", "CAUSAL_INFERENCE"],
        families=["cross_regulatory", "qualification", "false_premise", "true_premise_adversarial"],
        related=["SFDR-R-008", "SFDR-R-013", "AMF-R-001"], exceptions_status="unknown",
    ),
    dict(
        id="AMF-R-005", subdomain="Règlement général AMF", rule_type="SCOPE",
        title="Portée du règlement général de l'AMF",
        statement=(
            "Le règlement général de l'AMF fixe les règles applicables aux acteurs et aux "
            "produits relevant de la compétence de l'Autorité des marchés financiers, et se "
            "distingue de la doctrine, qui explicite l'interprétation retenue par l'Autorité."
        ),
        operational_rule=(
            "Le règlement général est une norme opposable ; une position ou recommandation "
            "de doctrine en éclaire l'application sans avoir la même portée."
        ),
        common_confusions=[
            "citer une position de doctrine comme s'il s'agissait du règlement général",
            "confondre position, recommandation et article du règlement général",
        ],
        text="Règlement général de l'AMF", article="Règlement général", url=RG,
        regime="AMF_RG", valid_from="2004-11-24",
        priority="HIGH",
        traps=["FALSE_ARTICLE", "CONCEPT_CONFLATION", "DEFINITION_DRIFT"],
        families=["qualification", "false_premise", "abstention"],
        related=["AMF-R-001"], exceptions_status="unknown",
    ),
]
