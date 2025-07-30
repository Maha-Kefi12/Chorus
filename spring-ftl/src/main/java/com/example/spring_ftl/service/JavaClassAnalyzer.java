package com.example.spring_ftl.service;

import com.example.spring_ftl.dto.DevFieldProperties;
import com.example.spring_ftl.dto.FieldConfig;
import com.github.javaparser.StaticJavaParser;
import com.github.javaparser.ast.CompilationUnit;
import com.github.javaparser.ast.body.FieldDeclaration;
import com.github.javaparser.ast.body.MethodDeclaration;
import com.github.javaparser.ast.expr.Expression;
import com.github.javaparser.ast.expr.MethodCallExpr;
import com.github.javaparser.ast.stmt.ExpressionStmt;
import com.github.javaparser.ast.visitor.VoidVisitorAdapter;
import org.springframework.stereotype.Service;

import java.io.File;
import java.io.FileNotFoundException;
import java.util.*;
import java.util.stream.Collectors;
import java.util.stream.IntStream;

@Service
public class JavaClassAnalyzer {
    private final Map < String, FieldConfig > flatFieldMap = new LinkedHashMap < > ();
    private final Map < String, String > componentParentMap = new HashMap < > ();
    private Map<String, String> extractedLabels = new HashMap<>();

    private static final Map<String, String> TYPE_TO_NATURE_MAPPING = Map.of(
            "ldssinglefieldstring", "string",
            "textfield", "string",
            "ldssinglefieldtimestamp", "date",
            "date", "date",
            "ldscheckbox", "checkbox",
            "ldscombobox", "lov",
            "ldscombobox6", "lov",
            "combobox", "lov",
            "LdsComboBox","lov",
           "dualfield", "dualfield");


    /**
     * Analyse un fichier Java et renvoie une structure JSON-like groupée par formId
     */
    public Map<String, Map<String, Map<String, Object>>> analyze(File file) throws FileNotFoundException {
        flatFieldMap.clear();
        componentParentMap.clear();

        // Parsing
        CompilationUnit cu = StaticJavaParser.parse(file);

        // Create and populate the label & component maps
        Map<String, String> champLabelMap = new HashMap<>();
        Map<String, String> componentParentMap = new HashMap<>();

        // Visit the AST to extract label texts and component hierarchies
        LabelAndComponentVisitor visitor = new LabelAndComponentVisitor(champLabelMap, componentParentMap);
        visitor.visit(cu, null);

        // Store the extracted maps in your analyzer class if needed globally
        this.extractedLabels = champLabelMap;
        this.componentParentMap.clear();
        this.componentParentMap.putAll(componentParentMap);

        // Récupération des types de champs
        Map<String, String> fieldTypes = new HashMap<>();
        cu.findAll(FieldDeclaration.class).forEach(fd -> {
            String fieldType = fd.getElementType().asString();
            fd.getVariables().forEach(v -> fieldTypes.put(v.getNameAsString(), fieldType));
        });

        System.out.println("Found field types: " + fieldTypes);

        // Traitement de jbInit
        cu.findAll(MethodDeclaration.class).stream()
                .filter(md -> md.getNameAsString().equals("jbInit"))
                .findFirst()
                .ifPresent(md -> {
                    System.out.println("Found jbInit method");

                    md.getBody().ifPresent(body -> {
                        body.findAll(MethodCallExpr.class).forEach(call -> {
                            System.out.println("Processing method call: " + call.toString());
                            processMethodCall(call, fieldTypes, flatFieldMap);
                        });
                    });
                });

        System.out.println("Processed fields: " + flatFieldMap.keySet());
        System.out.println("Extracted labels: " + extractedLabels);

        // NEW: Ensure LOV fields are properly configured
        ensureLovFieldsAreProperlyConfigured(flatFieldMap);

        // Force nature lov pour xceopt
        FieldConfig xceopt = flatFieldMap.get("xceopt");
        if (xceopt != null) {
            xceopt.setNature("lov");
            if (xceopt.getLov() == null || xceopt.getLov().isEmpty()) {
                xceopt.setLov("xceoptLovServiceImpl");
            }
        }

        // Application des défauts LOV et suppression des doublons
        flatFieldMap.values().forEach(this::applyLovDefaults);
        removePrefixedDuplicates(flatFieldMap);

        // Apply extracted labels to fields that don't have labels
        applyExtractedLabels();

        // Attribution du formId
        String formId = extractFormIdFromClassName(file.getName());
        flatFieldMap.values().forEach(f -> f.setFormId(formId));

        // Regroupement et conversion en JSON-ready
        return groupByFormId(flatFieldMap);
    }

    /**
     * NEW: Apply extracted labels to fields that don't have labels set
     */
    private void applyExtractedLabels() {
        for (Map.Entry<String, String> entry : extractedLabels.entrySet()) {
            String fieldId = entry.getKey();
            String label = entry.getValue();

            FieldConfig field = flatFieldMap.get(fieldId);
            if (field != null && (field.getLabel() == null || field.getLabel().isEmpty())) {
                System.out.println("🔍 Applying extracted label '" + label + "' to field " + fieldId);
                field.setLabel(label);
            }
        }
    }

    private void processMethodCall(MethodCallExpr call, Map<String, String> fieldTypes, Map<String, FieldConfig> map) {
        String methodName = call.getNameAsString();

        // === STEP 1: Special case: handle setComponents ===
        if (methodName.equals("setComponents") && call.getArguments().size() == 1) {
            call.getScope().ifPresent(scope -> {
                String parent = extractBaseFieldName(scope.toString());
                Expression arg = call.getArgument(0);

                if (arg.isArrayInitializerExpr()) {
                    arg.asArrayInitializerExpr().getValues().forEach(v -> {
                        String child = extractBaseFieldName(v.toString());
                        componentParentMap.put(child, parent);
                        System.out.printf("🔗 Mapped subcomponent '%s' to parent '%s'%n", child, parent);
                    });
                }
            });
            return; // Don't continue below, since setComponents is already handled
        }

        // === STEP 2: Handle label extraction for ANY field (even if not in fieldTypes) ===
        if ((methodName.equals("setLabel") || methodName.equals("setLabelText")) && call.getArguments().size() > 0) {
            call.getScope().ifPresent(scope -> {
                String scopeStr = scope.toString();
                String baseField = extractBaseFieldName(scopeStr);

                Expression labelExpr = call.getArgument(0);
                String labelValue = extractArgumentValue(labelExpr);

                System.out.println("🔍 Found label setting: " + baseField + " = '" + labelValue + "'");
                extractedLabels.put(baseField, labelValue);
            });
        }

        // === STEP 3: Normal field method calls ===
        call.getScope().ifPresent(scope -> {
            String scopeStr = scope.toString();
            String baseField = extractBaseFieldName(scopeStr);

            if (fieldTypes.containsKey(baseField)) {
                FieldConfig field = map.computeIfAbsent(baseField, k -> {
                    FieldConfig fc = new FieldConfig();
                    fc.setId(k);
                    fc.setNature(determineNature(fieldTypes.get(baseField), baseField));
                    fc.setLabel(""); // Start with empty label
                    fc.setHidden("false");
                    fc.setReadOnly("false");
                    System.out.println("🆕 Created new field: " + k + " with nature: " + fc.getNature());
                    return fc;
                });

                System.out.println("⚙️  Processing method " + methodName + " on field " + baseField);
                processFieldAttributes(call, field);
            } else {
                System.out.println("⏭️ Skipped method call: unknown scope '" + scopeStr + "'");
            }
        });
    }

    private void processFieldAttributes(MethodCallExpr call, FieldConfig field) {
        if (call.getArguments().isEmpty()) return;
        String method = call.getNameAsString();
        Expression argument = call.getArgument(0);

        // Better argument parsing to handle different types of expressions
        try {
            switch (method) {
                case "setComponents" -> {
                    if (call.getArguments().size() == 1 && call.getArgument(0).isArrayInitializerExpr()) {
                        call.getArgument(0).asArrayInitializerExpr().getValues().forEach(compExpr -> {
                            String child = extractBaseFieldName(compExpr.toString());
                            componentParentMap.put(child, field.getId());
                            System.out.println("Mapped child " + child + " → parent " + field.getId());
                        });
                    }
                }
                case "setLabel", "setLabelText" -> {
                    String labelValue = extractArgumentValue(argument);
                    System.out.println("🔍 setLabelText raw: " + argument);
                    System.out.println("✅ Extracted label value: '" + labelValue + "'");
                    System.out.println("🎯 Setting label on field: " + field.getId());

                    field.setLabel(labelValue);
                    extractedLabels.put(field.getId(), labelValue); // Store in extracted labels too

                    // Verify the label was set
                    System.out.println("🔍 After setting, field.getLabel() = '" + field.getLabel() + "'");
                }
                case "setEditable" -> {
                    String arg = extractArgumentValue(argument);
                    field.setReadOnly(String.valueOf(!Boolean.parseBoolean(arg.toLowerCase())));
                }
                case "setVisible" -> {
                    String arg = extractArgumentValue(argument);
                    field.setHidden(String.valueOf(!Boolean.parseBoolean(arg.toLowerCase())));
                }
                case "setDefaultValue" -> {
                    String arg = extractArgumentValue(argument);
                    field.setDefaultValue(arg);
                }
                case "setColumnNumber" -> {
                    String arg = extractArgumentValue(argument);
                    field.setColumnNumber(Integer.parseInt(arg));
                }
                case "setSortNumber" -> {
                    String arg = extractArgumentValue(argument);
                    field.setSortNumber(Integer.parseInt(arg));
                }
                case "setLov" -> {
                    String arg = extractArgumentValue(argument);
                    field.setLov(arg);
                }
                case "setValueField" -> {
                    String arg = extractArgumentValue(argument);
                    field.setValueField(arg);
                }
                case "setDisplayTemplate" -> {
                    String arg = extractArgumentValue(argument);
                    field.setDisplayTemplate(arg);
                }
                // NEW: Handle setWithValuesList method
                case "setWithValuesList" -> {
                    String arg = extractArgumentValue(argument);
                    boolean withValuesList = Boolean.parseBoolean(arg.toLowerCase());

                    if (withValuesList) {
                        System.out.println("🔍 Field " + field.getId() + " has setWithValuesList(true) - setting nature to 'lov'");
                        field.setNature("lov");

                        // Apply default LOV settings if not already set
                        if (field.getLov() == null) {
                            field.setLov(field.getId() + "LovServiceImpl");
                        }
                        if (field.getValueField() == null) {
                            field.setValueField("value");
                        }
                        if (field.getDisplayTemplate() == null) {
                            field.setDisplayTemplate("{value} - {longLabel}");
                        }

                        System.out.println("✅ Field " + field.getId() + " converted to LOV type with default settings");
                    }
                }
            }
        } catch (Exception e) {
            System.err.printf("Failed to parse %s(%s): %s%n", method, argument, e.getMessage());
        }
    }

    // Also add a post-processing method to ensure all setWithValuesList fields are properly configured
    private void ensureLovFieldsAreProperlyConfigured(Map<String, FieldConfig> fieldMap) {
        System.out.println("🔍 Ensuring all LOV fields are properly configured...");

        for (FieldConfig field : fieldMap.values()) {
            if ("lov".equals(field.getNature())) {
                // Ensure all LOV fields have required properties
                if (field.getLov() == null || field.getLov().isEmpty()) {
                    field.setLov(field.getId() + "LovServiceImpl");
                    System.out.println("✅ Set default LOV service for field: " + field.getId());
                }

                if (field.getValueField() == null || field.getValueField().isEmpty()) {
                    field.setValueField("value");
                    System.out.println("✅ Set default value field for LOV: " + field.getId());
                }

                if (field.getDisplayTemplate() == null || field.getDisplayTemplate().isEmpty()) {
                    field.setDisplayTemplate("{value} - {longLabel}");
                    System.out.println("✅ Set default display template for LOV: " + field.getId());
                }
            }
        }
    }

    private String extractArgumentValue(Expression expr) {
        if (expr.isStringLiteralExpr()) {
            return expr.asStringLiteralExpr().getValue();
        } else if (expr.isNameExpr()) {
            return expr.asNameExpr().getNameAsString();
        } else if (expr.isBooleanLiteralExpr()) {
            return String.valueOf(expr.asBooleanLiteralExpr().getValue());
        } else if (expr.isIntegerLiteralExpr()) {
            return expr.asIntegerLiteralExpr().getValue();
        } else {
            // For other types, convert to string and remove quotes if present
            String result = expr.toString();
            if (result.startsWith("\"") && result.endsWith("\"")) {
                result = result.substring(1, result.length() - 1);
            }
            return result;
        }
    }

    private void applyLovDefaults(FieldConfig field) {
        if ("lov".equals(field.getNature())) {
            if (field.getLov() == null) field.setLov(field.getId() + "LovServiceImpl");
            if (field.getValueField() == null) field.setValueField("value");
            if (field.getDisplayTemplate() == null) field.setDisplayTemplate("{value} - {longLabel}");
        } else if ("dualfield".equals(field.getNature())) {
            // Valeurs fixes spécifiques à dualfield
            if (field.getLov() == null) field.setLov("IPrapRtinRidtinLov");
            if (field.getValueField() == null) field.setValueField("value");
            if (field.getDisplayTemplate() == null) field.setDisplayTemplate("{value} - {longLabel}");
            if (field.getMaxDualFieldValues() == null) field.setMaxDualFieldValues("4");
            if (field.getHidden() == null) field.setHidden("false");
            if (field.getReadOnly() == null) field.setReadOnly("false");
        }
    }


    private void removePrefixedDuplicates(Map<String, FieldConfig> map) {
        Set<String> toRemove = new HashSet<>();
        for (String k1 : map.keySet()) {
            for (String k2 : map.keySet()) {
                if (!k1.equals(k2) && k2.startsWith(k1)) toRemove.add(k2);
            }
        }
        toRemove.forEach(map::remove);
    }

    private String determineNature(String type, String name) {
        if ("aidtrp".equalsIgnoreCase(name)) return "lov";
        // Normalize type and name
        String t = type != null ? type.toLowerCase().replaceAll("[^a-z]", "") : "";
        String n = name != null ? name.toLowerCase() : "";

        // ✅ Force LOV if both 'lds' and 'combobox' are present anywhere in raw type or name
        if ((t + n).contains("lds") && (t + n).contains("combobox")) return "lov";

        // Optional: exact match fallback
        if (t.matches(".*ldscombobox.*")) return "lov";

        if (TYPE_TO_NATURE_MAPPING.containsKey(t)) {
            return TYPE_TO_NATURE_MAPPING.get(t);
        }

        if (n.matches(".*(combobox|lov|dropdown|cbo|ddl).*")) return "lov";
        if (n.contains("date") || n.contains("dt")) return "date";
        if (n.contains("check") || n.contains("flag") || (n.contains("opt") && !n.contains("option"))) return "checkbox";
        if (n.matches(".*(dualfield|ridtins|multi|multi.*field).*")) return "dualfield";

        return "string";
    }



    private String cleanFieldName(String original) {
        return original.replaceAll("(?i)(ldscombobox\\d*|combobox|ldscheckbox|textfield|date|ldssinglefieldstring|ldssinglefieldtimestamp)$", "");
    }

    private String extractFormIdFromClassName(String fileName) {
        String name = fileName.replace(".java", "");
        return name.length() >= 4 ? name.substring(name.length() - 4).toLowerCase() : name.toLowerCase();
    }


    public void handleRidtinsFields(Map<String, FieldConfig> fieldMap) {
        // Trouver toutes les clés qui correspondent à "ridtin" suivi d'un nombre
        List<String> ridtinFields = fieldMap.keySet().stream()
                .filter(key -> key.matches("ridtin\\d+"))
                .sorted() // tri optionnel par ordre alphabétique / numérique
                .toList();

        if (!ridtinFields.isEmpty()) {
            System.out.println("🔍 Detected ridtin fields: " + ridtinFields + ", creating unified ridtins field");

            Integer minColumnNumber = null;
            Integer minSortNumber = null;
            String ridtinLabel = null;

            for (String ridtinField : ridtinFields) {
                FieldConfig field = fieldMap.get(ridtinField);
                if (field != null) {
                    if (field.getColumnNumber() != null) {
                        minColumnNumber = (minColumnNumber == null) ? field.getColumnNumber() :
                                Math.min(minColumnNumber, field.getColumnNumber());
                    }
                    if (field.getSortNumber() != null) {
                        minSortNumber = (minSortNumber == null) ? field.getSortNumber() :
                                Math.min(minSortNumber, field.getSortNumber());
                    }
                    if (field.getLabel() != null && !field.getLabel().isEmpty() && ridtinLabel == null) {
                        ridtinLabel = field.getLabel();
                    }

                    System.out.println("🗑️ Removing ridtin field: " + ridtinField);
                }
            }

            // Supprimer tous les ridtins détectés
            ridtinFields.forEach(fieldMap::remove);

            FieldConfig ridtinsField = new FieldConfig();
            ridtinsField.setId("ridtins");
            ridtinsField.setNature("dualfield");
            ridtinsField.setColumnNumber(minColumnNumber != null ? minColumnNumber : 1);
            ridtinsField.setSortNumber(minSortNumber != null ? minSortNumber : 2);
            ridtinsField.setLov("IPrapRtinRidtinLov");
            ridtinsField.setValueField("value");
            ridtinsField.setDisplayTemplate("{value} - {longLabel}");
            ridtinsField.setMaxDualFieldValues("4");
            ridtinsField.setHidden("false");
            ridtinsField.setReadOnly("false");
            if (ridtinLabel != null) {
                ridtinsField.setLabel(ridtinLabel);
            }
            FieldConfig ridtin_dualfieldField = new FieldConfig();
            ridtinsField.setId("ridtin_dualfield");
            ridtinsField.setNature("dualfield");
            ridtinsField.setColumnNumber(minColumnNumber != null ? minColumnNumber : 1);
            ridtinsField.setSortNumber(minSortNumber != null ? minSortNumber : 2);
            ridtinsField.setLov("IPrapRtinRidtin_dualfieldLov");
            ridtinsField.setValueField("value");
            ridtinsField.setDisplayTemplate("{value} - {longLabel}");
            ridtinsField.setMaxDualFieldValues("4");
            ridtinsField.setHidden("false");
            ridtinsField.setReadOnly("false");
            if (ridtinLabel != null) {
                ridtinsField.setLabel(ridtinLabel);
            }

            // Vérifier que les données sont complètes avant d'ajouter
            boolean isMeaningful =
                    ridtinsField.getLov() != null &&
                            ridtinsField.getValueField() != null &&
                            ridtinsField.getDisplayTemplate() != null &&
                            (ridtinsField.getLabel() != null && !ridtinsField.getLabel().isEmpty());

            if (isMeaningful) {
                fieldMap.put("ridtins", ridtinsField);
                System.out.println("✅ Created unified ridtins field with properties:");
                System.out.println("   - columnNumber: " + ridtinsField.getColumnNumber());
                System.out.println("   - sortNumber: " + ridtinsField.getSortNumber());
                System.out.println("   - label: " + ridtinsField.getLabel());
            } else {
                System.out.println("⛔ Skipped creating ridtins field due to incomplete data.");
            }
        }
    }


    private String extractBaseFieldName(String scopeStr) {
        System.out.println("🔍 Extracting base field name from: '" + scopeStr + "'");

        // Cas complexes avec casting et accès imbriqués
        String result = scopeStr;

        // Gérer les casts comme "(LDSComboBox6)field" ou "((Component)field)"
        if (result.contains(")") && result.contains("(")) {
            String[] parts = result.split("\\)");
            if (parts.length > 1) {
                result = parts[parts.length - 1];
            }
        }

        // Gérer les accès par propriété comme "this.field" ou "component.field"
        if (result.contains(".")) {
            result = result.substring(result.lastIndexOf('.') + 1);
        }

        // Nettoyer les espaces et caractères spéciaux
        result = result.trim();

        // Gérer les accès par méthode comme "getField()" -> "field"
        if (result.startsWith("get") && result.endsWith("()")) {
            result = result.substring(3, result.length() - 2);
            if (!result.isEmpty()) {
                result = Character.toLowerCase(result.charAt(0)) + result.substring(1);
            }
        }

        System.out.println("✅ Extracted field name: '" + result + "'");
        return result;
    }
    private String guessNatureFromName(String name) {
        if (name == null) return "string";

        String n = name.toLowerCase();

        // Patterns pour LOV/ComboBox
        if (n.matches(".*(combobox|lov|dropdown|cbo|ddl|opt).*")) return "lov";

        // Patterns pour dates
        if (n.matches(".*(date|dt|time|timestamp|dat|jour|annee|mois|cou).*")) return "date";

        // Patterns pour checkbox
        if (n.matches(".*(check|flag|bool|opt|oui|non|actif).*")) return "checkbox";

        // Patterns pour numérique
        if (n.matches(".*(num|nbr|count|qty|amount|prix|montant|total).*")) return "number";

        // Par défaut
        return "string";
    }


    /**
     * Regroupe les FieldConfig par formId et convertit vers Maps JSON-ready
     */
    public Map<String, Map<String, Map<String, Object>>> groupByFormId(Map<String, FieldConfig> fieldMap) {
        // Synchroniser flatFieldMap avec la map reçue en paramètre
        handleRidtinsFields(flatFieldMap);
        // NEW: Handle dev fields
        handleCdevFields(flatFieldMap);

        // Appeler la méthode pour fusionner les champs ridtin
        handleRidtinsFields(flatFieldMap);

        System.out.println("🔍 groupByFormId - extracted labels: " + extractedLabels);

        // Promotion des labels et attributs des enfants vers les parents
        for (Map.Entry<String, String> entry : componentParentMap.entrySet()) {
            String childId = entry.getKey();
            String parentId = entry.getValue();

            FieldConfig child = flatFieldMap.get(childId);
            FieldConfig parent = flatFieldMap.get(parentId);

            if (child != null && parent != null) {
                if ((parent.getLabel() == null || parent.getLabel().isEmpty()) && child.getLabel() != null) {
                    System.out.println("🔍 Promoting label '" + child.getLabel() + "' from child " + childId + " to parent " + parentId);
                    parent.setLabel(child.getLabel());
                }
                if (child.getHidden() != null && "true".equals(child.getHidden())) {
                    System.out.println("🔁 Propagating hidden=true from child " + child.getId() + " to parent " + parent.getId());
                    parent.setHidden("true");
                }
                if ((parent.getDefaultValue() == null || parent.getDefaultValue().isEmpty()) &&
                        child.getDefaultValue() != null && !child.getDefaultValue().isEmpty()) {
                    System.out.println("🔁 Propagating defaultValue '" + child.getDefaultValue() + "' from child " + childId + " to parent " + parentId);
                    parent.setDefaultValue(child.getDefaultValue());
                }
                if ((parent.getReadOnly() == null || parent.getReadOnly().isEmpty()) && child.getReadOnly() != null) {
                    parent.setReadOnly(child.getReadOnly());
                }
                if ("lov".equals(child.getNature())) {
                    parent.setNature("lov");
                    if (parent.getLov() == null) parent.setLov(child.getLov());
                    if (parent.getValueField() == null) parent.setValueField(child.getValueField());
                    if (parent.getDisplayTemplate() == null) parent.setDisplayTemplate(child.getDisplayTemplate());
                }
            }
        }

        // Groupement par formId
        Map<String, Map<String, Map<String, Object>>> root = new LinkedHashMap<>();
        for (FieldConfig f : flatFieldMap.values()) {
            String fid = f.getFormId() != null ? f.getFormId() : "default";
            root.putIfAbsent(fid, new LinkedHashMap<>());
            Map<String, Map<String, Object>> fields = root.get(fid);

            Map<String, Object> jsonF = new LinkedHashMap<>();
            jsonF.put("id", f.getId());
            jsonF.put("nature", f.getNature());

            String finalLabel = f.getLabel();
            System.out.println("🔍 Final label for field " + f.getId() + ": '" + finalLabel + "'");
            jsonF.put("label", finalLabel != null ? finalLabel : "");

            String hidden = f.getHidden();
            System.out.println("📌 Champ " + f.getId() + " hidden dans FieldConfig = '" + hidden + "'");
            String isHidden = "false".equalsIgnoreCase(hidden) ? "false" : "true";
            System.out.println("📌 Champ " + f.getId() + " hidden finale = '" + isHidden + "'");
            jsonF.put("hidden", isHidden);

            String readOnly = f.getReadOnly();
            String editable = readOnly != null ? String.valueOf(!Boolean.parseBoolean(readOnly)) : "true";
            jsonF.put("readOnly", editable);

            if ("lov".equals(f.getNature())) {
                jsonF.put("lov", f.getLov());
                jsonF.put("valueField", f.getValueField());
                jsonF.put("displayTemplate", f.getDisplayTemplate());
            }


            if ("dualfield".equals(f.getNature())) {
                jsonF.put("lov", f.getLov());                          // "IPrapRtinRidtinLov"
                jsonF.put("valueField", f.getValueField());            // "value"
                jsonF.put("displayTemplate", f.getDisplayTemplate());  // "{value} - {longLabel}"
                jsonF.put("maxDualFieldValues", f.getMaxDualFieldValues()); // "4"
                jsonF.put("hidden", f.getHidden());
            }


// ✅ dev
            if ("dev".equals(f.getId())) {
                jsonF.put("lov", "IPrapDevLov");
                jsonF.put("valueField", "value");
                jsonF.put("displayTemplate", "{value} - {longLabel}");
                jsonF.put("maxDualFieldValues", "4");
                if (f.getLabel() == null || f.getLabel().isEmpty()) {
                    jsonF.put("label", "Devises");
                }
            }

            if ("ridtin_dualfield".equals(f.getId())) {
                jsonF.put("lov", f.getLov() != null ? f.getLov() : "ridtin_dualfieldLovServiceImpl");
                jsonF.put("valueField", "value");
                jsonF.put("displayTemplate", "{value} - {longLabel}");
                jsonF.put("maxDualFieldValues", "4");
                if (f.getLabel() == null || f.getLabel().isEmpty()) {
                    jsonF.put("label", "");
                }
            }
// ✅ rcedevs
            if ("rcedevs".equals(f.getId())) {
                jsonF.put("lov", f.getLov() != null ? f.getLov() : "rcedevsLovServiceImpl");
                jsonF.put("valueField", "value");
                jsonF.put("displayTemplate", "{value} - {longLabel}");
                jsonF.put("maxDualFieldValues", "4");
                if (f.getLabel() == null || f.getLabel().isEmpty()) {
                    jsonF.put("label", "");
                }
            }
            if ("devs".equals(f.getId())) {
                jsonF.put("lov", f.getLov() != null ? f.getLov() : "devsLovServiceImpl");
                jsonF.put("valueField", "value");
                jsonF.put("displayTemplate", "{value} - {longLabel}");
                jsonF.put("maxDualFieldValues", "4");
                if (f.getLabel() == null || f.getLabel().isEmpty()) {
                    jsonF.put("label", "");
                }
            }

// ✅ ridtints
            if ("ridtints".equals(f.getId())) {
                jsonF.put("lov", f.getLov() != null ? f.getLov() : "ridtintsLovServiceImpl");
                jsonF.put("valueField", "value");
                jsonF.put("displayTemplate", "{value} - {longLabel}");
                jsonF.put("maxDualFieldValues", "4");
                if (f.getLabel() == null || f.getLabel().isEmpty()) {
                    jsonF.put("label", "");
                }
            }
            // ✅ ridtints
            if ("cdevs".equals(f.getId())) {
                jsonF.put("lov", f.getLov() != null ? f.getLov() : "ridtintsLovServiceImpl");
                jsonF.put("valueField", "value");
                jsonF.put("displayTemplate", "{value} - {longLabel}");
                jsonF.put("maxDualFieldValues", "4");
                if (f.getLabel() == null || f.getLabel().isEmpty()) {
                    jsonF.put("label", "");
                }
            }


            String defaultValue = f.getDefaultValue();
            if (defaultValue != null && !defaultValue.isEmpty()) {
                jsonF.put("defaultValue", defaultValue);
            }
            System.out.println("📌 Adding defaultValue to field " + f.getId() + ": " + defaultValue);

            if (f.getColumnNumber() != null) jsonF.put("columnNumber", f.getColumnNumber());
            if (f.getSortNumber() != null) jsonF.put("sortNumber", f.getSortNumber());

            fields.put(f.getId(), jsonF);
        }

        for (FieldConfig f : flatFieldMap.values()) {
            System.out.println("�� " + f.getId() + " → hidden=" + f.getHidden() + ", readOnly=" + f.getReadOnly() + ", label=" + f.getLabel());
        }
        Map<String, Map<String, Map<String, Object>>> result=new LinkedHashMap<>();;
        Map<String, Map<String, Object>> defaultGroup = result.get("default");
        if (defaultGroup != null) {
            Map<String, Object> ridtins = defaultGroup.get("ridtins");
            if (ridtins != null) {
                boolean allNullOrEmpty = ridtins.values().stream().allMatch(v ->
                        v == null || (v instanceof String && ((String) v).isEmpty())
                );
                if (allNullOrEmpty) {
                    System.out.println("⛔ Suppression du champ 'ridtins' car tous ses attributs sont vides.");
                    defaultGroup.remove("ridtins");
                }
            }
            // Suppression forcée de tous les cdev1, cdev2, cdev3 ... dans defaultGroup
            List<String> keysToRemove = new ArrayList<>();
            for (String key : defaultGroup.keySet()) {
                if (key.matches("cdev\\d+")) {
                    keysToRemove.add(key);
                }

            }
            for (String key : keysToRemove) {
                System.out.println("⛔ Suppression forcée du champ '" + key + "' car remplacé par cdevs.");
                defaultGroup.remove(key);
            }




        }
        flatFieldMap.remove("devs");


        return root;
    }
    private String normalizeComponentId(String componentId) {
        // Example: remove suffix "ReportDatePanel" or "Panel"
        if (componentId.endsWith("ReportDatePanel")) {
            return componentId.substring(0, componentId.length() - "ReportDatePanel".length());
        }
        if (componentId.endsWith("Panel")) {
            return componentId.substring(0, componentId.length() - "Panel".length());
        }
        return componentId;
    }




    private Map<String, String> champLabelMap = new LinkedHashMap<>();

    public class LabelAndComponentVisitor extends VoidVisitorAdapter<Void> {

        private final Map<String, String> champLabelMap;
        private final Map<String, String> componentParentMap;

        public LabelAndComponentVisitor(Map<String, String> champLabelMap, Map<String, String> componentParentMap) {
            this.champLabelMap = champLabelMap;
            this.componentParentMap = componentParentMap;
        }

        @Override
        public void visit(MethodDeclaration md, Void arg) {
            super.visit(md, arg);

            if ("jbInit".equals(md.getNameAsString())) {
                md.findAll(ExpressionStmt.class).forEach(exprStmt -> {
                    Expression expr = exprStmt.getExpression();
                    if (expr instanceof MethodCallExpr) {
                        MethodCallExpr methodCall = (MethodCallExpr) expr;
                        String methodName = methodCall.getNameAsString();

                        if ("setLabelText".equals(methodName) || "setText".equals(methodName)) {
                            methodCall.getScope().ifPresent(scope -> {
                                String componentId = normalizeComponentId(scope.toString());
                                methodCall.getArgument(0).ifStringLiteralExpr(argText -> {
                                    System.out.println("Label found: componentId='" + componentId + "', label='" + argText.getValue() + "'");
                                    champLabelMap.put(componentId, argText.getValue());
                                });
                            });
                        }

                        else if ("setComponents".equals(methodName)) {
                            methodCall.getScope().ifPresent(scope -> {
                                String parentId = normalizeComponentId(scope.toString());
                                methodCall.getArgument(0).ifArrayInitializerExpr(arrayInit -> {
                                    for (Expression childExpr : arrayInit.getValues()) {
                                        String childId = normalizeComponentId(childExpr.toString());
                                        System.out.println("Component relation found: childId='" + childId + "', parentId='" + parentId + "'");
                                        componentParentMap.put(childId, parentId);
                                    }
                                });
                            });
                        }
                    }
                });
            }
        }

        private String normalizeComponentId(String componentId) {
            if (componentId == null) return "";

            // Remove common UI suffixes to match field IDs
            if (componentId.endsWith("ReportDatePanel")) {
                return componentId.substring(0, componentId.length() - "ReportDatePanel".length());
            }
            if (componentId.endsWith("Panel")) {
                return componentId.substring(0, componentId.length() - "Panel".length());
            }
            if (componentId.endsWith("Panel1")) {
                return componentId.substring(0, componentId.length() - "Panel1".length());
            }
            // Add other suffixes to remove here as needed

            return componentId;
        }
    }


    public Map<String, String> extractLabelTexts() {
        Map<String, String> labelMap = new LinkedHashMap<>();

        System.out.println("🔍 extractLabelTexts() - flatFieldMap size: " + flatFieldMap.size());
        System.out.println("🔍 extractLabelTexts() - componentParentMap size: " + componentParentMap.size());

        // Phase 0 : appliquer le visitor pour remplir champLabelMap
        // Par exemple : visitor.visit(compilationUnit, null);
        // (Doit être fait avant cet appel, sinon déplacer cette logique dans l'appelant)

        // Phase 1: Ajouter les labels extraits via champLabelMap (labels du code Java)
        if (!champLabelMap.isEmpty()) {
            labelMap.putAll(champLabelMap);
            System.out.println("✅ Added " + champLabelMap.size() + " labels extracted from Java source");
        }

        // Phase 2: Ajouter labels pré-extraits s’il y en a (extractedLabels)
        if (extractedLabels != null) {
            labelMap.putAll(extractedLabels);
            System.out.println("✅ Added " + extractedLabels.size() + " pre-extracted labels");
        }

        // Phase 3: Direct labels from field configs with normalization
        for (FieldConfig field : flatFieldMap.values()) {
            String fieldId = field.getId();
            String rawLabel = field.getLabel();

            System.out.println("🔍 Processing field " + fieldId + " with raw label: '" + rawLabel + "'");

            String normalizedLabel = normalizeLabel(rawLabel);
            if (normalizedLabel != null) {
                labelMap.put(fieldId, normalizedLabel);
                System.out.println("✅ Added normalized label for field " + fieldId + ": '" + normalizedLabel + "'");
            } else {
                labelMap.put(fieldId, "");
                System.out.println("✅ Set empty label for field " + fieldId);
            }
        }

        // Phase 4: Component-parent relationship labels
        for (Map.Entry<String, String> entry : componentParentMap.entrySet()) {
            String childId = entry.getKey();
            String parentId = entry.getValue();

            FieldConfig child = flatFieldMap.get(childId);
            if (child != null) {
                String childLabel = normalizeLabel(child.getLabel());
                if (childLabel != null && !labelMap.containsKey(childId)) {
                    labelMap.put(childId, childLabel);
                    System.out.println("✅ Added child label for " + childId + ": '" + childLabel + "'");
                } else if (!labelMap.containsKey(childId)) {
                    labelMap.put(childId, "");
                    System.out.println("✅ Set empty label for child " + childId);
                }
            }

            FieldConfig parent = flatFieldMap.get(parentId);
            if (parent != null) {
                String parentLabel = normalizeLabel(parent.getLabel());
                if (parentLabel != null && !labelMap.containsKey(parentId)) {
                    labelMap.put(parentId, parentLabel);
                    System.out.println("✅ Added parent label for " + parentId + ": '" + parentLabel + "'");
                } else if (!labelMap.containsKey(parentId)) {
                    labelMap.put(parentId, "");
                    System.out.println("✅ Set empty label for parent " + parentId);
                }
            }
        }

        return labelMap;
    }

    /**
     * Normalizes and validates label text
     */
    private String normalizeLabel(String rawLabel) {
        if (rawLabel == null) {
            return null;
        }

        // Remove extra whitespace and trim
        String normalized = rawLabel.trim().replaceAll("\\s+", " ");

        // Return null if empty or just whitespace
        if (normalized.isEmpty()) {
            return null;
        }

        // Remove common prefixes/suffixes that aren't useful
        normalized = normalized.replaceAll("^(Label:|Field:|Input:)\\s*", "");
        normalized = normalized.replaceAll("\\s*(:)$", "");

        // Check again after cleanup - return null if now empty
        normalized = normalized.trim();
        if (normalized.isEmpty()) {
            return null;
        }

        // Convert to proper case if all caps or all lowercase
        if (normalized.equals(normalized.toUpperCase()) || normalized.equals(normalized.toLowerCase())) {
            normalized = toProperCase(normalized);
        }

        return normalized;
    }

    /**
     * Applies fallback strategies for fields without labels
     */
    private void applyFallbackStrategies(Map<String, String> labelMap) {
        System.out.println("🔄 Applying fallback strategies...");

        for (FieldConfig field : flatFieldMap.values()) {
            String fieldId = field.getId();

            // Skip if we already have a label
            if (labelMap.containsKey(fieldId)) {
                continue;
            }

            String fallbackLabel = null;

            // Strategy 1: Use placeholder text (if available)
            if (hasPlaceholder(field)) {
                fallbackLabel = normalizeLabel(getPlaceholder(field));
                if (fallbackLabel != null) {
                    System.out.println("📝 Using placeholder as label for " + fieldId + ": '" + fallbackLabel + "'");
                }
            }

            // Strategy 2: Look for nearby text or hints
            if (fallbackLabel == null) {
                fallbackLabel = findNearbyTextHints(field);
                if (fallbackLabel != null) {
                    System.out.println("🔍 Found nearby text hint for " + fieldId + ": '" + fallbackLabel + "'");
                }
            }

            // Si aucune stratégie ne fonctionne, utiliser une chaîne vide
            if (fallbackLabel == null) {
                fallbackLabel = "";
                System.out.println("📝 Set empty label for " + fieldId);
            }

            labelMap.put(fieldId, fallbackLabel);
        }
    }

    private boolean isGenericLabel(String label, String fieldId) {
        if (label == null || fieldId == null) {
            return true;
        }

        // Consider it generic if it's just the field ID with minor modifications
        String normalizedLabel = label.toLowerCase().replaceAll("[^a-z0-9]", "");
        String normalizedFieldId = fieldId.toLowerCase().replaceAll("[^a-z0-9]", "");

        // If they're very similar, it's probably generic
        return normalizedLabel.equals(normalizedFieldId) ||
                normalizedLabel.startsWith(normalizedFieldId) ||
                normalizedFieldId.startsWith(normalizedLabel);
    }

    /**
     * Generates a human-readable label from field ID
     */
    private String generateLabelFromFieldId(String fieldId) {
        if (fieldId == null || fieldId.trim().isEmpty()) {
            return null;
        }

        // Split on common separators
        String[] parts = fieldId.split("[_\\-\\.]");
        StringBuilder result = new StringBuilder();

        for (String part : parts) {
            if (!part.isEmpty()) {
                if (result.length() > 0) {
                    result.append(" ");
                }
                result.append(toProperCase(part));
            }
        }

        return result.toString();
    }

    /**
     * Helper method to check if field has placeholder (adapt to your FieldConfig structure)
     */
    private boolean hasPlaceholder(FieldConfig field) {
        // Adapt this method based on your actual FieldConfig structure
        // For example: return field.getPlaceholder() != null && !field.getPlaceholder().trim().isEmpty();
        return false; // Placeholder - implement based on your FieldConfig
    }

    /**
     * Helper method to get placeholder text (adapt to your FieldConfig structure)
     */
    private String getPlaceholder(FieldConfig field) {
        // Adapt this method based on your actual FieldConfig structure
        // For example: return field.getPlaceholder();
        return null; // Placeholder - implement based on your FieldConfig
    }

    /**
     * Looks for nearby text hints in the field configuration
     */
    private String findNearbyTextHints(FieldConfig field) {
        // This method can be extended based on your specific FieldConfig structure
        // For now, it returns null as a placeholder for future implementation
        return null;
    }

    /**
     * Converts text to proper case
     */
    private String toProperCase(String text) {
        if (text == null || text.isEmpty()) {
            return text;
        }

        StringBuilder result = new StringBuilder();
        boolean capitalizeNext = true;

        for (char c : text.toCharArray()) {
            if (Character.isWhitespace(c)) {
                capitalizeNext = true;
                result.append(c);
            } else if (capitalizeNext) {
                result.append(Character.toUpperCase(c));
                capitalizeNext = false;
            } else {
                result.append(Character.toLowerCase(c));
            }
        }

        return result.toString();
    }
    private void propagateVisibility() {
        System.out.println("🔄 Starting visibility propagation...");

        // Remonter les hidden=true vers les parents
        for (Map.Entry<String, String> entry : componentParentMap.entrySet()) {
            String childId = entry.getKey();
            String parentId = entry.getValue();

            FieldConfig child = flatFieldMap.get(childId);
            FieldConfig parent = flatFieldMap.get(parentId);

            if (child != null && "true".equals(child.getHidden())) {
                System.out.println("⬆️ Child " + childId + " is hidden → propagating to parent " + parentId);
                if (parent != null) parent.setHidden("true");
            }
        }

        // Redescendre les hidden=true vers les enfants
        for (Map.Entry<String, String> entry : componentParentMap.entrySet()) {
            String childId = entry.getKey();
            String parentId = entry.getValue();

            FieldConfig child = flatFieldMap.get(childId);
            FieldConfig parent = flatFieldMap.get(parentId);

            if (parent != null && "true".equals(parent.getHidden())) {
                System.out.println("⬇️ Parent " + parentId + " is hidden → propagating to child " + childId);
                if (child != null) child.setHidden("true");
            }
        }
    }


    public Map<String, FieldConfig> getFieldMap() {
        return flatFieldMap;
    }

    /**
     * Extrait le nom de la fonction depuis un fichier XML screen
     * En analysant l'attribut id de la balise <function>
     *
     * @param xmlContent Le contenu XML du fichier screen
     * @return Le nom de la fonction (ex: "InventoryReport" depuis id="InventoryReport")
     */
    public String extractFunctionNameFromXml(String xmlContent) {
        if (xmlContent == null || xmlContent.trim().isEmpty()) {
            return "";
        }

        // Rechercher la balise <function avec l'attribut id
        String pattern = "<function[^>]*id=\"([^\"]+)\"";
        java.util.regex.Pattern regex = java.util.regex.Pattern.compile(pattern);
        java.util.regex.Matcher matcher = regex.matcher(xmlContent);

        if (matcher.find()) {
            return matcher.group(1);
        }

        return "";
    }

    /**
     * Extrait le nom de la fonction depuis un fichier XML screen
     *
     * @param xmlFile Le fichier XML
     * @return Le nom de la fonction
     * @throws FileNotFoundException si le fichier n'existe pas
     */
    public String extractFunctionNameFromXml(File xmlFile) throws FileNotFoundException {
        StringBuilder content = new StringBuilder();

        try (java.util.Scanner scanner = new java.util.Scanner(xmlFile)) {
            while (scanner.hasNextLine()) {
                content.append(scanner.nextLine()).append("\n");
            }
        }

        return extractFunctionNameFromXml(content.toString());
    }

    /**
     * Méthode générique pour extraire le nom de fonction depuis n'importe quel type de fichier
     *
     * @param file Le fichier (Java ou XML)
     * @return Le nom de la fonction
     * @throws FileNotFoundException si le fichier n'existe pas
     */
    public String extractFunctionNameGeneric(File file) throws FileNotFoundException {
        String fileName = file.getName().toLowerCase();

        if (fileName.endsWith(".xml")) {
            // Pour les fichiers XML, extraire depuis l'attribut id
            return extractFunctionNameFromXml(file);
        } else if (fileName.endsWith(".java")) {
            // Pour les fichiers Java, extraire depuis le nom de fichier
            return extractFunctionName(file.getName());
        } else {
            // Par défaut, utiliser le nom de fichier sans extension
            return file.getName().replaceAll("\\.[^.]+$", "");
        }
    }
    public String extractFunctionName(String fileName) {
        if (fileName == null || fileName.trim().isEmpty()) {
            return "";
        }


        // Supprimer l'extension .java
        String name = fileName.replace(".java", "");

        // Supprimer le suffixe "Report" s'il existe
        if (name.endsWith("Report")) {
            name = name.substring(0, name.length() - "Report".length());
        }

        // Supprimer d'autres suffixes communs si nécessaire
        if (name.endsWith("Screen")) {
            name = name.substring(0, name.length() - "Screen".length());
        }

        if (name.endsWith("Form")) {
            name = name.substring(0, name.length() - "Form".length());
        }

        return name;
    }
    public String cleanFunctionName(String name) {
        if (name == null || name.trim().isEmpty()) {
            return "";
        }

        // 1. Retirer l'extension si elle existe
        name = name.replaceAll("\\.java$", "").replaceAll("\\.xml$", "");

        // 2. Liste des préfixes à ignorer
        String[] prefixes = {"APprt", "IPrap", "ADtcou", "APcrm", "ACom", "ARep", "ISecu", "Ctrl", "Frm"};
        for (String prefix : prefixes) {
            if (name.startsWith(prefix)) {
                name = name.substring(prefix.length());
                break;
            }
        }

        // 3. Liste des suffixes à ignorer
        String[] suffixes = {"Report", "IRap", "Screen", "Form", "List", "View", "Edition"};
        for (String suffix : suffixes) {
            if (name.endsWith(suffix)) {
                name = name.substring(0, name.length() - suffix.length());
                break;
            }
        }

        // 4. Si le nom est de type code (comme AE9I), le garder tel quel
        if (name.matches("[A-Z0-9]{3,}")) {
            return name;
        }

        // 5. Si le nom contient plusieurs majuscules, retourner la dernière partie significative
        java.util.regex.Matcher matcher = java.util.regex.Pattern
                .compile("([A-Z][a-zA-Z]*)")
                .matcher(name);

        String lastWord = name;
        while (matcher.find()) {
            lastWord = matcher.group(); // garde la dernière correspondance
        }

        // 6. Mettre la première lettre en majuscule et le reste en minuscules
        if (lastWord.length() > 1) {
            lastWord = lastWord.substring(0, 1).toUpperCase() + lastWord.substring(1).toLowerCase();
        } else {
            lastWord = lastWord.toUpperCase();
        }

        return lastWord;
    }
    public void handleCdevFields(Map<String, FieldConfig> fieldMap) {
        handleGenericDevMerge(fieldMap, "dev", "devs", "IPrapDevLov", "Devises");

    }
    private void handleGenericDevMerge(Map<String, FieldConfig> fieldMap, String prefix, String unifiedFieldId, String lov, String label) {
        // Trouver les champs avec le préfixe donné (ex: cdev1, dev2, etc.)
        List<String> devFields = fieldMap.keySet().stream()
                .filter(key -> key.matches(prefix + "\\d+"))
                .sorted(Comparator.comparingInt(k -> Integer.parseInt(k.substring(prefix.length()))))
                .collect(Collectors.toList());

        if (devFields.isEmpty()) {
            System.out.println("ℹ️ Aucun champ " + prefix + " détecté, aucune action nécessaire");
            return;
        }

        System.out.println("🔍 Champs " + prefix + " détectés: " + devFields + ", création du champ unifié: " + unifiedFieldId);

        // Supprimer les anciens champs
        devFields.forEach(field -> {
            fieldMap.remove(field);
            System.out.println("🗑️ Suppression du champ " + prefix + ": " + field);
        });

        // Propriétés par défaut
        DevFieldProperties defaultProperties = new DevFieldProperties();
        defaultProperties.minColumnNumber = 1;
        defaultProperties.minSortNumber = 19;
        defaultProperties.label = label;
        defaultProperties.hidden = "false";
        defaultProperties.readOnly = "false";
        defaultProperties.defaultValue = "";

        // Créer le champ fusionné
        FieldConfig unifiedField = createUnifiedField(defaultProperties, unifiedFieldId);

        fieldMap.put(unifiedFieldId, unifiedField);
    }





    /**
     * Extrait les propriétés des champs cdev existants

    /**
     * Crée le champ cdev unifié avec les propriétés extraites
     */
    public static FieldConfig createUnifiedField(DevFieldProperties properties, String id) {
        FieldConfig field = new FieldConfig();

        field.setId(id);                                // ex: "dev" ou "cdevs"
        field.setNature("dualfield");
        field.setColumnNumber(properties.minColumnNumber != null ? properties.minColumnNumber : 1);
        field.setSortNumber(properties.minSortNumber != null ? properties.minSortNumber : 19);
        field.setReadOnly(properties.readOnly != null ? properties.readOnly : "false");
        field.setHidden(properties.hidden != null ? properties.hidden : "false");
        field.setLov("IPrapDevLov");                    // fixe la valeur demandée
        field.setValueField("value");                   // fixe "value"
        field.setDisplayTemplate("{value} - {longLabel}");  // fixe le template
        field.setDefaultValue(properties.defaultValue != null ? properties.defaultValue : "");
        field.setLabel(properties.label != null ? properties.label : "Devises");
        field.setMaxDualFieldValues("4");

        return field;
    }


    /**
     * Log les informations du champ créé
     */
    private void logCreatedField(FieldConfig cdevField) {
        System.out.println("✅ Champ cdev unifié créé avec les propriétés:");
        System.out.println("   - id: " + cdevField.getId());
        System.out.println("   - nature: " + cdevField.getNature());
        System.out.println("   - columnNumber: " + cdevField.getColumnNumber());
        System.out.println("   - sortNumber: " + cdevField.getSortNumber());
        System.out.println("   - label: " + cdevField.getLabel());
        System.out.println("   - lov: " + cdevField.getLov());
        System.out.println("   - valueField: " + cdevField.getValueField());
        System.out.println("   - displayTemplate: " + cdevField.getDisplayTemplate());
        System.out.println("   - maxDualFieldValues: " + cdevField.getMaxDualFieldValues());
        System.out.println("   - hidden: " + cdevField.getHidden());
        System.out.println("   - readOnly: " + cdevField.getReadOnly());
        System.out.println("   - defaultValue: " + cdevField.getDefaultValue());
    }
    public FieldConfig handleNumberedFieldsByPrefix(Map<String, FieldConfig> fieldMap, String prefix, String lov, String defaultLabel) {
        // Collecte tous les champs qui commencent par prefix + numéro (ex: ridint1, ridint2, ...)
        List<String> numberedFields = fieldMap.keySet().stream()
                .filter(id -> id.matches(prefix + "\\d+"))
                .toList();

        if (numberedFields.isEmpty()) {
            return null; // Rien à faire
        }

        Integer minColumnNumber = null;
        Integer minSortNumber = null;
        String label = null;

        for (String id : numberedFields) {
            FieldConfig f = fieldMap.get(id);
            if (f == null) continue;

            if (f.getColumnNumber() != null) {
                minColumnNumber = (minColumnNumber == null) ? f.getColumnNumber() : Math.min(minColumnNumber, f.getColumnNumber());
            }
            if (f.getSortNumber() != null) {
                minSortNumber = (minSortNumber == null) ? f.getSortNumber() : Math.min(minSortNumber, f.getSortNumber());
            }
            if (label == null && f.getLabel() != null && !f.getLabel().isEmpty()) {
                label = f.getLabel();
            }
            // Supprimer les champs individuels
            fieldMap.remove(id);
        }

        FieldConfig unifiedField = new FieldConfig();
        unifiedField.setId(prefix);
        unifiedField.setNature("dualfield");
        unifiedField.setLov(lov);
        unifiedField.setValueField("value");
        unifiedField.setDisplayTemplate("{value} - {longLabel}");
        unifiedField.setMaxDualFieldValues("4");
        unifiedField.setHidden("false");
        unifiedField.setReadOnly("false");
        unifiedField.setColumnNumber(minColumnNumber != null ? minColumnNumber : 1);
        unifiedField.setSortNumber(minSortNumber != null ? minSortNumber : 1);
        unifiedField.setLabel(label != null ? label : defaultLabel);

        return unifiedField;
    }



}




