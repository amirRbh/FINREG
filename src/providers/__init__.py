"""Adaptateurs de fournisseurs.

Importer ce paquet enregistre les adaptateurs fournis avec le harnais. Un
adaptateur vers un fournisseur réel s'ajoute ici, en appelant
`enregistrer_adaptateur` depuis son module.
"""

from src.providers import fake as _fake  # noqa: F401  (effet de bord : enregistrement)
