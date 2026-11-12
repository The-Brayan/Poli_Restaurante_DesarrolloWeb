
package com.polirestaurante.controlador;

import com.polirestaurante.DAO.CategoriaRepository;
import com.polirestaurante.modelo.Categoria;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/categorias")
public class CategoriaController {

    @Autowired
    private CategoriaRepository categoriaRepository;


    @PostMapping
    public ResponseEntity<Categoria> crearCategoria(
            @RequestBody Categoria categoria) {

        Categoria guardada = categoriaRepository.save(categoria);
        return ResponseEntity.status(HttpStatus.CREATED).body(guardada);
    }

    
    @GetMapping
    public List<Categoria> listarCategorias() {
        return categoriaRepository.findAll();
    }

    
    @GetMapping("/{id}")
    public ResponseEntity<Categoria> obtenerCategoriaPorId(
            @PathVariable Integer id) {

        return categoriaRepository.findById(id)
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }

    
    @PutMapping("/{id}")
    public ResponseEntity<Categoria> actualizarCategoria(
            @PathVariable Integer id,
            @RequestBody Categoria detallesCategoria) {

        return categoriaRepository.findById(id)
                .map(categoria -> {
                    categoria.setNombre(detallesCategoria.getNombre());
                    Categoria actualizada =
                            categoriaRepository.save(categoria);
                    return ResponseEntity.ok(actualizada);
                })
                .orElse(ResponseEntity.notFound().build());
    }

    
    @DeleteMapping("/{id}")
    public ResponseEntity<Void> eliminarCategoria(
            @PathVariable Integer id) {

        if (!categoriaRepository.existsById(id)) {
            return ResponseEntity.notFound().build();
        }

        categoriaRepository.deleteById(id);
        return ResponseEntity.noContent().build();
    }
}
