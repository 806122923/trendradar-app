"""Product catalog — populated by scraper jobs, read by query path."""
from datetime import datetime

from sqlalchemy import BigInteger, DateTime, Index, Numeric, String, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    platform: Mapped[str] = mapped_column(String(32), index=True)  # 'tiktok_shop_us' etc
    platform_id: Mapped[str] = mapped_column(String(64))
    title: Mapped[str] = mapped_column(String(512))
    category: Mapped[str | None] = mapped_column(String(64), index=True, nullable=True)
    price_usd: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    gmv_14d: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)
    growth_14d: Mapped[float | None] = mapped_column(Numeric(7, 2), nullable=True)  # percent
    raw: Mapped[dict | None] = mapped_column(JSONB, nullable=True)  # original scraped payload
    last_synced_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        UniqueConstraint("platform", "platform_id", name="uq_platform_productid"),
        Index("ix_products_category_growth", "category", "growth_14d"),
    )
