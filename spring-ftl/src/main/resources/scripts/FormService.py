import json
from pathlib import Path
from jinja2 import Template

JAVA_TEMPLATE = """\
package com.linedata.chorus.std.gui;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Component;
import com.linedata.chorus.std.services.utils.UtilsService;
import com.linedata.ekip.commons.shared.context.ActionContext;
import com.linedata.ekip.commons.shared.lov.LovOpenFunctionMode;
import com.linedata.ekip.core.server.screenservices.FormService;
import com.linedata.ekip.core.shared.context.functionalcontext.FunctionalContext;
import com.linedata.ekip.core.shared.context.screencontext.ScreenContext;
import com.linedata.ekip.core.shared.data.Data;
import com.linedata.ekip.core.shared.lov.LovEvent;

@Component
public class {{ functionId }}IRAPFormService implements FormService
{
    public static final String BEANID = "{{ functionId }}IRAPFormService";

    @Autowired
    UtilsService utilsService;

    @Override
    public String getBeanId()
    {
        return BEANID;
    }

    @Override
    public Data provideData(ActionContext actionContext, LovEvent event,
                            LovOpenFunctionMode openFunctionMode, ScreenContext screenContext, Data inParameters,
                            FunctionalContext functionalContext)
    {
        if (event.getValue().equals(LovEvent.SCREENOPENED.getValue()) &&
            inParameters.get("SCREENID").equals("{{ functionId }}IRAP"))
        {
            Data data = new Data();
            String xidlog = utilsService.xlogCreate("{{ functionId_upper }}C");
            String xidclg = utilsService.getXetbXidclg();
            String xidcev = utilsService.getXetbXidcev();
            data.set("xidlog", xidlog);
            data.set("xidclg", xidclg);
            data.set("reiv_xidcev", xidcev);
            return data;
        }
        return null;
    }
}
"""

def generate_form_service(json_path: str):
    with open(json_path, encoding="utf-8") as f:
        data = json.load(f)

    # Récupérer la valeur du functionId depuis "functionName" (car ton JSON a "functionName")
    functionId = data.get("functionName")
    if not functionId:
        print("Contenu JSON :", data)
        raise ValueError("La clé 'functionName' doit être présente dans le JSON.")

    # Pas de formId dans ton JSON, donc on crée un dossier avec functionId comme nom
    base_path = Path(r"C:\Users\USER\Downloads\spring-ftl\.idea\demo") / functionId
    base_path.mkdir(parents=True, exist_ok=True)

    template = Template(JAVA_TEMPLATE)
    java_content = template.render(
        functionId=functionId,
        functionId_upper=functionId.upper()
    )

    filename = f"{functionId}IRAPFormService.java"  # Dollar devant le nom du fichier
    output_path = base_path / filename

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(java_content)

    print(f"✅ Fichier généré : {output_path}")

if __name__ == "__main__":
    json_file = r"C:\Users\USER\Downloads\spring-ftl\output\function-name-f.json"
    generate_form_service(json_file)
