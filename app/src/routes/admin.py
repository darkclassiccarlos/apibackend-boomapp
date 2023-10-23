# -*- coding: utf-8 -*-
from fastapi import (
    APIRouter,  
    Depends, 
    HTTPException, 
    Request, 
    UploadFile
)
from sqlalchemy import select, join, and_
import os
from dotenv import load_dotenv
from ftplib import FTP
from PIL import Image
from io import BytesIO
import base64

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
    DesignsConfigurations,
    PayloadUploadFile
)
dotenv_path = os.path.join(os.path.dirname(__file__), "../../config/prod.env")
load_dotenv(dotenv_path)

ftp_host =os.getenv("FTP_HOST")
ftp_usuario =os.getenv("FTP_USER")
ftp_contrasena =os.getenv("FTP_PASS")

router = APIRouter(
    prefix="/admin",
    tags=['admin']
)


@router.get("/user_catalog/")
async def get_user_catalog(user_id: int, db = Depends(get_db)):
    # try:
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
        .where(users.id == user_id)
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

    user_data = {"user": user_id, "catalog": list(catalog.values())}

    return user_data
    # except Exception as e:
    #     raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

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
            businessdb.attributes = businessObject.attributes
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
                                attributes=businessObject.attributes,
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
                business.id,
                business.name,
                business.address,
                business.telephone,
                business.attributes,
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
                "business_id": row.id,
                "name": row.name,
                "address": row.address,
                "telephone": row.telephone,
                "attributes": row.attributes,
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
                designsconfigurations.button_name,
                business.id
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
                "button_name": row.button_name,
                "business_id": row.id
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

### Acciones FTP
#subir archivo 
@router.post("/upload_file")
async def upload_file(file: UploadFile, folder: str):
    try:
    # Crear una conexión FTP
        with FTP(ftp_host) as ftp:
            # Iniciar sesión con las credenciales FTP
            ftp.login(user=ftp_usuario, passwd=ftp_contrasena)

            # Verificar si el directorio ya existe
            if folder not in ftp.nlst():
                # Si el directorio no existe, créalo
                ftp.mkd(folder)

            # Cambiar al directorio de destino en el servidor externo
            ftp.cwd(folder)

            # Leer el contenido del archivo en partes pequeñas y cargarlo por FTP
            with file.file as archivo:
                ftp.storbinary(f"STOR {file.filename}", archivo)

        return {"mensaje": f"El archivo '{file.filename}' se ha subido exitosamente al servidor FTP."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al subir el archivo: {str(e)}")


@router.get("/download_file/")
async def download_file(nombre_archivo: str, folder: str):
    try:
        # Crear una conexión FTP
        with FTP(ftp_host) as ftp:
            # Iniciar sesión con las credenciales FTP
            ftp.login(user=ftp_usuario, passwd=ftp_contrasena)

            ftp.cwd(folder)

            # Descargar el archivo desde el servidor FTP
            with open(nombre_archivo, "wb") as archivo_local:
                ftp.retrbinary(f"RETR {nombre_archivo}", archivo_local.write)
            
            # Leer el contenido del archivo descargado
            with open(nombre_archivo, "rb") as archivo_local:
                contenido = archivo_local.read()

        imagen = Image.open(BytesIO(contenido))
        imagen_base64 = base64.b64encode(contenido).decode("utf-8")

        # Eliminar el archivo después de leerlo
        os.remove(nombre_archivo)

        imagen_json = {
            "name": nombre_archivo,
            "type": Image.MIME[imagen.format],
            "data": imagen_base64
        }

        return imagen_json
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al descargar el archivo: {str(e)}")

@router.post("/remove_directory/")
async def remove_directory(nombre_directorio: str):
    try:
        # Crear una conexión FTP
        with FTP(ftp_host) as ftp:
            # Iniciar sesión con las credenciales FTP
            ftp.login(user=ftp_usuario, passwd=ftp_contrasena)

            # Cambiar al directorio que se va a eliminar
            ftp.cwd(nombre_directorio)

            # Listar archivos y subdirectorios en el directorio
            lista_archivos = []
            lista_new = []

            ftp.retrlines("LIST", lista_archivos.append)
            for linea in lista_archivos:
                if not (linea.startswith("d") and (linea.endswith(" .") or linea.endswith(" .."))):
                    # Si la línea no comienza con "d" o no termina con " ." o " ..", la agregamos
                    nombre_item = linea.split()[-1]
                    lista_new.append(nombre_item)                         

            # Eliminar archivos en el directorio
            for nombre_archivo in lista_new:
                ftp.delete(nombre_archivo)

            # Regresar al directorio padre
            ftp.cwd("..")

            # Eliminar el directorio actual
            ftp.rmd(nombre_directorio)

        return {"mensaje": f"Directorio '{nombre_directorio}' y su contenido eliminados exitosamente en el servidor FTP."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al eliminar directorio y su contenido: {str(e)}")


@router.post("/build")
async def build(subdomain: str, db = Depends(get_db)):

    try:
        stmt = (
            select(
                business.users_id,
                business.name,
                business.address,
                business.telephone,
                business.attributes,
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
                business.instagram,
                designsconfigurations.main_color,
                designsconfigurations.secondary_color,
                designsconfigurations.cover_image_filename,
                designsconfigurations.logo_filename,
                designsconfigurations.button_name
            )
            .join(designsconfigurations, and_(business.users_id == designsconfigurations.user_id, business.id == designsconfigurations.business_id))
            .where(business.subdomain == subdomain)
        )
        result = db.execute(stmt)
        
        response_obj = {} 
        for row in result:
            user_id = row.users_id
            data_point = {
                "user_id":row.users_id,
                "name": row.name,
                "address": row.address,
                "telephone": row.telephone,
                "attributes": row.attributes,
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
                "instagram": row.instagram,
                "main_color": row.main_color,
                "secondary_color": row.secondary_color,
                "cover_image_filename": row.cover_image_filename,
                "logo_filename": row.logo_filename,
                "button_name": row.button_name
            }
            response_obj["build"] = data_point

        subquery = (
            db.query(
                familys.user_id,
                products.namefile.label("namefile")
            )
            .select_from(familys)
            .join(familyproducts, familys.id == familyproducts.family_id)
            .join(products, familyproducts.product_id == products.id)
            .filter(and_(familys.user_id == user_id, products.namefile.isnot(None), products.namefile != ''))
            .subquery()
        )

        results = (
            db.query(subquery.c.user_id, subquery.c.namefile)
            .filter(subquery.c.namefile.isnot(None))
            .all()
        )
        response_obj['multimedia'] = []
        for mul in results:
            response_obj['multimedia'].append(mul.namefile)
    
        return {"subdomain": subdomain, "data": response_obj} 

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
