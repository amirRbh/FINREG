"""Règles MiFID II du Rulebook V0. Références non confrontées au texte primaire."""

from __future__ import annotations

MIFID = "https://eur-lex.europa.eu/legal-content/FR/TXT/?uri=CELEX:32014L0065"
DA = "https://eur-lex.europa.eu/legal-content/FR/TXT/?uri=CELEX:32017R0565"
DA_ESG = "https://eur-lex.europa.eu/legal-content/FR/TXT/?uri=CELEX:32021R1253"

TEXTE = "Directive 2014/65/UE (MIFID II)"
TEXTE_DA = "Règlement délégué (UE) 2017/565"

REGLES = [
    dict(
        id="MIFID-R-001", subdomain="Article 24 — principes généraux", rule_type="OBLIGATION",
        title="Agir de manière honnête, équitable et professionnelle",
        statement=(
            "L'article 24 de la directive 2014/65/UE impose aux entreprises "
            "d'investissement d'agir d'une manière honnête, équitable et professionnelle "
            "qui serve au mieux les intérêts de leurs clients, et fixe les exigences "
            "générales d'information, notamment le caractère correct, clair et non trompeur "
            "des informations adressées aux clients."
        ),
        operational_rule=(
            "Socle applicable à tous les services d'investissement, indépendamment de la "
            "fourniture d'un conseil."
        ),
        common_confusions=[
            "restreindre le devoir d'agir au mieux des intérêts au seul conseil en investissement",
        ],
        article="Article 24", url=MIFID, priority="HIGH",
        traps=["SCOPE_CONFUSION", "OVERGENERALIZATION"],
        families=["recall", "qualification"], related=["MIFID-R-002"],
        exceptions_status="unknown",
    ),
    dict(
        id="MIFID-R-002", subdomain="Article 25 — adéquation", rule_type="OBLIGATION",
        title="Évaluation de l'adéquation dans le conseil et la gestion de portefeuille",
        statement=(
            "L'article 25 de la directive 2014/65/UE impose, lorsqu'un conseil en "
            "investissement ou un service de gestion de portefeuille est fourni, de se "
            "procurer les informations nécessaires sur les connaissances et l'expérience du "
            "client, sa situation financière y compris sa capacité à subir des pertes, et "
            "ses objectifs d'investissement y compris sa tolérance au risque, afin de "
            "recommander les services et instruments qui lui conviennent."
        ),
        operational_rule=(
            "Le test d'adéquation est réservé au conseil et à la gestion de portefeuille. "
            "Hors de ces deux services, c'est le test du caractère approprié qui s'applique."
        ),
        common_confusions=[
            "appliquer le test d'adéquation à une simple exécution d'ordre",
            "confondre adéquation (suitability) et caractère approprié (appropriateness)",
            "omettre la capacité à subir des pertes parmi les éléments à recueillir",
        ],
        article="Article 25", paragraph="paragraphe 2", url=MIFID, priority="CRITICAL",
        traps=["SCOPE_CONFUSION", "CONCEPT_CONFLATION", "EXCEPTION_OMISSION"],
        families=["qualification", "false_premise", "true_premise_adversarial"],
        related=["MIFID-R-003", "MIFID-R-004", "MIFID-R-006"],
        exceptions_status="unknown",
    ),
    dict(
        id="MIFID-R-003", subdomain="Article 25 — caractère approprié", rule_type="OBLIGATION",
        title="Évaluation du caractère approprié hors conseil",
        statement=(
            "L'article 25 impose, pour les services autres que le conseil en investissement "
            "et la gestion de portefeuille, de demander au client des informations sur ses "
            "connaissances et son expérience afin d'évaluer si le service ou l'instrument "
            "est approprié, et de l'avertir lorsque tel n'est pas le cas."
        ),
        operational_rule=(
            "Le test du caractère approprié ne porte que sur connaissances et expérience — "
            "ni la situation financière ni les objectifs n'y entrent. Un avis négatif "
            "n'interdit pas l'opération : il déclenche un avertissement."
        ),
        common_confusions=[
            "inclure la situation financière dans le test du caractère approprié",
            "croire qu'un test négatif interdit l'opération",
        ],
        article="Article 25", paragraph="paragraphe 3", url=MIFID, priority="CRITICAL",
        traps=["CONCEPT_CONFLATION", "CAUSAL_INFERENCE", "SCOPE_CONFUSION"],
        families=["qualification", "false_premise", "true_premise_adversarial"],
        related=["MIFID-R-002", "MIFID-R-004"], exceptions_status="unknown",
    ),
    dict(
        id="MIFID-R-004", subdomain="Article 25 — exécution simple", rule_type="EXCEPTION",
        title="Régime d'exécution simple pour les instruments non complexes",
        statement=(
            "L'article 25 permet, à certaines conditions, de fournir des services de "
            "réception-transmission ou d'exécution d'ordres sans procéder à l'évaluation du "
            "caractère approprié, lorsque le service porte sur des instruments financiers "
            "non complexes, qu'il est fourni à l'initiative du client et que celui-ci a été "
            "averti."
        ),
        operational_rule=(
            "Trois conditions cumulatives, dont l'initiative du client. Le régime est une "
            "exception d'interprétation stricte, pas un régime par défaut."
        ),
        common_confusions=[
            "appliquer l'exécution simple à un instrument complexe",
            "oublier la condition d'initiative du client",
            "présenter les conditions comme alternatives",
        ],
        article="Article 25", paragraph="paragraphe 4", url=MIFID, priority="CRITICAL",
        traps=["EXCEPTION_OMISSION", "SCOPE_CONFUSION", "OVERGENERALIZATION"],
        families=["qualification", "false_premise", "abstention"],
        related=["MIFID-R-003"], exceptions_status="unknown",
    ),
    dict(
        id="MIFID-R-005", subdomain="Article 25 — rapport d'adéquation", rule_type="DISCLOSURE",
        title="Rapport d'adéquation au client de détail",
        statement=(
            "L'article 25 impose, en cas de conseil en investissement à un client de détail, "
            "de lui fournir une déclaration d'adéquation précisant le conseil fourni et la "
            "manière dont il répond à ses préférences, objectifs et autres caractéristiques."
        ),
        operational_rule=(
            "Le rapport d'adéquation est la trace opposable du raisonnement de "
            "recommandation ; son absence rend le conseil indéfendable en contrôle."
        ),
        common_confusions=[
            "croire que le rapport d'adéquation est dû à tout client, y compris professionnel",
        ],
        article="Article 25", paragraph="paragraphe 6", url=MIFID, priority="HIGH",
        traps=["SCOPE_CONFUSION", "OVERGENERALIZATION"],
        families=["qualification", "recall"], related=["MIFID-R-002"],
        exceptions_status="unknown",
    ),
    dict(
        id="MIFID-R-006", subdomain="Préférences de durabilité", rule_type="DEFINITION",
        title="Préférences en matière de durabilité",
        statement=(
            "Le règlement délégué (UE) 2021/1253, qui modifie le règlement délégué (UE) "
            "2017/565, introduit la notion de préférences en matière de durabilité et "
            "impose de les recueillir dans le cadre de l'évaluation de l'adéquation."
        ),
        operational_rule=(
            "Les préférences de durabilité sont une composante de l'adéquation, pas un test "
            "séparé : elles n'interviennent qu'une fois l'adéquation financière établie."
        ),
        common_confusions=[
            "traiter les préférences de durabilité comme un test autonome",
            "faire primer les préférences de durabilité sur l'adéquation financière",
            "attribuer cette notion à la directive de niveau 1 plutôt qu'au règlement délégué",
        ],
        text=TEXTE_DA + ", modifié par le règlement délégué (UE) 2021/1253",
        article="Article 2 et article 54 du règlement délégué (UE) 2017/565 modifié",
        url=DA_ESG, regime="MIFID2_ESG_2022", valid_from="2022-08-02",
        priority="CRITICAL", time_sensitive=True,
        traps=["CROSS_REGULATORY_CONFLATION", "TEMPORAL_CONFUSION", "CONCEPT_CONFLATION"],
        families=["qualification", "temporal", "cross_regulatory", "true_premise_adversarial"],
        related=["MIFID-R-002", "MIFID-R-007", "SFDR-R-008"], exceptions_status="unknown",
    ),
    dict(
        id="MIFID-R-007", subdomain="Préférences de durabilité — adaptation", rule_type="PROCEDURE",
        title="Adaptation des préférences de durabilité",
        statement=(
            "Le règlement délégué (UE) 2017/565 modifié prévoit que, lorsqu'aucun instrument "
            "financier ne correspond aux préférences de durabilité exprimées par le client, "
            "celui-ci peut adapter ses préférences, l'entreprise devant consigner cette "
            "adaptation et la raison qui la motive."
        ),
        operational_rule=(
            "L'adaptation vient du client et doit être documentée. Elle ne peut pas être "
            "présumée par le conseiller, ni servir de contournement systématique."
        ),
        common_confusions=[
            "laisser le conseiller adapter les préférences à la place du client",
            "omettre l'obligation de documenter la raison de l'adaptation",
            "conclure qu'un produit non conforme peut être recommandé sans adaptation",
        ],
        text=TEXTE_DA + " modifié", article="Article 54", url=DA_ESG,
        regime="MIFID2_ESG_2022", valid_from="2022-08-02",
        priority="CRITICAL", time_sensitive=True,
        traps=["CAUSAL_INFERENCE", "EXCEPTION_OMISSION", "MISSING_INFORMATION"],
        families=["qualification", "false_premise", "abstention", "true_premise_adversarial"],
        related=["MIFID-R-006"], exceptions_status="unknown",
        negative_claims=[dict(
            claim="Le texte fixerait une proportion minimale chiffrée d'investissements durables à proposer.",
            note="Les proportions minimales sont exprimées par le client dans ses préférences, non imposées par le texte.",
        )],
    ),
    dict(
        id="MIFID-R-008", subdomain="Article 16 — organisation", rule_type="RECORD_KEEPING",
        title="Conservation des enregistrements",
        statement=(
            "L'article 16 de la directive 2014/65/UE impose de conserver les "
            "enregistrements de tous les services, activités et transactions, d'une manière "
            "permettant à l'autorité compétente de reconstituer chaque étape essentielle du "
            "traitement de chaque transaction."
        ),
        operational_rule=(
            "L'obligation porte sur la reconstitution du parcours complet, pas sur la seule "
            "conservation de pièces isolées."
        ),
        common_confusions=[
            "citer une durée de conservation sans la rattacher au texte applicable",
            "confondre la conservation MiFID II et la conservation LCB-FT",
        ],
        article="Article 16", url=MIFID, priority="HIGH",
        traps=["CROSS_REGULATORY_CONFLATION", "FALSE_THRESHOLD", "TEMPORAL_CONFUSION"],
        families=["recall", "cross_regulatory", "abstention"],
        related=["LCBFT-R-011"], exceptions_status="unknown",
    ),
    dict(
        id="MIFID-R-009", subdomain="Article 27 — exécution", rule_type="OBLIGATION",
        title="Meilleure exécution",
        statement=(
            "L'article 27 de la directive 2014/65/UE impose de prendre toutes les mesures "
            "suffisantes pour obtenir, lors de l'exécution des ordres, le meilleur résultat "
            "possible pour le client, compte tenu du prix, du coût, de la rapidité, de la "
            "probabilité d'exécution et du règlement, de la taille et de la nature de l'ordre."
        ),
        operational_rule=(
            "La meilleure exécution est une obligation de moyens portant sur un faisceau de "
            "facteurs, pas une obligation d'obtenir le meilleur prix."
        ),
        common_confusions=[
            "réduire la meilleure exécution au meilleur prix",
            "en faire une obligation de résultat",
        ],
        article="Article 27", url=MIFID, priority="HIGH",
        traps=["OVERGENERALIZATION", "CAUSAL_INFERENCE", "DEFINITION_DRIFT"],
        families=["qualification", "false_premise"], related=[],
        exceptions_status="unknown",
    ),
    dict(
        id="MIFID-R-010", subdomain="Article 9 — gouvernance", rule_type="GOVERNANCE",
        title="Responsabilité de l'organe de direction",
        statement=(
            "L'article 9 de la directive 2014/65/UE fixe les exigences relatives à l'organe "
            "de direction des entreprises d'investissement, notamment sa responsabilité dans "
            "la définition et la surveillance des dispositifs de gouvernance assurant une "
            "gestion efficace et prudente."
        ),
        operational_rule=(
            "La responsabilité de gouvernance n'est pas délégable à la fonction conformité : "
            "celle-ci contrôle, l'organe de direction répond."
        ),
        common_confusions=[
            "attribuer à la fonction conformité la responsabilité qui incombe à l'organe de direction",
        ],
        article="Article 9", url=MIFID, priority="MEDIUM",
        traps=["CONCEPT_CONFLATION", "SCOPE_CONFUSION"],
        families=["recall", "qualification"], related=["DORA-R-002"],
        exceptions_status="unknown",
    ),
    dict(
        id="MIFID-R-011", subdomain="Règlement délégué 2017/565", rule_type="PROCEDURE",
        title="Modalités de l'évaluation de l'adéquation au niveau 2",
        statement=(
            "Le règlement délégué (UE) 2017/565 précise les modalités de l'évaluation de "
            "l'adéquation, notamment l'étendue des informations à recueillir et les "
            "diligences à accomplir pour s'assurer de leur fiabilité."
        ),
        operational_rule=(
            "Le détail opérationnel de l'adéquation est au niveau 2 ; citer la seule "
            "directive pour un point de procédure est une erreur de niveau de norme."
        ),
        common_confusions=[
            "attribuer à la directive 2014/65/UE des exigences qui figurent au règlement délégué",
        ],
        text=TEXTE_DA, article="Article 54", url=DA,
        regime="MIFID2_L2_1.0", valid_from="2018-01-03",
        priority="HIGH",
        traps=["CROSS_REGULATORY_CONFLATION", "FALSE_ARTICLE", "DEFINITION_DRIFT"],
        families=["recall", "cross_regulatory", "abstention"],
        related=["MIFID-R-002", "MIFID-R-006"], exceptions_status="unknown",
    ),
]
