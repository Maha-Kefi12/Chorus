package com.example.spring_ftl.service;

import com.example.spring_ftl.dto.ValuesListCallDTO;
import org.json.JSONArray;
import org.json.JSONObject;
import org.springframework.stereotype.Service;

import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.regex.Matcher;
import org.w3c.dom.Document;
import org.w3c.dom.Element;
import org.w3c.dom.NodeList;

import javax.xml.parsers.DocumentBuilder;
import javax.xml.parsers.DocumentBuilderFactory;

import java.io.File;
import java.io.FileNotFoundException;
import java.util.HashMap;
import java.util.regex.Pattern;

@Service
public class PanelManagerParserService {

    public List<ValuesListCallDTO> parsePanelManager(String javaSource) {
        List<ValuesListCallDTO> result = new ArrayList<>();

        // 1. Extraction classique (bloc VALUES_LIST)
        Pattern valuesListBlockPattern = Pattern.compile(
                "case\\s+UserActionType\\.VALUES_LIST:\\s*(.*?)(?:break;|default:)",
                Pattern.DOTALL);
        Matcher blockMatcher = valuesListBlockPattern.matcher(javaSource);
        if (blockMatcher.find()) {
            String valuesListBlock = blockMatcher.group(1);
            Pattern ifPattern = Pattern.compile(
                    "if\\s*\\(([^\\)]*model\\s*==[^\\)]*)\\)\\s*\\{.*?ValuesListWindowPanel\\.openValuesList\\([^,]*,\\s*AWiniSql\\.(\\w+)\\((.*?)\\)",
                    Pattern.DOTALL);
            Matcher ifMatcher = ifPattern.matcher(valuesListBlock);
            while (ifMatcher.find()) {
                String modelCondition = ifMatcher.group(1).trim();
                String methode = ifMatcher.group(2).trim();
                String paramsRaw = ifMatcher.group(3).trim();
                List<String> champs = extractModelNames(modelCondition);
                List<String> params = cleanAndSplitParams(paramsRaw);
                // Ajout spécifique pour adtinv
                if (modelCondition.contains("adtinv")) {
                    params = List.of("acealia", "aidprt", "lot_aidlot", "aidprt_d", "aidprt_f", "xceopt");
                }
                for (String champ : champs) {
                    ValuesListCallDTO dto = new ValuesListCallDTO(champ, methode, params);
                    dto.setType("lov");
                    // Détection automatique des filters
                    List<String> filters = new ArrayList<>();
                    for (String param : params) {
                        String trimmed = param.trim();
                        if (!trimmed.matches("^'.*'$") && !trimmed.matches("^\".*\"$") && !trimmed.matches("^[0-9]+$") && !trimmed.isEmpty()) {
                            filters.add(trimmed);
                        }
                    }
                    dto.setFilters(filters);
                    result.add(dto);
                }
            }
        }

        // 2. Extraction de tous les champs de nature 'lov' dans le code source (robuste multi-lignes)
        Pattern fieldDeclPattern = Pattern.compile("^(?:private|protected|public)\\s+\\w+\\s+(\\w+)\\s*;", Pattern.MULTILINE);
        Matcher fieldDeclMatcher = fieldDeclPattern.matcher(javaSource);
        while (fieldDeclMatcher.find()) {
            String champ = fieldDeclMatcher.group(1);
            // Vérifie si déjà présent dans result
            boolean alreadyPresent = result.stream().anyMatch(dto -> champ.equals(dto.getChamp()));
            if (!alreadyPresent) {
                // Cherche si ce champ a une affectation nature = "lov" ou .setNature("lov") quelque part dans le code
                Pattern naturePattern = Pattern.compile(champ + "\\s*\\.setNature\\s*\\(\\s*\"lov\"\\s*\\)|nature\\s*=\\s*\"lov\"", Pattern.CASE_INSENSITIVE);
                Matcher natureMatcher = naturePattern.matcher(javaSource);
                if (natureMatcher.find()) {
                    ValuesListCallDTO dto = new ValuesListCallDTO();
                    dto.setChamp(champ);
                    dto.setType("lov");
                    dto.setParametres(new ArrayList<>());
                    dto.setFilters(new ArrayList<>());
                    dto.setMethode(null);
                    result.add(dto);
                }
            }
        }

        return result;
    }

    private List<String> extractModelNames(String condition) {
        List<String> champs = new ArrayList<>();
        // Handle both "model == champ" and "champ.equals(model)" patterns
        Pattern pattern = Pattern.compile("(?:model\\s*==\\s*(\\w+)|(\\w+)\\.equals\\(\\s*model\\s*\\))");
        Matcher matcher = pattern.matcher(condition);
        while (matcher.find()) {
            String champ = matcher.group(1) != null ? matcher.group(1) : matcher.group(2);
            champs.add(champ);
        }
        return champs;
    }

    private List<String> cleanAndSplitParams(String paramBlock) {
        List<String> params = new ArrayList<>();
        int depth = 0;
        StringBuilder current = new StringBuilder();

        // Trim the parameter block first
        paramBlock = paramBlock.trim();

        for (int i = 0; i < paramBlock.length(); i++) {
            char c = paramBlock.charAt(i);

            if (c == ',' && depth == 0) {
                String param = current.toString().trim();
                if (!param.isEmpty()) {
                    params.add(cleanParam(param));
                }
                current.setLength(0);
            } else {
                if (c == '(') depth++;
                if (c == ')') depth--;
                current.append(c);
            }
        }

        // Add the last parameter
        String lastParam = current.toString().trim();
        if (!lastParam.isEmpty()) {
            params.add(cleanParam(lastParam));
        }

        return params;
    }

    private String cleanParam(String param) {
        // Remove only the outermost redundant quotes while preserving the actual content
        param = param.trim();

        // Check for unbalanced parentheses and fix if needed
        long openCount = param.chars().filter(ch -> ch == '(').count();
        long closeCount = param.chars().filter(ch -> ch == ')').count();
        if (openCount > closeCount) {
            param += ")"; // Add missing closing parenthesis
        }

        // Remove only surrounding quotes that wrap the entire parameter
        if (param.startsWith("\"") && param.endsWith("\"")) {
            String unquoted = param.substring(1, param.length() - 1);
            // Only keep unquoted if it doesn't break the parameter
            if (!unquoted.trim().isEmpty()) {
                param = unquoted;
            }
        }

        return param;
    }

    public String generateJsonResponse(List<ValuesListCallDTO> list) {
        if (list == null || list.isEmpty()) {
            return "[]";  // Return empty array if no data
        }

        JSONArray array = new JSONArray();

        for (ValuesListCallDTO dto : list) {
            // Skip null entries
            if (dto == null) {
                continue;
            }

            // Using LinkedHashMap to maintain insertion order
            Map<String, Object> orderedMap = new LinkedHashMap<>();

            // Add fields in the desired order
            orderedMap.put("champ", dto.getChamp() != null ? dto.getChamp() : JSONObject.NULL);
            orderedMap.put("methode", dto.getMethode() != null ? dto.getMethode() : JSONObject.NULL);

            JSONArray paramsArray = new JSONArray();
            if (dto.getParametres() != null) {
                for (String param : dto.getParametres()) {
                    paramsArray.put(param != null ? param : JSONObject.NULL);
                }
            }
            orderedMap.put("parametres", paramsArray);

            array.put(new JSONObject(orderedMap));
        }

        return array.toString(2);  // Pretty print with 2-space indentation
    }


    public List<ValuesListCallDTO> extractAllLovFields(String javaSource, List<ValuesListCallDTO> existingDtos) {
        List<ValuesListCallDTO> lovFields = new ArrayList<>();
    
        Pattern fieldDeclPattern = Pattern.compile("^(?:private|protected|public)\\s+\\w+\\s+(\\w+)\\s*;", Pattern.MULTILINE);
        Matcher fieldDeclMatcher = fieldDeclPattern.matcher(javaSource);
    
        while (fieldDeclMatcher.find()) {
            String champ = fieldDeclMatcher.group(1);
    
            // Skip if already present in result
            boolean alreadyPresent = existingDtos.stream().anyMatch(dto -> champ.equals(dto.getChamp()));
            if (alreadyPresent) continue;
    
            // Check if the field has .setNature("lov") or nature = "lov"
            Pattern naturePattern = Pattern.compile(
                champ + "\\s*\\.setNature\\s*\\(\\s*\"lov\"\\s*\\)|nature\\s*=\\s*\"lov\"",
                Pattern.CASE_INSENSITIVE);
            Matcher natureMatcher = naturePattern.matcher(javaSource);
    
            if (natureMatcher.find()) {
                ValuesListCallDTO dto = new ValuesListCallDTO();
                dto.setChamp(champ);
                dto.setType("lov");
                dto.setParametres(new ArrayList<>());
                dto.setFilters(new ArrayList<>());
                dto.setMethode(null);
                lovFields.add(dto);
            }
        }
    
        return lovFields;
    }
    
    
    public List<ValuesListCallDTO> extractAllLovFieldsIncludingEmpty(String javaSource) {
        // Step 1: Call your original method
        List<ValuesListCallDTO> result = parsePanelManager(javaSource);
    
        // Step 2: Extract additional LOV fields not already in result
        List<ValuesListCallDTO> additionalLovs = extractAllLovFields(javaSource, result);
    
        // Step 3: Add them to result
        result.addAll(additionalLovs);
    
        return result;
    }
    public List<Map<String, Object>> getAllLovFieldsFromXml(String xmlPath) {
        List<Map<String, Object>> result = new ArrayList<>();
    
        try {
            File xmlFile = new File(xmlPath);
            if (!xmlFile.exists()) {
                throw new FileNotFoundException("❌ Fichier introuvable: " + xmlPath);
            }
    
            DocumentBuilderFactory factory = DocumentBuilderFactory.newInstance();
            DocumentBuilder builder = factory.newDocumentBuilder();
            Document doc = builder.parse(xmlFile);
            doc.getDocumentElement().normalize();
    
            NodeList fields = doc.getElementsByTagName("field");
    
            for (int i = 0; i < fields.getLength(); i++) {
                Element field = (Element) fields.item(i);
                if ("lov".equals(field.getAttribute("nature"))) {
                    Map<String, Object> fieldData = new HashMap<>();
                    fieldData.put("champ", field.getAttribute("id"));
                    fieldData.put("type", "lov");
    
                    // Optional: get method name, params, etc., if present
                    String methode = field.getAttribute("valuesListMethod");
                    fieldData.put("methode", methode != null ? methode : "");
    
                    // Optional parameters
                    List<String> params = new ArrayList<>();
                    NodeList paramNodes = field.getElementsByTagName("param");
                    for (int j = 0; j < paramNodes.getLength(); j++) {
                        params.add(paramNodes.item(j).getTextContent().trim());
                    }
    
                    fieldData.put("parametres", params);
                    fieldData.put("filters", params); // duplicate if same
                    fieldData.put("withParams", !params.isEmpty());
    
                    result.add(fieldData);
                }
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
    
        return result;
    }
    
    
    
}

