from schemas import Item, FilterParams, FormData
from fastapi import APIRouter, Query, Form, File, UploadFile, HTTPException, Path
from config import settings
from typing import Annotated
from fastapi.responses import HTMLResponse
from pathlib import Path as FilePath
import uuid

router = APIRouter(
    tags=["Lab1 Misc"],
    prefix=settings.url.lab1a1,
)

# ============================================================================
# ЧАСТЬ А1
# ============================================================================


@router.post("/Body/")
async def create_item(item: Item):
    return item


@router.get("/QueryParamsAndValidation/")
async def read_items_query(q: Annotated[str | None, Query(max_length=50)] = None):
    results = {"items": [{"item_id": "Foo"}, {"item_id": "Bar"}]}
    if q:
        results.update({"q": q})
    return results


@router.get("/PathParamsAndValidation/{item_id}")
async def read_items_path(
    *,
    item_id: Annotated[
        int, Path(description="The ID of the item to get", ge=0, le=1000)
    ],
    q: str,
    size: Annotated[
        float, Query(gt=0, lt=10.5, description="Size must be between 0 and 10.5")
    ],
):
    results = {"item_id": item_id}
    if q:
        results.update({"q": q})
    if size:
        results.update({"size": size})
    return results


@router.get("/QueryParamsModels/")
async def read_items_models(filter_query: Annotated[FilterParams, Query()]):
    return filter_query


@router.put("/NestedModels/{item_id}")
async def update_item(item_id: int, item: Item):
    results = {"item_id": item_id, "item": item}
    return results


@router.post("/RequestForms/")
async def login_form(username: Annotated[str, Form()], password: Annotated[str, Form()]):
    return {"username": username}


@router.post("/RequstFormModels/")
async def login_form_models(data: Annotated[FormData, Form()]):
    return data


# ============================================================================
# ЧАСТЬ А2
# ============================================================================


@router.get("/format-test")
async def get_data_view(format: str = Query("json", pattern="^(json|html)$")):
    data = {"message": "Hello from FastAPI!", "status": "success"}

    if format == "html":
        html_content = f"""
        <html>
            <body>
                <h1>Data Response</h1>
                <p>Message: {data['message']}</p>
                <p>Status: {data['status']}</p>
            </body>
        </html>
        """
        return HTMLResponse(content=html_content)

    return data


# ============================================================================
# ЧАСТЬ А3
# ============================================================================

UPLOAD_DIR = FilePath("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@router.post("/upload-image/")
async def upload_image(file: UploadFile = File(...)):
    if not allowed_file(file.filename or ""):
        raise HTTPException(
            status_code=400, detail="Invalid file format. Allowed: PNG, JPG, JPEG, WEBP"
        )

    # генерация уникального имени
    ext = file.filename.split(".")[-1] if file.filename else "jpg"
    filename = f"{uuid.uuid4()}.{ext}"
    file_path = UPLOAD_DIR / filename

    # сохранение
    with open(file_path, "wb") as f:
        f.write(await file.read())

    file_url = f"/uploads/{filename}"
    return {"url": file_url}
