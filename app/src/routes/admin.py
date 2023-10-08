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
from ..dependencies import (cryptpass,create_jwt_token,get_current_user,enviar_correo,decode_jwt_token,update_familys,update_product)
from ..db.database import get_db
from ..db.db_models import users, roluser, passwordRecoveryRequest,familys,products,familyproducts,business,designsconfigurations
from ..db.models import UserBase,UserBaseCatalog,RolBase,FamilyproductsBase,FamilysBase,ProductsBase,CustomOAuth2PasswordRequestForm,emailRequest,PasswordRecovery,recoveryPassword,FamilyCreateBase,ProductCreate,BusinessSave,DesignsConfigurations
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
                familyproducts.id, ### Campo nuevo
                products.id,
                products.name.label('name'),
                products.namefile,
                products.price
            )
            .select_from(
                join(familys,familyproducts, familys.id == familyproducts.family_id,  isouter=True)
                .join(products, familyproducts.product_id == products.id,  isouter=True)
                .join(users, familys.user_id == users.id, isouter=True)
            )
            .where(users.email == email)
        )
        result = db.execute(stmt)
        # Organizar los resultados en la estructura JSON requerida
        catalog = {}
        for row in result:
            family_name = row[1],
            if row[3]:
                product_data = {
                    "product_id": row[4],
                    "name": row[5],
                    "image": row[6],
                    "price": row[7]
                }
            else:
                product_data = None
            if family_name not in catalog:
                catalog[family_name] = {"family": row[1],"family_id": row[2], "products": []}

            catalog[family_name]["products"].append(product_data)

        user_data = {"user": email, "catalog": list(catalog.values())}

        return user_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

# Endpoint para crear una familia de productos ( modificar, para hacerlo updateSave)
@router.post("/families/")
async def create_family(request: Request, family: FamilysBase, db = Depends(get_db)):
    try:
        familydb = db.query(familys).filter(familys.id == family.id, familys.user_id == family.user_id).first()
        if familydb:
            formdata=await request.form()
            familydb.isactive = family.isactive
            familydb.name = family.name
            familydb.user_id = family.user_id
            updated_familys = update_familys(db=db, familyupdate=familydb)
            response = {
                        "success": True,  # Puedes utilizar otro campo si tienes el nombre en la base de datos
                        "message": "familia actualizada",
                        "family_id": updated_familys.id
                    }
            return response
        else:
            familynew = familys(isactive=family.isactive,name=family.name,user_id=family.user_id)
            db_family = familys(**familynew.as_dict())
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
async def create_product(request: Request, product: ProductCreate, db = Depends(get_db)):
    try:
        familyproductdb = db.query(familyproducts).filter(familyproducts.family_id == product.family_ids,familyproducts.product_id == product.id).first()
        if familyproductdb:
            productdb = db.query(products).filter(products.id == familyproductdb.product_id).first()
            formdata = await request.form()
            productdb.name = product.name
            productdb.namefile = product.namefile
            productdb.price = product.price
            updated_product = update_product(db=db, productupdate= productdb)
            response = {
                        "success": True,  # Puedes utilizar otro campo si tienes el nombre en la base de datos
                        "message": "producto actualizado",
                        "family_id": updated_product.id
                    }
            return response
        else:
            # Crear el producto
            #db_product = products(**product.dict(exclude={"family_ids"}))
            db_product = products(name=product.name,namefile=product.namefile,price=product.price)
            db_product = products(**db_product.as_dict())
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
                            "message": "Producto creado",
                            "family_id": db_product.id
                        }
            return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

# Endpoint para crear un negocio
@router.post("/save_business/")
def save_business(businessObject: BusinessSave, db = Depends(get_db)):
    try:
        businessdb = business(name=businessObject.name,
                            adress=businessObject.adress,
                            telephone=businessObject.telephone,
                            email=businessObject.email,
                            description=businessObject.description,
                            category=businessObject.category,
                            website=businessObject.website,
                            picture=businessObject.picture,
                            users_id=businessObject.users_id)
        db.add(businessdb)
        db.commit()
        db.refresh(businessdb)
        return { "success": True,  # Puedes utilizar otro campo si tienes el nombre en la base de datos
                            "message": "Negocio creado",
                            "family_id": businessdb.id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")



# Endpoint para crear una configuración de diseño
@router.post("/save_configuration_designs/")
def save_configuration_designs(configurations: DesignsConfigurations, db = Depends(get_db)):
    try:
        configurationsdb = designsconfigurations(business_id= configurations.business_id,
                            user_id=configurations.user_id,
                            main_color=configurations.main_color,
                            secondary_color=configurations.secondary_color,
                            cover_image_filename=configurations.cover_image_filename,
                            logo_filename=configurations.logo_filename)
        db.add(configurationsdb)
        db.commit()
        db.refresh(configurationsdb)
        return { "success": True,"message": "configuracion creado","family_id": configurationsdb.id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
