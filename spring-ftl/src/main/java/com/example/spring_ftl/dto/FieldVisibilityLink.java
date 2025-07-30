package com.example.spring_ftl.dto;

import java.util.ArrayList;
import java.util.List;
import java.util.UUID;

public class FieldVisibilityLink {
    private boolean disabled;
    private String id;
    private String childFieldId;
    private String methodName;
    private String nature;
    private String beanId;
    private List<String> fatherFieldIds;

    public FieldVisibilityLink(String id, String childFieldId, List<String> fatherFieldIds) {
        this.id = id;
        this.childFieldId = childFieldId;
        this.methodName = "isFieldIdVisible";
        this.nature = "CONDITIONNALHIDDEN";
        this.beanId = "FonctionNameFieldLinkService";
        this.fatherFieldIds = new ArrayList<>(fatherFieldIds);
    }

    // Getters et setters
    public String getId() { return id; }
    public void setId(String id) { this.id = id; }

    public String getChildFieldId() { return childFieldId; }
    public void setChildFieldId(String childFieldId) { this.childFieldId = childFieldId; }

    public String getMethodName() { return methodName; }
    public void setMethodName(String methodName) { this.methodName = methodName; }

    public String getNature() { return nature; }
    public void setNature(String nature) { this.nature = nature; }

    public String getBeanId() { return beanId; }
    public void setBeanId(String beanId) { this.beanId = beanId; }

    public List<String> getFatherFieldIds() { return fatherFieldIds; }
    public void setFatherFieldIds(List<String> fatherFieldIds) { this.fatherFieldIds = fatherFieldIds; }

    @Override
    public String toString() {
        return "FieldVisibilityLink{" +
                "id='" + id + '\'' +
                ", childFieldId='" + childFieldId + '\'' +
                ", methodName='" + methodName + '\'' +
                ", nature='" + nature + '\'' +
                ", beanId='" + beanId + '\'' +
                ", fatherFieldIds=" + fatherFieldIds +
                '}';
    }
    public FieldVisibilityLink(String id, String childFieldId, List<String> fatherFieldIds,
                               String methodName, String nature, String beanId, boolean disabled) {
        this.id = id;
        this.childFieldId = childFieldId;
        this.fatherFieldIds = fatherFieldIds;
        this.methodName = methodName;
        this.nature = nature;
        this.beanId = beanId;
        this.disabled = disabled;
    }

    public boolean isDisabled() {
        return this.disabled;
    }
}

/**
 * Analyse un fichier Java et extrait les relations de visibilité
 */