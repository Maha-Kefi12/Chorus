package com.example.spring_ftl.controller;

import com.example.spring_ftl.dto.DevFieldProperties;
import com.example.spring_ftl.dto.FieldConfig;
import com.example.spring_ftl.service.JavaClassAnalyzer;
import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.Getter;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.io.UnsupportedEncodingException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.*;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

@RestController
@RequestMapping("/api")
public class AnalyzerController {

    private final JavaClassAnalyzer analyzer;

    public AnalyzerController(JavaClassAnalyzer analyzer) {
        this.analyzer = analyzer;
    }

    @GetMapping("analyze")
    public ResponseEntity<Map<String, Map<String, Map<String, Object>>>> analyze(@RequestParam String path) {
        try {
            File file = new File(path);
            if (!file.exists()) {
                return ResponseEntity.badRequest().body(new HashMap<>());
            }

            // 1. Analyser le fichier pour obtenir la fieldMap
            analyzer.analyze(file);

            // 2. Récupérer la fieldMap depuis l'analyzer
            Map<String, FieldConfig> fieldMap = analyzer.getFieldMap();

            // Créer un objet DevFieldProperties avec valeurs par défaut fixes
            DevFieldProperties defaultProps = new DevFieldProperties();
            defaultProps.minColumnNumber = 1;
            defaultProps.minSortNumber = 19;
            defaultProps.label = "Devises";
            defaultProps.hidden = "false";
            defaultProps.readOnly = "false";
            defaultProps.defaultValue = "";

            // Appliquer la fusion des champs ridtins
            analyzer.handleRidtinsFields(fieldMap);

            // ✅ NOUVEAU : Calculer dynamiquement maxDualFieldValues pour chaque groupe
            Map<String, Integer> maxDualFieldValues = calculateMaxDualFieldValues(fieldMap);

            // Propriétés par défaut
            DevFieldProperties defaultProperties = new DevFieldProperties();
            defaultProperties.minColumnNumber = 1;
            defaultProperties.minSortNumber = 19;
            defaultProperties.label = "Devises";
            defaultProperties.hidden = "false";
            defaultProperties.readOnly = "false";
            defaultProperties.defaultValue = "";

            // Pour devs (fusion de dev1 → n)
            defaultProperties.label = "Devises";
            Integer devsMax = maxDualFieldValues.getOrDefault("dev", 4);
            fieldMap.put("devs", createFieldConfig(defaultProperties, "devs", "devsLovServiceImpl", "dualfield", devsMax));
            System.out.println("✅ Champ 'devs' ajouté avec maxDualFieldValues = " + devsMax);


            // Pour ridtinds (fusion de ridtind1 → n)
            //Integer ridtindsMax = maxDualFieldValues.getOrDefault("ridtind", 4);
            //fieldMap.put("ridtinds", createFieldConfig(defaultProperties, "ridtind", "ridtindsLovServiceImpl", "dualfield", ridtindsMax));
            //System.out.println("✅ Champ 'ridtinds' ajouté avec maxDualFieldValues = " + ridtindsMax);

            Integer ridtints_dualfieldMax = maxDualFieldValues.getOrDefault("ridtint", 4);
            fieldMap.put("ridtins_dualfield", createFieldConfig(defaultProperties, "ridtins_dualfield", "ridtinsLovServiceImpl", "dualfield", ridtints_dualfieldMax));
            //System.out.println("✅ Champ 'ridtints' ajouté avec maxDualFieldValues = " + ridtintsMax);

            // 3. Appliquer le regroupement des champs via groupByFormId
            Map<String, Map<String, Map<String, Object>>> rawResult = analyzer.groupByFormId(fieldMap);

            // === 🔁 Déplacement de 'ridtins' et 'cdev' depuis 'default' ===
            Map<String, Map<String, Object>> defaultGroup = rawResult.get("default");
            if (defaultGroup != null) {
                List<String> specialFields = Arrays.asList("ridtins","ridtint", "dev", "devs", "rcedevs", "rcedev","ridtints","ridtins_dualfield","ridtin_dualfield");

                for (String specialField : specialFields) {
                    if (defaultGroup.containsKey(specialField)) {
                        Map<String, Object> fieldData = defaultGroup.remove(specialField);

                        Optional<String> firstRealFormId = rawResult.keySet().stream()
                                .filter(k -> !"default".equals(k))
                                .findFirst();

                        if (firstRealFormId.isPresent()) {
                            String targetFormId = firstRealFormId.get();
                            rawResult.putIfAbsent(targetFormId, new LinkedHashMap<>());
                            Map<String, Map<String, Object>> targetGroup = rawResult.get(targetFormId);

                            if (!targetGroup.containsKey(specialField)) {
                                targetGroup.put(specialField, fieldData);
                                System.out.println("✅ Champ '" + specialField + "' déplacé vers le groupe '" + targetFormId + "'");
                            } else {
                                System.out.println("⚠️ Champ '" + specialField + "' déjà présent dans '" + targetFormId + "', non déplacé.");
                            }
                        }
                    }
                }

                // Supprimer "default" s'il est vide
                if (defaultGroup.isEmpty()) {
                    rawResult.remove("default");
                    System.out.println("🧹 Groupe 'default' supprimé car vide.");
                }
            }

            // Extraction et nettoyage des labels
            Map<String, String> labels = analyzer.extractLabelTexts();
            Map<String, String> fixedLabels = new HashMap<>();

            for (Map.Entry<String, String> entry : labels.entrySet()) {
                String key = entry.getKey();
                String value = entry.getValue();
                // Applique le nettoyage / correction d'encodage ici
                String cleanedValue = cleanLabel(value);
                fixedLabels.put(key, cleanedValue);
                System.out.println("🔧 Label nettoyé: " + key + " -> '" + value + "' devient '" + cleanedValue + "'");
            }

            // Reconstruction finale en excluant les anciens cdevX
            Map<String, Map<String, Map<String, Object>>> fixedResult = new HashMap<>();

            for (var entryFormId : rawResult.entrySet()) {
                String formId = entryFormId.getKey();
                Map<String, Map<String, Object>> fields = entryFormId.getValue();

                Map<String, Map<String, Object>> fixedFields = new HashMap<>();

                for (var entryField : fields.entrySet()) {
                    String fieldId = entryField.getKey();

                    // IGNORER les anciens champs cdev1, cdev2, cdev3, ...
                    // IGNORER tous les champs avec suffixes numériques ou doublons simples (ex: ridint, rcedev)
                    if (fieldId.matches("(cdev|dev|ridint|rcedev|ridtind|ridtint)\\d+")) {
                        System.out.println("🚫 Ignorer le champ ancien " + fieldId);
                        continue;
                    }

                    Map<String, Object> fieldProps = new HashMap<>(entryField.getValue());

                    Object defaultValue = entryField.getValue().get("defaultValue");
                    if (defaultValue != null) {
                        System.out.println("🟩 Field " + fieldId + " has defaultValue = " + defaultValue);
                        fieldProps.put("defaultValue", defaultValue);
                    } else {
                        System.out.println("🟥 Field " + fieldId + " has NO defaultValue set.");
                        fieldProps.put("defaultValue", ""); // force inclusion même vide
                    }

                    if (fieldProps.containsKey("visible")) {
                        Object visibleObj = fieldProps.get("visible");
                        boolean visible = false;
                        if (visibleObj instanceof Boolean) {
                            visible = (Boolean) visibleObj;
                        } else if (visibleObj instanceof String) {
                            visible = Boolean.parseBoolean((String) visibleObj);
                        }
                        fieldProps.put("hidden", String.valueOf(!visible));
                    } else {
                        if ("adtcou".equals(fieldId)) {
                            fieldProps.put("hidden", "false");
                        } else {
                            fieldProps.putIfAbsent("hidden", "false");
                        }
                        if ("xidcev".equals(fieldId)) {
                            fieldProps.put("hidden", "false");
                        } else {
                            fieldProps.putIfAbsent("hidden", "false");
                        }

                        if ("devs".equals(fieldId)) {
                            fieldProps.put("lov", "devsLovServiceImpl");
                            fieldProps.put("valueField", "value");
                            fieldProps.put("displayTemplate", "{value} - {longLabel}");
                        }

                        
                        if ("ridtins_dualfield".equals(fieldId)) {
                            fieldProps.put("lov", "devsLovServiceImpl");
                            fieldProps.put("valueField", "value");
                            fieldProps.put("displayTemplate", "{value} - {longLabel}");
                        }
                    }

                    // ✅ CORRECTION : Utiliser fixedLabels au lieu de labels
                    String labelFromExtracted = fixedLabels.get(fieldId);
                    if (labelFromExtracted != null && !labelFromExtracted.isEmpty()) {
                        fieldProps.put("label", labelFromExtracted);
                        System.out.println("✅ Label appliqué pour " + fieldId + ": " + labelFromExtracted);
                    } else if (!fieldProps.containsKey("label")) {
                        fieldProps.put("label", "");
                    }

                    fixedFields.put(fieldId, fieldProps);
                }
                fixedResult.put(formId, fixedFields);
            }

            // Optionnel : sauvegarde JSON dans un fichier (implémente ta méthode)
            ObjectMapper mapper = new ObjectMapper();
            String jsonResult = mapper.writerWithDefaultPrettyPrinter().writeValueAsString(fixedResult);
            saveResponseToFile(jsonResult);

            return ResponseEntity.ok(fixedResult);

        } catch (Exception e) {
            e.printStackTrace();
        }
        return ResponseEntity.internalServerError().body(new HashMap<>());
    }

    /**
     * ✅ NOUVELLE MÉTHODE : Calcule dynamiquement maxDualFieldValues pour chaque groupe de champs
     * @param fieldMap La carte des champs analysés
     * @return Map avec le préfixe du champ et le nombre maximum détecté
     */
    private Map<String, Integer> calculateMaxDualFieldValues(Map<String, FieldConfig> fieldMap) {
        Map<String, Integer> maxValues = new HashMap<>();

        // Pattern pour détecter les champs avec suffixes numériques
        Pattern pattern = Pattern.compile("^(dev|cdev|rcedev|ridtind|ridtint|ridint)(\\d+)$");

        for (String fieldId : fieldMap.keySet()) {
            Matcher matcher = pattern.matcher(fieldId);
            if (matcher.matches()) {
                String prefix = matcher.group(1);
                int number = Integer.parseInt(matcher.group(2));

                // Garder le maximum pour chaque préfixe
                maxValues.put(prefix, Math.max(maxValues.getOrDefault(prefix, 0), number));

                System.out.println("🔍 Détecté: " + fieldId + " -> préfixe: " + prefix + ", numéro: " + number);
            }
        }

        // Afficher les résultats
        for (Map.Entry<String, Integer> entry : maxValues.entrySet()) {
            System.out.println("📊 Groupe '" + entry.getKey() + "' -> maxDualFieldValues = " + entry.getValue());
        }

        return maxValues;
    }

    // ... (rest of your existing methods remain the same)

    private String fixEncoding(String s) {
        if (s == null) return null;
        try {
            byte[] bytes = s.getBytes("ISO-8859-1");
            return new String(bytes, StandardCharsets.UTF_8);
        } catch (Exception e) {
            return s;
        }
    }

    public String cleanLabel(String input) {
        if (input == null || input.isEmpty()) {
            return input;
        }

        String result = input;

        // 1. Nettoyer les séquences d'échappement mal formées
        result = result.replace("\\'", "'");
        result = result.replace("\\\"", "\"");
        result = result.replace("\\\\", "\\");

        // 2. Remplacer les caractères de remplacement courants
        result = result.replace("?", "é"); // Cas spécifique pour échéance
        result = result.replace("�", "é"); // Caractère de remplacement Unicode

        // 3. Corrections spécifiques pour les mots français courants
        result = applyFrenchCorrections(result);

        // 4. Corrections avec regex pour les patterns restants
        result = result.replaceAll("(?i)d'(.?)ch(.?)ance", "d'échéance");
        result = result.replaceAll("(?i)ech(.?)ance", "échéance");

        // 5. Tentative de correction de l'encodage UTF-8 mal interprété
        try {
            // Vérifier si la chaîne contient des caractères suspects
            if (containsSuspiciousChars(result)) {
                // Essayer différentes conversions d'encodage
                String[] encodings = {"ISO-8859-1", "Windows-1252", "UTF-8"};

                for (String fromEncoding : encodings) {
                    try {
                        byte[] bytes = result.getBytes(fromEncoding);
                        String decoded = new String(bytes, "UTF-8");

                        // Vérifier si le décodage a amélioré la chaîne
                        if (isValidUTF8(decoded) && !containsSuspiciousChars(decoded)) {
                            result = decoded;
                            break;
                        }
                    } catch (Exception e) {
                        // Continuer avec l'encodage suivant
                    }
                }
            }
        } catch (Exception e) {
            // Log l'erreur mais continuer avec la chaîne originale
            System.err.println("Erreur d'encodage lors du nettoyage du label: " + e.getMessage());
        }

        // 6. Nettoyage final des espaces
        result = result.trim();
        result = result.replaceAll("\\s+", " ");

        return result;
    }

    /**
     * Vérifie si la chaîne contient des caractères suspects indiquant un problème d'encodage
     */
    private boolean containsSuspiciousChars(String str) {
        // Recherche de séquences typiques d'UTF-8 mal interprété en ISO-8859-1
        return str.contains("�") || // Caractère de remplacement Unicode
                str.contains("?") || // Points d'interrogation suspects
                str.contains("Ã©") || // é mal encodé
                str.contains("Ã¨") || // è mal encodé
                str.contains("Ã ") || // à mal encodé
                str.contains("Ã§") || // ç mal encodé
                str.matches(".*[\\u00C0-\\u00FF]{2,}.*"); // Séquences de caractères Latin-1 étendus
    }

    /**
     * Vérifie si une chaîne est un UTF-8 valide et lisible
     */
    private boolean isValidUTF8(String str) {
        try {
            // Vérifier que la chaîne peut être encodée/décodée sans perte
            byte[] bytes = str.getBytes("UTF-8");
            String roundtrip = new String(bytes, "UTF-8");

            // Vérifier que le résultat est plus lisible (moins de caractères suspects)
            return roundtrip.equals(str) && !containsSuspiciousChars(str);
        } catch (UnsupportedEncodingException e) {
            return false;
        }
    }

    /**
     * Dictionnaire de corrections spécifiques pour les mots français courants
     */
    private String applyFrenchCorrections(String input) {
        Map<String, String> corrections = new HashMap<>();
        corrections.put("d'?ch?ance", "d'échéance");
        corrections.put("d'�ch�ance", "d'échéance");
        corrections.put("?ch?ance", "échéance");
        corrections.put("�ch�ance", "échéance");
        corrections.put("cr?ation", "création");
        corrections.put("cr�ation", "création");
        corrections.put("mod?le", "modèle");
        corrections.put("mod�le", "modèle");
        corrections.put("r?f?rence", "référence");
        corrections.put("r�f�rence", "référence");
        corrections.put("cat?gorie", "catégorie");
        corrections.put("cat�gorie", "catégorie");

        String result = input;
        for (Map.Entry<String, String> entry : corrections.entrySet()) {
            result = result.replace(entry.getKey(), entry.getValue());
        }

        return result;
    }

    private void saveResponseToFile(String jsonResult) {
        try {
            // ✅ Chemin fixe — à ajuster selon ton environnement si besoin
            String outputPath = "C:\\Users\\USER\\Downloads\\spring-ftl\\output\\response.json";
            File outputFile = new File(outputPath);

            // ✅ Créer le dossier s'il n'existe pas
            outputFile.getParentFile().mkdirs();

            // ✅ Écraser à chaque fois
            try (FileWriter writer = new FileWriter(outputFile, false)) {
                writer.write(jsonResult);
                System.out.println("✅ Résultat sauvegardé dans : " + outputFile.getAbsolutePath());
            }
        } catch (IOException e) {
            System.err.println("❌ Erreur lors de la sauvegarde : " + e.getMessage());
        }
    }

    @GetMapping("extract-function")
    public ResponseEntity<Map<String, String>> extractFunction(@RequestParam String path) {
        File file = new File(path);
        if (!file.exists()) {
            Map<String, String> errorResponse = new HashMap<>();
            errorResponse.put("error", "File not found: " + path);
            return ResponseEntity.badRequest().body(errorResponse);
        }

        try {
            // ✅ Appel via instance car méthode NON statique
            String functionName = analyzer.extractFunctionNameGeneric(file);

            // ✅ Créer la réponse
            Map<String, String> response = new LinkedHashMap<>();
            response.put("fileName", file.getName());
            response.put("functionName", functionName);
            response.put("filePath", file.getAbsolutePath());

            // ✅ Sauvegarde dans un fichier
            saveFunctionNameToFile(response);

            return ResponseEntity.ok(response);

        } catch (Exception e) {
            e.printStackTrace();
            Map<String, String> errorResponse = new HashMap<>();
            errorResponse.put("error", "Error processing file: " + e.getMessage());
            return ResponseEntity.internalServerError().body(errorResponse);
        }
    }

    private void saveFunctionNameToFile2(String functionName) {
        try {
            String outputPath = "C:\\Users\\USER\\Downloads\\spring-ftl\\output\\function-name-f.json";

            // Écraser et sauvegarder le nouveau nom
            Map<String, String> output = new HashMap<>();
            output.put("functionName", functionName);

            ObjectMapper mapper = new ObjectMapper();
            mapper.writerWithDefaultPrettyPrinter().writeValue(new File(outputPath), output);

            System.out.println("✅ Nom de fonction sauvegardé dans : " + outputPath);
        } catch (IOException e) {
            System.err.println("❌ Erreur lors de la sauvegarde du nom de fonction : " + e.getMessage());
        }
    }

    private void saveFunctionNameToFile(Map<String, String> data) {
        try {
            String outputPath = "C:\\Users\\USER\\Downloads\\spring-ftl\\output\\function-name.json";
            File outputFile = new File(outputPath);
            outputFile.getParentFile().mkdirs(); // Crée le dossier s'il n'existe pas

            ObjectMapper mapper = new ObjectMapper();
            String json = mapper.writerWithDefaultPrettyPrinter().writeValueAsString(data);

            try (FileWriter writer = new FileWriter(outputFile, false)) {
                writer.write(json);
                System.out.println("✅ Nom de fonction sauvegardé dans : " + outputFile.getAbsolutePath());
            }

        } catch (IOException e) {
            System.err.println("❌ Erreur lors de la sauvegarde du nom de fonction : " + e.getMessage());
        }
    }

    @GetMapping("/extract-function-name")
    public ResponseEntity<Map<String, String>> extractFunctionNameFromFile(@RequestParam String path) {
        Map<String, String> response = new HashMap<>();
        File file = new File(path);

        if (!file.exists()) {
            response.put("error", "❌ Le fichier n'existe pas : " + path);
            return ResponseEntity.badRequest().body(response);
        }

        try {
            // Appel de ta méthode générique
            String functionName = analyzer.extractFunctionNameGeneric(file);

            response.put("filePath", file.getAbsolutePath());
            response.put("fileName", file.getName());
            response.put("functionName", functionName);

            return ResponseEntity.ok(response);
        } catch (Exception e) {
            e.printStackTrace();
            response.put("error", "❌ Erreur lors de l'extraction : " + e.getMessage());
            return ResponseEntity.internalServerError().body(response);
        }
    }

    @GetMapping("/extract-function-name-1")
    public ResponseEntity<Map<String, String>> extractFunctionNameFromFileF(@RequestParam String path) {
        Map<String, String> response = new HashMap<>();
        File file = new File(path);

        if (!file.exists()) {
            response.put("error", "❌ Le fichier n'existe pas : " + path);
            return ResponseEntity.badRequest().body(response);
        }

        try {
            // Étape 1 : extraire le nom brut via méthode générique
            String rawFunctionName = analyzer.extractFunctionNameGeneric(file);

            // Étape 2 : nettoyer via méthode du service
            String cleanedFunctionName = analyzer.cleanFunctionName(rawFunctionName);
            // ✅ Sauvegarde automatique
            saveFunctionNameToFile2(cleanedFunctionName);

            response.put("filePath", file.getAbsolutePath());
            response.put("fileName", file.getName());
            response.put("rawFunctionName", rawFunctionName);
            response.put("functionName", cleanedFunctionName);

            return ResponseEntity.ok(response);
        } catch (Exception e) {
            e.printStackTrace();
            response.put("error", "❌ Erreur lors de l'extraction : " + e.getMessage());
            return ResponseEntity.internalServerError().body(response);
        }
    }

    /**
     * ✅ MÉTHODE MODIFIÉE : Crée une FieldConfig avec maxDualFieldValues dynamique
     */
    private FieldConfig createFieldConfig(DevFieldProperties properties, String id, String lovService, String nature, Integer maxDualFieldValues) {
        FieldConfig field = new FieldConfig();

        field.setId(id);
        field.setNature(nature);
        field.setColumnNumber(properties.minColumnNumber != null ? properties.minColumnNumber : 1);
        field.setSortNumber(properties.minSortNumber != null ? properties.minSortNumber : 19);
        field.setReadOnly(properties.readOnly != null ? properties.readOnly : "false");
        field.setHidden(properties.hidden != null ? properties.hidden : "false");

        field.setLov(lovService);
        field.setValueField("value");
        field.setDisplayTemplate("{value} - {longLabel}");
        field.setDefaultValue(properties.defaultValue != null ? properties.defaultValue : "");
        field.setLabel(properties.label != null ? properties.label : "Valeur par défaut");

        // ✅ Définir maxDualFieldValues de manière dynamique
        if ("dualfield".equals(nature)) {
            field.setMaxDualFieldValues(String.valueOf(maxDualFieldValues != null ? maxDualFieldValues : 4));
        }

        return field;
    }

    /**
     * ✅ MÉTHODE DE COMPATIBILITÉ : Version avec maxDualFieldValues par défaut
     */
    private FieldConfig createFieldConfig(DevFieldProperties properties, String id, String lovService, String nature) {
        return createFieldConfig(properties, id, lovService, nature, 4);
    }
}