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

    @GetMapping("/crear")
    public String crearCategoriaPrueba() {
        Categoria c = new Categoria();
        c.setNombre("Bebidas y Cocteles");
        categoriaRepository.save(c); 
        return "¡Categoría guardada con éxito en la base de datos!";
    }

    @GetMapping
    public List<Categoria> listarCategorias() {
        return categoriaRepository.findAll(); 
    }
}
