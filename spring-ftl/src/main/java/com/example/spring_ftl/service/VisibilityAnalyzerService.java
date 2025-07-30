package com.example.spring_ftl.service;

import com.example.spring_ftl.dto.FieldVisibilityLink;
import com.github.javaparser.JavaParser;
import com.github.javaparser.ParseResult;
import com.github.javaparser.ast.CompilationUnit;
import com.github.javaparser.ast.body.VariableDeclarator;
import com.github.javaparser.ast.expr.MethodCallExpr;
import com.github.javaparser.ast.expr.NameExpr;
import com.github.javaparser.ast.expr.FieldAccessExpr;
import com.github.javaparser.ast.visitor.VoidVisitorAdapter;
import org.springframework.stereotype.Service;

import java.io.File;
import java.io.FileNotFoundException;
import java.nio.file.Paths;
import java.util.*;
import java.util.regex.Pattern;
import java.util.regex.Matcher;

@Service
public class VisibilityAnalyzerService {

    private final JavaParser javaParser;
    private String formId;

    public VisibilityAnalyzerService() {
        this.javaParser = new JavaParser();
        this.formId = null;
    }

    public VisibilityAnalyzerService(String formId) {
        this.javaParser = new JavaParser();
        this.formId = formId;
    }

    /**
     * Analyze a Java file for visibility relations with automatic formId detection
     */
    public List<FieldVisibilityLink> analyzeFile(String filePath) throws FileNotFoundException {
        File file = new File(filePath);
        if (!file.exists()) {
            throw new FileNotFoundException("File not found: " + filePath);
        }

        // Auto-detect formId if not set
        if (this.formId == null) {
            this.formId = extractFormIdFromFile(file);
        }

        List<FieldVisibilityLink> links = extractLinksFromJavaFile(filePath);
        String beanId = generateBeanId(this.formId);

        // Set the beanId for all links
        for (FieldVisibilityLink link : links) {
            link.setBeanId(beanId);
        }

        return links;
    }

    /**
     * Analyze a Java file for visibility relations with specific formId
     */
    public List<FieldVisibilityLink> analyzeFile(String filePath, String formId) throws FileNotFoundException {
        this.formId = formId;
        return analyzeFile(filePath);
    }

    /**
     * Extract visibility links from Java file
     */
    private List<FieldVisibilityLink> extractLinksFromJavaFile(String filePath) throws FileNotFoundException {
        File file = new File(filePath);
        List<FieldVisibilityLink> links = new ArrayList<>();

        try {
            ParseResult<CompilationUnit> parseResult = javaParser.parse(file);

            if (parseResult.getResult().isPresent()) {
                CompilationUnit cu = parseResult.getResult().get();

                VisibilityVisitor visitor = new VisibilityVisitor();
                visitor.visit(cu, null);

                links = visitor.getFieldVisibilityLinks();

                // Apply field corrections
                correctFieldLinksReferences(links);

                // Remove duplicates
                links = removeDuplicateLinks(links);

                System.out.println("✅ File analyzed: " + filePath);
                System.out.println("✅ " + links.size() + " visibility links found");
                System.out.println("✅ FormId detected: " + formId);

            } else {
                System.err.println("❌ Error parsing file: " + filePath);
                parseResult.getProblems().forEach(problem ->
                        System.err.println("  - " + problem.getMessage()));
            }

        } catch (Exception e) {
            throw new RuntimeException("Error analyzing file: " + e.getMessage(), e);
        }

        return links;
    }

    /**
     * Extract formId from file (improved logic)
     */
    private String extractFormIdFromFile(File file) {
        String fileName = file.getName();

        if (fileName.endsWith(".java")) {
            fileName = fileName.substring(0, fileName.length() - 5);
        }

        return cleanFormId(fileName);
    }

    /**
     * Clean and normalize form ID
     */
    private String cleanFormId(String name) {
        if (name == null || name.trim().isEmpty()) {
            return "default";
        }

        // Remove common prefixes
        String[] prefixes = {"APprt", "IPrap", "ADtcou", "APcrm", "ACom", "ARep", "ISecu", "Ctrl", "Frm"};
        for (String prefix : prefixes) {
            if (name.startsWith(prefix)) {
                name = name.substring(prefix.length());
                break;
            }
        }

        // Remove common suffixes
        String[] suffixes = {"Report", "IRap", "Screen", "Form", "List", "View", "Edition"};
        for (String suffix : suffixes) {
            if (name.endsWith(suffix)) {
                name = name.substring(0, name.length() - suffix.length());
                break;
            }
        }

        // Handle special cases
        if (name.matches("[A-Z0-9]{3,}")) {
            return name.toLowerCase();
        }

        if (name.matches("[A-Z]{2,6}")) {
            return name.toLowerCase();
        }

        // Extract significant part (usually 4 characters)
        String lowerName = name.toLowerCase();
        java.util.regex.Matcher endMatcher = java.util.regex.Pattern
                .compile("([a-z]{4})$")
                .matcher(lowerName);

        if (endMatcher.find()) {
            String extracted = endMatcher.group(1);
            if (isValidFormId(extracted)) {
                return extracted;
            }
        }

        // Known patterns
        if (lowerName.contains("aini")) return "aini";
        if (lowerName.contains("crm")) return "crm";
        if (lowerName.contains("com")) return "com";
        if (lowerName.contains("secu")) return "secu";
        if (lowerName.contains("dtcou")) return "dtcou";
        if (lowerName.contains("prt")) return "prt";

        return name.toLowerCase();
    }

    /**
     * Check if a form ID is valid
     */
    private boolean isValidFormId(String name) {
        if (name == null || name.length() < 3) {
            return false;
        }

        String[] validNames = {"aini", "crm", "com", "secu", "dtcou", "prt"};
        for (String validName : validNames) {
            if (name.equals(validName)) {
                return true;
            }
        }

        return name.length() == 4 && !name.matches("(.)\\1{2,}");
    }

    /**
     * Generate bean ID from form ID
     */
    private String generateBeanId(String formId) {
        if (formId == null || formId.trim().isEmpty()) {
            return "defaultFieldLinkService";
        }
        return formId.toLowerCase() + "FieldLinkService";
    }

    /**
     * Analyze directory recursively
     */
    public List<FieldVisibilityLink> analyzeDirectory(String directoryPath) {
        return analyzeDirectory(directoryPath, null);
    }

    public List<FieldVisibilityLink> analyzeDirectory(String directoryPath, String defaultFormId) {
        List<FieldVisibilityLink> allLinks = new ArrayList<>();

        try {
            File directory = new File(directoryPath);
            if (!directory.exists() || !directory.isDirectory()) {
                throw new IllegalArgumentException("Directory does not exist: " + directoryPath);
            }

            System.out.println("🔍 Analyzing directory: " + directoryPath);
            analyzeDirectoryRecursive(directory, allLinks, defaultFormId);

            correctFieldLinksReferences(allLinks);
            allLinks = removeDuplicateLinks(allLinks);

            System.out.println("✅ Directory analysis completed");
            System.out.println("✅ " + allLinks.size() + " total visibility links found");

        } catch (Exception e) {
            throw new RuntimeException("Error analyzing directory: " + e.getMessage(), e);
        }

        return allLinks;
    }

    private void analyzeDirectoryRecursive(File directory, List<FieldVisibilityLink> allLinks, String defaultFormId) {
        File[] files = directory.listFiles();
        if (files == null) return;

        for (File file : files) {
            if (file.isDirectory()) {
                analyzeDirectoryRecursive(file, allLinks, defaultFormId);
            } else if (file.getName().endsWith(".java")) {
                try {
                    String fileFormId = defaultFormId != null ? defaultFormId : extractFormIdFromFile(file);
                    List<FieldVisibilityLink> fileLinks = analyzeFile(file.getAbsolutePath(), fileFormId);
                    allLinks.addAll(fileLinks);
                } catch (Exception e) {
                    System.err.println("❌ Error analyzing file: " + file.getAbsolutePath());
                    System.err.println("   " + e.getMessage());
                }
            }
        }
    }

    /**
     * Remove duplicate links
     */
    private List<FieldVisibilityLink> removeDuplicateLinks(List<FieldVisibilityLink> links) {
        Set<String> seen = new HashSet<>();
        List<FieldVisibilityLink> uniqueLinks = new ArrayList<>();
        int duplicatesRemoved = 0;

        for (FieldVisibilityLink link : links) {
            List<String> sortedFatherIds = new ArrayList<>(link.getFatherFieldIds());
            Collections.sort(sortedFatherIds);
            String uniqueKey = link.getChildFieldId() + "|" + String.join(",", sortedFatherIds);

            if (!seen.contains(uniqueKey)) {
                seen.add(uniqueKey);
                uniqueLinks.add(link);
            } else {
                duplicatesRemoved++;
                System.out.println("🔄 Removing duplicate link: " + link.getId() +
                        " (childFieldId: " + link.getChildFieldId() +
                        ", fatherFieldIds: " + link.getFatherFieldIds() + ")");
            }
        }

        if (duplicatesRemoved > 0) {
            System.out.println("✅ " + duplicatesRemoved + " duplicate links removed");
        }

        return uniqueLinks;
    }

    /**
     * Create field mappings with corrected dev → devs mapping
     */
    private Map<String, String> createFieldMappings() {
        Map<String, String> mappings = new HashMap<>();

        // CORRECTED: dev mappings → devs (not rcedevs)
        for (int i = 1; i <= 5; i++) {
            mappings.put("dev" + i, "devs");
        }
        mappings.put("dev", "devs");

        // rcedev mappings → rcedevs
        for (int i = 1; i <= 5; i++) {
            mappings.put("rcedev" + i, "rcedevs");
        }
        mappings.put("rcedev", "rcedevs");

        // cdev mappings → cdevs
        for (int i = 1; i <= 5; i++) {
            mappings.put("cdev" + i, "cdevs");
        }
        mappings.put("cdev", "cdevs");

        // ridtin mappings
        for (int i = 1; i <= 10; i++) {
            mappings.put("ridtin" + i, "ridtins");
            mappings.put("ridtind" + i, "ridtinds");
            mappings.put("ridtint" + i, "ridtints");
        }
        mappings.put("ridtin", "ridtins");
        mappings.put("ridtind", "ridtinds");
        mappings.put("ridtint", "ridtints");

        // Address mappings
        for (int i = 1; i <= 5; i++) {
            mappings.put("adresse" + i, "adresses");
        }
        mappings.put("adresse", "adresses");

        // Date mappings
        for (int i = 1; i <= 5; i++) {
            mappings.put("date" + i, "dates");
        }
        mappings.put("date", "dates");

        // Amount mappings
        for (int i = 1; i <= 5; i++) {
            mappings.put("montant" + i, "montants");
        }
        mappings.put("montant", "montants");

        // Reference mappings
        for (int i = 1; i <= 5; i++) {
            mappings.put("ref" + i, "refs");
        }
        mappings.put("ref", "refs");

        return mappings;
    }

    /**
     * Correct field link references using mappings
     */
    private void correctFieldLinksReferences(List<FieldVisibilityLink> links) {
        Map<String, String> fieldMappings = createFieldMappings();
        int correctionsApplied = 0;

        for (FieldVisibilityLink link : links) {
            boolean linkModified = false;

            // Correct childFieldId
            String originalChildId = link.getChildFieldId();
            String correctedChildId = fieldMappings.getOrDefault(originalChildId.toLowerCase(), originalChildId);

            if (!originalChildId.equals(correctedChildId)) {
                link.setChildFieldId(correctedChildId);
                linkModified = true;
                System.out.println("🔄 Correction: childFieldId '" + originalChildId + "' → '" + correctedChildId + "'");
            }

            // Correct fatherFieldIds
            List<String> correctedFatherIds = new ArrayList<>();
            for (String fatherId : link.getFatherFieldIds()) {
                String newFatherId = fieldMappings.getOrDefault(fatherId.toLowerCase(), fatherId);
                correctedFatherIds.add(newFatherId);
                if (!fatherId.equals(newFatherId)) {
                    linkModified = true;
                    System.out.println("🔄 Correction: fatherFieldId '" + fatherId + "' → '" + newFatherId + "'");
                }
            }
            link.setFatherFieldIds(correctedFatherIds);

            // Update link ID and method name if childFieldId changed
            if (!originalChildId.equals(correctedChildId)) {
                String newLinkId = generateLinkId(correctedChildId);
                String newMethodName = generateMethodName(correctedChildId);
                link.setId(newLinkId);
                link.setMethodName(newMethodName);
                System.out.println("🔄 Update: linkId → '" + newLinkId + "', methodName → '" + newMethodName + "'");
            }

            if (linkModified) {
                correctionsApplied++;
            }
        }

        System.out.println("✅ " + correctionsApplied + " field links corrected out of " + links.size() + " total");
    }

    /**
     * Generate link ID
     */
    private String generateLinkId(String childFieldId) {
        return "link_" + childFieldId;
    }

    /**
     * Generate method name
     */
    private String generateMethodName(String childFieldId) {
        return "is" + capitalizeFirstLetter(childFieldId) + "Visible";
    }

    /**
     * Capitalize first letter
     */
    private String capitalizeFirstLetter(String str) {
        if (str == null || str.isEmpty()) {
            return str;
        }
        return str.substring(0, 1).toUpperCase() + str.substring(1);
    }

    /**
     * Visitor class for analyzing setVisible calls
     */
    private class VisibilityVisitor extends VoidVisitorAdapter<Void> {

        private final List<FieldVisibilityLink> fieldVisibilityLinks = new ArrayList<>();
        private final Map<String, String> variableAssignments = new HashMap<>();
        private final Map<String, String> fieldMappings = createFieldMappings();

        public List<FieldVisibilityLink> getFieldVisibilityLinks() {
            return fieldVisibilityLinks;
        }

        @Override
        public void visit(VariableDeclarator varDecl, Void arg) {
            super.visit(varDecl, arg);
            String varName = varDecl.getNameAsString();
            if (varDecl.getInitializer().isPresent()) {
                String expr = varDecl.getInitializer().get().toString();
                variableAssignments.put(varName, expr);
            }
        }

        @Override
        public void visit(MethodCallExpr methodCall, Void arg) {
            super.visit(methodCall, arg);

            if ("setVisible".equals(methodCall.getNameAsString())) {
                analyzeSetVisibleCall(methodCall);
            }
        }

        private void analyzeSetVisibleCall(MethodCallExpr methodCall) {
            String originalChildFieldId = extractChildFieldId(methodCall);
            if (originalChildFieldId == null) return;

            Set<String> fatherFields = new HashSet<>();

            methodCall.getArguments().forEach(arg -> {
                String argText = arg.toString();
                Set<String> directVars = new HashSet<>();
                extractVariablesFromExpression(argText, directVars);

                for (String var : directVars) {
                    collectFatherFieldsRecursive(var, fatherFields);
                }
            });

            // Filter out invalid values
            fatherFields.removeIf(f -> f == null || f.isEmpty() || f.equals("b"));

            if (fatherFields.isEmpty()) return;

            // Map the childFieldId
            String mappedChildFieldId = fieldMappings.getOrDefault(originalChildFieldId.toLowerCase(), originalChildFieldId);

            String linkId = generateLinkId(mappedChildFieldId);
            String methodName = generateMethodName(mappedChildFieldId);
            String beanId = getBeanId();

            FieldVisibilityLink link = new FieldVisibilityLink(
                    linkId,
                    mappedChildFieldId,
                    new ArrayList<>(fatherFields),
                    methodName,
                    "CONDITIONNALHIDDEN",
                    beanId,
                    false
            );
            fieldVisibilityLinks.add(link);
        }

        private String getBeanId() {
            return generateBeanId(formId);
        }

        private void collectFatherFieldsRecursive(String variable, Set<String> collected) {
            if (variable == null || variable.isEmpty()) return;

            String normalizedVar = mapVariableToSourceField(variable);

            if (collected.contains(normalizedVar)) return;
            collected.add(normalizedVar);

            if (variableAssignments.containsKey(variable)) {
                String expr = variableAssignments.get(variable);
                Set<String> varsInExpr = new HashSet<>();
                extractVariablesFromExpression(expr, varsInExpr);
                for (String var : varsInExpr) {
                    collectFatherFieldsRecursive(var, collected);
                }
            }
        }

        private String extractChildFieldId(MethodCallExpr methodCall) {
            if (methodCall.getScope().isPresent()) {
                var scope = methodCall.getScope().get();

                if (scope instanceof NameExpr nameExpr) {
                    return nameExpr.getNameAsString();
                } else if (scope instanceof FieldAccessExpr fieldAccess) {
                    return fieldAccess.getNameAsString();
                }
            }
            return null;
        }

        private void extractVariablesFromExpression(String expression, Set<String> variables) {
            List<Pattern> patterns = Arrays.asList(
                    Pattern.compile("\\b([a-zA-Z_][a-zA-Z0-9_]*)Opt[a-zA-Z0-9_]*\\b"),
                    Pattern.compile("\\b(b[A-Z][a-zA-Z0-9_]*)\\b"),
                    Pattern.compile("\\b(is[A-Z][a-zA-Z0-9_]*)\\b"),
                    Pattern.compile("\\b(has[A-Z][a-zA-Z0-9_]*)\\b"),
                    Pattern.compile("\\b([a-zA-Z_][a-zA-Z0-9_]*)\\.isVisible\\(\\)"),
                    Pattern.compile("\\b([a-zA-Z_][a-zA-Z0-9_]*)\\.getValue\\(\\)")
            );

            for (Pattern pattern : patterns) {
                Matcher matcher = pattern.matcher(expression);
                while (matcher.find()) {
                    String variable = matcher.group(1);
                    if (variable.length() <= 1) continue;
                    String sourceField = mapVariableToSourceField(variable);
                    variables.add(sourceField);
                }
            }
        }

        private String mapVariableToSourceField(String variable) {
            if (variable == null || variable.isEmpty()) {
                return variable;
            }

            // bOpt... → xceopt
            if (variable.startsWith("bOpt")) {
                return "xceopt";
            }

            // b... → remove 'b' prefix
            if (variable.startsWith("b") && variable.length() > 1) {
                String baseVar = variable.substring(1);
                for (String candidate : variableAssignments.keySet()) {
                    if (candidate.toLowerCase().contains(baseVar.toLowerCase())) {
                        return candidate.toLowerCase();
                    }
                }
                return baseVar.toLowerCase();
            }

            return variable.toLowerCase();
        }
    }

    /**
     * Display analysis results
     */
    public void displayResults(List<FieldVisibilityLink> links) {
        System.out.println("=== Conditional visibility relations detected ===");
        System.out.println("Total links: " + links.size());
        System.out.println("FormId used: " + formId);
        System.out.println();

        String xmlOutput = generateXmlOutput(links);
        System.out.println("XML Format:");
        System.out.println(xmlOutput);
        System.out.println();

        System.out.println("Link details:");
        for (FieldVisibilityLink link : links) {
            System.out.println("ID: " + link.getId());
            System.out.println("  Child Field: " + link.getChildFieldId());
            System.out.println("  Father Fields: " + link.getFatherFieldIds());
            System.out.println("  Method: " + link.getMethodName());
            System.out.println("  Nature: " + link.getNature());
            System.out.println("  Bean: " + link.getBeanId());
            System.out.println();
        }
    }

    /**
     * Generate XML output
     */
    public String generateXmlOutput(List<FieldVisibilityLink> links) {
        StringBuilder xmlOutput = new StringBuilder();

        for (int i = 0; i < links.size(); i++) {
            FieldVisibilityLink link = links.get(i);
            xmlOutput.append("<fieldLink ")
                    .append("childFieldId=\"").append(link.getChildFieldId()).append("\" ")
                    .append("id=\"").append(link.getId()).append("\" ")
                    .append("methodName=\"").append(link.getMethodName()).append("\" ")
                    .append("nature=\"").append(link.getNature()).append("\" ")
                    .append("disabled=\"").append(link.isDisabled()).append("\" ")
                    .append("beanId=\"").append(link.getBeanId()).append("\"")
                    .append("/>");

            if (i < links.size() - 1) {
                xmlOutput.append(",\n");
            }
        }

        return xmlOutput.toString();
    }

    /**
     * Filter links for output
     */
    public List<FieldVisibilityLink> filterLinksForOutput(List<FieldVisibilityLink> allLinks) {
        List<FieldVisibilityLink> filteredLinks = new ArrayList<>();

        if (allLinks == null || allLinks.isEmpty()) {
            return filteredLinks;
        }

        for (FieldVisibilityLink link : allLinks) {
            // Skip invalid child field IDs
            if (link.getChildFieldId() == null || link.getChildFieldId().trim().isEmpty()) {
                continue;
            }

            // Skip links with no valid father fields
            if (link.getFatherFieldIds() == null || link.getFatherFieldIds().isEmpty()) {
                continue;
            }

            // Filter valid father fields
            List<String> validFatherFields = new ArrayList<>();
            for (String fatherId : link.getFatherFieldIds()) {
                if (fatherId != null && !fatherId.trim().isEmpty() &&
                        !fatherId.equals("b") && !fatherId.equals("true") && !fatherId.equals("false")) {
                    validFatherFields.add(fatherId);
                }
            }

            if (validFatherFields.isEmpty()) {
                continue;
            }

            // Skip system fields
            if (isSystemField(link.getChildFieldId())) {
                continue;
            }

            // Skip self-references
            if (validFatherFields.contains(link.getChildFieldId())) {
                continue;
            }

            link.setFatherFieldIds(validFatherFields);
            filteredLinks.add(link);
        }

        System.out.println("✅ Filtering completed: " + filteredLinks.size() + " links kept out of " + allLinks.size() + " total");
        return filteredLinks;
    }

    /**
     * Check if field is a system field to exclude
     */
    private boolean isSystemField(String fieldId) {
        if (fieldId == null) return true;

        String lowerFieldId = fieldId.toLowerCase();

        String[] systemPrefixes = {"sys", "internal", "temp", "debug", "test"};
        String[] systemSuffixes = {"_temp", "_debug", "_test", "_internal"};

        for (String prefix : systemPrefixes) {
            if (lowerFieldId.startsWith(prefix)) {
                return true;
            }
        }

        for (String suffix : systemSuffixes) {
            if (lowerFieldId.endsWith(suffix)) {
                return true;
            }
        }

        return lowerFieldId.contains("$") || lowerFieldId.contains("#") || lowerFieldId.contains("@");
    }
}