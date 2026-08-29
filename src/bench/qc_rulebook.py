"""Contrôle qualité du Rulebook (spécification §17).

Rend une liste de constats plutôt qu'un booléen : un Rulebook se corrige à partir
d'un rapport, pas d'un échec global.
"""

from __future__ import annotations

import datetime as dt
import json
import re
from dataclasses import dataclass
from pathlib import Path

from src.bench.regles import Rule
from src.bench.rulebook import (
    METHODES_SUFFISANTES,
    NegativeClaimStatus,
    RuleStatus,
)

RACINE_RULEBOOK = Path("data/rules")

#: Domaines dont une URL trahit une source fabriquée.
DOMAINES_SOURCES_ATTENDUS = (
    "eur-lex.europa.eu",
    "legifrance.gouv.fr",
    "amf-france.org",
    "acpr.banque-france.fr",
    "economie.gouv.fr",
    "esma.europa.eu",
)

NIVEAUX = ("ERREUR", "AVERTISSEMENT", "INFO")

#: Un identifiant CELEX désigne un acte : secteur, année, type, numéro.
CELEX = re.compile(r"CELEX[:%3A]{1,3}\s*(?P<secteur>\d)(?P<annee>\d{4})(?P<type>[A-Z])(?P<numero>\d{4})")

#: « (UE) 2019/2088 », « 2014/65/UE » : l'année et le numéro d'un acte européen.
ACTE_CITE = re.compile(r"(?<!\d)(?P<annee>(?:19|20)\d{2})/(?P<numero>\d{1,4})(?!\d)")

#: Marques d'un ancrage qui ne désigne pas une disposition unique.
ANCRAGES_IMPRECIS = ("ensemble", " à ", " et ", "articles", "et s.", "et suivants")

#: Au-delà, deux énoncés du même article disent la même chose. En deçà, ils
#: traitent deux dispositions distinctes du même article — le cas ordinaire.
SEUIL_DOUBLON = 0.5


@dataclass(frozen=True)
class Constat:
    niveau: str
    regle_id: str
    controle: str
    message: str

    def __str__(self) -> str:
        return f"[{self.niveau}] {self.regle_id} — {self.controle} : {self.message}"


def charger_par_fichier(racine: Path = RACINE_RULEBOOK) -> dict[Path, list[Rule]]:
    """Charge le Rulebook en gardant l'origine de chaque règle, manifeste exclu.

    L'origine est nécessaire pour réécrire les fichiers après une vérification :
    le Rulebook est rangé par domaine, et il doit le rester.
    """
    par_fichier: dict[Path, list[Rule]] = {}
    for chemin in sorted(Path(racine).glob("*.json")):
        if "manifest" in chemin.name:
            continue
        par_fichier[chemin] = [
            Rule.model_validate(brut)
            for brut in json.loads(chemin.read_text(encoding="utf-8"))
        ]
    return par_fichier


def charger_rulebook(racine: Path = RACINE_RULEBOOK) -> list[Rule]:
    """Charge toutes les règles du Rulebook, manifeste exclu."""
    return [regle for regles in charger_par_fichier(racine).values() for regle in regles]


def controler(regles: list[Rule]) -> list[Constat]:
    """Tous les contrôles de la spécification §17, rapportés ensemble."""
    constats: list[Constat] = []
    ids = [r.id for r in regles]
    connus = set(ids)

    for regle in regles:
        rid = regle.id

        if ids.count(rid) > 1:
            constats.append(Constat("ERREUR", rid, "id_unique", "identifiant en double"))

        if not regle.statement.strip():
            constats.append(Constat("ERREUR", rid, "statement", "énoncé vide"))

        if not regle.source.url.strip():
            constats.append(Constat("ERREUR", rid, "source_url", "URL absente"))
        elif not any(d in regle.source.url for d in DOMAINES_SOURCES_ATTENDUS):
            constats.append(
                Constat(
                    "ERREUR", rid, "source_fictive",
                    f"URL hors des domaines officiels attendus : {regle.source.url}",
                )
            )

        if not regle.source.article.strip():
            constats.append(Constat("ERREUR", rid, "source_article", "article absent"))

        if not regle.regulatory_regime.strip():
            constats.append(Constat("ERREUR", rid, "regulatory_regime", "régime absent"))

        if regle.source.version_date is None:
            constats.append(Constat("ERREUR", rid, "version_date", "date de version absente"))

        if regle.status is RuleStatus.VALIDATED and regle.source.verification_date is None:
            constats.append(
                Constat("ERREUR", rid, "validated_sans_verification",
                        "statut validated sans date de vérification")
            )

        for cible in regle.related_rules:
            if cible not in connus:
                constats.append(
                    Constat("ERREUR", rid, "related_rules", f"règle liée inconnue « {cible} »")
                )

        for revendication in regle.negative_claims:
            if (
                revendication.status is NegativeClaimStatus.VERIFIED_ABSENT
                and revendication.verification_method not in METHODES_SUFFISANTES
            ):
                constats.append(
                    Constat("ERREUR", rid, "negative_claim",
                            "absence déclarée vérifiée sans consultation du texte primaire")
                )

        # Avertissements : ce qui n'invalide pas mais limite l'exploitation.
        if regle.needs_verification:
            constats.append(
                Constat("AVERTISSEMENT", rid, "verification",
                        f"source non consultée ({regle.verification_method.value})")
            )
        if not regle.needs_verification and regle.status is RuleStatus.DRAFT:
            constats.append(
                Constat(
                    "AVERTISSEMENT", rid, "verification_sans_promotion",
                    "source consultée mais règle restée en « draft » : réfutée ou non "
                    "tranchée, elle ne reviendra pas d'elle-même dans le dossier de "
                    "vérification",
                )
            )
        if regle.exceptions_status.value == "unknown":
            constats.append(
                Constat("AVERTISSEMENT", rid, "exceptions",
                        "exceptions inconnues : la règle peut produire une question simplifiée")
            )
        if not regle.operational_rule.strip():
            constats.append(
                Constat("AVERTISSEMENT", rid, "operational_rule", "interprétation opérationnelle absente")
            )
        if not regle.common_confusions:
            constats.append(
                Constat("AVERTISSEMENT", rid, "common_confusions", "aucune confusion typique identifiée")
            )
        if not regle.candidate_question_families:
            constats.append(
                Constat("AVERTISSEMENT", rid, "candidate_question_families", "aucune famille suggérée")
            )
        if not regle.reasoning_traps:
            constats.append(
                Constat("AVERTISSEMENT", rid, "reasoning_traps", "aucun piège identifié")
            )

        constats.extend(_coherence_de_la_source(regle))
        constats.extend(_precision_de_l_ancrage(regle))

    constats.extend(_doublons_conceptuels(regles))
    return sorted(constats, key=lambda c: (NIVEAUX.index(c.niveau), c.regle_id, c.controle))


# -- ce qui se vérifie sans le texte primaire -------------------------------------- #


def _acte_de_l_url(url: str) -> tuple[int, int] | None:
    """Année et numéro de l'acte désigné par l'identifiant CELEX de l'URL."""
    trouve = CELEX.search(url)
    if trouve is None:
        return None
    return int(trouve.group("annee")), int(trouve.group("numero"))


def _acte_du_texte(texte: str) -> tuple[int, int] | None:
    """Année et numéro de l'acte cité en toutes lettres (« (UE) 2019/2088 »)."""
    trouve = ACTE_CITE.search(texte)
    if trouve is None:
        return None
    return int(trouve.group("annee")), int(trouve.group("numero"))


def _coherence_de_la_source(regle: Rule) -> list[Constat]:
    """Deux incohérences que la citation trahit d'elle-même, sans consulter le texte.

    Un acte porte son année dans son numéro. Une version consultée ne peut donc
    pas précéder l'acte qu'elle est censée porter, et l'URL est censée désigner
    l'acte que la règle cite.
    """
    constats: list[Constat] = []
    par_url = _acte_de_l_url(regle.source.url)
    par_texte = _acte_du_texte(regle.source.text)
    acte = par_url or par_texte

    if acte is not None and regle.source.version_date.year < acte[0]:
        constats.append(
            Constat(
                "AVERTISSEMENT", regle.id, "version_date_placeholder",
                f"version consultée datée {regle.source.version_date.isoformat()}, "
                f"antérieure à l'acte {acte[0]}/{acte[1]} lui-même : la date est un "
                f"placeholder, à établir lors de la vérification",
            )
        )

    if par_url is not None and par_texte is not None and par_url != par_texte:
        constats.append(
            Constat(
                "AVERTISSEMENT", regle.id, "url_acte_different",
                f"l'URL désigne l'acte {par_url[0]}/{par_url[1]} alors que la source "
                f"cite {par_texte[0]}/{par_texte[1]} : légitime pour un acte "
                f"modificatif, à confirmer sinon",
            )
        )

    return constats


def _precision_de_l_ancrage(regle: Rule) -> list[Constat]:
    """Un ancrage qui couvre plusieurs articles ne source aucune réponse précisément."""
    article = regle.source.article.lower()
    if not any(marque in article for marque in ANCRAGES_IMPRECIS):
        return []
    return [
        Constat(
            "AVERTISSEMENT", regle.id, "ancrage_imprecis",
            f"l'ancrage « {regle.source.article} » ne désigne pas une disposition "
            f"unique : un gold ancré ici ne pourra pas citer son article",
        )
    ]


def _normaliser_titre(titre: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", titre.lower()).strip()


def _mots(texte: str) -> set[str]:
    """Mots signifiants d'un énoncé, pour comparer deux règles sans les lire."""
    return {m for m in re.split(r"[^0-9a-zà-ÿ]+", texte.lower()) if len(m) > 3}


def _proximite(gauche: str, droite: str) -> float:
    """Jaccard sur les mots signifiants. 1.0 = mêmes mots, 0.0 = aucun commun."""
    a, b = _mots(gauche), _mots(droite)
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def _doublons_conceptuels(regles: list[Rule]) -> list[Constat]:
    """Deux règles du même domaine visant le même article et le même type.

    Partager un article ne suffit pas à faire un doublon : un même article porte
    couramment plusieurs obligations distinctes, et les signaler toutes noierait
    le vrai doublon — deux fois la même règle — dans le bruit. Le constat n'est
    donc un avertissement que si les énoncés se ressemblent aussi ; sinon il
    reste une information, que le vérificateur lit comme un rappel de découper
    l'ancrage au paragraphe.
    """
    constats: list[Constat] = []
    vus: dict[tuple[str, str, str], Rule] = {}
    for regle in regles:
        cle = (regle.domain.value, regle.source.article.strip().lower(), regle.rule_type.value)
        precedente = vus.get(cle)
        if precedente is None:
            vus[cle] = regle
            continue

        proximite = _proximite(regle.statement, precedente.statement)
        if proximite >= SEUIL_DOUBLON:
            constats.append(
                Constat(
                    "AVERTISSEMENT", regle.id, "doublon_conceptuel",
                    f"même domaine, même article et même type que « {precedente.id} », "
                    f"et énoncés proches ({proximite:.0%} de mots communs)",
                )
            )
        else:
            constats.append(
                Constat(
                    "INFO", regle.id, "meme_article",
                    f"partage l'article de « {precedente.id} » mais dit autre chose "
                    f"({proximite:.0%} de mots communs) : ancrage à préciser au paragraphe",
                )
            )
    return constats


def erreurs(constats: list[Constat]) -> list[Constat]:
    return [c for c in constats if c.niveau == "ERREUR"]


def rapport_markdown(regles: list[Rule], constats: list[Constat]) -> str:
    """Rapport RULEBOOK_QC.md : ce qui bloque, ce qui limite, et ce qui reste à faire."""
    par_niveau = {n: [c for c in constats if c.niveau == n] for n in NIVEAUX}

    lignes = [
        "# Rulebook — contrôle qualité",
        "",
        "Rapport généré par `src/bench/qc_rulebook.py`. Il liste ce qui bloque",
        "l'exploitation du Rulebook et ce qui la limite.",
        "",
        "## Synthèse",
        "",
        f"- règles : **{len(regles)}**",
        f"- erreurs bloquantes : **{len(par_niveau['ERREUR'])}**",
        f"- avertissements : **{len(par_niveau['AVERTISSEMENT'])}**",
        "",
        "## État de vérification",
        "",
        f"- règles dont la source n'a pas été consultée : "
        f"**{sum(1 for r in regles if r.needs_verification)} / {len(regles)}**",
        f"- règles utilisables pour ancrer un gold : "
        f"**{sum(1 for r in regles if r.is_usable)} / {len(regles)}**",
        "",
        "> Les sources primaires (EUR-Lex, Légifrance, AMF, ACPR, TRACFIN, ESMA) sont",
        "> inaccessibles depuis l'environnement de génération. Aucune règle ne peut donc",
        "> dépasser le statut `draft`, et **aucune n'est utilisable pour ancrer un gold**.",
        "> C'est une propriété tenue par le schéma, pas une convention.",
        "",
        "> Contrôle du 29 août 2026 : la passerelle réseau répond toujours 403 sur les",
        "> six domaines (`eur-lex.europa.eu`, `legifrance.gouv.fr`, `amf-france.org`,",
        "> `acpr.banque-france.fr`, `esma.europa.eu`, `economie.gouv.fr`), y compris par",
        "> l'outil de récupération de pages. La vérification se fait donc hors de cet",
        "> environnement, par le circuit ci-dessous.",
        "",
        "## Circuit de vérification",
        "",
        "La vérification ne s'improvise pas dans les fichiers de règles : elle passe",
        "par un dossier CSV, relu et réinjecté (`src/bench/verification.py`).",
        "",
        "```sh",
        "finreg-bench rulebook exporter-verification --sortie verification.csv",
        "# le vérificateur consulte les textes et remplit les colonnes de constat",
        "finreg-bench rulebook appliquer-verification verification.csv",
        "```",
        "",
        "Les constats sont conservés dans `data/verification/rulebook-ledger.json`,",
        "hors de `data/rules/`, pour qu'une régénération du Rulebook ne les efface pas.",
        "Le verrou reste entier : `appliquer` refuse toute promotion sans méthode sur",
        "texte primaire, vérificateur nommé et date, et refuse un statut `validated`",
        "tant que les exceptions de la règle sont inconnues.",
        "",
        "## Ce que la vérification doit établir",
        "",
        "Constats qui n'exigent pas de lire le texte : ils sont déductibles de la",
        "citation elle-même, et devront être corrigés au passage.",
        "",
    ]

    for controle, phrase in (
        ("version_date_placeholder", "date de version antérieure à l'acte cité"),
        ("ancrage_imprecis", "ancrage couvrant plusieurs dispositions"),
        ("url_acte_different", "URL désignant un autre acte que la source citée"),
        ("meme_article", "règles distinctes partageant un article"),
    ):
        concernees = sorted({c.regle_id for c in constats if c.controle == controle})
        if not concernees:
            continue
        lignes.append(f"- **{phrase}** — {len(concernees)} règle(s) : "
                      + ", ".join(f"`{r}`" for r in concernees))
    lignes.append("")

    for niveau in NIVEAUX:
        trouves = par_niveau[niveau]
        if not trouves:
            continue
        lignes += [f"## {niveau.capitalize()}s ({len(trouves)})", ""]
        groupes: dict[str, list[Constat]] = {}
        for constat in trouves:
            groupes.setdefault(constat.controle, []).append(constat)
        for controle, elements in sorted(groupes.items()):
            lignes.append(f"### `{controle}` — {len(elements)}")
            lignes.append("")
            for constat in elements[:20]:
                lignes.append(f"- `{constat.regle_id}` : {constat.message}")
            if len(elements) > 20:
                lignes.append(f"- … et {len(elements) - 20} autre(s)")
            lignes.append("")

    return "\n".join(lignes) + "\n"


# -- manifeste ---------------------------------------------------------------------- #

VERSION_RULEBOOK = "v0.1.0"

#: Pas d'horodatage : le manifeste doit être reproductible à l'identique.
DATE_GENERATION = dt.date(2026, 8, 29)

NOTE_AUCUNE_VERIFICATION = (
    "Aucune règle n'a été confrontée à sa source primaire : EUR-Lex, Légifrance, "
    "AMF, ACPR, TRACFIN et ESMA sont inaccessibles depuis l'environnement de "
    "génération. Toutes les règles sont en « draft » et aucune n'est utilisable "
    "pour ancrer un gold tant qu'un humain n'a pas vérifié la source."
)


def construire_manifeste(regles: list[Rule], par_fichier: dict[str, int]) -> dict:
    """Récapitulatif chiffré du Rulebook, écrit à côté des règles.

    Il vit ici et non dans le script de génération : la vérification le réécrit
    elle aussi, et deux constructions concurrentes du même artefact finiraient
    par diverger.
    """

    def compter(cle) -> dict[str, int]:
        valeurs: dict[str, int] = {}
        for regle in regles:
            v = cle(regle)
            valeurs[v] = valeurs.get(v, 0) + 1
        return dict(sorted(valeurs.items()))

    verifiees = sum(1 for r in regles if not r.needs_verification)

    return {
        "rulebook_version": VERSION_RULEBOOK,
        "generation_date": DATE_GENERATION.isoformat(),
        "number_of_rules": len(regles),
        "rules_per_domain": compter(lambda r: r.domain.value),
        "rules_per_file": dict(sorted(par_fichier.items())),
        "rules_per_type": compter(lambda r: r.rule_type.value),
        "rules_per_priority": compter(lambda r: r.priority.value),
        "rules_per_status": compter(lambda r: r.status.value),
        "number_source_checked": sum(1 for r in regles if r.status is RuleStatus.SOURCE_CHECKED),
        "number_validated": sum(1 for r in regles if r.status is RuleStatus.VALIDATED),
        "number_time_sensitive": sum(1 for r in regles if r.time_sensitive),
        "number_critical": sum(1 for r in regles if r.priority.value == "CRITICAL"),
        "number_needing_verification": sum(1 for r in regles if r.needs_verification),
        "number_with_negative_claims": sum(1 for r in regles if r.negative_claims),
        "verification_note": (
            NOTE_AUCUNE_VERIFICATION
            if verifiees == 0
            else (
                f"{verifiees} règle(s) sur {len(regles)} ont été confrontées à leur "
                f"source primaire ; les autres restent en « draft » et ne peuvent pas "
                f"ancrer un gold. Les constats sont dans "
                f"data/verification/rulebook-ledger.json."
            )
        ),
    }
