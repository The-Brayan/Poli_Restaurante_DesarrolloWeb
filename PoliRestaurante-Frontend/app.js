
const API_URL = "http://127.0.0.1:5000/api";

// Función para consultar los servicios REST
async function cargarDatos(endpoint, titulo) {

    document.getElementById("titulo").textContent = titulo;

    const contenido = document.getElementById("contenido");
    contenido.textContent = "Cargando datos...";

    try {

        const respuesta = await fetch(`${API_URL}/${endpoint}`, {
            method: "GET"
        });

        if (!respuesta.ok) {
            throw new Error(`Error HTTP: ${respuesta.status}`);
        }

        const datos = await respuesta.json();

        mostrarTabla(datos, endpoint);

    } catch (error) {

        contenido.textContent = "Error al consultar los datos: " + error.message;
        console.error(error);

    }
}

// ========================================
// PANEL PRINCIPAL - DASHBOARD
// ========================================

async function mostrarInicio() {

    document.getElementById("titulo").textContent =
        "Resumen general del restaurante";

    const contenido = document.getElementById("contenido");

    contenido.innerHTML = `
        <div class="dashboard-welcome">
            <h2>¡Bienvenido a PoliRestaurante! 🍽️</h2>
            <p>Este es el resumen general de tu restaurante.</p>
        </div>

        <div class="stats-grid">

            <div class="stat-card clientes-card">
                <div class="stat-icon">👥</div>
                <div>
                    <p>Clientes</p>
                    <h3 id="total-clientes">...</h3>
                    <span>Registrados</span>
                </div>
            </div>

            <div class="stat-card productos-card">
                <div class="stat-icon">🍔</div>
                <div>
                    <p>Productos</p>
                    <h3 id="total-productos">...</h3>
                    <span>Registrados</span>
                </div>
            </div>

            <div class="stat-card pedidos-card">
                <div class="stat-icon">📋</div>
                <div>
                    <p>Pedidos</p>
                    <h3 id="total-pedidos">...</h3>
                    <span>Registrados</span>
                </div>
            </div>

            <div class="stat-card reservas-card">
                <div class="stat-icon">📅</div>
                <div>
                    <p>Reservas</p>
                    <h3 id="total-reservas">...</h3>
                    <span>Registradas</span>
                </div>
            </div>

        </div>

        <div class="dashboard-info">
            <h3>Administración del restaurante</h3>
            <p>
                Selecciona cualquiera de las secciones del menú
                lateral para consultar y gestionar la información.
            </p>
        </div>
    `;

    const servicios = [
        { endpoint: "clientes", elemento: "total-clientes" },
        { endpoint: "productos", elemento: "total-productos" },
        { endpoint: "pedidos", elemento: "total-pedidos" },
        { endpoint: "reservas", elemento: "total-reservas" }
    ];

    for (const servicio of servicios) {

        try {

            const respuesta = await fetch(
                `${API_URL}/${servicio.endpoint}`
            );

            if (!respuesta.ok) {
                throw new Error("No se pudieron consultar los datos");
            }

            const datos = await respuesta.json();

            document.getElementById(servicio.elemento).textContent =
                Array.isArray(datos) ? datos.length : "N/D";

        } catch (error) {

            document.getElementById(servicio.elemento).textContent = "Error";
            console.error(
                `Error al consultar ${servicio.endpoint}:`,
                error
            );

        }
    }
}


// Función para mostrar los datos en una tabla

function mostrarTabla(datos, endpoint) {

    const contenido = document.getElementById("contenido");
    contenido.replaceChildren();

    if (!Array.isArray(datos) || datos.length === 0) {
        contenido.textContent = "No hay registros disponibles.";
        return;
    }

    const columnas = Object.keys(datos[0]);

    const tabla = document.createElement("table");
    const encabezado = tabla.createTHead();
    const filaEncabezado = encabezado.insertRow();

    columnas.forEach(columna => {
        const th = document.createElement("th");
        th.textContent = columna.replace(/_/g, " ").toUpperCase();
        filaEncabezado.appendChild(th);
    });

    // Nueva columna de acciones
    const thAcciones = document.createElement("th");
    thAcciones.textContent = "ACCIONES";
    filaEncabezado.appendChild(thAcciones);

    const cuerpo = tabla.createTBody();

    datos.forEach(registro => {

        const fila = cuerpo.insertRow();

        columnas.forEach(columna => {
            const celda = fila.insertCell();
            celda.textContent = registro[columna] ?? "";
        });

        // Botones de editar y eliminar
        const acciones = fila.insertCell();

        const botonEditar = document.createElement("button");
        botonEditar.textContent = "Editar";
        botonEditar.className = "btn-editar";

        botonEditar.onclick = () => {
            editarRegistro(endpoint, registro);
        };

        const botonEliminar = document.createElement("button");
        botonEliminar.textContent = "Eliminar";
        botonEliminar.className = "btn-eliminar";

        botonEliminar.onclick = () => {
            eliminarRegistro(endpoint, registro);
        };

        acciones.appendChild(botonEditar);
        acciones.appendChild(botonEliminar);
    });

    contenido.appendChild(tabla);
}


// Servicio REST de clientes

async function cargarClientes() {

    await cargarDatos("clientes", "Gestión de clientes");

    const formulario = document.createElement("form");

    formulario.innerHTML = `
        <h3>Registrar nuevo cliente</h3>

        <input type="text" id="nombre"
               placeholder="Nombre completo" required>

        <input type="text" id="telefono"
               placeholder="Teléfono">

        <input type="email" id="correo"
               placeholder="Correo electrónico">

        <button type="submit">Registrar cliente</button>
    `;

    formulario.addEventListener("submit", registrarCliente);

    document.getElementById("contenido").prepend(formulario);
}



async function cargarReservas() {

    await cargarDatos("reservas", "Gestión de reservas");

    const formulario = document.createElement("form");

    formulario.innerHTML = `
        <h3>Registrar nueva reserva</h3>

        <label>Cliente</label>
        <select id="id_cliente" required></select>

        <label>Mesa</label>
        <select id="id_mesa" required></select>

        <label>Fecha y hora</label>
        <input type="datetime-local" id="fecha_reserva" required>

        <label>Cantidad de personas</label>
        <input type="number" id="cantidad_personas" min="1" required>

        <label>Estado</label>
        <select id="estado">
            <option value="Pendiente">Pendiente</option>
            <option value="Confirmada">Confirmada</option>
            <option value="Cancelada">Cancelada</option>
        </select>

        <button type="submit">Registrar reserva</button>
    `;

    formulario.addEventListener("submit", registrarReserva);

    document.getElementById("contenido").prepend(formulario);

    try {
        const respuestaClientes = await fetch(`${API_URL}/clientes`);
        const respuestaMesas = await fetch(`${API_URL}/mesas`);

        if (!respuestaClientes.ok || !respuestaMesas.ok) {
            throw new Error("No se pudieron cargar las opciones");
        }

        const clientes = await respuestaClientes.json();
        const mesas = await respuestaMesas.json();

        clientes.forEach(cliente => {
            const opcion = document.createElement("option");
            opcion.value = cliente.id_cliente;
            opcion.textContent = cliente.nombre;
            formulario.querySelector("#id_cliente").appendChild(opcion);
        });

        mesas.forEach(mesa => {
            const opcion = document.createElement("option");
            opcion.value = mesa.id_mesa;
            opcion.textContent = `Mesa ${mesa.numero} - ${mesa.estado}`;
            formulario.querySelector("#id_mesa").appendChild(opcion);
        });

    } catch (error) {
        formulario.querySelector("button").disabled = true;
        alert(error.message);
    }
}


// Servicio REST de mesas

async function cargarMesas() {

    await cargarDatos("mesas", "Gestión de mesas");

    const formulario = document.createElement("form");

    formulario.innerHTML = `
        <h3>Registrar nueva mesa</h3>

        <label>Número de mesa</label>
        <input type="number" id="numero" min="1" required>

        <label>Estado</label>
        <select id="estado_mesa">
            <option value="Libre">Libre</option>
            <option value="Ocupada">Ocupada</option>
            <option value="Reservada">Reservada</option>
        </select>

        <button type="submit">Registrar mesa</button>
    `;

    formulario.addEventListener("submit", registrarMesa);

    document.getElementById("contenido").prepend(formulario);
}


// Servicio REST de inventario

async function cargarInventario() {

    await cargarDatos("inventario", "Gestión de inventario");

    const formulario = document.createElement("form");

    formulario.innerHTML = `
        <h3>Registrar nuevo insumo</h3>

        <label>Nombre del insumo</label>
        <input type="text" id="nombre_insumo" required>

        <label>Cantidad</label>
        <input type="number" id="cantidad" min="0" step="0.01" required>

        <label>Unidad de medida</label>
        <input type="text" id="unidad_medida" required>

        <label>Stock mínimo</label>
        <input type="number" id="stock_minimo" min="0" step="0.01" required>

        <button type="submit">Registrar insumo</button>
    `;

    formulario.addEventListener("submit", registrarInsumo);

    document.getElementById("contenido").prepend(formulario);
}

async function cargarProductos() {

    await cargarDatos("productos", "Gestión de productos");

    const formulario = document.createElement("form");

    formulario.innerHTML = `
        <h3>Registrar nuevo producto</h3>

        <label>Nombre del producto</label>
        <input type="text" id="nombre_producto" required>

        <label>Descripción</label>
        <textarea id="descripcion_producto" required></textarea>

        <label>Precio</label>
        <input type="number" id="precio_producto" min="0" step="0.01" required>

        <label>Disponibilidad</label>
        <select id="disponibilidad_producto" required>
            <option value="1">Disponible</option>
            <option value="0">No disponible</option>
        </select>

        <label>Categoría</label>
        <select id="id_categoria" required>
            <option value="">Cargando categorías...</option>
        </select>

        <button type="submit">Registrar producto</button>
    `;

    try {

        const respuesta = await fetch(`${API_URL}/categorias`);

        if (!respuesta.ok) {
            throw new Error("No se pudieron consultar las categorías");
        }

        const categorias = await respuesta.json();

        const selector = formulario.querySelector("#id_categoria");
        selector.innerHTML = '<option value="">Selecciona una categoría</option>';

        categorias.forEach(categoria => {
            const opcion = document.createElement("option");
            opcion.value = categoria.id_categoria;
            opcion.textContent = categoria.nombre;
            selector.appendChild(opcion);
        });

    } catch (error) {
        alert(error.message);
        return;
    }

    formulario.addEventListener("submit", registrarProducto);

    document.getElementById("contenido").prepend(formulario);
}

async function cargarCocina() {
    await cargarDatos("cocina", "Gestión de cocina");

    const formulario = document.createElement("form");

    formulario.innerHTML = `
        <h3>Registrar personal de cocina</h3>

        <label>Nombre</label>
        <input type="text" id="nombre_cocina" required>

        <label>Usuario de acceso</label>
        <input type="text" id="usuario_cocina" required>

        <label>Contraseña</label>
        <input type="password" id="contrasena_cocina" required>

        <label>Estado</label>
        <select id="estado_cocina" required>
            <option value="1">Activo</option>
            <option value="0">Inactivo</option>
        </select>

        <button type="submit">Registrar personal</button>
    `;

    formulario.addEventListener("submit", registrarCocina);

    document.getElementById("contenido").prepend(formulario);
}

async function cargarCategorias() {
    await cargarDatos("categorias", "Gestión de categorías");

    const formulario = document.createElement("form");

    formulario.innerHTML = `
        <h3>Registrar categoría</h3>

        <label>Nombre de la categoría</label>
        <input type="text" id="nombre_categoria" maxlength="255" required>

        <button type="submit">Registrar categoría</button>
    `;

    formulario.addEventListener("submit", registrarCategoria);

    document.getElementById("contenido").prepend(formulario);
}

async function cargarHistorialEstados() {
    await cargarDatos(
        "historial-estados",
        "Gestión de historial de estados"
    );

    const formulario = document.createElement("form");

    formulario.innerHTML = `
        <h3>Registrar historial de estado</h3>

        <label>Pedido</label>
        <select id="id_pedido_historial" required>
            <option value="">Seleccione un pedido</option>
        </select>

        <label>Estado</label>
        <select id="estado_historial" required>
            <option value="Pendiente">Pendiente</option>
            <option value="En preparación">En preparación</option>
            <option value="Listo">Listo</option>
            <option value="Entregado">Entregado</option>
            <option value="Cancelado">Cancelado</option>
        </select>

        <label>Rol del usuario</label>
        <select id="rol_usuario_cambio">
            <option value="">Seleccione un rol</option>
            <option value="administrador">Administrador</option>
            <option value="cajero">Cajero</option>
            <option value="mesero">Mesero</option>
            <option value="cocina">Cocina</option>
        </select>

        <label>ID del usuario que realiza el cambio</label>
        <input type="number" id="id_usuario_cambio" min="1" step="1">

        <button type="submit">Registrar historial</button>
    `;

    try {
        const respuesta = await fetch(`${API_URL}/pedidos`);

        if (!respuesta.ok) {
            throw new Error("No se pudieron cargar los pedidos");
        }

        const pedidos = await respuesta.json();

        const selectPedidos = formulario.querySelector(
            "#id_pedido_historial"
        );

        pedidos.forEach(pedido => {
            const opcion = document.createElement("option");

            opcion.value = pedido.id_pedido;

            opcion.textContent =
                `Pedido #${pedido.id_pedido} - ${pedido.tipo_pedido} - ${pedido.estado}`;

            selectPedidos.appendChild(opcion);
        });

        formulario.addEventListener(
            "submit",
            registrarHistorialEstado
        );

        document.getElementById("contenido").prepend(formulario);

    } catch (error) {
        console.error("Error:", error);
        alert(error.message);
    }
}

async function cargarPedidos() {
    await cargarDatos("pedidos", "Gestión de pedidos");

    const formulario = document.createElement("form");

    formulario.innerHTML = `
        <h3>Registrar pedido</h3>

        <label>Tipo de pedido</label>
        <select id="tipo_pedido" required>
            <option value="Mesa">Mesa</option>
            <option value="Domicilio">Domicilio</option>
            <option value="Para llevar">Para llevar</option>
        </select>

        <div id="campo_mesa_pedido">
            <label>Mesa</label>
            <select id="id_mesa_pedido">
                <option value="">Seleccione una mesa</option>
            </select>
        </div>

        <div id="campo_direccion_pedido">
            <label>Dirección de entrega</label>
            <input type="text" id="direccion_entrega" maxlength="255">
        </div>

        <label>Mesero responsable</label>
        <select id="id_mesero_pedido" required>
            <option value="">Seleccione un mesero</option>
        </select>

        <label>Estado</label>
        <select id="estado_pedido" required>
            <option value="Pendiente">Pendiente</option>
            <option value="En preparación">En preparación</option>
            <option value="Listo">Listo</option>
            <option value="Entregado">Entregado</option>
            <option value="Cancelado">Cancelado</option>
        </select>

        <button type="submit">Registrar pedido</button>
    `;

    try {
        const [respuestaMesas, respuestaMeseros] = await Promise.all([
            fetch(`${API_URL}/mesas`),
            fetch(`${API_URL}/meseros`)
        ]);

        if (!respuestaMesas.ok || !respuestaMeseros.ok) {
            throw new Error("No se pudieron cargar las mesas o los meseros");
        }

        const mesas = await respuestaMesas.json();
        const meseros = await respuestaMeseros.json();

        const selectMesas = formulario.querySelector("#id_mesa_pedido");
        const selectMeseros = formulario.querySelector("#id_mesero_pedido");

        mesas.forEach(mesa => {
            const opcion = document.createElement("option");
            opcion.value = mesa.id_mesa;
            opcion.textContent = `Mesa ${mesa.numero} - ${mesa.estado}`;
            selectMesas.appendChild(opcion);
        });

        meseros.forEach(mesero => {
            const opcion = document.createElement("option");
            opcion.value = mesero.id_mesero;
            opcion.textContent = `${mesero.nombre} - ${Number(mesero.estado) === 1 ? "Activo" : "Inactivo"}`;
            selectMeseros.appendChild(opcion);
        });

        formulario.addEventListener("submit", registrarPedido);

        document.getElementById("contenido").prepend(formulario);

        document.getElementById("tipo_pedido")
            .addEventListener("change", actualizarCamposPedido);

        actualizarCamposPedido();

    } catch (error) {
        console.error("Error:", error);
        alert(error.message);
    }
}

function actualizarCamposPedido() {

    const tipo = document.getElementById("tipo_pedido").value;

    const campoMesa = document.getElementById("campo_mesa_pedido");
    const campoDireccion = document.getElementById("campo_direccion_pedido");

    const mesa = document.getElementById("id_mesa_pedido");
    const direccion = document.getElementById("direccion_entrega");

    campoMesa.style.display = tipo === "Mesa" ? "block" : "none";

    campoDireccion.style.display =
        tipo === "Domicilio" ? "block" : "none";

    mesa.required = tipo === "Mesa";
    direccion.required = tipo === "Domicilio";

    if (tipo !== "Mesa") {
        mesa.value = "";
    }

    if (tipo !== "Domicilio") {
        direccion.value = "";
    }
}

async function cargarMeseros() {
    await cargarDatos("meseros", "Gestión de meseros");

    const formulario = document.createElement("form");

    formulario.innerHTML = `
        <h3>Registrar mesero</h3>

        <label>Nombre</label>
        <input type="text" id="nombre_mesero" maxlength="100" required>

        <label>Usuario de acceso</label>
        <input type="text" id="usuario_mesero" maxlength="50" required>

        <label>Contraseña</label>
        <input type="password" id="contrasena_mesero" autocomplete="new-password" required>

        <label>Estado</label>
        <select id="estado_mesero" required>
            <option value="1">Activo</option>
            <option value="0">Inactivo</option>
        </select>

        <button type="submit">Registrar mesero</button>
    `;

    formulario.addEventListener("submit", registrarMesero);

    document.getElementById("contenido").prepend(formulario);
}

async function cargarCajeros() {
    await cargarDatos("cajeros", "Gestión de cajeros");

    const formulario = document.createElement("form");

    formulario.innerHTML = `
        <h3>Registrar cajero</h3>

        <label>Nombre</label>
        <input type="text" id="nombre_cajero" maxlength="100" required>

        <label>Usuario de acceso</label>
        <input type="text" id="usuario_cajero" maxlength="50" required>

        <label>Contraseña</label>
        <input type="password" id="contrasena_cajero" autocomplete="new-password" required>

        <label>Estado</label>
        <select id="estado_cajero" required>
            <option value="1">Activo</option>
            <option value="0">Inactivo</option>
        </select>

        <button type="submit">Registrar cajero</button>
    `;

    formulario.addEventListener("submit", registrarCajero);

    document.getElementById("contenido").prepend(formulario);
}

async function cargarAdministradores() {
    await cargarDatos("administradores", "Gestión de administradores");

    const formulario = document.createElement("form");

    formulario.innerHTML = `
        <h3>Registrar administrador</h3>

        <label>Nombre</label>
        <input type="text" id="nombre_administrador" required>

        <label>Usuario de acceso</label>
        <input type="text" id="usuario_administrador" required>

        <label>Contraseña</label>
        <input type="password" id="contrasena_administrador" required>

        <label>Estado</label>
        <select id="estado_administrador" required>
            <option value="1">Activo</option>
            <option value="0">Inactivo</option>
        </select>

        <button type="submit">Registrar administrador</button>
    `;

    formulario.addEventListener("submit", registrarAdministrador);

    document.getElementById("contenido").prepend(formulario);
}
async function cargarPagos() {
    await cargarDatos("pagos", "Gestión de pagos");

    const formulario = document.createElement("form");

    formulario.innerHTML = `
        <h3>Registrar nuevo pago</h3>

        <label>ID del pedido</label>
        <input type="number" id="id_pedido_pago" min="1" required>

        <label>ID del cajero</label>
        <input type="number" id="id_cajero_pago" min="1" required>

        <label>Método de pago</label>
        <select id="metodo_pago" required>
            <option value="">Seleccione</option>
            <option value="Efectivo">Efectivo</option>
            <option value="Tarjeta">Tarjeta</option>
            <option value="Transferencia">Transferencia</option>
        </select>

        <label>Monto</label>
        <input type="number" id="monto_pago" min="0.01" step="0.01" required>

        <button type="submit">Registrar pago</button>
    `;

    formulario.addEventListener("submit", registrarPago);

    document.getElementById("contenido").prepend(formulario);
}
async function cargarDetallesPedido() {
    await cargarDatos("detalles-pedido", "Gestión de detalles de pedido");

    const formulario = document.createElement("form");

    formulario.innerHTML = `
        <h3>Registrar detalle de pedido</h3>

        <label>ID del pedido</label>
        <input type="number" id="id_pedido_detalle" min="1" required>

        <label>ID del producto</label>
        <input type="number" id="id_producto_detalle" min="1" required>

        <label>Cantidad</label>
        <input type="number" id="cantidad_detalle" min="1" required>

        <label>Precio unitario</label>
        <input type="number" id="precio_unitario_detalle" min="0" step="0.01" required>

        <label>Notas</label>
        <textarea id="notas_detalle"></textarea>

        <button type="submit">Registrar detalle</button>
    `;

    formulario.addEventListener("submit", registrarDetallePedido);

    document.getElementById("contenido").prepend(formulario);
}
async function registrarDetallePedido(event) {
    event.preventDefault();

    const formulario = event.target;
    const id = formulario.dataset.id;

    const datos = {
        id_pedido: Number(document.getElementById("id_pedido_detalle").value),
        id_producto: Number(document.getElementById("id_producto_detalle").value),
        cantidad: Number(document.getElementById("cantidad_detalle").value),
        precio_unitario: Number(document.getElementById("precio_unitario_detalle").value),
        notas: document.getElementById("notas_detalle").value
    };

    const metodo = id ? "PUT" : "POST";

    const url = id
        ? `${API_URL}/detalles-pedido/${id}`
        : `${API_URL}/detalles-pedido`;

    try {
        const respuesta = await fetch(url, {
            method: metodo,
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(datos)
        });

        const resultado = await respuesta.json();

        if (!respuesta.ok) {
            alert(resultado.error || "No se pudo guardar el detalle");
            return;
        }

        alert(id
            ? "Detalle de pedido actualizado correctamente"
            : "Detalle de pedido registrado correctamente"
        );

        cargarDetallesPedido();

    } catch (error) {
        console.error("Error:", error);
        alert("Error al conectar con el servidor");
    }
}
async function registrarPago(event) {
    event.preventDefault();

    const formulario = event.target;
    const id = formulario.dataset.id;

    const datos = {
        id_pedido: Number(document.getElementById("id_pedido_pago").value),
        id_cajero: Number(document.getElementById("id_cajero_pago").value),
        metodo_pago: document.getElementById("metodo_pago").value,
        monto: Number(document.getElementById("monto_pago").value)
    };

    const metodo = id ? "PUT" : "POST";

    const url = id
        ? `${API_URL}/pagos/${id}`
        : `${API_URL}/pagos`;

    try {
        const respuesta = await fetch(url, {
            method: metodo,
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(datos)
        });

        const resultado = await respuesta.json();

        if (!respuesta.ok) {
            alert(resultado.error || "No se pudo guardar el pago");
            return;
        }

        alert(id ? "Pago actualizado correctamente" : "Pago registrado correctamente");

        cargarPagos();

    } catch (error) {
        console.error("Error:", error);
        alert("Error al conectar con el servidor");
    }
}

async function registrarCategoria(event) {
    event.preventDefault();

    const formulario = event.target;
    const id = formulario.dataset.id;

    const datos = {
        nombre: document.getElementById("nombre_categoria").value.trim()
    };

    if (!datos.nombre) {
        alert("El nombre de la categoría no puede estar vacío");
        return;
    }

    const metodo = id ? "PUT" : "POST";

    const url = id
        ? `${API_URL}/categorias/${id}`
        : `${API_URL}/categorias`;

    try {
        const respuesta = await fetch(url, {
            method: metodo,
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(datos)
        });

        const resultado = await respuesta.json();

        if (!respuesta.ok) {
            alert(resultado.error || "No se pudo guardar la categoría");
            return;
        }

        alert(id
            ? "Categoría actualizada correctamente"
            : "Categoría registrada correctamente");

        cargarCategorias();

    } catch (error) {
        console.error("Error:", error);
        alert("Error al conectar con el servidor");
    }
}

async function registrarHistorialEstado(event) {
    event.preventDefault();

    const formulario = event.target;
    const id = formulario.dataset.id;

    const usuario = document.getElementById(
        "id_usuario_cambio"
    ).value;

    const datos = {
        estado: document.getElementById("estado_historial").value,

        rol_usuario_cambio:
            document.getElementById("rol_usuario_cambio").value || null,

        id_usuario_cambio:
            usuario ? Number(usuario) : null
    };

    if (!id) {
        datos.id_pedido = Number(
            document.getElementById("id_pedido_historial").value
        );
    }

    const metodo = id ? "PUT" : "POST";

    const url = id
        ? `${API_URL}/historial-estados/${id}`
        : `${API_URL}/historial-estados`;

    try {
        const respuesta = await fetch(url, {
            method: metodo,
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(datos)
        });

        const resultado = await respuesta.json();

        if (!respuesta.ok) {
            alert(resultado.error || "No se pudo guardar el historial");
            return;
        }

        alert(id
            ? "Historial actualizado correctamente"
            : "Historial registrado correctamente");

        cargarHistorialEstados();

    } catch (error) {
        console.error("Error:", error);
        alert("Error al conectar con el servidor");
    }
}

async function registrarPedido(event) {
    event.preventDefault();

    const formulario = event.target;
    const id = formulario.dataset.id;

    const tipo = document.getElementById("tipo_pedido").value;

    const datos = {
        tipo_pedido: tipo,

        id_mesa: tipo === "Mesa"
            ? Number(document.getElementById("id_mesa_pedido").value)
            : null,

        direccion_entrega: tipo === "Domicilio"
            ? document.getElementById("direccion_entrega").value.trim()
            : null,

        id_mesero: Number(
            document.getElementById("id_mesero_pedido").value
        ),

        estado: document.getElementById("estado_pedido").value.trim()
    };

    if (!datos.estado) {
        alert("El estado no puede estar vacío");
        return;
    }

    if (tipo === "Domicilio" && !datos.direccion_entrega) {
        alert("Debes ingresar una dirección de entrega");
        return;
    }

    const metodo = id ? "PUT" : "POST";

    const url = id
        ? `${API_URL}/pedidos/${id}`
        : `${API_URL}/pedidos`;

    try {
        const respuesta = await fetch(url, {
            method: metodo,
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(datos)
        });

        const resultado = await respuesta.json();

        if (!respuesta.ok) {
            alert(resultado.error || "No se pudo guardar el pedido");
            return;
        }

        alert(id
            ? "Pedido actualizado correctamente"
            : "Pedido registrado correctamente");

        cargarPedidos();

    } catch (error) {
        console.error("Error:", error);
        alert("Error al conectar con el servidor");
    }
}

async function registrarMesero(event) {
    event.preventDefault();

    const formulario = event.target;
    const id = formulario.dataset.id;

    const datos = {
        nombre: document.getElementById("nombre_mesero").value,
        usuario_login: document.getElementById("usuario_mesero").value,
        estado: Number(document.getElementById("estado_mesero").value)
    };

    const contrasena = document.getElementById("contrasena_mesero").value;

    if (contrasena) {
        datos.contrasena_hash = contrasena;
    }

    const metodo = id ? "PUT" : "POST";

    const url = id
        ? `${API_URL}/meseros/${id}`
        : `${API_URL}/meseros`;

    try {
        const respuesta = await fetch(url, {
            method: metodo,
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(datos)
        });

        const resultado = await respuesta.json();

        if (!respuesta.ok) {
            alert(resultado.error || "No se pudo guardar el mesero");
            return;
        }

        alert(id
            ? "Mesero actualizado correctamente"
            : "Mesero registrado correctamente");

        cargarMeseros();

    } catch (error) {
        console.error("Error:", error);
        alert("Error al conectar con el servidor");
    }
}

async function registrarCajero(event) {
    event.preventDefault();

    const formulario = event.target;
    const id = formulario.dataset.id;

    const datos = {
        nombre: document.getElementById("nombre_cajero").value,
        usuario_login: document.getElementById("usuario_cajero").value,
        estado: Number(document.getElementById("estado_cajero").value)
    };

    const contrasena = document.getElementById("contrasena_cajero").value;

    if (contrasena) {
        datos.contrasena_hash = contrasena;
    }

    const metodo = id ? "PUT" : "POST";

    const url = id
        ? `${API_URL}/cajeros/${id}`
        : `${API_URL}/cajeros`;

    try {
        const respuesta = await fetch(url, {
            method: metodo,
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(datos)
        });

        const resultado = await respuesta.json();

        if (!respuesta.ok) {
            alert(resultado.error || "No se pudo guardar el cajero");
            return;
        }

        alert(id
            ? "Cajero actualizado correctamente"
            : "Cajero registrado correctamente");

        cargarCajeros();

    } catch (error) {
        console.error("Error:", error);
        alert("Error al conectar con el servidor");
    }
}

async function registrarAdministrador(event) {
    event.preventDefault();

    const formulario = event.target;
    const id = formulario.dataset.id;

    const datos = {
        nombre: document.getElementById("nombre_administrador").value,
        usuario_login: document.getElementById("usuario_administrador").value,
        estado: document.getElementById("estado_administrador").value
    };

    const contrasena = document.getElementById("contrasena_administrador").value;

    if (contrasena) {
        datos.contrasena = contrasena;
    }

    const metodo = id ? "PUT" : "POST";
    const url = id
        ? `${API_URL}/administradores/${id}`
        : `${API_URL}/administradores`;

    try {
        const respuesta = await fetch(url, {
            method: metodo,
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(datos)
        });

        const resultado = await respuesta.json();

        if (!respuesta.ok) {
            alert(resultado.error || "No se pudo guardar el administrador");
            return;
        }

        alert(id ? "Administrador actualizado" : "Administrador registrado");

        cargarAdministradores();

    } catch (error) {
        console.error("Error:", error);
        alert("Error al conectar con el servidor");
    }
}

async function registrarCocina(event) {
    event.preventDefault();

    const formulario = event.currentTarget;
    const id = formulario.dataset.id;

    const cocina = {
        nombre: document.getElementById("nombre_cocina").value,
        usuario_login: document.getElementById("usuario_cocina").value,
        estado: Number(document.getElementById("estado_cocina").value)
    };

    const contrasena = document.getElementById("contrasena_cocina").value;

    if (contrasena) {
        cocina.contrasena = contrasena;
    }

    const url = id
        ? `${API_URL}/cocina/${id}`
        : `${API_URL}/cocina`;

    const metodo = id ? "PUT" : "POST";

    try {
        const respuesta = await fetch(url, {
            method: metodo,
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(cocina)
        });

        const resultado = await respuesta.json();

        if (!respuesta.ok) {
            throw new Error(resultado.error || "Error al guardar el registro");
        }

        alert(id
            ? "Registro de cocina actualizado correctamente"
            : "Personal de cocina registrado correctamente"
        );

        cargarCocina();

    } catch (error) {
        alert(error.message);
    }
}

async function registrarProducto(event) {

    event.preventDefault();

    const formulario = event.currentTarget;
    const id = formulario.dataset.id;

    const producto = {
        nombre: document.getElementById("nombre_producto").value,
        descripcion: document.getElementById("descripcion_producto").value,
        precio: Number(document.getElementById("precio_producto").value),
        disponibilidad: Number(document.getElementById("disponibilidad_producto").value),
        id_categoria: Number(document.getElementById("id_categoria").value)
    };

    const url = id
        ? `${API_URL}/productos/${id}`
        : `${API_URL}/productos`;

    const metodo = id ? "PUT" : "POST";

    try {

        const respuesta = await fetch(url, {
            method: metodo,
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(producto)
        });

        const resultado = await respuesta.json();

        if (!respuesta.ok) {
            throw new Error(resultado.error || "Error al guardar producto");
        }

        alert(id
            ? "Producto actualizado correctamente"
            : "Producto registrado correctamente"
        );

        cargarProductos();

    } catch (error) {
        alert(error.message);
    }
}



// Servicio REST de movimientos

async function cargarMovimientos() {

    await cargarDatos("movimientos", "Movimientos de inventario");

    const formulario = document.createElement("form");

    formulario.innerHTML = `
        <h3>Registrar movimiento de inventario</h3>

        <label>Insumo</label>
        <select id="id_inventario" required></select>

        <label>Tipo de movimiento</label>
        <select id="tipo_movimiento">
            <option value="Entrada">Entrada</option>
            <option value="Salida">Salida</option>
        </select>

        <label>Cantidad</label>
        <input type="number" id="cantidad_movimiento"
               min="0.01" step="0.01" required>

        <label>Motivo</label>
        <input type="text" id="motivo" maxlength="255">

        <button type="submit">Registrar movimiento</button>
    `;

    formulario.addEventListener("submit", registrarMovimiento);

    document.getElementById("contenido").prepend(formulario);

    try {

        const respuesta = await fetch(`${API_URL}/inventario`);

        if (!respuesta.ok) {
            throw new Error("Error al consultar inventario");
        }

        const insumos = await respuesta.json();

        insumos.forEach(insumo => {

            const opcion = document.createElement("option");

            opcion.value = insumo.id_inventario;
            opcion.textContent = `${insumo.nombre_insumo} - Stock: ${insumo.cantidad}`;

            formulario.querySelector("#id_inventario").appendChild(opcion);

        });

    } catch (error) {
        formulario.querySelector("button").disabled = true;
        alert(error.message);
    }
}




async function registrarCliente(event) {

    event.preventDefault();

    const formulario = event.currentTarget;
    const id = formulario.dataset.id;

    const cliente = {
        nombre: document.getElementById("nombre").value,
        telefono: document.getElementById("telefono").value,
        correo: document.getElementById("correo").value
    };

    const url = id
        ? `${API_URL}/clientes/${id}`
        : `${API_URL}/clientes`;

    const metodo = id ? "PUT" : "POST";

    try {

        const respuesta = await fetch(url, {
            method: metodo,
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(cliente)
        });

        const resultado = await respuesta.json();

        if (!respuesta.ok) {
            throw new Error(resultado.error || "Error al guardar");
        }

        alert(id
            ? "Cliente actualizado correctamente"
            : "Cliente registrado correctamente"
        );

        cargarClientes();

    } catch (error) {
        alert(error.message);
    }
}




async function registrarReserva(event) {

    event.preventDefault();

    const formulario = event.currentTarget;
    const id = formulario.dataset.id;

    const reserva = {
        id_cliente: Number(document.getElementById("id_cliente").value),
        id_mesa: Number(document.getElementById("id_mesa").value),
        fecha_reserva: document.getElementById("fecha_reserva")
            .value.replace("T", " ") + ":00",
        cantidad_personas: Number(document.getElementById("cantidad_personas").value),
        estado: document.getElementById("estado").value
    };

    const url = id
        ? `${API_URL}/reservas/${id}`
        : `${API_URL}/reservas`;

    const metodo = id ? "PUT" : "POST";

    try {

        const respuesta = await fetch(url, {
            method: metodo,
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(reserva)
        });

        const resultado = await respuesta.json();

        if (!respuesta.ok) {
            throw new Error(resultado.error || "Error al guardar reserva");
        }

        alert(id
            ? "Reserva actualizada correctamente"
            : "Reserva registrada correctamente"
        );

        cargarReservas();

    } catch (error) {
        alert(error.message);
    }
}




async function registrarMesa(event) {

    event.preventDefault();

    const formulario = event.currentTarget;
    const id = formulario.dataset.id;

    const mesa = {
        numero: Number(document.getElementById("numero").value),
        estado: document.getElementById("estado_mesa").value
    };

    const url = id
        ? `${API_URL}/mesas/${id}`
        : `${API_URL}/mesas`;

    const metodo = id ? "PUT" : "POST";

    try {

        const respuesta = await fetch(url, {
            method: metodo,
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(mesa)
        });

        const resultado = await respuesta.json();

        if (!respuesta.ok) {
            throw new Error(resultado.error || "Error al guardar mesa");
        }

        alert(id
            ? "Mesa actualizada correctamente"
            : "Mesa registrada correctamente"
        );

        cargarMesas();

    } catch (error) {
        alert(error.message);
    }
}




async function registrarInsumo(event) {

    event.preventDefault();

    const formulario = event.currentTarget;
    const id = formulario.dataset.id;

    const insumo = {
        nombre_insumo: document.getElementById("nombre_insumo").value,
        cantidad: Number(document.getElementById("cantidad").value),
        unidad_medida: document.getElementById("unidad_medida").value,
        stock_minimo: Number(document.getElementById("stock_minimo").value)
    };

    const url = id
        ? `${API_URL}/inventario/${id}`
        : `${API_URL}/inventario`;

    const metodo = id ? "PUT" : "POST";

    try {

        const respuesta = await fetch(url, {
            method: metodo,
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(insumo)
        });

        const resultado = await respuesta.json();

        if (!respuesta.ok) {
            throw new Error(resultado.error || "Error al guardar insumo");
        }

        alert(id
            ? "Insumo actualizado correctamente"
            : "Insumo registrado correctamente"
        );

        cargarInventario();

    } catch (error) {
        alert(error.message);
    }
}





async function registrarMovimiento(event) {

    event.preventDefault();

    const formulario = event.currentTarget;
    const id = formulario.dataset.id;

    const movimiento = {
        id_inventario: Number(document.getElementById("id_inventario").value),
        tipo_movimiento: document.getElementById("tipo_movimiento").value,
        cantidad: Number(document.getElementById("cantidad_movimiento").value),
        motivo: document.getElementById("motivo").value
    };

    const url = id
        ? `${API_URL}/movimientos/${id}`
        : `${API_URL}/movimientos`;

    const metodo = id ? "PUT" : "POST";

    try {

        const respuesta = await fetch(url, {
            method: metodo,
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(movimiento)
        });

        const resultado = await respuesta.json();

        if (!respuesta.ok) {
            throw new Error(resultado.error || "Error al guardar movimiento");
        }

        alert(id
            ? "Movimiento actualizado correctamente"
            : "Movimiento registrado correctamente"
        );

        cargarMovimientos();

    } catch (error) {
        alert(error.message);
    }
}


async function eliminarRegistro(endpoint, registro) {

    const identificadores = {
        clientes: "id_cliente",
        reservas: "id_reserva",
        mesas: "id_mesa",
        inventario: "id_inventario",
        movimientos: "id_movimiento",
        productos: "id_producto",
        cocina: "id_cocina",
        administradores: "id_administrador",
        pagos: "id_pago",
        "detalles-pedido": "id_detalle",
        cajeros: "id_cajero",
        categorias: "id_categoria",
        meseros: "id_mesero",
        pedidos: "id_pedido",
        "historial-estados": "id_historial",
    };

    const id = registro[identificadores[endpoint]];

    if (id == null) {
        alert("No se encontró el ID del registro");
        return;
    }

    if (!confirm("¿Estás seguro de eliminar este registro?")) {
        return;
    }

    try {

        const respuesta = await fetch(`${API_URL}/${endpoint}/${id}`, {
            method: "DELETE"
        });

        const resultado = await respuesta.json();

        if (!respuesta.ok) {
            throw new Error(resultado.error || "Error al eliminar");
        }

        alert("Registro eliminado correctamente");

        switch (endpoint) {
            case "clientes":
                cargarClientes();
                break;
            case "reservas":
                cargarReservas();
                break;
            case "mesas":
                cargarMesas();
                break;
            case "inventario":
                cargarInventario();
                break;
            case "movimientos":
                cargarMovimientos();
                break;
            case "productos":
                cargarDatos();
                break;
            case "cocina":
                cargarCocina();
                break;
            case "administradores":
                cargarAdministradores();
                break;
            case "pagos":
                cargarPagos();
                break;
            case "detalles-pedido":
               cargarDetallesPedido();
                break;
            case "cajeros":
                cargarCajeros();
                break;
            case "categorias":
                cargarCategorias();
                break;
            case "categorias":
                cargarCategorias();
                break;
            case "meseros":
                cargarMeseros();
                break;
            case "pedidos":
                cargarPedidos();
                break;
            case "historial-estados":
                cargarHistorialEstados();
                break;
        }

    } catch (error) {
        alert(error.message);
    }
}



function editarRegistro(endpoint, registro) {

    const formulario = document.querySelector("#contenido form");

    if (endpoint === "historial-estados") {

        formulario.dataset.id = registro.id_historial;

        const pedido = document.getElementById(
            "id_pedido_historial"
        );

        pedido.value = registro.id_pedido;
        pedido.disabled = true;

        document.getElementById("estado_historial").value =
            registro.estado;

        document.getElementById("rol_usuario_cambio").value =
            registro.rol_usuario_cambio ?? "";

        document.getElementById("id_usuario_cambio").value =
            registro.id_usuario_cambio ?? "";

        formulario.querySelector("h3").textContent =
            "Editar historial de estado";
    }

    if (endpoint === "pedidos") {

        formulario.dataset.id = registro.id_pedido;

        document.getElementById("tipo_pedido").value =
            registro.tipo_pedido;

        actualizarCamposPedido();

        document.getElementById("id_mesa_pedido").value =
            registro.id_mesa ?? "";

        document.getElementById("direccion_entrega").value =
            registro.direccion_entrega ?? "";

        document.getElementById("id_mesero_pedido").value =
            registro.id_mesero;

        document.getElementById("estado_pedido").value =
            registro.estado;

        formulario.querySelector("h3").textContent =
            "Editar pedido";
    }

    if (endpoint === "meseros") {

        formulario.dataset.id = registro.id_mesero;

        document.getElementById("nombre_mesero").value =
            registro.nombre ?? "";

        document.getElementById("usuario_mesero").value =
            registro.usuario_login ?? "";

        const contrasena = document.getElementById("contrasena_mesero");

        contrasena.value = "";
        contrasena.required = false;
        contrasena.placeholder = "Dejar vacía para conservar la contraseña";

        document.getElementById("estado_mesero").value =
            registro.estado;

        formulario.querySelector("h3").textContent =
            "Editar mesero";
    }

    if (endpoint === "categorias") {

        formulario.dataset.id = registro.id_categoria;

        document.getElementById("nombre_categoria").value =
            registro.nombre ?? "";

        formulario.querySelector("h3").textContent =
            "Editar categoría";
    }

    if (endpoint === "cajeros") {

        formulario.dataset.id = registro.id_cajero;

        document.getElementById("nombre_cajero").value =
            registro.nombre ?? "";

        document.getElementById("usuario_cajero").value =
            registro.usuario_login ?? "";

        const contrasena = document.getElementById("contrasena_cajero");

        contrasena.value = "";
        contrasena.required = false;
        contrasena.placeholder = "Dejar vacía para conservar la contraseña";

        document.getElementById("estado_cajero").value =
            registro.estado;

        formulario.querySelector("h3").textContent =
            "Editar cajero";
    }

    if (endpoint === "clientes") {

        formulario.dataset.id = registro.id_cliente;

        document.getElementById("nombre").value =
            registro.nombre ?? "";

        document.getElementById("telefono").value =
            registro.telefono ?? "";

        document.getElementById("correo").value =
            registro.correo ?? "";

        formulario.querySelector("h3").textContent =
            "Editar cliente";
    }
    if (endpoint === "detalles-pedido") {
        const formulario = document.querySelector("#contenido form");
    
        formulario.dataset.id = registro.id_detalle;
    
        document.getElementById("id_pedido_detalle").value = registro.id_pedido;
        document.getElementById("id_producto_detalle").value = registro.id_producto;
        document.getElementById("cantidad_detalle").value = registro.cantidad;
        document.getElementById("precio_unitario_detalle").value = registro.precio_unitario;
        document.getElementById("notas_detalle").value = registro.notas ?? "";
    
        formulario.querySelector("h3").textContent = "Editar detalle de pedido";
        formulario.querySelector("button[type='submit']").textContent = "Actualizar detalle";
    }
    if (endpoint === "pagos") {
        const formulario = document.querySelector("#contenido form");
    
        formulario.dataset.id = registro.id_pago;
    
        document.getElementById("id_pedido_pago").value = registro.id_pedido;
        document.getElementById("id_cajero_pago").value = registro.id_cajero;
        document.getElementById("metodo_pago").value = registro.metodo_pago;
        document.getElementById("monto_pago").value = registro.monto;
    
        formulario.querySelector("h3").textContent = "Editar pago";
        formulario.querySelector("button[type='submit']").textContent = "Actualizar pago";
    }
    if (endpoint === "administradores") {
        const formulario = document.querySelector("#contenido form");
    
        formulario.dataset.id = registro.id_administrador;
    
        document.getElementById("nombre_administrador").value = registro.nombre ?? "";
        document.getElementById("usuario_administrador").value = registro.usuario_login ?? "";
    
        const contrasena = document.getElementById("contrasena_administrador");
        contrasena.value = "";
        contrasena.required = false;
    
        document.getElementById("estado_administrador").value = registro.estado;
    
        formulario.querySelector("h3").textContent = "Editar administrador";
        formulario.querySelector("button[type='submit']").textContent = "Actualizar administrador";
    }

    if (endpoint === "reservas") {

        formulario.dataset.id = registro.id_reserva;

        document.getElementById("id_cliente").value =
            registro.id_cliente;

        document.getElementById("id_mesa").value =
            registro.id_mesa;

        document.getElementById("fecha_reserva").value =
            registro.fecha_reserva.replace(" ", "T").slice(0, 16);

        document.getElementById("cantidad_personas").value =
            registro.cantidad_personas;

        document.getElementById("estado").value =
            registro.estado;

        formulario.querySelector("h3").textContent =
            "Editar reserva";
    }
      if (endpoint === "mesas") {

      formulario.dataset.id = registro.id_mesa;

      document.getElementById("numero").value =
          registro.numero;

      document.getElementById("estado_mesa").value =
          registro.estado;

      formulario.querySelector("h3").textContent =
          "Editar mesa";
  }

    if (endpoint === "inventario") {

        formulario.dataset.id = registro.id_inventario;

        document.getElementById("nombre_insumo").value =
            registro.nombre_insumo;

        document.getElementById("cantidad").value =
            registro.cantidad;

        document.getElementById("unidad_medida").value =
            registro.unidad_medida;

        document.getElementById("stock_minimo").value =
            registro.stock_minimo ?? 0;

        formulario.querySelector("h3").textContent =
            "Editar insumo";
    }

if (endpoint === "productos") {

    formulario.dataset.id = registro.id_producto;

    document.getElementById("nombre_producto").value =
        registro.nombre ?? "";

    document.getElementById("descripcion_producto").value =
        registro.descripcion ?? "";

    document.getElementById("precio_producto").value =
        registro.precio ?? "";

    document.getElementById("disponibilidad_producto").value =
        registro.disponibilidad;

    document.getElementById("id_categoria").value =
        registro.id_categoria;

    formulario.querySelector("h3").textContent =
        "Editar producto";
}

if (endpoint === "cocina") {
    formulario.dataset.id = registro.id_cocina;

    document.getElementById("nombre_cocina").value =
        registro.nombre ?? "";

    document.getElementById("usuario_cocina").value =
        registro.usuario_login ?? "";

    document.getElementById("contrasena_cocina").value = "";
    document.getElementById("contrasena_cocina").required = false;

    document.getElementById("estado_cocina").value =
        registro.estado;

    formulario.querySelector("h3").textContent =
        "Editar personal de cocina";
}




    if (endpoint === "movimientos") {

        formulario.dataset.id = registro.id_movimiento;

        document.getElementById("id_inventario").value =
            registro.id_inventario;

        document.getElementById("tipo_movimiento").value =
            registro.tipo_movimiento;

        document.getElementById("cantidad_movimiento").value =
            registro.cantidad;

        document.getElementById("motivo").value =
            registro.motivo ?? "";

        formulario.querySelector("h3").textContent =
            "Editar movimiento";
    }


    formulario.querySelector("button[type='submit']").textContent =
        "Guardar cambios";

    formulario.scrollIntoView({
        behavior: "smooth"
    });
}
