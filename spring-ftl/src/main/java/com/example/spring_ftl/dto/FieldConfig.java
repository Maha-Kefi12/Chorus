package com.example.spring_ftl.dto;

import com.fasterxml.jackson.annotation.*;

@JsonInclude(JsonInclude.Include.NON_NULL)
public class FieldConfig {
    // === CHAMPS DE CORRESPONDANCE UNIQUEMENT ===
    // Basés sur le tableau de correspondance fourni
    @JsonIgnore
    private String formId;
    private String id;              // name → id (renommage)
    private String nature;          // type → nature (renommage)
    private String hidden;          // visible → hidden (valeur inversée)
    private String readOnly;
    private Integer columnNumber;
    private Integer sortNumber;
    @JsonProperty("column_number")
    private Integer column_number;

    public Integer getSort_number() {
        return sort_number;
    }

    public void setSort_number(Integer sort_number) {
        this.sort_number = sort_number;
    }

    public Integer getColumn_number() {
        return column_number;
    }

    public void setColumn_number(Integer column_number) {
        this.column_number = column_number;
    }

    @JsonProperty("sort_number")
    private Integer sort_number;
    // inchangé - ordre d'affichage en colonne
    private String defaultValue;
    private String area;

    // Labels - IMPORTANT: pas d'annotations Jackson pour éviter les conflits
    private String label1;  // Ancien libellé
    private String label2;  // Nouveau libellé
    private String label;   // Label principal (pour JSON)

    private String name; // Add this new field

    // LOV fields
    private String maxDualFieldValues;
    private String visible;

    // Champs LOV de correspondance
    private String displayField;
    private String preValueField;
    private String preDisplayField;

    // Champs techniques (toujours null sauf pour LOV)
    private String type;
    private String lov;
    private String valueField;
    private String displayTemplate;

    // === GETTERS ET SETTERS POUR LABELS ===

    // Label1 - pas d'annotation Jackson pour éviter les conflits
    public String getLabel1() {
        return label1;
    }
    @JsonProperty("label1")
    public void setLabel1(String label1) {
        this.label1 = label1;
    }
    @JsonProperty("label2")
    // Label2 - pas d'annotation Jackson pour éviter les conflits
    public String getLabel2() {
        return label2;
    }
    public void setLabel2(String label2) {
        this.label2 = label2;
    }

    // Label principal - utilisé pour la sérialisation JSON
    @JsonGetter("label")
    public String getLabel() {
        System.out.println("getLabel() called, label = '" + label + "'");
        return label != null ? label : "";
    }

    @JsonSetter("label")
    public void setLabel(String label) {
        System.out.println("FieldConfig.setLabel called with: '" + label + "'");
        if(label == null) {
            this.label = "";
        } else {
            this.label = label;
        }
    }

    // === GETTERS POUR JSON (SEULEMENT CHAMPS DE CORRESPONDANCE) ===

    @JsonGetter("name")
    public String getName() {
        return name;
    }

    @JsonSetter("name")
    public void setName(String name) {
        this.name = name;
    }

    @JsonGetter("area")
    public String getArea() {
        return area;
    }

    @JsonSetter("area")
    public void setArea(String area) {
        this.area = area;
    }

    @JsonGetter("columnNumber")
    public Integer getColumnNumber() {
        return columnNumber;
    }

    @JsonSetter("columnNumber")
    @JsonProperty("column_number")
    public void setColumnNumber(Integer columnNumber) {
        this.columnNumber = columnNumber;
    }

    @JsonGetter("sortNumber")
    @JsonProperty("sort_number")
    public Integer getSortNumber() {
        return sortNumber;
    }

    @JsonSetter("sortNumber")
    public void setSortNumber(Integer sortNumber) {
        this.sortNumber = sortNumber;
    }

    @JsonGetter("lov")
    public String getLov() {
        return "lov".equals(this.nature) ?
                (this.lov != null ? this.lov : this.id + "LovServiceImpl") : null;
    }

    @JsonGetter("valueField")
    public String getValueField() {
        return "lov".equals(this.nature) ?
                (this.valueField != null ? this.valueField : "value") : null;
    }

    @JsonGetter("displayTemplate")
    public String getDisplayTemplate() {
        return "lov".equals(this.nature) ?
                (this.displayTemplate != null ? this.displayTemplate : "{value} - {longLabel}") : null;
    }

    @JsonGetter("defaultValue")
    public String getDefaultValue() {
        return defaultValue;
    }

    @JsonSetter("defaultValue")
    public void setDefaultValue(String defaultValue) {
        this.defaultValue = defaultValue;
    }

    @JsonGetter("hidden")
    public String getHidden() {
        return hidden != null ? hidden : "false";
    }

    @JsonSetter("hidden")
    public void setHidden(String hiddenValue) {
        System.out.println("setHidden called with: " + hiddenValue);
        if (hiddenValue != null) {
            this.hidden = hiddenValue.toLowerCase();
        } else {
            this.hidden = "false";
        }
    }

    @JsonGetter("editable")
    public String getEditable() {
        return readOnly != null ? String.valueOf(!Boolean.parseBoolean(readOnly)) : "true";
    }

    @JsonGetter("readOnly")
    public String getReadOnly() {
        return readOnly;
    }

    @JsonSetter("readOnly")
    public void setReadOnly(String editable) {
        System.out.println("setReadOnly called with: " + editable);
        if (editable != null) {
            boolean isEditable = Boolean.parseBoolean(editable.toLowerCase());
            this.readOnly = String.valueOf(!isEditable);
        } else {
            this.readOnly = "false"; // Default to false (meaning editable=true) instead of null
        }
    }

    // === GETTERS ET SETTERS STANDARDS ===

    public String getFormId() {
        return formId;
    }

    public void setFormId(String formId) {
        this.formId = formId;
    }

    public String getId() {
        return id;
    }

    public void setId(String id) {
        if (id != null && id.matches("^[a-zA-Z0-9_]+(Lds[A-Za-z]+)?\\d*$")) {
            // Extrait la partie avant "Lds..." s'il y en a
            this.id = id.replaceFirst("(Lds\\w+.*)$", "");
        } else {
            this.id = id;
        }
    }

    public String getNature() {
        return nature;
    }

    public void setNature(String nature) {
        this.nature = nature;
    }

    public String getMaxDualFieldValues() {
        return maxDualFieldValues;
    }

    public void setMaxDualFieldValues(String maxDualFieldValues) {
        this.maxDualFieldValues = maxDualFieldValues;
    }

    public String getVisible() {
        return visible;
    }

    public boolean isVisible() {
        // hidden is a String "true"/"false"
        return hidden == null || hidden.equalsIgnoreCase("false");
    }

    public void setVisible(boolean visible) {
        this.hidden = String.valueOf(!visible);
    }

    public String getDisplayField() {
        return displayField;
    }

    public void setDisplayField(String displayField) {
        this.displayField = displayField;
    }

    public String getPreValueField() {
        return preValueField;
    }

    public void setPreValueField(String preValueField) {
        this.preValueField = preValueField;
    }

    public String getPreDisplayField() {
        return preDisplayField;
    }

    public void setPreDisplayField(String preDisplayField) {
        this.preDisplayField = preDisplayField;
    }

    @JsonIgnore
    public String getType() {
        return type;
    }

    // Getters pour sérialisation JSON en String
    @JsonIgnore
    public String getColumnNumberAsString() {
        return columnNumber != null ? columnNumber.toString() : null;
    }

    @JsonIgnore
    public String getSortNumberAsString() {
        return sortNumber != null ? sortNumber.toString() : null;
    }

    public void setType(String type) {
        this.type = type;
        // Conversion automatique type → nature selon la correspondance
        if (type != null) {
            String lower = type.toLowerCase();
            if (lower.contains("ldscombobox") || lower.contains("combobox")) {
                this.nature = "lov";
            } else if (lower.contains("ldscheckbox") || lower.contains("checkbox")) {
                this.nature = "checkbox";
            } else if (lower.contains("ldssinglefieldtimestamp") || lower.contains("date")) {
                this.nature = "date";
            } else if (lower.contains("ldssinglefieldstring") || lower.contains("textfield")) {
                this.nature = "string";
            } else {
                this.nature = "string"; // Valeur par défaut
            }
        }
    }

    public String toXml() {
        StringBuilder sb = new StringBuilder();
        sb.append("        <field");

        addAttribute(sb, "id", id);
        addAttribute(sb, "nature", nature);
        addAttribute(sb, "lov", getLov());
        addAttribute(sb, "valueField", getValueField());
        addAttribute(sb, "displayTemplate", getDisplayTemplate());
        addAttribute(sb, "defaultValue", defaultValue);
        addAttribute(sb, "columnNumber", columnNumber);
        addAttribute(sb, "sortNumber", sortNumber);
        addAttribute(sb, "label", label);
        addAttribute(sb, "hidden", getHidden());
        addAttribute(sb, "editable", getEditable());

        sb.append(" />\n");
        return sb.toString();
    }

    public void addAttribute(StringBuilder sb, String name, Object value) {
        if (value != null) {
            String val = value.toString().trim();
            if (!val.isEmpty() && !"None".equalsIgnoreCase(val)) {
                sb.append(" ").append(name).append("=\"").append(val).append("\"");
            }
        }
    }

    public void addBooleanAttribute(StringBuilder sb, String name, boolean value) {
        sb.append(" ").append(name).append("=\"").append(value ? "true" : "false").append("\"");
    }

    public void setLov(String lov) {
        this.lov = lov;
    }

    public void setValueField(String valueField) {
        this.valueField = valueField;
    }

    public void setDisplayTemplate(String displayTemplate) {
        this.displayTemplate = displayTemplate;
    }
}