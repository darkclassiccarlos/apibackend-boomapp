# -*- coding: utf-8 -*-
from fastapi import APIRouter, Response, Depends, HTTPException, Request, status,Header
from fastapi.responses import StreamingResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.hash import bcrypt  # Importa la biblioteca de hashing
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session
from datetime import datetime,timedelta
import jwt
from sqlalchemy import select, join

#local imports
from ..dependencies import (cryptpass,create_jwt_token,get_current_user,enviar_correo,decode_jwt_token)
from ..db.database import get_db
from ..db.db_models import users, roluser, passwordRecoveryRequest,familys,products,familyproducts,business,designsconfigurations
from ..db.models import UserBase,UserBaseCatalog,RolBase,FamilyproductsBase,FamilysBase,ProductsBase,CustomOAuth2PasswordRequestForm,emailRequest,PasswordRecovery,recoveryPassword,FamilyCreateBase,ProductCreate, Business,DesignsConfigurations
from ..db import users_actions


router = APIRouter(
    prefix="/admin",
    tags=['admin']
)

@router.get("/user_catalog/")
async def get_user_catalog(email: str, db = Depends(get_db)):
    try:
        user = UserBaseCatalog
        family = FamilysBase
        product = ProductsBase
        family_product = FamilyproductsBase
        # Consulta SQL para obtener el catálogo del usuario
        stmt = (
            select(
                users.email,
                familys.name.label('family'),
                familys.id,
                products.id,
                products.name.label('name'),
                products.namefile,
                products.price
            )
            .select_from(
                join(familyproducts, familys, familys.id == familyproducts.family_id)
                .join(products, familyproducts.product_id == products.id)
                .join(users, familys.user_id == users.id)
            )
            .where(users.email == email)
        )
        result = db.execute(stmt)
        # Organizar los resultados en la estructura JSON requerida
        catalog = {}
        for row in result:
            family_name = row[1],
            product_data = {
                "product_id": row[3],
                "name": row[4],
                "image": row[5],
                "price": row[6]
            }
            if family_name not in catalog:
                catalog[family_name] = {"family": row[1],"family_id": row[2], "products": []}

            catalog[family_name]["products"].append(product_data)

        user_data = {"user": email, "catalog": list(catalog.values())}

        return user_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

# Endpoint para crear una familia de productos
@router.post("/families/")
def create_family(family: FamilyCreateBase, db = Depends(get_db)):
    try:
        user = db.query(users).filter(users.id == family.user_id).first()
        if user is None:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        db_family = familys(**family.dict())
        db.add(db_family)
        db.commit()
        db.refresh(db_family)
        #family = db.query(familys).filter(familys.name == family.name, familys.user_id == family.user_id).first()
        #response = db_family.as_dict()
        response = {
                    "success": True,  # Puedes utilizar otro campo si tienes el nombre en la base de datos
                    "message": "familia creada",
                    "family_id": db_family.id
                }
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    
# Endpoint para crear un producto
@router.post("/products/")
def create_product(product: ProductCreate, db = Depends(get_db)):
    try:
        # Crear el producto
        db_product = products(**product.dict(exclude={"family_ids"}))
        db.add(db_product)
        db.commit()
        db.refresh(db_product)

        # Asociar el producto con las familias
        for family_id in product.family_ids:
            family_product = familyproducts(family_id=family_id, product_id=db_product.id)
            db.add(family_product)
        db.commit()
        response = {
                        "success": True,  # Puedes utilizar otro campo si tienes el nombre en la base de datos
                        "message": "producto creado",
                        "family_id": db_product.id
                    }
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

# Endpoint para crear un negocio
# @router.post("/save_business/")
# def save_business(business: Business, db = Depends(get_db)):
#     db.add(business)
#     db.commit()
#     db.refresh(business)
#     return business

# Endpoint para crear una configuración de diseño
# @router.post("/save_configuration_designs/")
# def save_configuration_designs(configurations: DesignsConfigurations, db = Depends(get_db)):
#     db.add(configurations)
#     db.commit()
#     db.refresh(configurations)
#     return configurations