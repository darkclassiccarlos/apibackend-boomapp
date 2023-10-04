# -*- coding: utf-8 -*-
from fastapi import APIRouter, Response, Depends, HTTPException, Request, File, UploadFile, Form
from sqlalchemy.orm import Session
from PIL import Image
import base64
from io import BytesIO
import os

#local imports
from ..db.database import get_db
# from ..db.db_models import 
# from ..db.models import 

router = APIRouter(
    prefix="/multimedia",
    tags=['multimedia']
)

#Actualizar un usuario por  ID
@router.post('/upload', name='multimedia:upload')
async def update_user(
    request: Request, 
    response:Response,
    image: UploadFile = File(...),
    db: Session = Depends(get_db)):

    buffered = BytesIO()
    image = Image.open(BytesIO(image.file.read()))

    width, height = image.size
    new_size = (width//2, height//2)
    resized_image = image.resize(new_size)
    
    resized_image.save(buffered, format="JPEG")
    img_str = base64.b64encode(buffered.getvalue())

    return {
        "name": img_str
    }