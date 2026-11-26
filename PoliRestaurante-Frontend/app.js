
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
        movimientos: "id_movimiento"
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
        }

    } catch (error) {
        alert(error.message);
    }
}



function editarRegistro(endpoint, registro) {

    const formulario = document.querySelector("#contenido form");

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
