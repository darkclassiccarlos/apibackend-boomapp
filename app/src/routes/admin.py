# -*- coding: utf-8 -*-
from fastapi import (
    APIRouter,  
    Depends, 
    HTTPException, 
    Request, 
)
from sqlalchemy import select, join

#local imports
from ..dependencies import (
    remove_products_familys,
    remove_products,
    create_business_qr,
    create_website,
    update_entity,
)
from ..db.database import get_db
from ..db.db_models import (
    users,
    familys,
    products,
    familyproducts,
    business,
    designsconfigurations
)
from ..db.models import (
    UserBaseCatalog, 
    FamilyproductsBase,
    FamilysBase,
    ProductsBase,
    ProductCreate,
    BusinessSave,
    DesignsConfigurations
)

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
                catalog[family_name] = {"family": row[1],"family_id": row[2], "products": None if product_data is None else []}
            
            if product_data is not None:
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
            updated_familys = update_entity(familydb, db=db)
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
            updated_product = update_entity(productdb, db=db)
            response = {
                        "success": True,  # Puedes utilizar otro campo si tienes el nombre en la base de datos
                        "message": "producto actualizado",
                        "family_id": updated_product.id
                    }
            return response
        else:
            # Crear el producto
            db_product = products(name=product.name,namefile=product.namefile,price=product.price)
            db_product = products(**db_product.as_dict())
            db.add(db_product)
            db.commit()
            db.refresh(db_product)
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
def save_business(request: Request, businessObject: BusinessSave, db = Depends(get_db)):
    try:
        website = create_website(businessObject.name)


        businessdb = db.query(business).filter(business.id == businessObject.id).first()
        if businessdb:
            businessdb.name = businessObject.name
            businessdb.address = businessObject.address
            businessdb.telephone = businessObject.telephone
            businessdb.email = businessObject.email
            businessdb.description = businessObject.description
            businessdb.category = businessObject.category
            businessdb.city = businessObject.city
            businessdb.state = businessObject.state
            businessdb.country = businessObject.country
            businessdb.whatsapp = businessObject.whatsapp
            businessdb.facebook = businessObject.facebook
            businessdb.instagram = businessObject.instagram

            updated_entity = update_entity(businessdb, db=db)
            response = {
                        "success": True,  # Puedes utilizar otro campo si tienes el nombre en la base de datos
                        "message": "negocio actualizado",
                        "entity_id": updated_entity.id
                    }
            
        else:

            
            businessdb = business(name=businessObject.name,
                                address=businessObject.address,
                                telephone=businessObject.telephone,
                                email=businessObject.email,
                                description=businessObject.description,
                                category=businessObject.category,
                                subdomain=website,
                                qrpicture=create_business_qr(website),
                                city = businessObject.city,
                                state = businessObject.state,
                                country = businessObject.country,
                                whatsapp = businessObject.whatsapp,
                                facebook = businessObject.facebook,
                                instagram = businessObject.instagram,
                                users_id=businessObject.users_id)
            db.add(businessdb)
            db.commit()
            response = {    "success": True,  # Puedes utilizar otro campo si tienes el nombre en la base de datos
                            "message": "Negocio creado",
                            "entity_id": businessdb.id
                        }
            
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@router.get("/business_data/")
async def get_business_data(email: str, db = Depends(get_db)):
    try:
        stmt = (
            select(
                business.name,
                business.address,
                business.telephone,
                business.email,
                business.description,
                business.category,
                business.subdomain,
                business.qrpicture,
                business.city,
                business.state,
                business.country,
                business.whatsapp,
                business.facebook,
                business.instagram
            )
            .join(users, users.id == business.users_id)
            .where(users.email == email)
        )
        result = db.execute(stmt)
        business_data = []
        for row in result:
            data_point = {
                "name": row.name,
                "address": row.address,
                "telephone": row.telephone,
                "email": row.email,
                "description": row.description,
                "category": row.category,
                "subdomain": row.subdomain,
                "qrpicture": row.qrpicture,
                "city": row.city,
                "state": row.state,
                "country": row.country,
                "whatsapp": row.whatsapp,
                "facebook": row.facebook,
                "instagram": row.instagram
            }
            business_data.append(data_point)

        return {"user": email, "data": business_data} 

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

# Endpoint para crear una configuración de diseño
@router.post("/save_configuration_designs/")
def save_configuration_designs(request: Request, configurations: DesignsConfigurations, db = Depends(get_db)):
    try:

        configurationdb = db.query(designsconfigurations).filter(designsconfigurations.business_id == configurations.business_id, designsconfigurations.user_id == configurations.user_id).first()
        if configurationdb:
            configurationdb.main_color = configurations.main_color
            configurationdb.secondary_color = configurations.secondary_color
            configurationdb.cover_image_filename = configurations.cover_image_filename
            configurationdb.logo_filename = configurations.logo_filename
            configurationdb.button_name = configurations.button_name
            updated_entity = update_entity(configurationdb, db=db)
            response = {
                        "success": True,  # Puedes utilizar otro campo si tienes el nombre en la base de datos
                        "message": "configuracion actualizada",
                        "entity_id": updated_entity.id
                    }
            
        else:
            configurationsdb = designsconfigurations(business_id= configurations.business_id,
                                user_id=configurations.user_id,
                                main_color=configurations.main_color,
                                secondary_color=configurations.secondary_color,
                                cover_image_filename=configurations.cover_image_filename,
                                logo_filename=configurations.logo_filename,
                                button_name=configurations.button_name)
            db.add(configurationsdb)
            db.commit()
            db.refresh(configurationsdb)
            response = { 
                            "success": True,
                            "message": "configuracion creado",
                            "entity_id": configurationsdb.id
                        }
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@router.get("/configuration_designs_data/")
async def get_designs_data(email: str, db = Depends(get_db)):
    try:
        stmt = (
            select(
                designsconfigurations.main_color,
                designsconfigurations.secondary_color,
                designsconfigurations.cover_image_filename,
                designsconfigurations.logo_filename,
                designsconfigurations.button_name
            )
            .join(users, users.id == designsconfigurations.user_id)
            .join(business, designsconfigurations.business_id == business.id)
            .where(users.email == email)
        )
        result = db.execute(stmt)
        designs_data = []
        for row in result:
            data_point = {
                "main_color": row.main_color,
                "secondary_color": row.secondary_color,
                "cover_image_filename": row.cover_image_filename,
                "logo_filename": row.logo_filename,
                "button_name": row.button_name
            }
            designs_data.append(data_point)

        return {"user": email, "data": designs_data} 

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@router.delete("/rm_family/{familia_id}")
async def remove_family(familia_id: int, db = Depends(get_db)):
    family = db.query(familys).filter(familys.id == familia_id).first()
    if family is None:
        raise HTTPException(status_code=404, detail="La familia no existe")
    response = remove_products_familys(db, familia_id)
    db.delete(family)
    db.commit()
    #db.refresh(familys)
    return {"success": True,  # Puedes utilizar otro campo si tienes el nombre en la base de datos
            "mensaje": response,
            "family_id": family.id
            }
    
@router.delete("/rm_product/{product_id}")
async def remove_family(product_id: int, db = Depends(get_db)):
    productdb = db.query(products).filter(products.id == product_id).first()
    if productdb is None:
        raise HTTPException(status_code=404, detail="el producto no existe")
    response = remove_products(db, product_id)
    return {"success": True,  # Puedes utilizar otro campo si tienes el nombre en la base de datos
            "mensaje": response,
            "family_id": productdb.id
            }

