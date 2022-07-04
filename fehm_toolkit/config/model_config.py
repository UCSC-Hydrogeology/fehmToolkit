from dataclasses import dataclass


@dataclass
class ModelConfig:
    kind: str
    params: dict

    @classmethod
    def from_dict(cls, dct):
        return cls(**dct)
