from fastapi import FastAPI, Depends, UploadFile, File, HTTPException
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import date
import os

from .db import Base, engine, get_db
from .models import User, SalaryTableVersion, SalaryRow
from .auth import verify_password, create_token, require_role, get_current_user
from .excel import build_template, parse_and_validate, export_version_to_excel
from .seed import seed_admin

app = FastAPI(title="Salary Table Tool")

origins = [os.getenv("CORS_ORIGIN", "http://localhost:3000")]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

@app.on_event("startup")
def startup():
    db = next(get_db())
    seed_admin(db)

@app.post("/auth/login")
def login(payload: dict, db: Session = Depends(get_db)):
    email = payload.get("email", "").strip().lower()
    password = payload.get("password", "")
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"token": create_token(user), "role": user.role, "email": user.email}

@app.get("/template/salary-table.xlsx")
def download_template(user=Depends(require_role("admin","editor","viewer"))):
    xlsx = build_template()
    return Response(
        content=xlsx,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=Salary_Table_Template.xlsx"}
    )

@app.post("/tables/upload")
def upload_table(
    name: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user=Depends(require_role("admin","editor"))
):
    content = file.file.read()
    try:
        meta, rows = parse_and_validate(content)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    if not meta["effective_date"]:
        raise HTTPException(status_code=400, detail="Effective_Date missing")

    version = SalaryTableVersion(
        name=name,
        effective_date=meta["effective_date"],
        currency=meta["currency"],
        created_by=user.id,
        notes=""
    )
    db.add(version)
    db.flush()  # get version.id

    for r in rows:
        row = SalaryRow(
            version_id=version.id,
            region_code=r["Region_Code"],
            region_name=r["Region_Name"],
            step_no=r["Step_No"],
            min_daily_wage=r["Min_Daily_Wage"],
            base_monthly_wage=r["Base_Monthly_Wage"],
            step_multiplier=r["Step_Multiplier"],
            monthly_salary=r["Monthly_Salary"],
            semi_month_1=r["Semi_Month_1"],
            semi_month_2=r["Semi_Month_2"],
            currency=r["Currency"],
            effective_date=r["Effective_Date"],
            notes=r["Notes"] or ""
        )
        db.add(row)

    db.commit()
    return {"version_id": version.id, "rows": len(rows), "effective_date": version.effective_date.isoformat()}

@app.get("/tables")
def list_versions(db: Session = Depends(get_db), user=Depends(require_role("admin","editor","viewer"))):
    versions = db.query(SalaryTableVersion).order_by(SalaryTableVersion.created_at.desc()).all()
    return [{
        "id": v.id,
        "name": v.name,
        "effective_date": v.effective_date.isoformat(),
        "currency": v.currency,
        "created_at": v.created_at.isoformat(),
        "created_by": v.created_by
    } for v in versions]

@app.get("/tables/{version_id}/export.xlsx")
def export_version(version_id: int, db: Session = Depends(get_db), user=Depends(require_role("admin","editor","viewer"))):
    v = db.query(SalaryTableVersion).get(version_id)
    if not v:
        raise HTTPException(status_code=404, detail="Version not found")
    rs = db.query(SalaryRow).filter(SalaryRow.version_id == version_id).order_by(SalaryRow.region_code, SalaryRow.step_no).all()

    rows = [{
        "region_code": r.region_code,
        "region_name": r.region_name,
        "step_no": r.step_no,
        "min_daily_wage": r.min_daily_wage,
        "base_monthly_wage": r.base_monthly_wage,
        "step_multiplier": r.step_multiplier,
        "monthly_salary": r.monthly_salary,
        "semi_month_1": r.semi_month_1,
        "semi_month_2": r.semi_month_2,
        "currency": r.currency,
        "effective_date": r.effective_date,
        "notes": r.notes,
    } for r in rs]

    xlsx = export_version_to_excel(v.name, rows)
    fname = f"Salary_Table_{v.effective_date.isoformat()}_{v.id}.xlsx"
    return Response(
        content=xlsx,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={fname}"}
    )
