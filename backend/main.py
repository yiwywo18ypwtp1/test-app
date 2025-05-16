from fastapi import FastAPI, Depends, HTTPException, Request, Response
from database import SpyCat, Mission, Target, get_db
from psycopg2 import IntegrityError
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import httpx


app = FastAPI()

app.add_middleware(
  CORSMiddleware,
  allow_origins=[
    "http://localhost:3000",
    "http://127.0.0.1:3000",
  ],
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"],
)


async def validate_cat_breed(breed_name: str):
    url = "https://api.thecatapi.com/v1/breeds"
    async with httpx.AsyncClient() as client:
      response = await client.get(url)
    
    if response.status_code != 200:
      raise HTTPException(status_code=502, detail="Failed to validate breed with TheCatAPI")

    breeds = response.json()
    valid_breeds = {breed["name"].lower() for breed in breeds}
    
    if breed_name.lower() not in valid_breeds:
      raise HTTPException(status_code=400, detail="Invalid cat breed")
  
  
class CatSpyCreate(BaseModel):
  catname: str
  experience: int
  breed: str
  salary: int
  
  
class TargetCreate(BaseModel):
    name: str
    country: str
    notes: str
    is_completed: bool = False

class MissionCreate(BaseModel):
    cat_id: int | None = None
    is_completed: bool = False
    targets: list[TargetCreate]

class TargetResponse(BaseModel):
    id: int
    name: str
    country: str
    notes: str
    is_completed: bool

    class Config:
        orm_mode = True

class MissionResponse(BaseModel):
    id: int
    cat_id: int | None
    is_completed: bool
    targets: list[TargetResponse]

    class Config:
        orm_mode = True
  

# CATS
@app.post('/cat/')
async def create_cat(cat: CatSpyCreate, db: Session = Depends(get_db)):
  await validate_cat_breed(cat.breed)
  
  cat_exists = db.query(SpyCat).filter(SpyCat.name == cat.catname).first()
  if cat_exists:
    raise HTTPException(status_code=400, detail="Agent with same name already exists!")
  
  new_cat = SpyCat(
    name=cat.catname,
    experience=cat.experience,
    breed=cat.breed,
    salary=cat.salary
  )
  
  db.add(new_cat)
  try:
    db.commit()
    db.refresh(new_cat)
  except IntegrityError:
    db.rollback
    raise HTTPException(status_code=400, detail="Agent with same name already exists!")
  
  return {'message': f'cat created: {cat.catname}'}


@app.delete('/cat/')
def remove_cat(catname: str, db: Session = Depends(get_db)):
  cat_to_delete = db.query(SpyCat).filter(SpyCat.name == catname).first()
  
  if cat_to_delete:
    db.delete(cat_to_delete)
    try:
      db.commit()
    except IntegrityError:
      db.rollback
  
  return {'message': f'cat created: {catname}'}


@app.get('/cat/')
def single_cat(catname: str, db: Session = Depends(get_db)):
  cat = db.query(SpyCat).filter(SpyCat.name == catname).first()
  
  if cat:
    response = {
      'catname': cat.name,
      'experience': cat.experience,
      'breed': cat.breed,
      'salary': cat.salary
    }
    return {'message': response}


@app.get('/cats/')
def all_cats(db: Session = Depends(get_db)):
  cats = db.query(SpyCat).all()

  if not cats:
    return {'message': 'Коты с таким именем не найдены'}

  cat_list = []
  for cat in cats:
    cat_data = {
      'catname': cat.name,
      'experience': cat.experience,
      'breed': cat.breed,
      'salary': cat.salary
    }
    cat_list.append(cat_data)

  return {'cats': cat_list}


@app.patch('/cat/')
def update_cat_salary(catname: str, salary: int, db: Session = Depends(get_db)):
  cat = db.query(SpyCat).filter(SpyCat.name == catname).first()

  if cat:
    cat.salary = salary
    try:
      db.commit()
    except IntegrityError:
      db.rollback()
      
  return {'message': f'{cat.name}`s salary has been updated to {salary}'}


# MISSIONS AND TAGETS
@app.post('/mission/', response_model=MissionResponse)
def create_mission(mission: MissionCreate, db: Session = Depends(get_db)):
  if mission.cat_id:
    db_cat = db.query(SpyCat).filter(SpyCat.id == mission.cat_id).first()
    if not db_cat:
      raise HTTPException(
        status_code=404,
        detail="Cat not found"
      )
    
    db_mission = Mission(
      cat_id=mission.cat_id,
      is_completed=mission.is_completed
    )
    
    db.add(db_mission)
    db.commit()
    db.refresh(db_mission)
    
    for target in mission.targets:
      db_target = Target(
        mission_id=db_mission.id,
        **target.dict()
      )
      db.add(db_target)
    
    db.commit()
    db.refresh(db_mission)
    return db_mission

@app.delete('/mission/{mission_id}')
def delete_mission(mission_id: int, db: Session = Depends(get_db)):
  db_mission = db.query(Mission).filter(Mission.id == mission_id).first()
  if not db_mission:
    raise HTTPException(
      status_code=404,
      detail="Mission not found"
    )
  
  if db_mission.cat_id is not None:
    raise HTTPException(
      status_code=400,
      detail="Cannot delete mission with assigned cat"
    )
  
  db.delete(db_mission)
  db.commit()
  return {"status": "Mission deleted"}

@app.patch('/mission/{mission_id}/assign')
def assign_cat(mission_id: int, cat_id: int, db: Session = Depends(get_db)):
  db_mission = db.query(Mission).filter(Mission.id == mission_id).first()
  if not db_mission:
    raise HTTPException(
      status_code=404,
      detail="Mission not found"
    )
  
  db_cat = db.query(SpyCat).filter(SpyCat.id == cat_id).first()
  if not db_cat:
    raise HTTPException(
      status_code=404,
      detail="Cat not found"
    )
  
  db_mission.cat_id = cat_id
  db.commit()
  return {"status": "Cat assigned"}

@app.get('/missions/', response_model=list[MissionResponse])
def list_missions(db: Session = Depends(get_db)):
  return db.query(Mission).all()

@app.get('/mission/{mission_id}', response_model=MissionResponse)
def get_mission(mission_id: int, db: Session = Depends(get_db)):
  db_mission = db.query(Mission).filter(Mission.id == mission_id).first()
  if not db_mission:
    raise HTTPException(
      status_code=404,
      detail="Mission not found"
    )
  return db_mission

@app.patch('/mission/{mission_id}/complete')
def complete_mission(mission_id: int, db: Session = Depends(get_db)):
  db_mission = db.query(Mission).filter(Mission.id == mission_id).first()
  if not db_mission:
    raise HTTPException(
      status_code=404,
      detail="Mission not found"
    )
  
  db_mission.is_completed = True
  db.commit()
  return {"status": "Mission completed"}


@app.patch('/target/{target_id}/complete')
def complete_target(target_id: int, db: Session = Depends(get_db)):
  db_target = db.query(Target).filter(Target.id == target_id).first()
  if not db_target:
    raise HTTPException(
      status_code=404,
      detail="Target not found"
    )
    
  db_target.is_completed = True
  db.commit()
  return {"status": "Target completed"}

@app.patch('/target/{target_id}/notes')
def update_notes(target_id: int, notes: str, db: Session = Depends(get_db)):
  db_target = db.query(Target).filter(Target.id == target_id).first()
  if not db_target:
    raise HTTPException(
      status_code=404,
      detail="Target not found"
    )
  
  if db_target.is_completed or db_target.mission.is_completed:
    raise HTTPException(
      status_code=400,
      detail="Cannot update completed target/mission"
    )
  
  db_target.notes = notes
  db.commit()
  return {"status": "Notes updated"}