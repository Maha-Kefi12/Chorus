import json
from pathlib import Path
from jinja2 import Template

JAVA_TEMPLATE = """\
package com.linedata.chorus.std.gui.{{ functionId_lower }};

import java.util.*;
import javax.annotation.Resource;

import org.dozer.DozerBeanMapper;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Component;

import com.linedata.chorus.std.gui.commons.server.ExceptionManager;
import com.linedata.chorus.std.services.irap.GenericReportService;
import com.linedata.chorus.std.services.commons.jdbc.ChorusStoredProcedure;
import com.linedata.ekip.commons.shared.context.ActionContext;
import com.linedata.ekip.core.server.screenservices.ScreenService;
import com.linedata.ekip.core.shared.context.screencontext.ScreenContext;
import com.linedata.ekip.core.shared.data.Data;
import com.linedata.ekip.core.shared.data.ScreenServiceResponse;

@Component
public class {{ functionId_cap }}IRAPFunctionService extends ScreenService
{
    private static final String BEANID = "{{ functionId_cap }}IRAPFunctionService";

    @Autowired
    protected ChorusStoredProcedure chorusStoredProcedure;

    @Autowired
    private GenericReportService genericService;

    @Resource(name = "ReportMapper")
    protected DozerBeanMapper mapper;

    @Resource(name = "ExceptionManager")
    private ExceptionManager exceptionManager;

    @Override
    public String getBeanId()
    {
        return BEANID;
    }

    @Override
    public void manageActionMappings()
    {
        getActionMappings().put("launch", "launch");
    }

    public ScreenServiceResponse launch(ActionContext actionContext, String functionId,
                                        ScreenContext screenContext, Data inParameters) throws Exception
    {
        ScreenServiceResponse response = initScreenServiceResponse(screenContext);
        
        return response;
    }
}
"""

def generate_irap_function_service(json_path: str):
    with open(json_path, encoding="utf-8") as f:
        data = json.load(f)

    functionId = data.get("functionName")
    if not functionId:
        print("Contenu JSON :", data)
        raise ValueError("La clé 'functionName' doit être présente dans le JSON.")

    # Préparer les formats nécessaires
    functionId_lower = functionId.lower()
    functionId_cap = functionId[0].upper() + functionId[1:] if len(functionId) > 1 else functionId.upper()

    # Construire le chemin de sortie
    base_path = Path(r"C:\Users\USER\Downloads\spring-ftl\.idea\demo") / functionId_lower
    base_path.mkdir(parents=True, exist_ok=True)

    template = Template(JAVA_TEMPLATE)
    java_content = template.render(
        functionId_lower=functionId_lower,
        functionId_cap=functionId_cap
    )

    filename = f"{functionId_cap}IRAPFunctionService.java"  # Dollar devant le nom de fichier
    output_path = base_path / filename

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(java_content)

    print(f"✅ Fichier généré : {output_path}")

if __name__ == "__main__":
    json_file = r"C:\Users\USER\Downloads\spring-ftl\output\function-name-f.json"
    generate_irap_function_service(json_file)
