package com.example.spring_ftl.controller;

import com.example.spring_ftl.dto.FieldVisibilityLink;
import com.example.spring_ftl.service.VisibilityAnalyzerService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/visibility-analyzer")
@CrossOrigin(origins = "*")
public class VisibiltyAnalyzerController {

    @Autowired
    private VisibilityAnalyzerService visibilityAnalyzerService;

        @PostMapping("/analyze/file")
        public ResponseEntity<Map<String, Object>> analyzeFile(@RequestParam("file") MultipartFile file) {
            try {
                // Validate file
                if (file == null || file.isEmpty()) {
                    return ResponseEntity.badRequest().body(Map.of("error", "Le fichier est vide"));
                }

                String originalFilename = file.getOriginalFilename();
                if (originalFilename == null || !originalFilename.endsWith(".java")) {
                    return ResponseEntity.badRequest().body(Map.of("error", "Seuls les fichiers .java sont acceptés"));
                }

                // Save temp file
                String tempFilePath = saveTempFile(file);

                // Analyze file using service
                List<FieldVisibilityLink> links = visibilityAnalyzerService.analyzeFile(tempFilePath);

                // Filter links for output
                List<FieldVisibilityLink> filteredLinks = visibilityAnalyzerService.filterLinksForOutput(links);

                // Save filtered links to JSON file
                saveLinksToJsonFile(filteredLinks);

                // Delete temp file
                Files.deleteIfExists(Paths.get(tempFilePath));

                // Extract formId from filename (implement this method yourself)
                String detectedFormId = extractFormIdFromFileName(originalFilename);

                // Build response map manually
                Map<String, Object> response = new HashMap<>();
                response.put("success", true);
                response.put("message", "Analyse de fichier terminée");
                response.put("fileName", originalFilename);
                response.put("formId", detectedFormId);
                response.put("linksCount", filteredLinks.size());
                response.put("links", filteredLinks);

                return ResponseEntity.ok(response);

            } catch (Exception e) {
                return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                        .body(Map.of("error", "Erreur lors de l'analyse: " + e.getMessage()));
            }
        }

        private void saveLinksToJsonFile(List<FieldVisibilityLink> links) {
            try {
                Path outputPath = Path.of("C:/Users/USER/Downloads/spring-ftl/output/fieldlink.json");
                Files.createDirectories(outputPath.getParent());

                com.fasterxml.jackson.databind.ObjectMapper mapper = new com.fasterxml.jackson.databind.ObjectMapper();

                Map<String, Object> result = new HashMap<>();
                result.put("success", true);
                result.put("outputPath", outputPath.toString());
                result.put("linksCount", links.size());
                result.put("links", links);

                mapper.writerWithDefaultPrettyPrinter().writeValue(outputPath.toFile(), result);

                System.out.println("✅ JSON sauvegardé dans : " + outputPath);

            } catch (IOException e) {
                System.err.println("❌ Erreur lors de la sauvegarde du fichier JSON: " + e.getMessage());
            }
        }

        // You still need to implement these utility methods:

        private String saveTempFile(MultipartFile file) throws IOException {
            Path tempDir = Files.createTempDirectory("spring_ftl_");
            Path tempFile = tempDir.resolve(file.getOriginalFilename());
            try (FileOutputStream fos = new FileOutputStream(tempFile.toFile())) {
                fos.write(file.getBytes());
            }
            return tempFile.toString();
        }

        private String extractFormIdFromFileName(String fileName) {
            // Simple example: remove .java extension and lowercase
            if (fileName == null) return "default";
            if (fileName.endsWith(".java")) {
                fileName = fileName.substring(0, fileName.length() - 5);
            }
            return fileName.toLowerCase();
        }
    }
