"""Limite de débit paramétrable, en jetons.

L'horloge et l'attente sont injectables : les tests vérifient l'espacement des
appels sans jamais dormir réellement.
"""

from __future__ import annotations

import asyncio
import time
from collections.abc import Awaitable, Callable


class LimiteurDebit:
    """Autorise au plus `requetes_par_minute` acquisitions par minute glissante."""

    def __init__(
        self,
        requetes_par_minute: int,
        horloge: Callable[[], float] = time.monotonic,
        dormir: Callable[[float], Awaitable[None]] = asyncio.sleep,
    ) -> None:
        if requetes_par_minute < 1:
            raise ValueError("requetes_par_minute doit valoir au moins 1")
        self.intervalle = 60.0 / requetes_par_minute
        self._horloge = horloge
        self._dormir = dormir
        self._verrou = asyncio.Lock()
        self._prochain_creneau: float | None = None

    async def acquerir(self) -> None:
        async with self._verrou:
            maintenant = self._horloge()
            if self._prochain_creneau is None or maintenant >= self._prochain_creneau:
                self._prochain_creneau = maintenant + self.intervalle
                return
            attente = self._prochain_creneau - maintenant
            self._prochain_creneau += self.intervalle
        await self._dormir(attente)
