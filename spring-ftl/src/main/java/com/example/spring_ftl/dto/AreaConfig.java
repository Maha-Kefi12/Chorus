package com.example.spring_ftl.dto;

import java.util.List;

public class AreaConfig {
    private String area;
    private List<FieldConfig> fields;

    public String getArea() {
        return area;
    }

    public void setArea(String area) {
        this.area = area;
    }

    public List<FieldConfig> getFields() {
        return fields;
    }

    public void setFields(List<FieldConfig> fields) {
        this.fields = fields;
    }
}
