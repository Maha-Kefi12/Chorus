import json
from pathlib import Path
from jinja2 import Template

JAVA_TEMPLATE = """\
import java.util.ArrayList;
import java.util.List;
import java.util.Locale;

import javax.annotation.Resource;

import org.dozer.DozerBeanMapper;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Component;
import com.linedata.chorus.std.services.objectconverters.DateFormatter;
import com.linedata.chorus.std.services.utils.UtilsService;
import com.linedata.ekip.commons.server.log.LogFactory;
import com.linedata.ekip.commons.server.log.Logger;
import com.linedata.ekip.commons.shared.context.ActionContext;
import com.linedata.ekip.commons.shared.lov.LovOpenFunctionMode;
import com.linedata.ekip.core.server.screenservices.GridService;
import com.linedata.ekip.core.shared.context.functionalcontext.FunctionalContext;
import com.linedata.ekip.core.shared.context.screencontext.ScreenContext;
import com.linedata.ekip.core.shared.data.Data;
import com.linedata.ekip.core.shared.lov.LovEvent;

@Component
public class {{ FunctionId }}IRAPListBlockService implements GridService
{
    private static final String BEANID = "{{ FunctionId }}IRAPListBlockService";
    private final Logger logger = LogFactory.getLog({{ FunctionId }}IRAPListBlockService.class);

    @Autowired
    private {{ FunctionId }}Service {{ functionId }}Service;

    @Resource(name = "ReportMapper")
    protected DozerBeanMapper mapper;

    @Autowired
    private UtilsService utilsService;

    public String getBeanId()
    {
        return BEANID;
    }

    @Override
    public List<? extends Data> provideData(ActionContext actionContext, LovEvent event,
                                            LovOpenFunctionMode openFunctionMode, ScreenContext screenContext, Data inParameters,
                                            FunctionalContext functionalContext)
    {
        List<{{ FunctionId }}Data> result = new ArrayList<>();
        Data {{ FunctionId }}FormData = inParameters.get("DATASERVICEPARAMETER");

        if ({{ FunctionId }}FormData != null && {{ FunctionId }}FormData.get("xidlog") != null)
            utilsService.xlogUpdate({{ FunctionId }}FormData.get("xidlog"), "{{ FunctionId }}I");

        {{ FunctionId }} {{ functionId }} = mapper.map({{ FunctionId }}FormData, {{ FunctionId }}Impl.class);

        List<{{ FunctionId }}> {{ FunctionId }}List = new ArrayList<>();
        for ({{ FunctionId }} {{ FunctionId }}Element : {{ FunctionId }}List)
        {
            if ({{ FunctionId }}Element != null)
            {
                {{ FunctionId }}Data {{ FunctionId }}Data = mapper.map({{ FunctionId }}Element, {{ FunctionId }}Data.class);
                result.add({{ FunctionId }}Data);
            }
        }
        return result;
    }
}
"""

def generate_irap_list_block_service(json_path: str):
    with open(json_path, encoding="utf-8") as f:
        data = json.load(f)

    functionId = data.get("functionName")
    if not functionId:
        print("Contenu JSON :", data)
        raise ValueError("La clé 'functionName' doit être présente dans le JSON.")

    # Formattage : première lettre majuscule (Class) et première lettre minuscule (instance)
    functionId_cap = functionId[0].upper() + functionId[1:] if len(functionId) > 1 else functionId.upper()
    functionId_lower = functionId[0].lower() + functionId[1:] if len(functionId) > 1 else functionId.lower()

    base_path = Path(r"C:\Users\USER\Downloads\spring-ftl\.idea\demo") / functionId_lower
    base_path.mkdir(parents=True, exist_ok=True)

    template = Template(JAVA_TEMPLATE)
    java_content = template.render(
        FunctionId=functionId_cap,
        functionId=functionId_lower
    )

    filename = f"{functionId_cap}IRAPGridService.java"
    output_path = base_path / filename

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(java_content)

    print(f"✅ Fichier généré : {output_path}")


if __name__ == "__main__":
    json_file = r"C:\Users\USER\Downloads\spring-ftl\output\function-name-f.json"
    generate_irap_list_block_service(json_file)
