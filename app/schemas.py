from pydantic import BaseModel

class ItemBase(BaseModel):
    content: str

class ItemCreate(ItemBase):
    pass

class Item(ItemBase):
    id: int
    model_config = {"from_attributes": True}
