package com.example.spring_ftl.service;

import com.example.spring_ftl.dto.AreaConfig;
import com.example.spring_ftl.dto.FieldConfig;
import com.example.spring_ftl.dto.LabelMappings;
import com.fasterxml.jackson.annotation.JsonInclude;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.JavaType;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.PropertyNamingStrategies;
import com.fasterxml.jackson.databind.node.ObjectNode;
import org.springframework.stereotype.Service;

import java.io.IOException;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.stream.Collectors;

@Service
public class JsonTransformerService {

    private final ObjectMapper objectMapper;

    public JsonTransformerService() {
        this.objectMapper = new ObjectMapper();
        objectMapper.setPropertyNamingStrategy(PropertyNamingStrategies.SNAKE_CASE);
        objectMapper.setSerializationInclusion(JsonInclude.Include.ALWAYS); // ✅ Move here
    }


    public Map<String, Map<String, FieldConfig>> transformJson(
            Map<String, Map<String, FieldConfig>> originalJson,
            List<LabelMappings> labelMappings,
            List<AreaConfig> areaConfigs) {

        // Deep copy to avoid mutating original
        Map<String, Map<String, FieldConfig>> workingCopy = deepCopy(originalJson);

        // Apply label mappings (set label1 = original label, label2 = new label)
        processLabels(workingCopy, labelMappings);

        // Apply area configs: set sortNumber, columnNumber, area by matching labels
        applyAreaConfigurations(workingCopy, areaConfigs);

        // Enforce defaults on sortNumber and columnNumber if missing
        enforceSortAndColumnNumbers(workingCopy);

        return workingCopy;
    }

    private Map<String, Map<String, FieldConfig>> deepCopy(Map<String, Map<String, FieldConfig>> original) {
        return original.entrySet().stream()
                .collect(Collectors.toMap(
                        Map.Entry::getKey,
                        e -> e.getValue().entrySet().stream()
                                .collect(Collectors.toMap(
                                        Map.Entry::getKey,
                                        entry -> cloneFieldConfig(entry.getValue()))
                                )
                ));
    }

    private FieldConfig cloneFieldConfig(FieldConfig original) {
        FieldConfig clone = new FieldConfig();
        clone.setId(original.getId());
        clone.setNature(original.getNature());
        clone.setLabel(original.getLabel());
        clone.setLabel1(original.getLabel1());
        clone.setLabel2(original.getLabel2());
        clone.setHidden(original.getHidden());
        clone.setReadOnly(original.getReadOnly());
        clone.setDefaultValue(original.getDefaultValue());
        clone.setSortNumber(original.getSortNumber());
        clone.setColumnNumber(original.getColumnNumber());
        clone.setArea(original.getArea());

        if ("lov".equalsIgnoreCase(original.getNature())) {
            clone.setLov(original.getLov());
            clone.setValueField(original.getValueField());
            clone.setDisplayTemplate(original.getDisplayTemplate());
        }
        return clone;
    }

    private void processLabels(Map<String, Map<String, FieldConfig>> json,
                               List<LabelMappings> labelMappings) {
        json.forEach((category, fields) -> {
            fields.forEach((fieldId, fieldConfig) -> {
                String originalLabel = fieldConfig.getLabel();
                fieldConfig.setLabel1(originalLabel);

                // Find matching labelMapping ignoring case, trimming spaces
                Optional<LabelMappings> mappingOpt = labelMappings.stream()
                        .filter(mapping -> mapping.getAncien() != null
                                && mapping.getAncien().trim().equalsIgnoreCase(originalLabel != null ? originalLabel.trim() : ""))
                        .findFirst();

                mappingOpt.ifPresent(mapping -> fieldConfig.setLabel2(mapping.getNouveau()));
            });
        });
    }

    private void applyAreaConfigurations(Map<String, Map<String, FieldConfig>> json,
                                         List<AreaConfig> areaConfigs) {
        areaConfigs.forEach(areaConfig -> {
            areaConfig.getFields().forEach(areaField -> {
                String areaFieldName = areaField.getName();

                // Find field in json by matching label1 or label2 to areaFieldName
                findFieldByLabel(json, areaFieldName).ifPresent(targetField -> {
                    // Update sortNumber and columnNumber from area config
                    targetField.setSortNumber(areaField.getSortNumber());
                    targetField.setColumnNumber(areaField.getColumnNumber());
                    targetField.setArea(areaConfig.getArea());

                    System.out.printf("Configured field %s: sort=%d, column=%d, area=%s%n",
                            targetField.getId(),
                            targetField.getSortNumber(),
                            targetField.getColumnNumber(),
                            targetField.getArea());
                });
            });
        });
    }

    private void enforceSortAndColumnNumbers(Map<String, Map<String, FieldConfig>> json) {
        json.values().forEach(fields -> {
            fields.values().forEach(field -> {
                if (field.getSortNumber() == null) {
                    field.setSortNumber(0); // default sortNumber if missing
                }
                if (field.getColumnNumber() == null) {
                    field.setColumnNumber(1); // default columnNumber if missing
                }
                // Optionally set default area if needed
                if (field.getArea() == null) {
                    field.setArea("Undefined");
                }
            });
        });
    }

    private Optional<FieldConfig> findFieldByLabel(Map<String, Map<String, FieldConfig>> json,
                                                   String searchTerm) {
        if (searchTerm == null || searchTerm.isEmpty()) return Optional.empty();

        return json.values().stream()
                .flatMap(fields -> fields.values().stream())
                .filter(field -> matchesFieldLabel(field, searchTerm))
                .findFirst();
    }

    private boolean matchesFieldLabel(FieldConfig field, String searchTerm) {
        if (searchTerm == null) return false;

        return searchTerm.equalsIgnoreCase(field.getLabel()) ||
                searchTerm.equalsIgnoreCase(field.getLabel1()) ||
                searchTerm.equalsIgnoreCase(field.getLabel2());
    }

    private boolean matchesNormalized(String fieldLabel, String searchNormalized) {
        if (fieldLabel == null) return false;
        return normalizeString(fieldLabel).equalsIgnoreCase(searchNormalized);
    }

    private String normalizeString(String input) {
        if (input == null) return "";
        // normalize accents, spaces, lowercase - you can add Apache Commons Lang if you want more advanced normalization
        return input.trim().toLowerCase().replaceAll("\\s+", " ");
    }

    public String serializeResult(Map<String, Map<String, FieldConfig>> transformedJson) throws IOException {
        Map<String, Map<String, JsonNode>> resultMap = transformedJson.entrySet().stream()
                .collect(Collectors.toMap(
                        Map.Entry::getKey,
                        entry -> entry.getValue().entrySet().stream()
                                .collect(Collectors.toMap(
                                        Map.Entry::getKey,
                                        fieldEntry -> {
                                            FieldConfig field = fieldEntry.getValue();
                                            ObjectNode node = objectMapper.valueToTree(field);
                                            node.remove("label");
                                            return node;
                                        }
                                ))
                ));

        objectMapper.setSerializationInclusion(JsonInclude.Include.ALWAYS);
        return objectMapper.writerWithDefaultPrettyPrinter().writeValueAsString(resultMap);
    }


    // Parsing method with ObjectMapper and snake_case naming strategy
    public Map<String, Map<String, FieldConfig>> parseJson(String jsonContent) throws JsonProcessingException {
        JavaType stringType = objectMapper.getTypeFactory().constructType(String.class);
        JavaType innerMapType = objectMapper.getTypeFactory()
                .constructMapType(Map.class, stringType, objectMapper.constructType(FieldConfig.class));
        JavaType outerMapType = objectMapper.getTypeFactory()
                .constructMapType(Map.class, stringType, innerMapType);

        return objectMapper.readValue(jsonContent, outerMapType);
    }
}
