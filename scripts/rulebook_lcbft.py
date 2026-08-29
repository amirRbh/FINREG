"""Règles LCB-FT du Rulebook V0. Références non confrontées au texte primaire."""

from __future__ import annotations

CMF = "https://www.legifrance.gouv.fr/codes/section_lc/LEGITEXT000006072026/LEGISCTA000020196177"
AMLD4 = "https://eur-lex.europa.eu/legal-content/FR/TXT/?uri=CELEX:32015L0849"
AMLD5 = "https://eur-lex.europa.eu/legal-content/FR/TXT/?uri=CELEX:32018L0843"

CMF_TXT = "Code monétaire et financier"
CMF_REGIME = "CMF_LCBFT"
UE_REGIME = "AMLD4_AMLD5"

def _cmf(**kw):
    base = dict(text=CMF_TXT, url=CMF, regime=CMF_REGIME, valid_from="2020-02-14")
    base.update(kw)
    return base

REGLES = [
    _cmf(
        id="LCBFT-R-001", subdomain="Personnes assujetties", rule_type="SCOPE",
        title="Périmètre des personnes assujetties",
        statement=(
            "L'article L.561-2 du code monétaire et financier énumère les personnes "
            "assujetties aux obligations de lutte contre le blanchiment de capitaux et le "
            "financement du terrorisme."
        ),
        operational_rule=(
            "L'assujettissement résulte d'une énumération limitative : il se vérifie par "
            "lecture de la liste, non par analogie avec une activité voisine."
        ),
        common_confusions=[
            "étendre l'assujettissement par analogie à une activité non énumérée",
            "confondre assujettissement LCB-FT et agrément prudentiel",
        ],
        article="Article L.561-2", priority="CRITICAL",
        traps=["SCOPE_CONFUSION", "OVERGENERALIZATION", "CROSS_REGULATORY_CONFLATION"],
        families=["qualification", "false_premise", "true_premise_adversarial"],
        related=["LCBFT-R-002"], exceptions_status="unknown",
    ),
    _cmf(
        id="LCBFT-R-002", subdomain="Approche par les risques", rule_type="OBLIGATION",
        title="Classification des risques",
        statement=(
            "L'article L.561-4-1 du code monétaire et financier impose aux personnes "
            "assujetties de définir et de mettre en place des dispositifs d'identification "
            "et d'évaluation des risques de blanchiment et de financement du terrorisme "
            "auxquels elles sont exposées, et d'élaborer une classification de ces risques."
        ),
        operational_rule=(
            "La classification des risques conditionne l'intensité de toutes les mesures de "
            "vigilance : c'est elle qu'un contrôleur examine en premier."
        ),
        common_confusions=[
            "appliquer une vigilance uniforme sans classification préalable",
            "confondre classification des risques et scoring client",
        ],
        article="Article L.561-4-1", priority="CRITICAL",
        traps=["CONCEPT_CONFLATION", "CAUSAL_INFERENCE", "OVERGENERALIZATION"],
        families=["qualification", "true_premise_adversarial"],
        related=["LCBFT-R-003", "LCBFT-R-006"], exceptions_status="unknown",
    ),
    _cmf(
        id="LCBFT-R-003", subdomain="Vigilance à l'entrée en relation", rule_type="OBLIGATION",
        title="Identification et vérification avant l'entrée en relation d'affaires",
        statement=(
            "L'article L.561-5 du code monétaire et financier impose d'identifier le client "
            "et, le cas échéant, le bénéficiaire effectif, et de vérifier ces éléments "
            "d'identification avant d'entrer en relation d'affaires."
        ),
        operational_rule=(
            "Le principe est l'antériorité de la vérification sur l'entrée en relation ; "
            "les aménagements de calendrier sont des exceptions encadrées, pas la règle."
        ),
        common_confusions=[
            "traiter la vérification différée comme le régime de droit commun",
            "confondre identification et vérification de l'identité",
            "omettre le bénéficiaire effectif",
        ],
        article="Article L.561-5", priority="CRITICAL",
        traps=["EXCEPTION_OMISSION", "TEMPORAL_CONFUSION", "CONCEPT_CONFLATION"],
        families=["qualification", "true_premise_adversarial", "false_premise"],
        related=["LCBFT-R-004", "LCBFT-R-005"], exceptions_status="unknown",
    ),
    _cmf(
        id="LCBFT-R-004", subdomain="Connaissance de la relation", rule_type="OBLIGATION",
        title="Recueil d'informations sur l'objet et la nature de la relation d'affaires",
        statement=(
            "L'article L.561-5-1 du code monétaire et financier impose de recueillir, avant "
            "d'entrer en relation d'affaires, les informations relatives à l'objet et à la "
            "nature de cette relation et tout élément d'information pertinent."
        ),
        operational_rule=(
            "La connaissance client ne se réduit pas à l'identification : elle porte aussi "
            "sur la finalité économique de la relation."
        ),
        common_confusions=[
            "réduire la connaissance client à la collecte d'une pièce d'identité",
        ],
        article="Article L.561-5-1", priority="HIGH",
        traps=["CONCEPT_CONFLATION", "OVERGENERALIZATION"],
        families=["qualification", "recall"], related=["LCBFT-R-003"],
        exceptions_status="unknown",
    ),
    _cmf(
        id="LCBFT-R-005", subdomain="Bénéficiaire effectif", rule_type="DEFINITION",
        title="Identification du bénéficiaire effectif",
        statement=(
            "Le code monétaire et financier impose d'identifier et de vérifier l'identité du "
            "bénéficiaire effectif de la relation d'affaires, les modalités et critères de "
            "détermination étant fixés par sa partie réglementaire."
        ),
        operational_rule=(
            "Le critère de détermination et les seuils de détention figurent dans la partie "
            "réglementaire, non dans la partie législative : affirmer un pourcentage en "
            "citant un article en L est une erreur de niveau de norme."
        ),
        common_confusions=[
            "citer un seuil de détention en l'attribuant à un article législatif",
            "confondre bénéficiaire effectif et représentant légal",
            "s'arrêter au premier niveau de détention",
        ],
        article="Articles L.561-2-2 et R.561-1 et suivants", priority="CRITICAL",
        traps=["FALSE_THRESHOLD", "FALSE_ARTICLE", "CONCEPT_CONFLATION", "MISSING_INFORMATION"],
        families=["qualification", "false_premise", "abstention", "calculation"],
        related=["LCBFT-R-003"], exceptions_status="unknown",
        negative_claims=[dict(
            claim="La partie législative du code monétaire et financier fixerait elle-même le seuil de détention du bénéficiaire effectif.",
            note="Le seuil relève de la partie réglementaire ; à confronter au texte.",
        )],
    ),
    _cmf(
        id="LCBFT-R-006", subdomain="Vigilance constante", rule_type="OBLIGATION",
        title="Vigilance constante pendant toute la relation d'affaires",
        statement=(
            "L'article L.561-6 du code monétaire et financier impose d'exercer une vigilance "
            "constante pendant toute la durée de la relation d'affaires et de procéder à un "
            "examen attentif des opérations effectuées, en veillant à ce qu'elles soient "
            "cohérentes avec la connaissance actualisée du client."
        ),
        operational_rule=(
            "La vigilance est continue : la connaissance client doit être actualisée, et "
            "l'incohérence d'une opération avec le profil connu est le déclencheur d'examen."
        ),
        common_confusions=[
            "traiter la vigilance comme un contrôle limité à l'entrée en relation",
            "confondre vigilance constante et vigilance renforcée",
        ],
        article="Article L.561-6", priority="CRITICAL",
        traps=["TEMPORAL_CONFUSION", "CONCEPT_CONFLATION", "SCOPE_CONFUSION"],
        families=["qualification", "true_premise_adversarial", "temporal"],
        related=["LCBFT-R-002", "LCBFT-R-007"], exceptions_status="unknown",
    ),
    _cmf(
        id="LCBFT-R-007", subdomain="Vigilance renforcée", rule_type="OBLIGATION",
        title="Mesures de vigilance renforcée",
        statement=(
            "L'article L.561-10 du code monétaire et financier énumère les situations dans "
            "lesquelles les personnes assujetties appliquent des mesures de vigilance "
            "complémentaires à l'égard de leur client."
        ),
        operational_rule=(
            "La vigilance renforcée découle de situations énumérées et de la classification "
            "des risques ; elle ne se déduit pas d'une intuition."
        ),
        common_confusions=[
            "confondre vigilance renforcée et refus d'entrer en relation",
            "croire que la vigilance renforcée est laissée à la seule appréciation de l'établissement",
        ],
        article="Article L.561-10", priority="CRITICAL",
        traps=["CAUSAL_INFERENCE", "CONCEPT_CONFLATION", "EXCEPTION_OMISSION"],
        families=["qualification", "false_premise", "true_premise_adversarial"],
        related=["LCBFT-R-008", "LCBFT-R-009"], exceptions_status="unknown",
    ),
    _cmf(
        id="LCBFT-R-008", subdomain="Personnes politiquement exposées", rule_type="CLASSIFICATION",
        title="Traitement des personnes politiquement exposées",
        statement=(
            "Le code monétaire et financier soumet les relations d'affaires avec des "
            "personnes politiquement exposées à des mesures de vigilance complémentaires, "
            "la définition et le périmètre de ces personnes étant précisés par sa partie "
            "réglementaire."
        ),
        operational_rule=(
            "La qualité de personne politiquement exposée déclenche des mesures "
            "complémentaires ; elle n'emporte par elle-même ni interdiction d'entrer en "
            "relation ni obligation de déclaration."
        ),
        common_confusions=[
            "déduire du statut de PPE une interdiction d'entrer en relation",
            "déduire du statut de PPE une obligation de déclaration de soupçon",
            "oublier les membres de la famille et les proches associés",
        ],
        article="Articles L.561-10 et R.561-18", priority="CRITICAL",
        traps=["CAUSAL_INFERENCE", "OVERGENERALIZATION", "EXCEPTION_OMISSION"],
        families=["qualification", "false_premise", "true_premise_adversarial"],
        related=["LCBFT-R-007", "LCBFT-R-009"], exceptions_status="unknown",
    ),
    _cmf(
        id="LCBFT-R-009", subdomain="Déclaration de soupçon", rule_type="OBLIGATION",
        title="Déclaration de soupçon à Tracfin",
        statement=(
            "L'article L.561-15 du code monétaire et financier impose de déclarer au service "
            "Tracfin les sommes ou opérations portant sur des sommes dont les personnes "
            "assujetties savent, soupçonnent ou ont de bonnes raisons de soupçonner qu'elles "
            "proviennent d'une infraction passible d'une peine privative de liberté "
            "supérieure à un an ou sont liées au financement du terrorisme."
        ),
        operational_rule=(
            "Le critère est le soupçon, pas la preuve ni la certitude. Le déclarant n'a pas "
            "à qualifier juridiquement l'infraction sous-jacente."
        ),
        common_confusions=[
            "exiger une certitude ou une preuve avant de déclarer",
            "croire que le déclarant doit qualifier l'infraction sous-jacente",
            "confondre déclaration de soupçon et information du client",
        ],
        article="Article L.561-15", priority="CRITICAL",
        traps=["DEFINITION_DRIFT", "CAUSAL_INFERENCE", "CONCEPT_CONFLATION", "NEGATIVE_ASSERTION"],
        families=["qualification", "false_premise", "true_premise_adversarial", "abstention"],
        related=["LCBFT-R-010"], exceptions_status="unknown",
    ),
    _cmf(
        id="LCBFT-R-010", subdomain="Confidentialité", rule_type="PROHIBITION",
        title="Interdiction d'informer le client de la déclaration",
        statement=(
            "Le code monétaire et financier interdit de porter à la connaissance du client "
            "ou de tiers l'existence et le contenu d'une déclaration de soupçon adressée à "
            "Tracfin, ainsi que les suites qui lui sont données."
        ),
        operational_rule=(
            "L'interdiction de divulgation est absolue vis-à-vis du client ; les partages "
            "admis sont limitativement définis par le texte."
        ),
        common_confusions=[
            "croire qu'un client peut être informé au motif de la transparence",
            "confondre interdiction de divulgation et secret professionnel général",
        ],
        article="Article L.561-18", priority="CRITICAL",
        traps=["OVERGENERALIZATION", "EXCEPTION_OMISSION", "CONCEPT_CONFLATION"],
        families=["qualification", "false_premise", "true_premise_adversarial"],
        related=["LCBFT-R-009"], exceptions_status="unknown",
    ),
    _cmf(
        id="LCBFT-R-011", subdomain="Conservation", rule_type="RECORD_KEEPING",
        title="Conservation des documents et informations",
        statement=(
            "L'article L.561-12 du code monétaire et financier impose de conserver pendant "
            "cinq ans à compter de la clôture des comptes ou de la cessation des relations "
            "les documents et informations relatifs à l'identité des clients et aux "
            "opérations effectuées."
        ),
        operational_rule=(
            "Le point de départ des cinq ans est la clôture ou la cessation de la relation, "
            "pas la date de l'opération."
        ),
        common_confusions=[
            "faire courir le délai depuis la date de l'opération",
            "confondre ce délai avec les obligations de conservation MiFID II",
        ],
        article="Article L.561-12", priority="HIGH",
        traps=["TEMPORAL_CONFUSION", "CROSS_REGULATORY_CONFLATION", "FALSE_THRESHOLD"],
        families=["recall", "temporal", "cross_regulatory", "false_premise"],
        related=["MIFID-R-008"], exceptions_status="unknown",
    ),
    _cmf(
        id="LCBFT-R-012", subdomain="Impossibilité d'identifier", rule_type="PROHIBITION",
        title="Refus ou cessation de la relation d'affaires",
        statement=(
            "L'article L.561-8 du code monétaire et financier dispose que, lorsque la "
            "personne assujettie n'est pas en mesure d'identifier son client ou d'obtenir "
            "les informations sur l'objet et la nature de la relation d'affaires, elle "
            "n'exécute aucune opération et n'établit ni ne poursuit aucune relation d'affaires."
        ),
        operational_rule=(
            "L'impossibilité d'identifier ferme la relation ; elle n'emporte pas "
            "automatiquement déclaration de soupçon, qui obéit à son propre critère."
        ),
        common_confusions=[
            "déduire mécaniquement une déclaration de soupçon de l'impossibilité d'identifier",
            "croire qu'une opération peut être exécutée en attendant les pièces",
        ],
        article="Article L.561-8", priority="CRITICAL",
        traps=["CAUSAL_INFERENCE", "CONCEPT_CONFLATION", "EXCEPTION_OMISSION"],
        families=["qualification", "false_premise", "true_premise_adversarial", "abstention"],
        related=["LCBFT-R-003", "LCBFT-R-009"], exceptions_status="unknown",
    ),
    dict(
        id="LCBFT-R-013", subdomain="Cadre européen", rule_type="SCOPE",
        title="Directives européennes de transposition",
        statement=(
            "La directive (UE) 2015/849, modifiée notamment par la directive (UE) 2018/843, "
            "constitue le cadre européen relatif à la prévention de l'utilisation du système "
            "financier aux fins du blanchiment de capitaux et du financement du terrorisme, "
            "transposé en droit français dans le code monétaire et financier."
        ),
        operational_rule=(
            "Une directive n'est pas d'application directe : l'obligation opposable en "
            "France est celle du code monétaire et financier, pas celle de la directive."
        ),
        common_confusions=[
            "citer un article de la directive comme directement opposable à un assujetti français",
            "confondre directive et règlement quant à l'effet direct",
        ],
        text="Directive (UE) 2015/849, modifiée par la directive (UE) 2018/843",
        article="Ensemble de la directive", url=AMLD4,
        regime=UE_REGIME, valid_from="2015-06-05",
        priority="HIGH",
        traps=["CROSS_REGULATORY_CONFLATION", "SCOPE_CONFUSION", "FALSE_ARTICLE"],
        families=["qualification", "cross_regulatory", "false_premise"],
        related=["LCBFT-R-001"], exceptions_status="unknown",
    ),
]
