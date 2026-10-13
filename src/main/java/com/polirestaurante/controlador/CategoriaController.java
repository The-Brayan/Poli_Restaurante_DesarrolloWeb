package com.polirestaurante.controlador;

import com.polirestaurante.DAO.CategoriaRepository;
import com.polirestaurante.modelo.Categoria;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

@RestController
@RequestMapping("/categorias")
public class CategoriaController {

    @Autowired
    private CategoriaRepository categoriaRepository;

    // 1. Ruta para insertar un dato de prueba automáticamente
    // Entra a: http://localhost:8080/categorias/crear
    @GetMapping("/crear")
    public String crearCategoriaPrueba() {
        Categoria c = new Categoria();
        c.setNombre("Bebidas y Cocteles");
        categoriaRepository.save(c); // ¡Aquí se ejecuta el INSERT hacia MySQL!
        return "¡Categoría guardada con éxito en la base de datos!";
    }

    // 2. Ruta para listar todas las categorías (El servicio Read)
    // Entra a: http://localhost:8080/categorias
    @GetMapping
    public List<Categoria> listarCategorias() {
        return categoriaRepository.findAll(); // ¡Aquí se ejecuta el SELECT de MySQL!
    }
}