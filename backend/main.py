from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.orm import Session

import models
import schemas
from database import Base, engine, get_db
from security import (
    create_access_token,
    decode_token,
    hash_password,
    verify_password,
)

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Job Application Tracker")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> models.User:
    user_id = decode_token(token)
    user = db.get(models.User, user_id) if user_id else None
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


@app.get("/")
def health():
    return {"status": "ok"}


@app.post("/auth/register", response_model=schemas.UserOut, status_code=201)
def register(data: schemas.UserCreate, db: Session = Depends(get_db)):
    existing = db.scalar(select(models.User).where(models.User.email == data.email))
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    user = models.User(email=data.email, hashed_password=hash_password(data.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@app.post("/auth/login", response_model=schemas.Token)
def login(
    form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    # The form field is called "username", but we use it for the email
    user = db.scalar(select(models.User).where(models.User.email == form.username))
    if not user or not verify_password(form.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    return schemas.Token(access_token=create_access_token(user.id))


@app.get("/auth/me", response_model=schemas.UserOut)
def me(current_user: models.User = Depends(get_current_user)):
    return current_user


def get_owned_application(
    app_id: int, db: Session, user: models.User
) -> models.Application:
    application = db.get(models.Application, app_id)
    if not application or application.user_id != user.id:
        raise HTTPException(status_code=404, detail="Application not found")
    return application


@app.post("/applications", response_model=schemas.ApplicationOut, status_code=201)
def create_application(
    data: schemas.ApplicationCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    application = models.Application(**data.model_dump(), user_id=current_user.id)
    db.add(application)
    db.commit()
    db.refresh(application)
    return application


@app.get("/applications", response_model=list[schemas.ApplicationOut])
def list_applications(
    status: schemas.Status | None = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    query = select(models.Application).where(
        models.Application.user_id == current_user.id
    )
    if status:
        query = query.where(models.Application.status == status)
    query = query.order_by(models.Application.applied_date.desc())
    return db.scalars(query).all()


@app.get("/applications/{app_id}", response_model=schemas.ApplicationOut)
def get_application(
    app_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return get_owned_application(app_id, db, current_user)


@app.patch("/applications/{app_id}", response_model=schemas.ApplicationOut)
def update_application(
    app_id: int,
    data: schemas.ApplicationUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    application = get_owned_application(app_id, db, current_user)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(application, field, value)
    db.commit()
    db.refresh(application)
    return application


@app.delete("/applications/{app_id}", status_code=204)
def delete_application(
    app_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    application = get_owned_application(app_id, db, current_user)
    db.delete(application)
    db.commit()