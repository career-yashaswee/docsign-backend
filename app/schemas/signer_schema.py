from pydantic import BaseModel, Field, ConfigDict
from typing import List, Dict


class AssignSignersRequest(BaseModel):
    signers: List[int] = Field(..., min_items=1, description="List of user IDs")


class AssignSignersResult(BaseModel):
    assigned: List[int]
    already_assigned: List[int]
    invalid_user_ids: List[int]
    self_assignment_rejected: List[int]

    model_config = ConfigDict(from_attributes=True)
