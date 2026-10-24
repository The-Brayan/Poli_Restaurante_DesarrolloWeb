from sqlalchemy import select
from orm import SesionLocal
from modelos_orm import Cliente


# CREATE - Crear cliente
def crear_cliente(nombre, telefono=None, correo=None):
    with SesionLocal() as sesion:
        cliente = Cliente(
            nombre=nombre,
            telefono=telefono,
            correo=correo
        )
        sesion.add(cliente)
        sesion.commit()
        sesion.refresh(cliente)
        return cliente.id_cliente


# READ - Consultar clientes
def listar_clientes():
    with SesionLocal() as sesion:
        clientes = sesion.scalars(select(Cliente)).all()

        return [
            {
                "id_cliente": c.id_cliente,
                "nombre": c.nombre,
                "telefono": c.telefono,
                "correo": c.correo
            }
            for c in clientes
        ]


# UPDATE - Actualizar cliente
def actualizar_cliente(id_cliente, nombre, telefono=None, correo=None):
    with SesionLocal() as sesion:
        cliente = sesion.get(Cliente, id_cliente)

        if cliente is None:
            return False

        cliente.nombre = nombre
        cliente.telefono = telefono
        cliente.correo = correo

        sesion.commit()
        return True


# DELETE - Eliminar cliente
def eliminar_cliente(id_cliente):
    with SesionLocal() as sesion:
        cliente = sesion.get(Cliente, id_cliente)

        if cliente is None:
            return False

        sesion.delete(cliente)
        sesion.commit()
        return True