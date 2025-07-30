package com.example.spring_ftl.controller;

import com.example.spring_ftl.dto.ValuesListCallDTO;
import com.example.spring_ftl.service.JavaClassAnalyzer;
import com.example.spring_ftl.service.PanelManagerParserService;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.MediaType;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.io.File;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.util.*;
import java.util.stream.Collectors;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;
import java.util.Map;


@RestController
@RequestMapping("/api/parser")
public class ValuesListParserController {

    private final PanelManagerParserService parserService;

    public ValuesListParserController() {
        this.parserService = new PanelManagerParserService();
    }

    @Autowired
    private JavaClassAnalyzer javaClassAnalyzer;

    private final ObjectMapper objectMapper = new ObjectMapper();

    @PostMapping(value = "/fromCode", consumes = MediaType.TEXT_PLAIN_VALUE, produces = MediaType.APPLICATION_JSON_VALUE)
    public List<ValuesListCallDTO> parseFromCode(@RequestBody String javaCode) throws IOException {
        List<ValuesListCallDTO> result = parseLogic(javaCode);
        saveJsonToFile(result, "parsed_result.json");
        return result;
    }

    @PostMapping(value = "/fromFile", consumes = MediaType.MULTIPART_FORM_DATA_VALUE, produces = MediaType.APPLICATION_JSON_VALUE)
    public List<ValuesListCallDTO> parseFromFile(@RequestParam("file") MultipartFile file) throws IOException {
        String javaCode = new String(file.getBytes(), StandardCharsets.UTF_8);
        List<ValuesListCallDTO> allResults = parseLogic(javaCode);

        // Filtrer uniquement les champs de type 'lov'
        List<ValuesListCallDTO> lovResults = allResults.stream()
                .filter(dto -> "lov".equalsIgnoreCase(dto.getType()))
                .toList();

        // Sauvegarder dans filters.json (écrasé à chaque fois)
        saveJsonToFile(lovResults, "filters.json");

        return lovResults;
    }

    // 🎯 Regroupement intelligent avec nom de méthode personnalisé
    private List<ValuesListCallDTO> parseLogic(String javaCode) {
        List<ValuesListCallDTO> original = parserService.parsePanelManager(javaCode);

        Map<String, String> patternToUnifiedChamp = Map.of(
                "dev[1-9]", "devs",
                "rcedev[1-9]", "rcedevs",
                "cdev[1-9]", "cdevs",
                "ridtin[1-9]", "ridtins"
        );

        Set<ValuesListCallDTO> used = new HashSet<>();
        List<ValuesListCallDTO> result = new ArrayList<>();

        for (Map.Entry<String, String> entry : patternToUnifiedChamp.entrySet()) {
            String pattern = entry.getKey();
            String unifiedName = entry.getValue();

            List<ValuesListCallDTO> matched = original.stream()
                    .filter(dto -> dto.getChamp().matches(pattern))
                    .collect(Collectors.toList());

            if (!matched.isEmpty()) {
                ValuesListCallDTO unified = new ValuesListCallDTO();
                unified.setChamp(unifiedName);
                unified.setMethode("aini_" + unifiedName + "_valuesList");
                unified.setParametres(matched.get(0).getParametres()); // Tu peux fusionner tous les paramètres ici si besoin
                result.add(unified);
                used.addAll(matched);
            }
        }

        // Ajout des champs non utilisés
        result.addAll(original.stream()
                .filter(dto -> !used.contains(dto))
                .collect(Collectors.toList()));

        // Enrichissement type, filters, withParams
        for (ValuesListCallDTO dto : result) {
            // Déduire le type si absent
            if (dto.getType() == null) {
                if (dto.getMethode() != null && dto.getMethode().contains("valuesList")) {
                    dto.setType("lov");
                }
            }
            if (dto.getFilters() == null) {
                dto.setFilters(new ArrayList<>());
            }
            if ("lov".equalsIgnoreCase(dto.getType())) {
                boolean hasFilters = dto.getFilters() != null && !dto.getFilters().isEmpty();
                dto.setWithParams(!hasFilters);
            }
        }

        return result;
    }

    private void saveJsonToFile(List<ValuesListCallDTO> data, String filename) throws IOException {
        // Define output directory and ensure it exists
        File outputDir = new File("C:\\Users\\USER\\Downloads\\spring-ftl\\output");
        if (!outputDir.exists()) {
            outputDir.mkdirs();
        }

        File outputFile = new File(outputDir, filename);

        // Serialize and write to file
        objectMapper.writerWithDefaultPrettyPrinter().writeValue(outputFile, data);
    }
    @PostMapping(value = "/lov-fields", consumes = MediaType.MULTIPART_FORM_DATA_VALUE, produces = MediaType.APPLICATION_JSON_VALUE)
    public ResponseEntity<?> extractLovFieldsFromJavaFile(@RequestParam("file") MultipartFile file) {
        try {
            // 1. Lire le contenu du fichier Java
            String javaSource = new String(file.getBytes(), StandardCharsets.UTF_8);
    
            // 2. Extraire les champs de type LOV même s'ils sont vides
            List<ValuesListCallDTO> allLovFields = parserService.extractAllLovFieldsIncludingEmpty(javaSource);
    
            // 3. Vérifier si des champs ont été extraits
            if (allLovFields.isEmpty()) {
                return ResponseEntity.status(HttpStatus.NOT_FOUND)
                                     .body("❌ Aucun champ de type 'lov' trouvé.");
            }
    
            // 4. Sauvegarder dans un fichier JSON
            saveJsonToFile(allLovFields, "lov_fields_from_java.json");
    
            // 5. Retourner les résultats
            return ResponseEntity.ok(allLovFields);
    
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                                 .body("❌ Erreur lors du traitement du fichier Java : " + e.getMessage());
        }
    }
    



}
