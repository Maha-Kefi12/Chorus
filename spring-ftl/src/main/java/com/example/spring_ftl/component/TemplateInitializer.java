package com.example.spring_ftl.component;

import org.springframework.boot.CommandLineRunner;
import org.springframework.stereotype.Component;

import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.nio.charset.StandardCharsets;

@Component
public class TemplateInitializer implements CommandLineRunner {

    private static final String TEMPLATE_DIR = "src/main/resources/templates/";
    private static final String TEMPLATE_NAME = "generated_complete_template_with_fieldlinks_sibling.ftl.j2";

    @Override
    public void run(String... args) {
        File templateDir = new File(TEMPLATE_DIR);
        if (!templateDir.exists()) {
            if (templateDir.mkdirs()) {
                System.out.println("📁 Templates directory created: " + templateDir.getAbsolutePath());
            } else {
                System.err.println("❌ Failed to create templates directory: " + templateDir.getAbsolutePath());
                return;
            }
        }

        File templateFile = new File(TEMPLATE_DIR + TEMPLATE_NAME);
        boolean forceOverwrite = true; // Set false if you want to keep existing files

        if (!templateFile.exists() || forceOverwrite) {
            try {
                writeFreeMarkerTemplate(templateFile);
                System.out.println("✅ FreeMarker template generated successfully: " + templateFile.getAbsolutePath());
            } catch (IOException e) {
                System.err.println("❌ Error writing template: " + e.getMessage());
                e.printStackTrace();
            }
        } else {
            System.out.println("ℹ️ Template already exists: " + templateFile.getAbsolutePath());
        }
    }

    private void writeFreeMarkerTemplate(File file) throws IOException {
        String templateContent =
                "<#-- Template FTL générique combiné générée par Jinja2 -->\n" +
                        "\n" +
                        "<form id=\"${form_id}\" beanId=\"${bean_id}\">\n" +
                        "    <graphic>\n" +
                        "        <headerVisible>false</headerVisible>\n" +
                        "        <collapsible>false</collapsible>\n" +
                        "        <collapsed>false</collapsed>\n" +
                        "    </graphic>\n" +
                        "    <fieldLinks>\n" +
                        "        <#list fieldLinks as link>\n" +
                        "        <fieldLink childFieldId=\"${link.childFieldId}\" id=\"link_${link.childFieldId}\"\n" +
                        "                   methodName=\"is${link.childFieldId}Visible\" nature=\"CONDITIONNALHIDDEN\" disabled=\"false\"\n" +
                        "                   beanId=\"${${FonctionName}}FieldLinkService\">\n" +
                        "            <#list link.fatherFieldIds as father>\n" +
                        "            <fieldLinkFather fatherFieldId=\"${father}\" />\n" +
                        "        </#list>\n" +
                        "        </fieldLink>\n" +
                        "    </#list>\n" +
                        "    </fieldLinks>\n" +
                        "    <areas>\n" +
                        "        <#list areas as area>\n" +
                        "            <area id=\"${area.id}\" sortNumber=\"${area.sortNumber!''}\">\n" +
                        "            <graphic>\n" +
                        "                <headerVisible>false</headerVisible>\n" +
                        "            </graphic>\n" +
                        "            <fields>\n" +
                        "                <#assign sort = 1>\n" +
                        "                <#list area.fields as field>\n" +
                        "                <field\n" +
                        "                <#if field.id??>id=\"${field.id}\"</#if>\n" +
                        "            <#if field.nature??>nature=\"${field.nature}\"</#if>\n" +
                        "            <#if field.defaultValue??>defaultValue=\"${field.defaultValue}\"</#if>\n" +
                        "            columnNumber=\"1\"\n" +
                        "            sortNumber=\"${sort}\"\n" +
                        "            <#if field.maxLength??>maxLength=\"${field.maxLength}\"</#if>\n" +
                        "            <#if field.readOnly??>readOnly=\"${field.readOnly}\"</#if>\n" +
                        "            <#if field.hidden??>hidden=\"${field.hidden}\"</#if>\n" +
                        "            <#if field.lov??>lov=\"${field.lov}\"</#if>\n" +
                        "            <#if field.valueField??>valueField=\"${field.valueField}\"</#if>\n" +
                        "            />\n" +
                        "            <#assign sort = sort + 1>\n" +
                        "            </#list>\n" +
                        "            </fields>\n" +
                        "            </area>\n" +
                        "        </#list>\n" +
                        "    </areas>\n" +
                        "</form>\n";

        // Ensure parent directories exist
        if (file.getParentFile() != null) {
            file.getParentFile().mkdirs();
        }

        try (FileOutputStream fos = new FileOutputStream(file)) {
            fos.write(templateContent.getBytes(StandardCharsets.UTF_8));
        }
    }
}
