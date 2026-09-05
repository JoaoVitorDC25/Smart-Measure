"""Estabilização temporal das leituras reconhecidas."""

from collections import Counter, deque

from config import HISTORY_SIZE, MINIMUM_VOTES, SEARCHING_TEXT

class ReadingStabilizer:
    """Seleciona por votação a leitura mais frequente nos quadros recentes."""

    def __init__(
        self,
        history_size: int = HISTORY_SIZE,
        minimum_votes: int = MINIMUM_VOTES,
        searching_text: str = SEARCHING_TEXT,
    ) -> None:
        self.minimum_votes = minimum_votes
        self.searching_text = searching_text
        self._history: deque[str] = deque(maxlen=history_size)
        self._stable_reading = searching_text

    @property
    def value(self) -> str:
        return self._stable_reading

    def update(self, reading: str) -> str:
        if reading:
            self._history.append(reading)

        if self._history:
            winner, votes = Counter(self._history).most_common(1)[0]
            if votes >= self.minimum_votes:
                self._stable_reading = winner

        return self._stable_reading

    def reset(self) -> None:
        self._history.clear()
        self._stable_reading = self.searching_text
