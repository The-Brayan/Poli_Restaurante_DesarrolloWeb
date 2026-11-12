
package com.polirestaurante.consola;

import com.polirestaurante.DAO.CategoriaRepository;
import com.polirestaurante.modelo.Categoria;
import org.springframework.boot.CommandLineRunner;
import org.springframework.stereotype.Component;

import java.util.List;
import java.util.Scanner;

@Component
public class MenuCategorias implements CommandLineRunner {

    private final CategoriaRepository categoriaRepository;

    public MenuCategorias(CategoriaRepository categoriaRepository) {
        this.categoriaRepository = categoriaRepository;
    }

    @Override
    public void run(String... args) {
        Scanner sc = new Scanner(System.in);
        int opcion;

        do {
            System.out.println("\n--- CRUD CATEGORÍAS ---");
            System.out.println("1. Crear");
            System.out.println("2. Listar");
            System.out.println("3. Ver una");
            System.out.println("4. Editar");
            System.out.println("5. Eliminar");
            System.out.println("0. Salir");
            System.out.print("Seleccione: ");

            try {
                opcion = Integer.parseInt(sc.nextLine());

                switch (opcion) {
                    case 1 -> crear(sc);
                    case 2 -> listar();
                    case 3 -> verUna(sc);
                    case 4 -> editar(sc);
                    case 5 -> eliminar(sc);
                    case 0 -> System.out.println("Programa finalizado.");
                    default -> System.out.println("Opción no válida.");
                }
            } catch (NumberFormatException e) {
                opcion = -1;
                System.out.println("Debes ingresar un número.");
            } catch (Exception e) {
                opcion = -1;
                System.out.println("Error: " + e.getMessage());
            }

        } while (opcion != 0);
    }

    private void crear(Scanner sc) {
        Categoria categoria = new Categoria();

        System.out.print("Nombre de la categoría: ");
        categoria.setNombre(sc.nextLine());

        categoriaRepository.save(categoria);
        System.out.println("Categoría creada correctamente.");
    }

    private void listar() {
        List<Categoria> categorias = categoriaRepository.findAll();

        if (categorias.isEmpty()) {
            System.out.println("No hay categorías registradas.");
            return;
        }

        for (Categoria c : categorias) {
            System.out.println(
                "ID: " + c.getId_categoria()
                + " | Nombre: " + c.getNombre()
            );
        }
    }

    private void verUna(Scanner sc) {
        System.out.print("ID de la categoría: ");
        Integer id = Integer.parseInt(sc.nextLine());

        Categoria c = categoriaRepository.findById(id).orElse(null);

        if (c == null) {
            System.out.println("Categoría no encontrada.");
        } else {
            System.out.println("ID: " + c.getId_categoria());
            System.out.println("Nombre: " + c.getNombre());
        }
    }

    private void editar(Scanner sc) {
        System.out.print("ID de la categoría a editar: ");
        Integer id = Integer.parseInt(sc.nextLine());

        Categoria c = categoriaRepository.findById(id).orElse(null);

        if (c == null) {
            System.out.println("Categoría no encontrada.");
            return;
        }

        System.out.print("Nuevo nombre: ");
        c.setNombre(sc.nextLine());

        categoriaRepository.save(c);
        System.out.println("Categoría actualizada correctamente.");
    }

    private void eliminar(Scanner sc) {
        System.out.print("ID de la categoría a eliminar: ");
        Integer id = Integer.parseInt(sc.nextLine());

        if (!categoriaRepository.existsById(id)) {
            System.out.println("Categoría no encontrada.");
            return;
        }

        categoriaRepository.deleteById(id);
        System.out.println("Categoría eliminada correctamente.");
    }
}
