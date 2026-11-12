from datetime import datetime

from sqlalchemy import Integer, String, TIMESTAMP, text
from sqlalchemy.orm import Mapped, mapped_column

from orm import Base


class Cliente(Base):
    __tablename__ = "cliente"

    id_cliente: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )

    nombre: Mapped[str] = mapped_column(String(100), nullable=False)

    telefono: Mapped[str | None] = mapped_column(String(20), nullable=True)

    correo: Mapped[str | None] = mapped_column(String(100), nullable=True)

    fecha_registro: Mapped[datetime | None] = mapped_column(
        TIMESTAMP,
        nullable=True,
        server_default=text("CURRENT_TIMESTAMP")
    )