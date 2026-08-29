"""Règles DORA du Rulebook V0. Références non confrontées au texte primaire."""

from __future__ import annotations

DORA = "https://eur-lex.europa.eu/legal-content/FR/TXT/?uri=CELEX:32022R2554"
TEXTE = "Règlement (UE) 2022/2554 (DORA)"
REGIME = "DORA_1.0"
DEPUIS = "2025-01-17"

def _r(**kw):
    base = dict(text=TEXTE, url=DORA, regime=REGIME, valid_from=DEPUIS)
    base.update(kw)
    return base

REGLES = [
    _r(
        id="DORA-R-001", subdomain="Article 2 — champ d'application", rule_type="SCOPE",
        title="Entités financières couvertes par DORA",
        statement=(
            "L'article 2 du règlement (UE) 2022/2554 énumère les catégories d'entités "
            "financières auxquelles le règlement s'applique, ainsi que les prestataires "
            "tiers de services TIC, et prévoit des exclusions pour certaines entités."
        ),
        operational_rule=(
            "Le périmètre est large et transsectoriel : il ne se limite ni aux banques ni "
            "aux entités systémiques. La question du périmètre se tranche par l'énumération, "
            "pas par la taille."
        ),
        common_confusions=[
            "restreindre DORA aux établissements bancaires",
            "conditionner l'application à un seuil de taille",
            "oublier que les prestataires tiers TIC entrent dans le dispositif",
        ],
        priority="CRITICAL", article="Article 2",
        traps=["SCOPE_CONFUSION", "FALSE_THRESHOLD", "OVERGENERALIZATION"],
        families=["qualification", "false_premise", "true_premise_adversarial"],
        related=["DORA-R-011"], exceptions_status="unknown",
    ),
    _r(
        id="DORA-R-002", subdomain="Article 5 — gouvernance", rule_type="GOVERNANCE",
        title="Responsabilité de l'organe de direction sur le risque TIC",
        statement=(
            "L'article 5 du règlement (UE) 2022/2554 dispose que l'organe de direction de "
            "l'entité financière définit, approuve, supervise et est responsable de la mise "
            "en œuvre du cadre de gestion du risque lié aux TIC."
        ),
        operational_rule=(
            "La responsabilité est nominative et non délégable : externaliser l'exécution "
            "ne transfère pas la responsabilité."
        ),
        common_confusions=[
            "considérer que l'externalisation transfère la responsabilité au prestataire",
            "attribuer la responsabilité à la DSI ou au RSSI plutôt qu'à l'organe de direction",
        ],
        priority="CRITICAL", article="Article 5",
        traps=["CAUSAL_INFERENCE", "CONCEPT_CONFLATION", "SCOPE_CONFUSION"],
        families=["qualification", "false_premise", "true_premise_adversarial"],
        related=["DORA-R-011", "MIFID-R-010"], exceptions_status="unknown",
    ),
    _r(
        id="DORA-R-003", subdomain="Article 6 — cadre de gestion", rule_type="OBLIGATION",
        title="Cadre de gestion du risque lié aux TIC",
        statement=(
            "L'article 6 impose de disposer d'un cadre de gestion du risque lié aux TIC "
            "solide, complet et bien documenté, faisant partie du dispositif global de "
            "gestion des risques, et de le réexaminer au moins une fois par an."
        ),
        operational_rule=(
            "Le cadre est vivant : sa documentation et son réexamen périodique font partie "
            "de l'obligation, pas seulement son existence."
        ),
        common_confusions=[
            "réduire l'obligation à l'existence d'un document",
            "inventer une fréquence de réexamen différente de celle du texte",
        ],
        priority="CRITICAL", article="Article 6", time_sensitive=True,
        traps=["FALSE_THRESHOLD", "TEMPORAL_CONFUSION", "OVERGENERALIZATION"],
        families=["recall", "qualification", "temporal"],
        related=["DORA-R-004", "DORA-R-010"], exceptions_status="unknown",
    ),
    _r(
        id="DORA-R-004", subdomain="Articles 8 à 13", rule_type="PROCEDURE",
        title="Identification, protection, détection, réponse et apprentissage",
        statement=(
            "Les articles 8 à 13 du règlement (UE) 2022/2554 organisent les fonctions du "
            "cadre de gestion du risque TIC : identification des fonctions et actifs, "
            "protection et prévention, détection des activités anormales, réponse et "
            "rétablissement, politiques de sauvegarde et de restauration, apprentissage et "
            "évolution."
        ),
        operational_rule=(
            "L'enchaînement est un cycle : un dispositif qui détecte sans savoir rétablir, "
            "ou qui rétablit sans apprendre, ne satisfait pas le cadre."
        ),
        common_confusions=[
            "traiter la sauvegarde comme suffisante à elle seule",
            "attribuer à un article unique l'ensemble du cycle",
        ],
        priority="HIGH", article="Articles 8 à 13",
        traps=["FALSE_ARTICLE", "OVERGENERALIZATION", "CONCEPT_CONFLATION"],
        families=["recall", "qualification", "abstention"],
        related=["DORA-R-003"], exceptions_status="unknown",
    ),
    _r(
        id="DORA-R-005", subdomain="Article 16 — cadre simplifié", rule_type="EXCEPTION",
        title="Cadre simplifié de gestion du risque TIC",
        statement=(
            "L'article 16 prévoit un cadre simplifié de gestion du risque lié aux TIC pour "
            "certaines entités financières limitativement énumérées."
        ),
        operational_rule=(
            "Le régime simplifié est ouvert par énumération d'entités, pas par appréciation "
            "de la taille ou de la complexité par l'entité elle-même."
        ),
        common_confusions=[
            "s'auto-attribuer le régime simplifié au motif d'une petite taille",
            "croire que le régime simplifié dispense de tout cadre",
        ],
        priority="HIGH", article="Article 16",
        traps=["EXCEPTION_OMISSION", "SCOPE_CONFUSION", "FALSE_THRESHOLD"],
        families=["qualification", "false_premise", "abstention"],
        related=["DORA-R-001", "DORA-R-003"], exceptions_status="unknown",
    ),
    _r(
        id="DORA-R-006", subdomain="Article 17 — incidents", rule_type="PROCEDURE",
        title="Processus de gestion des incidents liés aux TIC",
        statement=(
            "L'article 17 impose de définir, d'établir et de mettre en œuvre un processus de "
            "gestion des incidents liés aux TIC permettant de les détecter, de les gérer et "
            "de les notifier."
        ),
        operational_rule=(
            "Tous les incidents doivent être gérés et enregistrés ; seule la notification "
            "est réservée aux incidents majeurs."
        ),
        common_confusions=[
            "croire que seuls les incidents majeurs doivent être enregistrés",
            "confondre gestion (article 17), classification (article 18) et notification (article 19)",
        ],
        priority="HIGH", article="Article 17",
        traps=["CONCEPT_CONFLATION", "SCOPE_CONFUSION", "FALSE_ARTICLE"],
        families=["qualification", "true_premise_adversarial"],
        related=["DORA-R-007", "DORA-R-008"], exceptions_status="unknown",
    ),
    _r(
        id="DORA-R-007", subdomain="Article 18 — classification", rule_type="CLASSIFICATION",
        title="Classification des incidents et détermination du caractère majeur",
        statement=(
            "L'article 18 impose de classer les incidents liés aux TIC et de déterminer leur "
            "incidence selon des critères tels que le nombre de clients affectés, la durée, "
            "la répartition géographique, les pertes de données et la criticité des services "
            "touchés, les seuils étant précisés par des normes techniques."
        ),
        operational_rule=(
            "Les critères sont au niveau 1, leurs seuils chiffrés au niveau 2. Citer un "
            "seuil chiffré en l'attribuant à l'article 18 est une erreur de niveau de norme."
        ),
        common_confusions=[
            "citer un seuil chiffré comme figurant dans le règlement de niveau 1",
            "confondre criticité de l'incident et criticité du prestataire",
        ],
        priority="CRITICAL", article="Article 18", time_sensitive=True,
        traps=["FALSE_THRESHOLD", "CROSS_REGULATORY_CONFLATION", "MISSING_INFORMATION"],
        families=["qualification", "false_premise", "abstention", "calculation"],
        related=["DORA-R-008"], exceptions_status="unknown",
        negative_claims=[dict(
            claim="L'article 18 fixerait lui-même un nombre de clients affectés au-delà duquel l'incident est majeur.",
            note="Les seuils chiffrés relèvent des normes techniques ; à confronter au texte et aux RTS.",
        )],
    ),
    _r(
        id="DORA-R-008", subdomain="Article 19 — notification", rule_type="DEADLINE",
        title="Notification des incidents majeurs à l'autorité compétente",
        statement=(
            "L'article 19 impose de notifier les incidents majeurs liés aux TIC à l'autorité "
            "compétente, selon un processus comportant une notification initiale, un rapport "
            "intermédiaire et un rapport final, dont les délais sont précisés par des normes "
            "techniques."
        ),
        operational_rule=(
            "Le processus est en trois temps. Les délais exacts ne figurent pas dans le "
            "niveau 1 : les affirmer de mémoire est précisément l'erreur à tester."
        ),
        common_confusions=[
            "citer un délai chiffré comme figurant dans le règlement de niveau 1",
            "réduire la notification à un envoi unique",
            "confondre notification à l'autorité et information des clients",
        ],
        priority="CRITICAL", article="Article 19", time_sensitive=True,
        traps=["FALSE_THRESHOLD", "TEMPORAL_CONFUSION", "MISSING_INFORMATION", "FALSE_ARTICLE"],
        families=["recall", "false_premise", "abstention", "temporal"],
        related=["DORA-R-007"], exceptions_status="unknown",
        negative_claims=[dict(
            claim="Le règlement DORA de niveau 1 fixerait un délai de notification initiale en heures.",
            note="Le délai relève des normes techniques d'exécution ; à confronter au texte et aux ITS.",
        )],
    ),
    _r(
        id="DORA-R-009", subdomain="Articles 24 à 26 — tests", rule_type="OBLIGATION",
        title="Tests de résilience opérationnelle numérique",
        statement=(
            "Les articles 24 à 26 du règlement (UE) 2022/2554 imposent un programme de tests "
            "de résilience opérationnelle numérique et prévoient, pour certaines entités, des "
            "tests de pénétration fondés sur la menace."
        ),
        operational_rule=(
            "Deux niveaux d'exigence : un programme de tests pour toutes les entités "
            "concernées, et des tests avancés réservés à celles que l'autorité désigne."
        ),
        common_confusions=[
            "croire que les tests de pénétration avancés s'imposent à toutes les entités",
            "confondre programme de tests et audit de sécurité classique",
        ],
        priority="HIGH", article="Articles 24 à 26",
        traps=["OVERGENERALIZATION", "SCOPE_CONFUSION", "EXCEPTION_OMISSION"],
        families=["qualification", "false_premise", "true_premise_adversarial"],
        related=["DORA-R-001"], exceptions_status="unknown",
    ),
    _r(
        id="DORA-R-010", subdomain="Article 28 — registre d'information", rule_type="RECORD_KEEPING",
        title="Registre d'information des accords contractuels TIC",
        statement=(
            "L'article 28 du règlement (UE) 2022/2554 impose de tenir et de mettre à jour un "
            "registre d'information relatif à l'ensemble des accords contractuels portant sur "
            "l'utilisation de services TIC fournis par des prestataires tiers, en distinguant "
            "ceux qui soutiennent des fonctions critiques ou importantes."
        ),
        operational_rule=(
            "Le registre couvre tous les accords TIC, pas seulement ceux jugés critiques ; "
            "la criticité est une distinction interne au registre, pas un critère d'entrée."
        ),
        common_confusions=[
            "limiter le registre aux seuls prestataires critiques",
            "confondre le registre d'information et le registre des incidents",
        ],
        priority="CRITICAL", article="Article 28",
        traps=["SCOPE_CONFUSION", "CONCEPT_CONFLATION", "OVERGENERALIZATION"],
        families=["qualification", "false_premise", "true_premise_adversarial"],
        related=["DORA-R-011", "DORA-R-012"], exceptions_status="unknown",
    ),
    _r(
        id="DORA-R-011", subdomain="Article 30 — contrats", rule_type="OBLIGATION",
        title="Dispositions contractuelles essentielles avec les prestataires TIC",
        statement=(
            "L'article 30 énumère les dispositions que doivent contenir les accords "
            "contractuels avec les prestataires tiers de services TIC, avec des exigences "
            "renforcées lorsque les services soutiennent des fonctions critiques ou "
            "importantes, notamment en matière d'accès, d'inspection, d'audit et de "
            "stratégies de sortie."
        ),
        operational_rule=(
            "Deux niveaux d'exigences contractuelles selon la criticité de la fonction "
            "soutenue ; les droits d'audit et la stratégie de sortie relèvent du niveau "
            "renforcé."
        ),
        common_confusions=[
            "appliquer les exigences renforcées à tous les contrats indistinctement",
            "omettre la stratégie de sortie",
            "croire que la sous-traitance échappe au dispositif",
        ],
        priority="CRITICAL", article="Article 30",
        traps=["EXCEPTION_OMISSION", "SCOPE_CONFUSION", "OVERGENERALIZATION"],
        families=["qualification", "false_premise", "abstention"],
        related=["DORA-R-010", "DORA-R-012"], exceptions_status="unknown",
    ),
    _r(
        id="DORA-R-012", subdomain="Article 31 — prestataires critiques", rule_type="CLASSIFICATION",
        title="Désignation des prestataires tiers critiques de services TIC",
        statement=(
            "L'article 31 organise la désignation, par les autorités européennes de "
            "surveillance, des prestataires tiers de services TIC critiques, et les soumet à "
            "un cadre de supervision spécifique."
        ),
        operational_rule=(
            "La criticité d'un prestataire au sens de l'article 31 est désignée par "
            "l'autorité ; elle ne se confond pas avec la criticité d'une fonction appréciée "
            "par l'entité financière."
        ),
        common_confusions=[
            "croire qu'une entité financière désigne elle-même ses prestataires critiques",
            "confondre fonction critique ou importante et prestataire tiers critique",
        ],
        priority="HIGH", article="Article 31",
        traps=["CONCEPT_CONFLATION", "SCOPE_CONFUSION", "DEFINITION_DRIFT"],
        families=["qualification", "false_premise", "cross_regulatory"],
        related=["DORA-R-010", "DORA-R-011"], exceptions_status="unknown",
    ),
    _r(
        id="DORA-R-013", subdomain="Application", rule_type="DEADLINE",
        title="Date d'application du règlement DORA",
        statement=(
            "Le règlement (UE) 2022/2554 est entré en vigueur après sa publication et "
            "s'applique à compter du 17 janvier 2025."
        ),
        operational_rule=(
            "Toute question portant sur des obligations DORA avant cette date appelle une "
            "réponse temporellement située, non une application rétroactive."
        ),
        common_confusions=[
            "confondre entrée en vigueur et date d'application",
            "appliquer DORA à un exercice antérieur à 2025",
        ],
        priority="HIGH", article="Article 64", time_sensitive=True,
        traps=["TEMPORAL_CONFUSION", "DEFINITION_DRIFT"],
        families=["temporal", "recall", "false_premise"],
        related=["DORA-R-001"], exceptions_status="none_identified",
    ),
]
