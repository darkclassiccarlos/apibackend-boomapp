# -*- coding: utf-8 -*-
from fastapi import APIRouter, Response, Depends
from fastapi.responses import StreamingResponse


# from .orm.tables import ()

# from .dependencies import ()

# from .settings import ()

router = APIRouter()



@router.get("/check")
def root():
   return {'msg': "Hola amigos Boom "}

