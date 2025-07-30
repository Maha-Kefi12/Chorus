package com.example.spring_ftl.dto;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;

import java.util.List;
import java.util.Map;
@JsonIgnoreProperties(ignoreUnknown = true)

public class TransformationRequest {
    private Map<String, Map<String, FieldConfig>> originalJson;

    public Map<String, Map<String, FieldConfig>> getOriginalJson() {
        return originalJson;
    }

    public void setOriginalJson(Map<String, Map<String, FieldConfig>> originalJson) {
        this.originalJson = originalJson;
    }

    private List<LabelMappings> labelMappings;
    private List<AreaConfig> areaConfigs;



    public List<LabelMappings> getLabelMappings() {
        return labelMappings ;
    }

    public void setLabelMappings(List<LabelMappings> labelMappings) {
        this.labelMappings = labelMappings;
    }

    public List<AreaConfig> getAreaConfigs() {
        return areaConfigs;
    }

    public void setAreaConfigs(List<AreaConfig> areaConfigs) {
        this.areaConfigs = areaConfigs;
    }
}

