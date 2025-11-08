from enum import Enum

from pydantic import BaseModel


class SeedVariant(str, Enum):
    """Selectable seed scripts available via the admin API."""

    SEED = "seed"
    DEPLOY_TEST = "seed_deploy_test"


class AdminActionRequest(BaseModel):
    password: str
    seed_variant: SeedVariant = SeedVariant.SEED
