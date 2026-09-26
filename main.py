from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from app import models
from app.database import Base, SessionLocal, engine
from app.routers import auth_router, cases_router, departments_router, users_router
from app.websocket_manager import manager

Base.metadata.create_all(bind=engine)

app = FastAPI(title="СК РП — база дел")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # десктоп-клиент подключается напрямую, браузерный CORS не критичен
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router.router)
app.include_router(departments_router.router)
app.include_router(cases_router.router)
app.include_router(users_router.router)


# ---------- Сидирование отделов и категорий (только если база пустая) ----------

DEPARTMENTS_SEED = [
    ("УПРДЛ", "Управление по расследованию преступлений, совершённых должностными лицами"),
    ("УСБ", "Управление собственной безопасности"),
    ("УПК", "Управление по противодействию коррупции"),
    ("УПОВД", "Управление по преступлениям против общественной безопасности и другим делам"),
    ("ООСБ", "Отдел обеспечения собственной безопасности"),
    ("ФГГС", "Федеральная государственная гражданская служба"),
    ("УК", "Управление кадров"),
    ("РУКОВОДСТВО", "Руководство Центрального аппарата СК"),
]

# Категории для УПРДЛ по данным пользователя. Остальные отделы — добавляются через
# POST /departments/categories (см. README), когда придут детали по каждому отделу.
UPRDL_CATEGORIES = [
    "Дела по госвласти",
    "Экономические преступления",
    "Финансовые махинации",
    "Коррупционные дела",
    "Особо важные дела",
    "Текущие дела",
    "Тяжкие преступления",
    "Преступления против детей",
    "Семейное насилие",
    "Аналитика дел",
]
UPRDL_ARCHIVE_CATEGORY = "Архив дел"


def seed():
    db = SessionLocal()
    try:
        if db.query(models.Department).count() > 0:
            return  # уже засеяно

        code_to_department = {}
        for code, name in DEPARTMENTS_SEED:
            dep = models.Department(code=code, name=name)
            db.add(dep)
            db.flush()
            code_to_department[code] = dep

        uprdl = code_to_department["УПРДЛ"]
        for cat_name in UPRDL_CATEGORIES:
            db.add(models.CaseCategory(department_id=uprdl.id, name=cat_name, is_archive=False))
        db.add(models.CaseCategory(department_id=uprdl.id, name=UPRDL_ARCHIVE_CATEGORY, is_archive=True))

        db.commit()
    finally:
        db.close()


seed()


# ---------- WebSocket: живые уведомления о новых/изменённых делах ----------

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # клиент ничего не обязан присылать — просто держим соединение открытым
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)


@app.get("/")
def root():
    return {"status": "ok", "service": "СК РП — база дел"}
