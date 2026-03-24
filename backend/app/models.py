from sqlalchemy import String, Integer, Float, Date, DateTime, ForeignKey, UniqueConstraint, func, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .db import Base

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(20), default="viewer")  # admin/editor/viewer
    created_at: Mapped = mapped_column(DateTime(timezone=True), server_default=func.now())

class SalaryTableVersion(Base):
    __tablename__ = "salary_table_versions"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(200))  # e.g., "2026.01 Initial"
    effective_date: Mapped = mapped_column(Date)
    currency: Mapped[str] = mapped_column(String(10), default="PHP")
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped = mapped_column(DateTime(timezone=True), server_default=func.now())
    notes: Mapped[str] = mapped_column(Text, default="")

    rows: Mapped[list["SalaryRow"]] = relationship(back_populates="version", cascade="all, delete-orphan")

class SalaryRow(Base):
    __tablename__ = "salary_rows"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    version_id: Mapped[int] = mapped_column(ForeignKey("salary_table_versions.id"))
    region_code: Mapped[str] = mapped_column(String(30))
    region_name: Mapped[str] = mapped_column(String(200))
    step_no: Mapped[int] = mapped_column(Integer)

    min_daily_wage: Mapped[float] = mapped_column(Float)
    base_monthly_wage: Mapped[float] = mapped_column(Float)
    step_multiplier: Mapped[float] = mapped_column(Float)
    monthly_salary: Mapped[float] = mapped_column(Float)
    semi_month_1: Mapped[float] = mapped_column(Float)
    semi_month_2: Mapped[float] = mapped_column(Float)

    currency: Mapped[str] = mapped_column(String(10))
    effective_date: Mapped = mapped_column(Date)
    notes: Mapped[str] = mapped_column(Text, default="")

    version: Mapped["SalaryTableVersion"] = relationship(back_populates="rows")

    __table_args__ = (
        UniqueConstraint("version_id", "region_code", "step_no", name="uq_version_region_step"),
    )
