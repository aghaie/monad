from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class WorkerRequest:
    capability: str
    input_payload: dict
    prev_stage: str


class ReasoningWorker(ABC):
    name = "base"

    @abstractmethod
    def reason(self, request: WorkerRequest) -> dict:
        ...
