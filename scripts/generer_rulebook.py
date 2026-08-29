"""Génère data/rules/ et le manifeste à partir des règles déclarées.

Toutes les règles sortent en `status = draft` avec
`verification_method = model_knowledge_unverified` : les sources primaires sont
inaccessibles depuis cet environnement, et la spécification §1 et §15 interdit
d'aller plus loin sans consultation du texte.

Une exception, et une seule : les constats du **registre de vérification** sont
réappliqués après génération. Sans cela, régénérer le Rulebook effacerait
silencieusement le travail d'un vérificateur — le seul travail que ce fichier ne
sait pas refaire.
"""

from __future__ import annotations

from pathlib import Path

from src.bench.qc_rulebook import construire_manifeste
from src.bench.regles import Rule
from src.bench.verification import VerificationInvalide, appliquer, charger_registre
from src.io_utils import ecrire_json
from scripts import rulebook_amf, rulebook_dora, rulebook_lcbft, rulebook_mifid, rulebook_sfdr

SORTIE = Path("data/rules")

#: Aucune source n'a pu être consultée : le proxy réseau bloque EUR-Lex,
#: Légifrance, l'AMF, l'ACPR, TRACFIN et l'ESMA.
METHODE = "model_knowledge_unverified"
STATUT = "draft"

DOMAINES = {
    "sfdr": ("SFDR", rulebook_sfdr.REGLES),
    "mifid": ("MIFID", rulebook_mifid.REGLES),
    "amf": ("AMF", rulebook_amf.REGLES),
    "dora": ("DORA", rulebook_dora.REGLES),
    "lcbft": ("LCBFT", rulebook_lcbft.REGLES),
}

DEFAUTS = {
    "sfdr": dict(text="Règlement (UE) 2019/2088 (SFDR)", regime="SFDR_1.0", valid_from="2021-03-10"),
    "mifid": dict(text="Directive 2014/65/UE (MIFID II)", regime="MIFID2_1.0", valid_from="2018-01-03"),
    "amf": dict(text="Doctrine AMF", regime="AMF_DOC", valid_from="2020-03-11"),
    "dora": dict(text="Règlement (UE) 2022/2554 (DORA)", regime="DORA_1.0", valid_from="2025-01-17"),
    "lcbft": dict(text="Code monétaire et financier", regime="CMF_LCBFT", valid_from="2020-02-14"),
}

#: Date de version des textes retenue par défaut, faute d'avoir pu la vérifier.
VERSION_DATE_DEFAUT = "2020-01-01"


def normaliser(brut: dict, fichier: str, domaine: str) -> dict:
    """Transforme une déclaration compacte en règle complète et validable."""
    defauts = DEFAUTS[fichier]
    return {
        "id": brut["id"],
        "version": brut.get("version", 1),
        "domain": domaine,
        "subdomain": brut.get("subdomain", ""),
        "rule_type": brut["rule_type"],
        "title": brut["title"],
        "statement": brut["statement"],
        "operational_rule": brut.get("operational_rule", ""),
        "common_confusions": brut.get("common_confusions", []),
        "exceptions": brut.get("exceptions", []),
        "exceptions_status": brut.get("exceptions_status", "unknown"),
        "negative_claims": [
            {
                "claim": n["claim"],
                # Une absence non vérifiée reste « unverified » : « je n'ai pas
                # trouvé » n'est pas « cela n'existe pas » (spécification §6).
                "status": "unverified",
                "verification_method": METHODE,
                "note": n.get("note", ""),
            }
            for n in brut.get("negative_claims", [])
        ],
        "source": {
            "text": brut.get("text", defauts["text"]),
            "article": brut["article"],
            "paragraph": brut.get("paragraph", ""),
            "url": brut["url"],
            "version_date": brut.get("version_date", VERSION_DATE_DEFAUT),
            "verified_by": "",
            "verification_date": None,
        },
        "verification_method": METHODE,
        "regulatory_regime": brut.get("regime", defauts["regime"]),
        "regulatory_status": brut.get("regulatory_status", "in_force"),
        "valid_from": brut.get("valid_from", defauts["valid_from"]),
        "valid_until": brut.get("valid_until"),
        "time_sensitive": brut.get("time_sensitive", False),
        "priority": brut.get("priority", "MEDIUM"),
        "candidate_question_families": brut.get("families", []),
        "reasoning_traps": brut.get("traps", []),
        "related_rules": brut.get("related", []),
        "status": STATUT,
        "notes": brut.get("notes", ""),
    }


def generer() -> tuple[list[Rule], dict]:
    SORTIE.mkdir(parents=True, exist_ok=True)
    registre = charger_registre()
    toutes: list[Rule] = []
    par_fichier: dict[str, int] = {}

    for fichier, (domaine, brutes) in DOMAINES.items():
        regles = [normaliser(b, fichier, domaine) for b in brutes]
        # Validation avant écriture : un fichier de règles invalide ne doit pas exister.
        objets = [Rule.model_validate(r) for r in regles]
        # Le registre est réappliqué ici : ce que la génération ne sait pas refaire.
        connus = {r.id for r in objets}
        objets = appliquer(objets, [v for v in registre if v.rule_id in connus])
        ecrire_json(SORTIE / f"{fichier}.json", [o.model_dump(mode="json") for o in objets])
        toutes.extend(objets)
        par_fichier[fichier] = len(objets)

    # Un constat orphelin est du travail de vérification perdu : la règle qu'il
    # nomme a été renommée ou retirée. Le signaler bruyamment, ne pas l'ignorer.
    orphelins = sorted({v.rule_id for v in registre} - {r.id for r in toutes})
    if orphelins:
        raise VerificationInvalide(
            [f"{rid} : constat de vérification sans règle correspondante" for rid in orphelins]
        )

    manifeste = construire_manifeste(toutes, par_fichier)
    ecrire_json(SORTIE / "rulebook-manifest.json", manifeste)
    return toutes, manifeste


if __name__ == "__main__":
    regles, manifeste = generer()
    print(f"{manifeste['number_of_rules']} règles écrites dans {SORTIE}")
    for domaine, nombre in manifeste["rules_per_domain"].items():
        print(f"  {domaine:8} {nombre}")
