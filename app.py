
from flask import Flask, render_template, request, redirect, url_for, jsonify
from conexion import obtener_conexion
from decimal import Decimal, InvalidOperation
from decimal import Decimal, InvalidOperation

app = Flask(__name__)

@app.route("/")
def inicio():
    conexion = obtener_conexion()

    if conexion:
        conexion.close()
        return render_template("index.html")

    return "Error: No se pudo conectar con MySQL", 500


@app.route("/clientes")
def listar_clientes():
    conexion = obtener_conexion()

    if conexion:
        cursor = conexion.cursor(dictionary=True)

        try:
            cursor.execute("SELECT * FROM cliente")
            clientes = cursor.fetchall()
        finally:
            cursor.close()
            conexion.close()

        return render_template("clientes.html", clientes=clientes)

    return "Error al conectar con MySQL", 500


@app.route("/clientes/agregar", methods=["GET", "POST"])
def agregar_cliente():
    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        telefono = request.form.get("telefono", "").strip()
        correo = request.form.get("correo", "").strip()

        if not nombre:
            return "El nombre es obligatorio", 400

        conexion = obtener_conexion()

        if not conexion:
            return "Error al conectar con MySQL", 500

        cursor = conexion.cursor()

        try:
            sql = """
                INSERT INTO cliente (nombre, telefono, correo)
                VALUES (%s, %s, %s)
            """
            cursor.execute(sql, (nombre, telefono, correo))
            conexion.commit()
        except Exception:
            conexion.rollback()
            app.logger.exception("Error al guardar cliente")
            return "Error al guardar el cliente", 500
        finally:
            cursor.close()
            conexion.close()

        return redirect(url_for("listar_clientes"))

    return render_template("agregar_cliente.html")



@app.route("/clientes/editar/<int:id_cliente>", methods=["GET", "POST"])
def editar_cliente(id_cliente):
    conexion = obtener_conexion()

    if not conexion:
        return "Error al conectar con MySQL", 500

    cursor = conexion.cursor(dictionary=True)

    try:
        if request.method == "POST":
            nombre = request.form.get("nombre", "").strip()
            telefono = request.form.get("telefono", "").strip()
            correo = request.form.get("correo", "").strip()

            if not nombre:
                return "El nombre es obligatorio", 400

            sql = """
                UPDATE cliente
                SET nombre = %s, telefono = %s, correo = %s
                WHERE id_cliente = %s
            """

            cursor.execute(
                sql, (nombre, telefono, correo, id_cliente)
            )
            conexion.commit()

            return redirect(url_for("listar_clientes"))

        cursor.execute(
            "SELECT * FROM cliente WHERE id_cliente = %s",
            (id_cliente,)
        )

        cliente = cursor.fetchone()

        if not cliente:
            return "Cliente no encontrado", 404

        return render_template(
            "editar_cliente.html", cliente=cliente
        )

    except Exception:
        conexion.rollback()
        app.logger.exception("Error al editar cliente")
        return "Error al editar el cliente", 500

    finally:
        cursor.close()
        conexion.close()



@app.route("/clientes/eliminar/<int:id_cliente>", methods=["POST"])
def eliminar_cliente(id_cliente):
    conexion = obtener_conexion()

    if not conexion:
        return "Error al conectar con MySQL", 500

    cursor = conexion.cursor()

    try:
        cursor.execute(
            "DELETE FROM cliente WHERE id_cliente = %s",
            (id_cliente,)
        )
        conexion.commit()

        return redirect(url_for("listar_clientes"))

    except Exception:
        conexion.rollback()
        app.logger.exception("Error al eliminar cliente")
        return "No se pudo eliminar el cliente", 500

    finally:
        cursor.close()
        conexion.close()



@app.route("/reservas")
def listar_reservas():
    conexion = obtener_conexion()

    if not conexion:
        return "Error al conectar con MySQL", 500

    cursor = conexion.cursor(dictionary=True)

    try:
        sql = """
            SELECT
                r.id_reserva,
                c.nombre AS cliente,
                m.numero AS mesa,
                r.fecha_reserva,
                r.cantidad_personas,
                r.estado
            FROM reserva r
            INNER JOIN cliente c
                ON r.id_cliente = c.id_cliente
            INNER JOIN mesa m
                ON r.id_mesa = m.id_mesa
            ORDER BY r.fecha_reserva DESC
        """

        cursor.execute(sql)
        reservas = cursor.fetchall()

        return render_template(
            "reservas.html",
            reservas=reservas
        )

    except Exception:
        app.logger.exception("Error al consultar reservas")
        return "Error al consultar reservas", 500

    finally:
        cursor.close()
        conexion.close()



@app.route("/reservas/agregar", methods=["GET", "POST"])
def agregar_reserva():
    conexion = obtener_conexion()

    if not conexion:
        return "Error al conectar con MySQL", 500

    cursor = conexion.cursor(dictionary=True)

    try:
        if request.method == "POST":
            id_cliente = request.form.get("id_cliente")
            id_mesa = request.form.get("id_mesa")
            fecha_reserva = request.form.get("fecha_reserva")
            cantidad_personas = request.form.get(
                "cantidad_personas", type=int
            )

            if not all([id_cliente, id_mesa, fecha_reserva]):
                return "Todos los campos son obligatorios", 400

            if cantidad_personas is None or cantidad_personas < 1:
                return "La cantidad de personas debe ser mayor a cero", 400

            sql = """
                INSERT INTO reserva
                (id_cliente, id_mesa, fecha_reserva,
                 cantidad_personas, estado)
                VALUES (%s, %s, %s, %s, %s)
            """

            cursor.execute(sql, (
                id_cliente,
                id_mesa,
                fecha_reserva,
                cantidad_personas,
                "Pendiente"
            ))

            conexion.commit()

            return redirect(url_for("listar_reservas"))

        cursor.execute(
            "SELECT id_cliente, nombre FROM cliente ORDER BY nombre"
        )
        clientes = cursor.fetchall()

        cursor.execute(
            "SELECT id_mesa, numero FROM mesa ORDER BY numero"
        )
        mesas = cursor.fetchall()

        return render_template(
            "agregar_reserva.html",
            clientes=clientes,
            mesas=mesas
        )

    except Exception:
        conexion.rollback()
        app.logger.exception("Error al registrar reserva")
        return "Error al registrar la reserva", 500

    finally:
        cursor.close()
        conexion.close()



@app.route("/reservas/editar/<int:id_reserva>", methods=["GET", "POST"])
def editar_reserva(id_reserva):
    conexion = obtener_conexion()

    if not conexion:
        return "Error al conectar con MySQL", 500

    cursor = conexion.cursor(dictionary=True)

    try:
        if request.method == "POST":
            id_cliente = request.form.get("id_cliente", type=int)
            id_mesa = request.form.get("id_mesa", type=int)
            fecha_reserva = request.form.get("fecha_reserva")
            cantidad_personas = request.form.get(
                "cantidad_personas", type=int
            )
            estado = request.form.get("estado")

            if not all([id_cliente, id_mesa, fecha_reserva]):
                return "Faltan campos obligatorios", 400

            if cantidad_personas is None or cantidad_personas < 1:
                return "Cantidad de personas inválida", 400

            if estado not in ["Pendiente", "Confirmada", "Cancelada"]:
                return "Estado inválido", 400

            sql = """
                UPDATE reserva
                SET id_cliente = %s,
                    id_mesa = %s,
                    fecha_reserva = %s,
                    cantidad_personas = %s,
                    estado = %s
                WHERE id_reserva = %s
            """

            cursor.execute(sql, (
                id_cliente,
                id_mesa,
                fecha_reserva,
                cantidad_personas,
                estado,
                id_reserva
            ))

            conexion.commit()
            return redirect(url_for("listar_reservas"))

        cursor.execute(
            "SELECT * FROM reserva WHERE id_reserva = %s",
            (id_reserva,)
        )
        reserva = cursor.fetchone()

        if not reserva:
            return "Reserva no encontrada", 404

        cursor.execute(
            "SELECT id_cliente, nombre FROM cliente ORDER BY nombre"
        )
        clientes = cursor.fetchall()

        cursor.execute(
            "SELECT id_mesa, numero FROM mesa ORDER BY numero"
        )
        mesas = cursor.fetchall()

        return render_template(
            "editar_reserva.html",
            reserva=reserva,
            clientes=clientes,
            mesas=mesas
        )

    except Exception:
        conexion.rollback()
        app.logger.exception("Error al editar reserva")
        return "Error al editar la reserva", 500

    finally:
        cursor.close()
        conexion.close()



@app.route("/reservas/eliminar/<int:id_reserva>", methods=["POST"])
def eliminar_reserva(id_reserva):
    conexion = obtener_conexion()

    if not conexion:
        return "Error al conectar con MySQL", 500

    cursor = conexion.cursor()

    try:
        cursor.execute(
            "DELETE FROM reserva WHERE id_reserva = %s",
            (id_reserva,)
        )

        conexion.commit()

        return redirect(url_for("listar_reservas"))

    except Exception:
        conexion.rollback()
        app.logger.exception("Error al eliminar reserva")
        return "Error al eliminar la reserva", 500

    finally:
        cursor.close()
        conexion.close()



@app.route("/inventario")
def listar_inventario():
    conexion = obtener_conexion()

    if not conexion:
        return "Error al conectar con MySQL", 500

    cursor = conexion.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT
                id_inventario,
                nombre_insumo,
                cantidad,
                unidad_medida,
                stock_minimo,
                fecha_actualizacion
            FROM inventario
            ORDER BY id_inventario DESC
        """)

        inventario = cursor.fetchall()

        return render_template(
            "inventario.html",
            inventario=inventario
        )

    except Exception:
        app.logger.exception("Error al consultar inventario")
        return "Error al consultar inventario", 500

    finally:
        cursor.close()
        conexion.close()



@app.route("/inventario/agregar", methods=["GET", "POST"])
def agregar_insumo():
    if request.method == "POST":
        nombre_insumo = request.form.get("nombre_insumo", "").strip()
        unidad_medida = request.form.get("unidad_medida", "").strip()

        try:
            cantidad = float(request.form.get("cantidad", ""))
            stock_minimo = float(request.form.get("stock_minimo", ""))
        except (ValueError, TypeError):
            return "Las cantidades deben ser números válidos", 400

        if not nombre_insumo or not unidad_medida:
            return "El nombre y la unidad son obligatorios", 400

        if cantidad < 0 or stock_minimo < 0:
            return "Las cantidades no pueden ser negativas", 400

        conexion = obtener_conexion()

        if not conexion:
            return "Error al conectar con MySQL", 500

        cursor = conexion.cursor()

        try:
            sql = """
                INSERT INTO inventario
                (nombre_insumo, cantidad, unidad_medida, stock_minimo)
                VALUES (%s, %s, %s, %s)
            """

            cursor.execute(sql, (
                nombre_insumo,
                cantidad,
                unidad_medida,
                stock_minimo
            ))

            conexion.commit()

            return redirect(url_for("listar_inventario"))

        except Exception:
            conexion.rollback()
            app.logger.exception("Error al agregar insumo")
            return "Error al registrar el insumo", 500

        finally:
            cursor.close()
            conexion.close()

    return render_template("agregar_insumo.html")



@app.route("/inventario/editar/<int:id_inventario>", methods=["GET", "POST"])
def editar_insumo(id_inventario):
    conexion = obtener_conexion()

    if not conexion:
        return "Error al conectar con MySQL", 500

    cursor = conexion.cursor(dictionary=True)

    try:
        if request.method == "POST":
            nombre_insumo = request.form.get(
                "nombre_insumo", ""
            ).strip()

            unidad_medida = request.form.get(
                "unidad_medida", ""
            ).strip()

            try:
                cantidad = float(request.form.get("cantidad", ""))
                stock_minimo = float(
                    request.form.get("stock_minimo", "")
                )
            except (ValueError, TypeError):
                return "Las cantidades deben ser números válidos", 400

            if not nombre_insumo or not unidad_medida:
                return "El nombre y la unidad son obligatorios", 400

            if cantidad < 0 or stock_minimo < 0:
                return "Las cantidades no pueden ser negativas", 400

            sql = """
                UPDATE inventario
                SET nombre_insumo = %s,
                    cantidad = %s,
                    unidad_medida = %s,
                    stock_minimo = %s
                WHERE id_inventario = %s
            """

            cursor.execute(sql, (
                nombre_insumo,
                cantidad,
                unidad_medida,
                stock_minimo,
                id_inventario
            ))

            conexion.commit()

            return redirect(url_for("listar_inventario"))

        cursor.execute(
            "SELECT * FROM inventario WHERE id_inventario = %s",
            (id_inventario,)
        )

        insumo = cursor.fetchone()

        if not insumo:
            return "Insumo no encontrado", 404

        return render_template(
            "editar_insumo.html",
            insumo=insumo
        )

    except Exception:
        conexion.rollback()
        app.logger.exception("Error al editar insumo")
        return "Error al editar el insumo", 500

    finally:
        cursor.close()
        conexion.close()



@app.route("/inventario/eliminar/<int:id_inventario>", methods=["POST"])
def eliminar_insumo(id_inventario):
    conexion = obtener_conexion()

    if not conexion:
        return "Error al conectar con MySQL", 500

    cursor = conexion.cursor()

    try:
        cursor.execute(
            "DELETE FROM inventario WHERE id_inventario = %s",
            (id_inventario,)
        )

        if cursor.rowcount == 0:
            conexion.rollback()
            return "Insumo no encontrado", 404

        conexion.commit()

        return redirect(url_for("listar_inventario"))

    except Exception:
        conexion.rollback()
        app.logger.exception("Error al eliminar insumo")
        return "No se pudo eliminar el insumo", 500

    finally:
        cursor.close()
        conexion.close()



@app.route("/movimientos")
def listar_movimientos():
    conexion = obtener_conexion()

    if not conexion:
        return "Error al conectar con MySQL", 500

    cursor = conexion.cursor(dictionary=True)

    try:
        sql = """
            SELECT
                m.id_movimiento,
                m.id_inventario,
                i.nombre_insumo,
                m.tipo_movimiento,
                m.cantidad,
                m.motivo,
                m.fecha_movimiento
            FROM movimiento_inventario AS m
            INNER JOIN inventario AS i
                ON m.id_inventario = i.id_inventario
            ORDER BY m.id_movimiento DESC
        """

        cursor.execute(sql)
        movimientos = cursor.fetchall()

        return render_template(
            "movimientos.html",
            movimientos=movimientos
        )

    except Exception:
        app.logger.exception(
            "Error al consultar movimientos de inventario"
        )
        return "Error al consultar movimientos", 500

    finally:
        cursor.close()
        conexion.close()



@app.route("/movimientos/agregar", methods=["GET", "POST"])
def agregar_movimiento():
    conexion = obtener_conexion()

    if not conexion:
        return "Error al conectar con MySQL", 500

    cursor = conexion.cursor(dictionary=True)

    try:
        if request.method == "POST":
            try:
                id_inventario = int(
                    request.form.get("id_inventario", "")
                )
                cantidad = Decimal(
                    request.form.get("cantidad", "")
                )
            except (ValueError, TypeError, InvalidOperation):
                return "Datos numéricos inválidos", 400

            tipo = request.form.get("tipo_movimiento", "")
            motivo = request.form.get("motivo", "").strip()

            if tipo not in ("Entrada", "Salida"):
                return "Tipo de movimiento inválido", 400

            if not cantidad.is_finite() or cantidad <= 0:
                return "La cantidad debe ser mayor que cero", 400

            if cantidad.as_tuple().exponent < -2:
                return "Máximo dos decimales permitidos", 400

            if len(motivo) > 255:
                return "El motivo es demasiado largo", 400

            # Bloqueamos el insumo mientras actualizamos su stock.
            cursor.execute("""
                SELECT cantidad
                FROM inventario
                WHERE id_inventario = %s
                FOR UPDATE
            """, (id_inventario,))

            insumo = cursor.fetchone()

            if not insumo:
                conexion.rollback()
                return "Insumo no encontrado", 404

            stock_actual = Decimal(str(insumo["cantidad"]))

            if tipo == "Entrada":
                nuevo_stock = stock_actual + cantidad
            else:
                nuevo_stock = stock_actual - cantidad

            if nuevo_stock < 0:
                conexion.rollback()
                return "No hay suficiente stock disponible", 400

            if nuevo_stock > Decimal("99999999.99"):
                conexion.rollback()
                return "La cantidad supera el límite permitido", 400

            cursor.execute("""
                INSERT INTO movimiento_inventario
                (id_inventario, tipo_movimiento, cantidad, motivo)
                VALUES (%s, %s, %s, %s)
            """, (id_inventario, tipo, cantidad, motivo))

            cursor.execute("""
                UPDATE inventario
                SET cantidad = %s
                WHERE id_inventario = %s
            """, (nuevo_stock, id_inventario))

            conexion.commit()

            return redirect(url_for("listar_movimientos"))

        cursor.execute("""
            SELECT id_inventario, nombre_insumo, cantidad,
                   unidad_medida
            FROM inventario
            ORDER BY nombre_insumo
        """)

        insumos = cursor.fetchall()

        return render_template(
            "agregar_movimiento.html",
            insumos=insumos
        )

    except Exception:
        conexion.rollback()
        app.logger.exception("Error al registrar movimiento")
        return "Error al registrar movimiento", 500

    finally:
        cursor.close()
        conexion.close()



@app.route("/movimientos/editar/<int:id_movimiento>", methods=["GET", "POST"])
def editar_movimiento(id_movimiento):
    conexion = obtener_conexion()

    if not conexion:
        return "Error al conectar con MySQL", 500

    cursor = conexion.cursor(dictionary=True)

    try:
        # Bloqueamos el inventario durante la modificación.
        cursor.execute("""
            SELECT id_inventario, cantidad
            FROM inventario
            ORDER BY id_inventario
            FOR UPDATE
        """)
        insumos = cursor.fetchall()

        cursor.execute("""
            SELECT *
            FROM movimiento_inventario
            WHERE id_movimiento = %s
            FOR UPDATE
        """, (id_movimiento,))
        movimiento = cursor.fetchone()

        if not movimiento:
            conexion.rollback()
            return "Movimiento no encontrado", 404

        if request.method == "GET":
            conexion.commit()
            return render_template(
                "editar_movimiento.html",
                movimiento=movimiento,
                insumos=insumos
            )

        try:
            nuevo_id = int(request.form.get("id_inventario", ""))
            nueva_cantidad = Decimal(
                request.form.get("cantidad", "")
            )
        except (ValueError, TypeError, InvalidOperation):
            conexion.rollback()
            return "Datos numéricos inválidos", 400

        nuevo_tipo = request.form.get("tipo_movimiento", "")
        nuevo_motivo = request.form.get("motivo", "").strip()

        if nuevo_tipo not in ("Entrada", "Salida"):
            conexion.rollback()
            return "Tipo de movimiento inválido", 400

        if (not nueva_cantidad.is_finite()
                or nueva_cantidad <= 0
                or nueva_cantidad.as_tuple().exponent < -2):
            conexion.rollback()
            return "Cantidad inválida", 400

        if len(nuevo_motivo) > 255:
            conexion.rollback()
            return "Motivo demasiado largo", 400

        stocks = {
            item["id_inventario"]: Decimal(str(item["cantidad"]))
            for item in insumos
        }

        if nuevo_id not in stocks:
            conexion.rollback()
            return "Insumo no encontrado", 404

        anterior_id = movimiento["id_inventario"]
        anterior_cantidad = Decimal(str(movimiento["cantidad"]))
        anterior_tipo = movimiento["tipo_movimiento"]

        # Revertimos el efecto del movimiento anterior.
        if anterior_tipo == "Entrada":
            stocks[anterior_id] -= anterior_cantidad
        else:
            stocks[anterior_id] += anterior_cantidad

        # Aplicamos el efecto del movimiento editado.
        if nuevo_tipo == "Entrada":
            stocks[nuevo_id] += nueva_cantidad
        else:
            stocks[nuevo_id] -= nueva_cantidad

        if any(stock < 0 for stock in stocks.values()):
            conexion.rollback()
            return "La edición dejaría un stock negativo", 400

        if any(stock > Decimal("99999999.99")
               for stock in stocks.values()):
            conexion.rollback()
            return "Stock fuera del límite permitido", 400

        cursor.execute("""
            UPDATE movimiento_inventario
            SET id_inventario = %s,
                tipo_movimiento = %s,
                cantidad = %s,
                motivo = %s
            WHERE id_movimiento = %s
        """, (
            nuevo_id,
            nuevo_tipo,
            nueva_cantidad,
            nuevo_motivo,
            id_movimiento
        ))

        for id_insumo in {anterior_id, nuevo_id}:
            cursor.execute("""
                UPDATE inventario
                SET cantidad = %s
                WHERE id_inventario = %s
            """, (stocks[id_insumo], id_insumo))

        conexion.commit()

        return redirect(url_for("listar_movimientos"))

    except Exception:
        conexion.rollback()
        app.logger.exception("Error al editar movimiento")
        return "Error al editar movimiento", 500

    finally:
        cursor.close()
        conexion.close()



@app.route("/movimientos/eliminar/<int:id_movimiento>", methods=["POST"])
def eliminar_movimiento(id_movimiento):
    conexion = obtener_conexion()

    if not conexion:
        return "Error al conectar con MySQL", 500

    cursor = conexion.cursor(dictionary=True)

    try:
        # Bloquear inventario para evitar cambios simultáneos.
        cursor.execute("""
            SELECT id_inventario, cantidad
            FROM inventario
            ORDER BY id_inventario
            FOR UPDATE
        """)

        insumos = cursor.fetchall()

        cursor.execute("""
            SELECT *
            FROM movimiento_inventario
            WHERE id_movimiento = %s
            FOR UPDATE
        """, (id_movimiento,))

        movimiento = cursor.fetchone()

        if not movimiento:
            conexion.rollback()
            return "Movimiento no encontrado", 404

        id_inventario = movimiento["id_inventario"]

        insumo = next(
            (item for item in insumos
             if item["id_inventario"] == id_inventario),
            None
        )

        if not insumo:
            conexion.rollback()
            return "Insumo no encontrado", 404

        stock_actual = Decimal(str(insumo["cantidad"]))
        cantidad = Decimal(str(movimiento["cantidad"]))

        # Revertir el efecto del movimiento eliminado.
        if movimiento["tipo_movimiento"] == "Entrada":
            nuevo_stock = stock_actual - cantidad
        else:
            nuevo_stock = stock_actual + cantidad

        if nuevo_stock < 0:
            conexion.rollback()
            return (
                "No se puede eliminar: el stock quedaría negativo",
                400
            )

        if nuevo_stock > Decimal("99999999.99"):
            conexion.rollback()
            return "El stock supera el límite permitido", 400

        cursor.execute("""
            DELETE FROM movimiento_inventario
            WHERE id_movimiento = %s
        """, (id_movimiento,))

        cursor.execute("""
            UPDATE inventario
            SET cantidad = %s
            WHERE id_inventario = %s
        """, (nuevo_stock, id_inventario))

        conexion.commit()

        return redirect(url_for("listar_movimientos"))

    except Exception:
        conexion.rollback()
        app.logger.exception("Error al eliminar movimiento")
        return "Error al eliminar movimiento", 500

    finally:
        cursor.close()
        conexion.close()



@app.route("/mesas")
def listar_mesas():
    conexion = obtener_conexion()

    if not conexion:
        return "Error al conectar con MySQL", 500

    cursor = conexion.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT id_mesa, numero, estado
            FROM mesa
            ORDER BY numero ASC
        """)

        mesas = cursor.fetchall()

        return render_template(
            "mesas.html",
            mesas=mesas
        )

    except Exception:
        app.logger.exception("Error al consultar mesas")
        return "Error al consultar las mesas", 500

    finally:
        cursor.close()
        conexion.close()



@app.route("/mesas/agregar", methods=["GET", "POST"])
def agregar_mesa():
    if request.method == "POST":
        try:
            numero = int(request.form.get("numero", ""))
        except (ValueError, TypeError):
            return "El número de mesa debe ser válido", 400

        estado = request.form.get("estado", "Libre").strip()

        if numero <= 0:
            return "El número de mesa debe ser mayor que cero", 400

        if estado not in ("Libre", "Ocupada", "Reservada"):
            return "Estado de mesa no válido", 400

        conexion = obtener_conexion()

        if not conexion:
            return "Error al conectar con MySQL", 500

        cursor = conexion.cursor()

        try:
            # Evitar números de mesa duplicados.
            cursor.execute(
                "SELECT id_mesa FROM mesa WHERE numero = %s",
                (numero,)
            )

            if cursor.fetchone():
                return "Ya existe una mesa con ese número", 400

            cursor.execute("""
                INSERT INTO mesa (numero, estado)
                VALUES (%s, %s)
            """, (numero, estado))

            conexion.commit()

            return redirect(url_for("listar_mesas"))

        except Exception:
            conexion.rollback()
            app.logger.exception("Error al agregar mesa")
            return "Error al registrar la mesa", 500

        finally:
            cursor.close()
            conexion.close()

    return render_template("agregar_mesa.html")



@app.route("/mesas/editar/<int:id_mesa>", methods=["GET", "POST"])
def editar_mesa(id_mesa):
    conexion = obtener_conexion()

    if not conexion:
        return "Error al conectar con MySQL", 500

    cursor = conexion.cursor(dictionary=True)

    try:
        # Buscar la mesa que queremos editar.
        cursor.execute("""
            SELECT id_mesa, numero, estado
            FROM mesa
            WHERE id_mesa = %s
        """, (id_mesa,))

        mesa = cursor.fetchone()

        if not mesa:
            return "Mesa no encontrada", 404

        if request.method == "POST":
            try:
                numero = int(request.form.get("numero", ""))
            except (ValueError, TypeError):
                return "El número de mesa debe ser válido", 400

            estado = request.form.get("estado", "").strip()

            if numero <= 0:
                return "El número de mesa debe ser mayor que cero", 400

            if estado not in ("Libre", "Ocupada", "Reservada"):
                return "Estado de mesa no válido", 400

            # Verificar que el número no pertenezca a otra mesa.
            cursor.execute("""
                SELECT id_mesa
                FROM mesa
                WHERE numero = %s AND id_mesa != %s
            """, (numero, id_mesa))

            if cursor.fetchone():
                return "Ya existe otra mesa con ese número", 400

            cursor.execute("""
                UPDATE mesa
                SET numero = %s, estado = %s
                WHERE id_mesa = %s
            """, (numero, estado, id_mesa))

            conexion.commit()

            return redirect(url_for("listar_mesas"))

        return render_template("editar_mesa.html", mesa=mesa)

    except Exception:
        conexion.rollback()
        app.logger.exception("Error al editar mesa")
        return "Error al actualizar la mesa", 500

    finally:
        cursor.close()
        conexion.close()



@app.route("/mesas/eliminar/<int:id_mesa>", methods=["POST"])
def eliminar_mesa(id_mesa):
    conexion = obtener_conexion()

    if not conexion:
        return "Error al conectar con MySQL", 500

    cursor = conexion.cursor(dictionary=True)

    try:
        # Comprobar que la mesa existe.
        cursor.execute("""
            SELECT id_mesa, numero
            FROM mesa
            WHERE id_mesa = %s
        """, (id_mesa,))

        mesa = cursor.fetchone()

        if not mesa:
            return "Mesa no encontrada", 404

        # Comprobar si tiene reservas asociadas.
        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM reserva
            WHERE id_mesa = %s
        """, (id_mesa,))

        resultado = cursor.fetchone()

        if resultado["total"] > 0:
            return (
                "No se puede eliminar esta mesa porque "
                "tiene reservas asociadas.",
                400
            )

        # Eliminar la mesa.
        cursor.execute("""
            DELETE FROM mesa
            WHERE id_mesa = %s
        """, (id_mesa,))

        conexion.commit()

        return redirect(url_for("listar_mesas"))

    except Exception:
        conexion.rollback()
        app.logger.exception("Error al eliminar mesa")
        return "Error al eliminar la mesa", 500

    finally:
        cursor.close()
        conexion.close()


# ==========================================
# API REST - CLIENTES
# ==========================================

@app.route("/api/clientes", methods=["GET"])
def api_listar_clientes():
    conexion = obtener_conexion()

    if not conexion:
        return jsonify({
            "error": "No se pudo conectar con MySQL"
        }), 500

    cursor = conexion.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT id_cliente, nombre, telefono, correo
            FROM cliente
            ORDER BY id_cliente ASC
        """)

        clientes = cursor.fetchall()

        return jsonify(clientes), 200

    except Exception:
        app.logger.exception("Error en API de clientes")

        return jsonify({
            "error": "No se pudieron consultar los clientes"
        }), 500

    finally:
        cursor.close()
        conexion.close()



@app.route("/api/clientes", methods=["POST"])
def api_agregar_cliente():
    datos = request.get_json(silent=True)

    if not isinstance(datos, dict):
        return jsonify({
            "error": "Debes enviar un objeto JSON válido"
        }), 400

    nombre = str(datos.get("nombre") or "").strip()
    telefono = str(datos.get("telefono") or "").strip()
    correo = str(datos.get("correo") or "").strip()

    if not nombre:
        return jsonify({
            "error": "El nombre es obligatorio"
        }), 400

    conexion = obtener_conexion()

    if not conexion:
        return jsonify({
            "error": "No se pudo conectar con MySQL"
        }), 500

    cursor = conexion.cursor()

    try:
        cursor.execute("""
            INSERT INTO cliente (nombre, telefono, correo)
            VALUES (%s, %s, %s)
        """, (nombre, telefono, correo))

        conexion.commit()
        id_cliente = cursor.lastrowid

        return jsonify({
            "mensaje": "Cliente registrado correctamente",
            "cliente": {
                "id_cliente": id_cliente,
                "nombre": nombre,
                "telefono": telefono,
                "correo": correo
            }
        }), 201

    except Exception:
        conexion.rollback()
        app.logger.exception("Error al registrar cliente desde la API")

        return jsonify({
            "error": "No se pudo registrar el cliente"
        }), 500

    finally:
        cursor.close()
        conexion.close()



@app.route("/api/clientes/<int:id_cliente>", methods=["PUT"])
def api_editar_cliente(id_cliente):
    datos = request.get_json(silent=True)

    if not isinstance(datos, dict):
        return jsonify({
            "error": "Debes enviar un objeto JSON válido"
        }), 400

    nombre = str(datos.get("nombre") or "").strip()
    telefono = str(datos.get("telefono") or "").strip()
    correo = str(datos.get("correo") or "").strip()

    if not nombre:
        return jsonify({
            "error": "El nombre es obligatorio"
        }), 400

    conexion = obtener_conexion()

    if not conexion:
        return jsonify({
            "error": "No se pudo conectar con MySQL"
        }), 500

    cursor = conexion.cursor(dictionary=True)

    try:
        # Comprobar que el cliente existe.
        cursor.execute("""
            SELECT id_cliente
            FROM cliente
            WHERE id_cliente = %s
        """, (id_cliente,))

        if not cursor.fetchone():
            return jsonify({
                "error": "Cliente no encontrado"
            }), 404

        # Actualizar los datos del cliente.
        cursor.execute("""
            UPDATE cliente
            SET nombre = %s,
                telefono = %s,
                correo = %s
            WHERE id_cliente = %s
        """, (nombre, telefono, correo, id_cliente))

        conexion.commit()

        return jsonify({
            "mensaje": "Cliente actualizado correctamente",
            "cliente": {
                "id_cliente": id_cliente,
                "nombre": nombre,
                "telefono": telefono,
                "correo": correo
            }
        }), 200

    except Exception:
        conexion.rollback()
        app.logger.exception("Error al actualizar cliente desde la API")

        return jsonify({
            "error": "No se pudo actualizar el cliente"
        }), 500

    finally:
        cursor.close()
        conexion.close()



@app.route("/api/clientes/<int:id_cliente>", methods=["DELETE"])
def api_eliminar_cliente(id_cliente):
    conexion = obtener_conexion()

    if not conexion:
        return jsonify({
            "error": "No se pudo conectar con MySQL"
        }), 500

    cursor = conexion.cursor(dictionary=True)

    try:
        # Comprobar si el cliente existe.
        cursor.execute("""
            SELECT id_cliente, nombre
            FROM cliente
            WHERE id_cliente = %s
        """, (id_cliente,))

        cliente = cursor.fetchone()

        if not cliente:
            return jsonify({
                "error": "Cliente no encontrado"
            }), 404

        # Evitar eliminar clientes con reservas asociadas.
        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM reserva
            WHERE id_cliente = %s
        """, (id_cliente,))

        resultado = cursor.fetchone()

        if resultado["total"] > 0:
            return jsonify({
                "error": "No se puede eliminar el cliente porque tiene reservas asociadas"
            }), 409

        # Eliminar el cliente.
        cursor.execute("""
            DELETE FROM cliente
            WHERE id_cliente = %s
        """, (id_cliente,))

        conexion.commit()

        return jsonify({
            "mensaje": "Cliente eliminado correctamente",
            "id_cliente": id_cliente
        }), 200

    except Exception:
        conexion.rollback()
        app.logger.exception("Error al eliminar cliente desde la API")

        return jsonify({
            "error": "No se pudo eliminar el cliente"
        }), 500

    finally:
        cursor.close()
        conexion.close()



# ==========================================
# API REST - RESERVAS
# ==========================================

@app.route("/api/reservas", methods=["GET"])
def api_listar_reservas():
    conexion = obtener_conexion()

    if not conexion:
        return jsonify({
            "error": "No se pudo conectar con MySQL"
        }), 500

    cursor = conexion.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT
                r.id_reserva,
                r.id_cliente,
                c.nombre AS nombre_cliente,
                r.id_mesa,
                m.numero AS numero_mesa,
                r.fecha_reserva,
                r.cantidad_personas,
                r.estado
            FROM reserva r
            INNER JOIN cliente c
                ON r.id_cliente = c.id_cliente
            INNER JOIN mesa m
                ON r.id_mesa = m.id_mesa
            ORDER BY r.id_reserva ASC
        """)

        reservas = cursor.fetchall()

        # Convertir fechas a texto compatible con JSON.
        for reserva in reservas:
            reserva["fecha_reserva"] = (
                reserva["fecha_reserva"].strftime("%Y-%m-%d %H:%M:%S")
            )

        return jsonify(reservas), 200

    except Exception:
        app.logger.exception("Error al consultar reservas desde la API")

        return jsonify({
            "error": "No se pudieron consultar las reservas"
        }), 500

    finally:
        cursor.close()
        conexion.close()



@app.route("/api/reservas", methods=["POST"])
def api_agregar_reserva():
    datos = request.get_json(silent=True)

    if not isinstance(datos, dict):
        return jsonify({
            "error": "Debes enviar un objeto JSON válido"
        }), 400

    try:
        id_cliente = int(datos.get("id_cliente"))
        id_mesa = int(datos.get("id_mesa"))
        cantidad_personas = int(datos.get("cantidad_personas"))
        fecha_reserva = str(datos.get("fecha_reserva") or "").strip()
        estado = str(datos.get("estado") or "Pendiente").strip()

        # Comprobar el formato de la fecha.
        from datetime import datetime
        datetime.strptime(fecha_reserva, "%Y-%m-%d %H:%M:%S")

    except (ValueError, TypeError):
        return jsonify({
            "error": "Datos inválidos. Usa fecha_reserva con formato YYYY-MM-DD HH:MM:SS"
        }), 400

    if id_cliente <= 0 or id_mesa <= 0 or cantidad_personas <= 0:
        return jsonify({
            "error": "Cliente, mesa y cantidad de personas deben ser mayores que cero"
        }), 400

    if estado not in ("Pendiente", "Confirmada", "Cancelada"):
        return jsonify({
            "error": "Estado de reserva no válido"
        }), 400

    conexion = obtener_conexion()

    if not conexion:
        return jsonify({
            "error": "No se pudo conectar con MySQL"
        }), 500

    cursor = conexion.cursor(dictionary=True)

    try:
        # Verificar que el cliente exista.
        cursor.execute(
            "SELECT id_cliente FROM cliente WHERE id_cliente = %s",
            (id_cliente,)
        )

        if not cursor.fetchone():
            return jsonify({
                "error": "El cliente no existe"
            }), 404

        # Verificar que la mesa exista.
        cursor.execute(
            "SELECT id_mesa FROM mesa WHERE id_mesa = %s",
            (id_mesa,)
        )

        if not cursor.fetchone():
            return jsonify({
                "error": "La mesa no existe"
            }), 404

        # Registrar la reserva.
        cursor.execute("""
            INSERT INTO reserva (
                id_cliente,
                id_mesa,
                fecha_reserva,
                cantidad_personas,
                estado
            )
            VALUES (%s, %s, %s, %s, %s)
        """, (
            id_cliente,
            id_mesa,
            fecha_reserva,
            cantidad_personas,
            estado
        ))

        conexion.commit()
        id_reserva = cursor.lastrowid

        return jsonify({
            "mensaje": "Reserva registrada correctamente",
            "reserva": {
                "id_reserva": id_reserva,
                "id_cliente": id_cliente,
                "id_mesa": id_mesa,
                "fecha_reserva": fecha_reserva,
                "cantidad_personas": cantidad_personas,
                "estado": estado
            }
        }), 201

    except Exception:
        conexion.rollback()
        app.logger.exception("Error al registrar reserva desde la API")

        return jsonify({
            "error": "No se pudo registrar la reserva"
        }), 500

    finally:
        cursor.close()
        conexion.close()



@app.route("/api/reservas/<int:id_reserva>", methods=["PUT"])
def api_editar_reserva(id_reserva):
    datos = request.get_json(silent=True)

    if not isinstance(datos, dict):
        return jsonify({
            "error": "Debes enviar un objeto JSON válido"
        }), 400

    try:
        id_cliente = int(datos.get("id_cliente"))
        id_mesa = int(datos.get("id_mesa"))
        cantidad_personas = int(datos.get("cantidad_personas"))
        fecha_reserva = str(datos.get("fecha_reserva") or "").strip()
        estado = str(datos.get("estado") or "").strip()

        from datetime import datetime
        datetime.strptime(fecha_reserva, "%Y-%m-%d %H:%M:%S")

    except (ValueError, TypeError):
        return jsonify({
            "error": "Datos inválidos. Usa la fecha YYYY-MM-DD HH:MM:SS"
        }), 400

    if id_cliente <= 0 or id_mesa <= 0 or cantidad_personas <= 0:
        return jsonify({
            "error": "Cliente, mesa y cantidad de personas deben ser mayores que cero"
        }), 400

    if estado not in ("Pendiente", "Confirmada", "Cancelada"):
        return jsonify({
            "error": "Estado de reserva no válido"
        }), 400

    conexion = obtener_conexion()

    if not conexion:
        return jsonify({
            "error": "No se pudo conectar con MySQL"
        }), 500

    cursor = conexion.cursor(dictionary=True)

    try:
        # Comprobar que la reserva existe.
        cursor.execute("""
            SELECT id_reserva
            FROM reserva
            WHERE id_reserva = %s
        """, (id_reserva,))

        if not cursor.fetchone():
            return jsonify({
                "error": "Reserva no encontrada"
            }), 404

        # Verificar que el cliente existe.
        cursor.execute("""
            SELECT id_cliente
            FROM cliente
            WHERE id_cliente = %s
        """, (id_cliente,))

        if not cursor.fetchone():
            return jsonify({
                "error": "Cliente no encontrado"
            }), 404

        # Verificar que la mesa existe.
        cursor.execute("""
            SELECT id_mesa
            FROM mesa
            WHERE id_mesa = %s
        """, (id_mesa,))

        if not cursor.fetchone():
            return jsonify({
                "error": "Mesa no encontrada"
            }), 404

        # Actualizar la reserva.
        cursor.execute("""
            UPDATE reserva
            SET id_cliente = %s,
                id_mesa = %s,
                fecha_reserva = %s,
                cantidad_personas = %s,
                estado = %s
            WHERE id_reserva = %s
        """, (
            id_cliente,
            id_mesa,
            fecha_reserva,
            cantidad_personas,
            estado,
            id_reserva
        ))

        conexion.commit()

        return jsonify({
            "mensaje": "Reserva actualizada correctamente",
            "reserva": {
                "id_reserva": id_reserva,
                "id_cliente": id_cliente,
                "id_mesa": id_mesa,
                "fecha_reserva": fecha_reserva,
                "cantidad_personas": cantidad_personas,
                "estado": estado
            }
        }), 200

    except Exception:
        conexion.rollback()
        app.logger.exception("Error al actualizar reserva desde la API")

        return jsonify({
            "error": "No se pudo actualizar la reserva"
        }), 500

    finally:
        cursor.close()
        conexion.close()



@app.route("/api/reservas/<int:id_reserva>", methods=["DELETE"])
def api_eliminar_reserva(id_reserva):
    conexion = obtener_conexion()

    if not conexion:
        return jsonify({
            "error": "No se pudo conectar con MySQL"
        }), 500

    cursor = conexion.cursor(dictionary=True)

    try:
        # Comprobar que la reserva existe.
        cursor.execute("""
            SELECT id_reserva, id_cliente, id_mesa
            FROM reserva
            WHERE id_reserva = %s
        """, (id_reserva,))

        reserva = cursor.fetchone()

        if not reserva:
            return jsonify({
                "error": "Reserva no encontrada"
            }), 404

        # Eliminar la reserva.
        cursor.execute("""
            DELETE FROM reserva
            WHERE id_reserva = %s
        """, (id_reserva,))

        conexion.commit()

        return jsonify({
            "mensaje": "Reserva eliminada correctamente",
            "id_reserva": id_reserva
        }), 200

    except Exception:
        conexion.rollback()
        app.logger.exception("Error al eliminar reserva desde la API")

        return jsonify({
            "error": "No se pudo eliminar la reserva"
        }), 500

    finally:
        cursor.close()
        conexion.close()



# ==========================================
# API REST - INVENTARIO
# ==========================================

@app.route("/api/inventario", methods=["GET"])
def api_listar_inventario():
    conexion = obtener_conexion()

    if not conexion:
        return jsonify({
            "error": "No se pudo conectar con MySQL"
        }), 500

    cursor = conexion.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT
                id_inventario,
                nombre_insumo,
                cantidad,
                unidad_medida,
                stock_minimo,
                fecha_actualizacion
            FROM inventario
            ORDER BY id_inventario ASC
        """)

        inventario = cursor.fetchall()

        # Convertir valores a formatos compatibles con JSON.
        for insumo in inventario:
            insumo["cantidad"] = float(insumo["cantidad"])
            insumo["stock_minimo"] = (
                float(insumo["stock_minimo"])
                if insumo["stock_minimo"] is not None
                else None
            )

            if insumo["fecha_actualizacion"]:
                insumo["fecha_actualizacion"] = (
                    insumo["fecha_actualizacion"].strftime(
                        "%Y-%m-%d %H:%M:%S"
                    )
                )

        return jsonify(inventario), 200

    except Exception:
        app.logger.exception(
            "Error al consultar inventario desde la API"
        )

        return jsonify({
            "error": "No se pudo consultar el inventario"
        }), 500

    finally:
        cursor.close()
        conexion.close()



@app.route("/api/inventario", methods=["POST"])
def api_agregar_inventario():
    datos = request.get_json(silent=True)

    if not isinstance(datos, dict):
        return jsonify({
            "error": "Debes enviar un objeto JSON válido"
        }), 400

    nombre_insumo = str(
        datos.get("nombre_insumo") or ""
    ).strip()

    unidad_medida = str(
        datos.get("unidad_medida") or ""
    ).strip()

    try:
        from decimal import Decimal, InvalidOperation

        cantidad = Decimal(str(datos.get("cantidad")))
        stock_minimo = Decimal(
            str(datos.get("stock_minimo", 0))
        )

    except (InvalidOperation, TypeError, ValueError):
        return jsonify({
            "error": "Cantidad o stock mínimo inválido"
        }), 400

    if not nombre_insumo or not unidad_medida:
        return jsonify({
            "error": "El nombre y la unidad de medida son obligatorios"
        }), 400

    if not cantidad.is_finite() or not stock_minimo.is_finite():
        return jsonify({
            "error": "Los valores deben ser números finitos"
        }), 400

    if cantidad < 0 or stock_minimo < 0:
        return jsonify({
            "error": "La cantidad y el stock mínimo no pueden ser negativos"
        }), 400

    conexion = obtener_conexion()

    if not conexion:
        return jsonify({
            "error": "No se pudo conectar con MySQL"
        }), 500

    cursor = conexion.cursor()

    try:
        cursor.execute("""
            INSERT INTO inventario (
                nombre_insumo,
                cantidad,
                unidad_medida,
                stock_minimo
            )
            VALUES (%s, %s, %s, %s)
        """, (
            nombre_insumo,
            cantidad,
            unidad_medida,
            stock_minimo
        ))

        conexion.commit()

        return jsonify({
            "mensaje": "Insumo registrado correctamente",
            "insumo": {
                "id_inventario": cursor.lastrowid,
                "nombre_insumo": nombre_insumo,
                "cantidad": float(cantidad),
                "unidad_medida": unidad_medida,
                "stock_minimo": float(stock_minimo)
            }
        }), 201

    except Exception:
        conexion.rollback()
        app.logger.exception(
            "Error al registrar insumo desde la API"
        )

        return jsonify({
            "error": "No se pudo registrar el insumo"
        }), 500

    finally:
        cursor.close()
        conexion.close()



@app.route("/api/inventario/<int:id_inventario>", methods=["PUT"])
def api_editar_inventario(id_inventario):
    datos = request.get_json(silent=True)

    if not isinstance(datos, dict):
        return jsonify({
            "error": "Debes enviar un objeto JSON válido"
        }), 400

    nombre_insumo = str(
        datos.get("nombre_insumo") or ""
    ).strip()

    unidad_medida = str(
        datos.get("unidad_medida") or ""
    ).strip()

    try:
        from decimal import Decimal, InvalidOperation

        cantidad = Decimal(str(datos.get("cantidad")))
        stock_minimo = Decimal(str(datos.get("stock_minimo", 0)))

    except (InvalidOperation, TypeError, ValueError):
        return jsonify({
            "error": "Cantidad o stock mínimo inválido"
        }), 400

    if not nombre_insumo or not unidad_medida:
        return jsonify({
            "error": "El nombre y la unidad de medida son obligatorios"
        }), 400

    if not cantidad.is_finite() or not stock_minimo.is_finite():
        return jsonify({
            "error": "Los valores deben ser números finitos"
        }), 400

    if cantidad < 0 or stock_minimo < 0:
        return jsonify({
            "error": "La cantidad y el stock mínimo no pueden ser negativos"
        }), 400

    conexion = obtener_conexion()

    if not conexion:
        return jsonify({
            "error": "No se pudo conectar con MySQL"
        }), 500

    cursor = conexion.cursor(dictionary=True)

    try:
        # Comprobar que el insumo existe.
        cursor.execute("""
            SELECT id_inventario
            FROM inventario
            WHERE id_inventario = %s
        """, (id_inventario,))

        if not cursor.fetchone():
            return jsonify({
                "error": "Insumo no encontrado"
            }), 404

        # Actualizar el insumo.
        cursor.execute("""
            UPDATE inventario
            SET nombre_insumo = %s,
                cantidad = %s,
                unidad_medida = %s,
                stock_minimo = %s
            WHERE id_inventario = %s
        """, (
            nombre_insumo,
            cantidad,
            unidad_medida,
            stock_minimo,
            id_inventario
        ))

        conexion.commit()

        return jsonify({
            "mensaje": "Insumo actualizado correctamente",
            "insumo": {
                "id_inventario": id_inventario,
                "nombre_insumo": nombre_insumo,
                "cantidad": float(cantidad),
                "unidad_medida": unidad_medida,
                "stock_minimo": float(stock_minimo)
            }
        }), 200

    except Exception:
        conexion.rollback()
        app.logger.exception(
            "Error al actualizar insumo desde la API"
        )

        return jsonify({
            "error": "No se pudo actualizar el insumo"
        }), 500

    finally:
        cursor.close()
        conexion.close()



@app.route("/api/inventario/<int:id_inventario>", methods=["DELETE"])
def api_eliminar_inventario(id_inventario):
    conexion = obtener_conexion()

    if not conexion:
        return jsonify({
            "error": "No se pudo conectar con MySQL"
        }), 500

    cursor = conexion.cursor(dictionary=True)

    try:
        # Verificar que el insumo exista.
        cursor.execute("""
            SELECT id_inventario, nombre_insumo
            FROM inventario
            WHERE id_inventario = %s
        """, (id_inventario,))

        insumo = cursor.fetchone()

        if not insumo:
            return jsonify({
                "error": "Insumo no encontrado"
            }), 404

        # Evitar eliminar insumos con movimientos asociados.
        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM movimiento_inventario
            WHERE id_inventario = %s
        """, (id_inventario,))

        resultado = cursor.fetchone()

        if resultado["total"] > 0:
            return jsonify({
                "error": "No se puede eliminar el insumo porque tiene movimientos asociados"
            }), 409

        # Eliminar el insumo.
        cursor.execute("""
            DELETE FROM inventario
            WHERE id_inventario = %s
        """, (id_inventario,))

        conexion.commit()

        return jsonify({
            "mensaje": "Insumo eliminado correctamente",
            "id_inventario": id_inventario
        }), 200

    except Exception:
        conexion.rollback()
        app.logger.exception(
            "Error al eliminar insumo desde la API"
        )

        return jsonify({
            "error": "No se pudo eliminar el insumo"
        }), 500

    finally:
        cursor.close()
        conexion.close()



# ==========================================
# API REST - MOVIMIENTOS DE INVENTARIO
# ==========================================

@app.route("/api/movimientos", methods=["GET"])
def api_listar_movimientos():
    conexion = obtener_conexion()

    if not conexion:
        return jsonify({
            "error": "No se pudo conectar con MySQL"
        }), 500

    cursor = conexion.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT
                m.id_movimiento,
                m.id_inventario,
                i.nombre_insumo,
                m.tipo_movimiento,
                m.cantidad,
                m.motivo,
                m.fecha_movimiento
            FROM movimiento_inventario m
            INNER JOIN inventario i
                ON m.id_inventario = i.id_inventario
            ORDER BY m.id_movimiento ASC
        """)

        movimientos = cursor.fetchall()

        for movimiento in movimientos:
            movimiento["cantidad"] = float(
                movimiento["cantidad"]
            )

            if movimiento["fecha_movimiento"]:
                movimiento["fecha_movimiento"] = (
                    movimiento["fecha_movimiento"].strftime(
                        "%Y-%m-%d %H:%M:%S"
                    )
                )

        return jsonify(movimientos), 200

    except Exception:
        app.logger.exception(
            "Error al consultar movimientos desde la API"
        )

        return jsonify({
            "error": "No se pudieron consultar los movimientos"
        }), 500

    finally:
        cursor.close()
        conexion.close()



@app.route("/api/movimientos", methods=["POST"])
def api_agregar_movimiento():
    datos = request.get_json(silent=True)

    if not isinstance(datos, dict):
        return jsonify({
            "error": "Debes enviar un objeto JSON válido"
        }), 400

    try:
        id_inventario = int(datos.get("id_inventario"))
        tipo_movimiento = str(
            datos.get("tipo_movimiento", "")
        ).strip()
        cantidad = Decimal(str(datos.get("cantidad")))
        motivo = str(datos.get("motivo") or "").strip()
    except (ValueError, TypeError, InvalidOperation):
        return jsonify({
            "error": "Datos del movimiento no válidos"
        }), 400

    if id_inventario <= 0 or cantidad <= 0 or not cantidad.is_finite():
        return jsonify({
            "error": "El ID y la cantidad deben ser positivos"
        }), 400

    if tipo_movimiento not in ("Entrada", "Salida"):
        return jsonify({
            "error": "El tipo debe ser Entrada o Salida"
        }), 400

    conexion = obtener_conexion()

    if not conexion:
        return jsonify({
            "error": "No se pudo conectar con MySQL"
        }), 500

    cursor = conexion.cursor(dictionary=True)

    try:
        # Bloqueamos el insumo durante la operación.
        cursor.execute("""
            SELECT id_inventario, nombre_insumo, cantidad
            FROM inventario
            WHERE id_inventario = %s
            FOR UPDATE
        """, (id_inventario,))

        insumo = cursor.fetchone()

        if not insumo:
            conexion.rollback()
            return jsonify({
                "error": "El insumo no existe"
            }), 404

        stock_actual = Decimal(str(insumo["cantidad"]))

        if tipo_movimiento == "Entrada":
            nuevo_stock = stock_actual + cantidad
        else:
            nuevo_stock = stock_actual - cantidad

            if nuevo_stock < 0:
                conexion.rollback()
                return jsonify({
                    "error": "Stock insuficiente",
                    "stock_actual": float(stock_actual)
                }), 409

        # Registrar el movimiento.
        cursor.execute("""
            INSERT INTO movimiento_inventario
                (id_inventario, tipo_movimiento, cantidad, motivo)
            VALUES (%s, %s, %s, %s)
        """, (
            id_inventario,
            tipo_movimiento,
            cantidad,
            motivo
        ))

        id_movimiento = cursor.lastrowid

        # Actualizar el inventario.
        cursor.execute("""
            UPDATE inventario
            SET cantidad = %s
            WHERE id_inventario = %s
        """, (nuevo_stock, id_inventario))

        conexion.commit()

        return jsonify({
            "mensaje": "Movimiento registrado correctamente",
            "id_movimiento": id_movimiento,
            "id_inventario": id_inventario,
            "nombre_insumo": insumo["nombre_insumo"],
            "tipo_movimiento": tipo_movimiento,
            "cantidad": float(cantidad),
            "stock_anterior": float(stock_actual),
            "stock_actual": float(nuevo_stock)
        }), 201

    except Exception:
        conexion.rollback()
        app.logger.exception(
            "Error al registrar movimiento desde la API"
        )
        return jsonify({
            "error": "No se pudo registrar el movimiento"
        }), 500

    finally:
        cursor.close()
        conexion.close()



@app.route("/api/movimientos/<int:id_movimiento>", methods=["PUT"])
def api_editar_movimiento(id_movimiento):
    datos = request.get_json(silent=True)

    if not isinstance(datos, dict):
        return jsonify({"error": "Debes enviar un JSON válido"}), 400

    try:
        id_inventario = int(datos.get("id_inventario"))
        tipo = str(datos.get("tipo_movimiento", "")).strip()
        cantidad = Decimal(str(datos.get("cantidad")))
        motivo = str(datos.get("motivo") or "").strip()
    except (ValueError, TypeError, InvalidOperation):
        return jsonify({"error": "Datos no válidos"}), 400

    if id_inventario <= 0 or cantidad <= 0 or not cantidad.is_finite():
        return jsonify({"error": "ID y cantidad deben ser positivos"}), 400

    if tipo not in ("Entrada", "Salida"):
        return jsonify({"error": "Tipo de movimiento no válido"}), 400

    conexion = obtener_conexion()

    if not conexion:
        return jsonify({"error": "Error de conexión"}), 500

    cursor = conexion.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT id_movimiento, id_inventario,
                   tipo_movimiento, cantidad
            FROM movimiento_inventario
            WHERE id_movimiento = %s
        """, (id_movimiento,))

        anterior = cursor.fetchone()

        if not anterior:
            conexion.rollback()
            return jsonify({"error": "Movimiento no encontrado"}), 404

        id_anterior = anterior["id_inventario"]

        # Bloquear los insumos involucrados en orden fijo.
        ids = sorted(set([id_anterior, id_inventario]))
        insumos = {}

        for id_insumo in ids:
            cursor.execute("""
                SELECT id_inventario, nombre_insumo, cantidad
                FROM inventario
                WHERE id_inventario = %s
                FOR UPDATE
            """, (id_insumo,))

            insumo = cursor.fetchone()

            if not insumo:
                conexion.rollback()
                return jsonify({
                    "error": "Uno de los insumos no existe"
                }), 404

            insumos[id_insumo] = insumo

        # Revertir el efecto del movimiento anterior.
        cantidad_anterior = Decimal(str(anterior["cantidad"]))
        signo_anterior = (
            1 if anterior["tipo_movimiento"] == "Entrada" else -1
        )

        stock_anterior = Decimal(
            str(insumos[id_anterior]["cantidad"])
        )

        stock_revertido = (
            stock_anterior - signo_anterior * cantidad_anterior
        )

        if stock_revertido < 0:
            conexion.rollback()
            return jsonify({
                "error": "No se puede revertir el movimiento anterior"
            }), 409

        # Aplicar el nuevo movimiento.
        signo_nuevo = 1 if tipo == "Entrada" else -1

        if id_anterior == id_inventario:
            nuevo_stock = stock_revertido + signo_nuevo * cantidad

            if nuevo_stock < 0:
                conexion.rollback()
                return jsonify({"error": "Stock insuficiente"}), 409

            cursor.execute("""
                UPDATE inventario
                SET cantidad = %s
                WHERE id_inventario = %s
            """, (nuevo_stock, id_inventario))

        else:
            stock_destino = Decimal(
                str(insumos[id_inventario]["cantidad"])
            )

            nuevo_stock = stock_destino + signo_nuevo * cantidad

            if nuevo_stock < 0:
                conexion.rollback()
                return jsonify({"error": "Stock insuficiente"}), 409

            cursor.execute("""
                UPDATE inventario
                SET cantidad = %s
                WHERE id_inventario = %s
            """, (stock_revertido, id_anterior))

            cursor.execute("""
                UPDATE inventario
                SET cantidad = %s
                WHERE id_inventario = %s
            """, (nuevo_stock, id_inventario))

        cursor.execute("""
            UPDATE movimiento_inventario
            SET id_inventario = %s,
                tipo_movimiento = %s,
                cantidad = %s,
                motivo = %s
            WHERE id_movimiento = %s
        """, (
            id_inventario, tipo, cantidad,
            motivo, id_movimiento
        ))

        conexion.commit()

        return jsonify({
            "mensaje": "Movimiento actualizado correctamente",
            "id_movimiento": id_movimiento,
            "id_inventario": id_inventario,
            "tipo_movimiento": tipo,
            "cantidad": float(cantidad),
            "stock_actual": float(nuevo_stock)
        }), 200

    except Exception:
        conexion.rollback()
        app.logger.exception("Error al editar movimiento")
        return jsonify({
            "error": "No se pudo actualizar el movimiento"
        }), 500

    finally:
        cursor.close()
        conexion.close()



@app.route("/api/movimientos/<int:id_movimiento>", methods=["DELETE"])
def api_eliminar_movimiento(id_movimiento):
    conexion = obtener_conexion()

    if not conexion:
        return jsonify({
            "error": "No se pudo conectar con MySQL"
        }), 500

    cursor = conexion.cursor(dictionary=True)

    try:
        # Buscar el movimiento que queremos eliminar.
        cursor.execute("""
            SELECT id_movimiento, id_inventario,
                   tipo_movimiento, cantidad
            FROM movimiento_inventario
            WHERE id_movimiento = %s
            FOR UPDATE
        """, (id_movimiento,))

        movimiento = cursor.fetchone()

        if not movimiento:
            conexion.rollback()
            return jsonify({
                "error": "Movimiento no encontrado"
            }), 404

        id_inventario = movimiento["id_inventario"]
        cantidad = Decimal(str(movimiento["cantidad"]))

        # Bloquear el insumo para actualizar su stock.
        cursor.execute("""
            SELECT id_inventario, cantidad
            FROM inventario
            WHERE id_inventario = %s
            FOR UPDATE
        """, (id_inventario,))

        insumo = cursor.fetchone()

        if not insumo:
            conexion.rollback()
            return jsonify({
                "error": "Insumo no encontrado"
            }), 404

        stock_actual = Decimal(str(insumo["cantidad"]))

        if movimiento["tipo_movimiento"] == "Entrada":
            nuevo_stock = stock_actual - cantidad
        else:
            nuevo_stock = stock_actual + cantidad

        if nuevo_stock < 0:
            conexion.rollback()
            return jsonify({
                "error": "No se puede eliminar: stock insuficiente"
            }), 409

        # Eliminar el movimiento.
        cursor.execute("""
            DELETE FROM movimiento_inventario
            WHERE id_movimiento = %s
        """, (id_movimiento,))

        # Actualizar el inventario.
        cursor.execute("""
            UPDATE inventario
            SET cantidad = %s
            WHERE id_inventario = %s
        """, (nuevo_stock, id_inventario))

        conexion.commit()

        return jsonify({
            "mensaje": "Movimiento eliminado correctamente",
            "id_movimiento": id_movimiento,
            "tipo_movimiento": movimiento["tipo_movimiento"],
            "cantidad": float(cantidad),
            "stock_anterior": float(stock_actual),
            "stock_actual": float(nuevo_stock)
        }), 200

    except Exception:
        conexion.rollback()
        app.logger.exception(
            "Error al eliminar movimiento desde la API"
        )

        return jsonify({
            "error": "No se pudo eliminar el movimiento"
        }), 500

    finally:
        cursor.close()
        conexion.close()



# ==========================================
# API REST - MESAS
# ==========================================

@app.route("/api/mesas", methods=["GET"])
def api_listar_mesas():
    conexion = obtener_conexion()

    if not conexion:
        return jsonify({
            "error": "No se pudo conectar con MySQL"
        }), 500

    cursor = conexion.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT id_mesa, numero, estado
            FROM mesa
            ORDER BY numero ASC
        """)

        mesas = cursor.fetchall()

        return jsonify(mesas), 200

    except Exception:
        app.logger.exception(
            "Error al consultar mesas desde la API"
        )

        return jsonify({
            "error": "No se pudieron consultar las mesas"
        }), 500

    finally:
        cursor.close()
        conexion.close()


@app.route("/api/mesas", methods=["POST"])
def api_agregar_mesa():
    datos = request.get_json(silent=True)

    if not isinstance(datos, dict):
        return jsonify({
            "error": "Debes enviar un JSON válido"
        }), 400

    try:
        numero = int(datos.get("numero"))
    except (TypeError, ValueError):
        return jsonify({
            "error": "El número de mesa debe ser válido"
        }), 400

    estado = datos.get("estado", "Libre")

    if numero <= 0:
        return jsonify({
            "error": "El número de mesa debe ser mayor que cero"
        }), 400

    if estado not in ("Libre", "Ocupada", "Reservada"):
        return jsonify({
            "error": "Estado de mesa no válido"
        }), 400

    conexion = obtener_conexion()

    if not conexion:
        return jsonify({
            "error": "No se pudo conectar con MySQL"
        }), 500

    cursor = conexion.cursor()

    try:
        cursor.execute(
            "SELECT id_mesa FROM mesa WHERE numero = %s",
            (numero,)
        )

        if cursor.fetchone():
            return jsonify({
                "error": "Ya existe una mesa con ese número"
            }), 409

        cursor.execute("""
            INSERT INTO mesa (numero, estado)
            VALUES (%s, %s)
        """, (numero, estado))

        id_mesa = cursor.lastrowid
        conexion.commit()

        return jsonify({
            "mensaje": "Mesa registrada correctamente",
            "mesa": {
                "id_mesa": id_mesa,
                "numero": numero,
                "estado": estado
            }
        }), 201

    except Exception:
        conexion.rollback()
        app.logger.exception("Error al registrar mesa desde la API")

        return jsonify({
            "error": "No se pudo registrar la mesa"
        }), 500

    finally:
        cursor.close()
        conexion.close()


@app.route("/api/mesas/<int:id_mesa>", methods=["PUT"])
def api_actualizar_mesa(id_mesa):
    datos = request.get_json(silent=True)

    if not isinstance(datos, dict):
        return jsonify({
            "error": "Debes enviar un JSON válido"
        }), 400

    try:
        numero = int(datos.get("numero"))
    except (TypeError, ValueError):
        return jsonify({
            "error": "El número de mesa debe ser válido"
        }), 400

    estado = datos.get("estado")

    if numero <= 0:
        return jsonify({
            "error": "El número de mesa debe ser mayor que cero"
        }), 400

    if estado not in ("Libre", "Ocupada", "Reservada"):
        return jsonify({
            "error": "Estado de mesa no válido"
        }), 400

    conexion = obtener_conexion()

    if not conexion:
        return jsonify({
            "error": "No se pudo conectar con MySQL"
        }), 500

    cursor = conexion.cursor(dictionary=True)

    try:
        # Verificar que la mesa exista
        cursor.execute(
            "SELECT id_mesa FROM mesa WHERE id_mesa = %s",
            (id_mesa,)
        )

        if not cursor.fetchone():
            return jsonify({
                "error": "La mesa no existe"
            }), 404

        # Evitar números de mesa duplicados
        cursor.execute("""
            SELECT id_mesa
            FROM mesa
            WHERE numero = %s AND id_mesa != %s
        """, (numero, id_mesa))

        if cursor.fetchone():
            return jsonify({
                "error": "Ya existe otra mesa con ese número"
            }), 409

        # Actualizar la mesa
        cursor.execute("""
            UPDATE mesa
            SET numero = %s, estado = %s
            WHERE id_mesa = %s
        """, (numero, estado, id_mesa))

        conexion.commit()

        return jsonify({
            "mensaje": "Mesa actualizada correctamente",
            "mesa": {
                "id_mesa": id_mesa,
                "numero": numero,
                "estado": estado
            }
        }), 200

    except Exception:
        conexion.rollback()
        app.logger.exception("Error al actualizar mesa desde la API")

        return jsonify({
            "error": "No se pudo actualizar la mesa"
        }), 500

    finally:
        cursor.close()
        conexion.close()


        # ==========================================
# API REST - ELIMINAR MESA (DELETE)
# ==========================================

@app.route("/api/mesas/<int:id_mesa>", methods=["DELETE"])
def api_eliminar_mesa(id_mesa):
    conexion = obtener_conexion()

    if not conexion:
        return jsonify({
            "error": "No se pudo conectar con MySQL"
        }), 500

    cursor = conexion.cursor(dictionary=True)

    try:
        # Verificar si la mesa existe
        cursor.execute(
            "SELECT id_mesa FROM mesa WHERE id_mesa = %s",
            (id_mesa,)
        )

        mesa = cursor.fetchone()

        if not mesa:
            return jsonify({
                "error": "La mesa no existe"
            }), 404

        # Evitar eliminar mesas que tengan reservas
        cursor.execute(
            "SELECT COUNT(*) AS total FROM reserva WHERE id_mesa = %s",
            (id_mesa,)
        )

        resultado = cursor.fetchone()

        if resultado["total"] > 0:
            return jsonify({
                "error": "No se puede eliminar la mesa porque tiene reservas asociadas"
            }), 409

        # Eliminar la mesa
        cursor.execute(
            "DELETE FROM mesa WHERE id_mesa = %s",
            (id_mesa,)
        )

        conexion.commit()

        return jsonify({
            "mensaje": "Mesa eliminada correctamente",
            "id_mesa": id_mesa
        }), 200

    except Exception:
        conexion.rollback()
        app.logger.exception("Error al eliminar mesa desde la API")

        return jsonify({
            "error": "No se pudo eliminar la mesa"
        }), 500

    finally:
        cursor.close()
        conexion.close()

if __name__ == "__main__":
    app.run(debug=True)
