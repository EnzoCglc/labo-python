from pydantic import BaseModel, ConfigDict , Field
from datetime import datetime

class EquipementCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    
    reference: str = Field(min_length=1, max_length=50 , pattern=r"^[A-Za-z0-9_-]+$")
    nom: str = Field(min_length=1, max_length=50)
    categorie: str = Field(min_length=1, max_length=50)

class EquipementOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id : int
    reference: str
    nom: str
    categorie: str

class LoanCreate(BaseModel):
    equipment_id: int = Field(gt=0)

class LoanOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    user_id: int
    equipment_id: int
    date_emprunt: datetime
    date_retour: datetime | None = None

class HistoryItem(BaseModel):
    loan_id: int
    user_id: int
    username: str
    date_emprunt: datetime
    date_retour: datetime | None = None
    
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"