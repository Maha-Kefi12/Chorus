package com.example.spring_ftl.controller;

import com.example.spring_ftl.dto.AreaConfig;
import com.example.spring_ftl.dto.FieldConfig;
import com.example.spring_ftl.dto.LabelMappings;
import com.example.spring_ftl.dto.TransformationRequest;
import com.example.spring_ftl.service.JsonTransformerService;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ObjectNode;
import org.apache.commons.lang3.tuple.Pair;
import org.springframework.http.ResponseEntity;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.*;

import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.time.Instant;
import java.util.Arrays;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.stream.Collectors;
import com.fasterxml.jackson.databind.PropertyNamingStrategies;
import org.springframework.web.multipart.MultipartFile;
import com.fasterxml.jackson.databind.SerializationFeature;
import java.util.ArrayList;


@RestController
@RequestMapping("/transform")
public class JsonTransformerController {
    private final JsonTransformerService jsonTransformerService;
    private ObjectMapper objectMapper = new ObjectMapper()
            .setPropertyNamingStrategy(PropertyNamingStrategies.SNAKE_CASE);

    public JsonTransformerController(JsonTransformerService jsonTransformerService) {
        this.jsonTransformerService = jsonTransformerService;
    }

    @RestController
    @RequestMapping("/transform")
    public class TransformController {

        @PostMapping("/updateFieldOrder")
        public ResponseEntity<?> updateFieldOrder(@RequestBody TransformationRequest request) {
            try {
                // Get components from request
                Map<String, Map<String, FieldConfig>> originalJson = request.getOriginalJson();
                List<LabelMappings> labelMappings = request.getLabelMappings();
                List<AreaConfig> areaConfigs = request.getAreaConfigs();

                // Apply label mappings
                applyLabelMappings(originalJson, labelMappings);

                // Apply field ordering
                applyFieldOrdering(originalJson, areaConfigs);

                // Handle unordered fields (sortNumber = 0)
                handleUnorderedFields(originalJson);

                // Save updated transformation to file (overwrite each time)
                String json = objectMapper.writerWithDefaultPrettyPrinter().writeValueAsString(request);
                String outputPath = "C:\\Users\\USER\\Downloads\\spring-ftl\\output\\transformed_result.json";
                File outputFile = new File(outputPath);
                outputFile.getParentFile().mkdirs();

                try (FileWriter writer = new FileWriter(outputFile, false)) { // false = overwrite mode
                    writer.write(json);
                }

                // Return updated JSON (without raw label fields)
                return ResponseEntity.ok(serializeWithLabelVariants(originalJson));

            } catch (Exception e) {
                return ResponseEntity.badRequest().body(
                        Map.of(
                                "error", "Processing failed",
                                "message", e.getMessage(),
                                "timestamp", Instant.now().toString()
                        )
                );
            }
        }


        private void applyLabelMappings(Map<String, Map<String, FieldConfig>> json, List<LabelMappings> labelMappings) {
            json.values().stream()
                    .flatMap(group -> group.values().stream())
                    .forEach(field -> {
                        String originalLabel = field.getLabel();
                        field.setLabel1(originalLabel); // Preserve original label

                        // Apply mapping if exists
                        labelMappings.stream()
                                .filter(mapping -> mapping.getAncien().equalsIgnoreCase(originalLabel))
                                .findFirst()
                                .ifPresent(mapping -> field.setLabel2(mapping.getNouveau()));
                    });
        }
        private String serializeWithLabelVariants(Map<String, Map<String, FieldConfig>> transformedJson) throws IOException {
            Map<String, Map<String, com.fasterxml.jackson.databind.JsonNode>> resultMap = transformedJson.entrySet().stream()
                    .collect(Collectors.toMap(
                            Map.Entry::getKey,
                            entry -> entry.getValue().entrySet().stream()
                                    .collect(Collectors.toMap(
                                            Map.Entry::getKey,
                                            fieldEntry -> {
                                                FieldConfig field = fieldEntry.getValue();
                                                ObjectNode node = objectMapper.valueToTree(field);
                                                node.remove("label");
                                                node.remove("editable");// Remove only the raw 'label', keep label1 and label2
                                                return node;
                                            })
                                    )
                    ));
            objectMapper.setSerializationInclusion(com.fasterxml.jackson.annotation.JsonInclude.Include.ALWAYS);
            return objectMapper.writerWithDefaultPrettyPrinter().writeValueAsString(resultMap);
        }


        private void applyFieldOrdering(Map<String, Map<String, FieldConfig>> json, List<AreaConfig> areaConfigs) {
            // Create mapping of label to sort/column info
            Map<String, Pair<Integer, Integer>> labelToOrderInfo = new HashMap<>();

            areaConfigs.forEach(area ->
                    area.getFields().forEach(field ->
                            labelToOrderInfo.put(field.getName().trim(),
                                    Pair.of(field.getSort_number(), field.getColumnNumber()))
                    )
            );

            // Apply ordering to all fields
            json.values().stream()
                    .flatMap(group -> group.values().stream())
                    .forEach(field -> {
                        // Try label2 first, then label1 as fallback
                        String lookupLabel = field.getLabel2() != null ? field.getLabel2() : field.getLabel1();

                        if (lookupLabel != null && labelToOrderInfo.containsKey(lookupLabel.trim())) {
                            Pair<Integer, Integer> orderInfo = labelToOrderInfo.get(lookupLabel.trim());
                            field.setSortNumber(orderInfo.getLeft());
                            field.setColumnNumber(orderInfo.getRight());
                        } else {
                            // Default values if no mapping found
                            field.setSortNumber(0);
                            field.setColumnNumber(0);
                        }
                    });
        }

        private void handleUnorderedFields(Map<String, Map<String, FieldConfig>> json) {
            int maxSortNumber = json.values().stream()
                    .flatMap(group -> group.values().stream())
                    .mapToInt(field -> field.getSortNumber() != null ? field.getSortNumber() : 0)
                    .max()
                    .orElse(0);

            AtomicInteger currentSortNumber = new AtomicInteger(maxSortNumber);

            json.values().stream()
                    .flatMap(group -> group.values().stream())
                    .filter(field -> (field.getSortNumber() == null || field.getSortNumber() == 0)
                            && (field.getColumnNumber() == null || field.getColumnNumber() == 0))
                    .forEach(field -> {
                        field.setSortNumber(currentSortNumber.incrementAndGet());
                        field.setColumnNumber(1);
                    });
        }


        private String serializeWithoutLabel(Map<String, Map<String, FieldConfig>> transformedJson) throws IOException {
            Map<String, Map<String, Map<String, Object>>> resultMap = transformedJson.entrySet().stream()
                    .collect(Collectors.toMap(
                            Map.Entry::getKey,
                            entry -> entry.getValue().entrySet().stream()
                                    .collect(Collectors.toMap(
                                            Map.Entry::getKey,
                                            fieldEntry -> {
                                                FieldConfig field = fieldEntry.getValue();
                                                Map<String, Object> fieldMap = objectMapper.convertValue(field, Map.class);
                                                // Remove all label-related fields from final output
                                                fieldMap.remove("label");
                                                fieldMap.remove("label1");
                                                fieldMap.remove("label2");
                                                return fieldMap;
                                            })
                                    )
                    ));
            return objectMapper.writerWithDefaultPrettyPrinter().writeValueAsString(resultMap);
        }

        // Save transformation request endpoint
        @PostMapping("/save-transformation")
        public ResponseEntity<String> saveTransformationRequest(@RequestBody TransformationRequest request) {
            try {
                // Serialize request back to JSON string
                String json = objectMapper.writerWithDefaultPrettyPrinter().writeValueAsString(request);

                // Save JSON to file
                String outputPath = "C:\\Users\\USER\\Downloads\\spring-ftl\\output\\correspondance.json";
                File outputFile = new File(outputPath);
                outputFile.getParentFile().mkdirs(); // Ensure directory exists

                try (FileWriter writer = new FileWriter(outputFile, false)) {
                    writer.write(json);
                }

                return ResponseEntity.ok("TransformationRequest JSON saved successfully at " + outputFile.getAbsolutePath());
            } catch (IOException e) {
                e.printStackTrace();
                return ResponseEntity.internalServerError()
                        .body("Failed to save TransformationRequest JSON: " + e.getMessage());
            }
        }

        @PostMapping("/field-mapping-table")
        public ResponseEntity<?> getFieldMappingTable(@RequestBody TransformationRequest request) {
            Map<String, Map<String, FieldConfig>> originalJson = request.getOriginalJson();
            List<LabelMappings> labelMappings = request.getLabelMappings();
            List<AreaConfig> areaConfigs = request.getAreaConfigs();

            // Build a mapping from all possible label/label2/label1/ancien/nouveau to fieldId
            Map<String, org.apache.commons.lang3.tuple.Pair<String, FieldConfig>> labelToField = new HashMap<>();
            for (Map.Entry<String, Map<String, FieldConfig>> group : originalJson.entrySet()) {
                for (Map.Entry<String, FieldConfig> entry : group.getValue().entrySet()) {
                    FieldConfig field = entry.getValue();
                    String id = entry.getKey();
                    if (field.getLabel() != null) labelToField.put(field.getLabel().trim(), org.apache.commons.lang3.tuple.Pair.of(id, field));
                    if (field.getLabel1() != null) labelToField.put(field.getLabel1().trim(), org.apache.commons.lang3.tuple.Pair.of(id, field));
                    if (field.getLabel2() != null) labelToField.put(field.getLabel2().trim(), org.apache.commons.lang3.tuple.Pair.of(id, field));
                }
            }
            // Add labelMappings
            for (LabelMappings mapping : labelMappings) {
                for (Map.Entry<String, Map<String, FieldConfig>> group : originalJson.entrySet()) {
                    for (Map.Entry<String, FieldConfig> entry : group.getValue().entrySet()) {
                        FieldConfig field = entry.getValue();
                        String id = entry.getKey();
                        if (field.getLabel() != null && (field.getLabel().equals(mapping.getAncien()) || field.getLabel().equals(mapping.getNouveau()))) {
                            labelToField.put(mapping.getAncien(), org.apache.commons.lang3.tuple.Pair.of(id, field));
                            labelToField.put(mapping.getNouveau(), org.apache.commons.lang3.tuple.Pair.of(id, field));
                        }
                    }
                }
            }

            // Build the result table
            List<Map<String, Object>> result = new java.util.ArrayList<>();
            String formId = groupKey(originalJson);
            
            // Process area configs
            for (AreaConfig area : areaConfigs) {
                for (FieldConfig field : area.getFields()) {
                    String name = field.getName().trim();
                    org.apache.commons.lang3.tuple.Pair<String, FieldConfig> match = labelToField.get(name);
                    if (match == null) {
                        // Try labelMappings
                        for (LabelMappings mapping : labelMappings) {
                            if (mapping.getNouveau().equals(name) && labelToField.containsKey(mapping.getAncien())) {
                                match = labelToField.get(mapping.getAncien());
                                break;
                            }
                        }
                    }
                    if (match != null) {
                        String fieldId = match.getLeft();
                        FieldConfig fieldData = match.getRight();
                        // Use labelMappings for label if available
                        String label = name;
                        for (LabelMappings mapping : labelMappings) {
                            if (mapping.getNouveau().equals(name) || mapping.getAncien().equals(name)) {
                                label = mapping.getNouveau();
                                break;
                            }
                        }
                        Map<String, Object> row = new HashMap<>();
                        row.put("formId", formId);
                        row.put("fieldId", fieldId);
                        row.put("area", area.getArea());
                        row.put("sortNumber", field.getSort_number());
                        row.put("columnNumber", field.getColumnNumber());
                        row.put("label", label);
                        result.add(row);
                    }
                }
            }

            // Always add static panel fields
            addStaticPanelFields(result, formId);

            // Save to area_map.json file
            try {
                saveToAreaMapJson(result, formId);
            } catch (Exception e) {
                return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body("Error saving to area_map.json: " + e.getMessage());
            }

            return ResponseEntity.ok(result);
        }

        private void addStaticPanelFields(List<Map<String, Object>> result, String formId) {
            // Static panel field definitions
            Map<String, List<Map<String, Object>>> staticPanels = new HashMap<>();
            
            // valeurPanel static fields (area2)
            staticPanels.put("valeurPanel", Arrays.asList(
                Map.of("fieldId", "reiv_rceval", "area", "Critères avancés", "sortNumber", 1, "columnNumber", 2, "label", "Revenu évalué"),
                Map.of("fieldId", "reiv_ridori", "area", "Critères avancés", "sortNumber", 2, "columnNumber", 2, "label", "Revenu origine"),
                Map.of("fieldId", "reic_rcepla", "area", "Critères avancés", "sortNumber", 3, "columnNumber", 2, "label", "Revenu crédit place"),
                Map.of("fieldId", "iprap_adtvalid", "area", "Critères avancés", "sortNumber", 4, "columnNumber", 2, "label", "Date de validation"),
                Map.of("fieldId", "rgvlm_rllgvl", "area", "Critères avancés", "sortNumber", 5, "columnNumber", 2, "label", "Réglement valeur")
            ));
            
            // csoPanel static fields (area3)
            staticPanels.put("csoPanel", Arrays.asList(
                Map.of("fieldId", "riddev", "area", "Critères de consolidation", "sortNumber", 1, "columnNumber", 1, "label", "Risque de défaut"),
                Map.of("fieldId", "adtchgo", "area", "Critères de consolidation", "sortNumber", 1, "columnNumber", 2, "label", "Date de changement"),
                Map.of("fieldId", "rcepla", "area", "Critères de consolidation", "sortNumber", 2, "columnNumber", 2, "label", "Risque de crédit"),
                Map.of("fieldId", "acetdev", "area", "Critères de consolidation", "sortNumber", 2, "columnNumber", 1, "label", "Acceptation de défaut")
            ));

            // Add static panel fields to result
            for (Map<String, Object> staticField : staticPanels.get("valeurPanel")) {
                Map<String, Object> row = new HashMap<>();
                row.put("formId", formId);
                row.put("fieldId", staticField.get("fieldId"));
                row.put("area", staticField.get("area"));
                row.put("sortNumber", staticField.get("sortNumber"));
                row.put("columnNumber", staticField.get("columnNumber"));
                row.put("label", staticField.get("label"));
                result.add(row);
            }

            for (Map<String, Object> staticField : staticPanels.get("csoPanel")) {
                Map<String, Object> row = new HashMap<>();
                row.put("formId", formId);
                row.put("fieldId", staticField.get("fieldId"));
                row.put("area", staticField.get("area"));
                row.put("sortNumber", staticField.get("sortNumber"));
                row.put("columnNumber", staticField.get("columnNumber"));
                row.put("label", staticField.get("label"));
                result.add(row);
            }
        }

        private void saveToAreaMapJson(List<Map<String, Object>> result, String formId) throws Exception {
            // Convert result to area_map.json format
            List<Map<String, Object>> areaMapData = new ArrayList<>();
            
            for (Map<String, Object> row : result) {
                Map<String, Object> entry = new HashMap<>();
                entry.put("formId", row.get("formId"));
                entry.put("area", row.get("area"));
                entry.put("columnNumber", row.get("columnNumber"));
                entry.put("sortNumber", row.get("sortNumber"));
                entry.put("label", row.get("label"));
                entry.put("fieldId", row.get("fieldId"));
                areaMapData.add(entry);
            }

            // Get the output directory path
            String outputPath = System.getProperty("user.dir") + "/output/area_map.json";
            File outputFile = new File(outputPath);
            
            // Create parent directories if they don't exist
            outputFile.getParentFile().mkdirs();

            // Write JSON to file
            ObjectMapper mapper = new ObjectMapper();
            mapper.enable(SerializationFeature.INDENT_OUTPUT);
            mapper.writeValue(outputFile, areaMapData);
        }

        // Helper to get the first key of originalJson (form id)
        private String groupKey(Map<String, Map<String, FieldConfig>> originalJson) {
            return originalJson.keySet().stream().findFirst().orElse("");
        }
    }
}