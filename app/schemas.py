from pydantic import BaseModel, EmailStr


class SubscriptionCreate(BaseModel):
    email: EmailStr
    bag_name: str


class SubscriptionOut(BaseModel):
    id: int
    email: EmailStr
    bag_name: str
    active: bool

    class Config:
        from_attributes = True
