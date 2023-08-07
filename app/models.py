from typing import List
from pydantic import BaseModel, Field


class FeaturesModel(BaseModel):
    filename: str
    filepath: str
    encoding: str


class UserListOutputModel(BaseModel):
    id: int
    email: str
    cpfcnpj: str = Field(None)
    full_name: str
    external_code: str = Field(None)
    num_photos: int
    submited_by: str
    app_context: str


class UserOutputModel(BaseModel):
    id: int
    email: str
    cpfcnpj: str = Field(None)
    full_name: str
    external_code: str = Field(None)
    features: List[FeaturesModel] = Field(None)
    num_photos: int
    submited_by: str
    app_context: str


class FacematchUserOutputModel(BaseModel):
    user_id: int
    email: str
    cpfcnpj: str = Field(None)
    distance: float


class FacematchOutputModel(BaseModel):
    type: str = Field(..., description='**ok**: authenticated with success; **needs_2fa**: needs validation using code sent by email; *more_than_one*: found more than one similar user ')
    id_2fa: int = Field(None, description='The 2 factor authentication ID to be used to validate users code sent by email')
    users: List[FacematchUserOutputModel]


class TwoFactorAuthOutputModel(BaseModel):
    id: int
    user_id: int


class EmotionRecogOutputModel(BaseModel):
    id: int = Field(None, description='id')
    emotion: dict = Field(None , description='emotion results')
    cpfcnpj: str = Field(None, description='users cpf or cnpj') 
