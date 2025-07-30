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
public class AINIIRAPListBlockService implements GridService
{
    private static final String BEANID = "AINIIRAPListBlockService";
    private final Logger logger = LogFactory.getLog(AINIIRAPListBlockService.class);

    @Autowired
    private AINIService aINIService;

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
        List<AINIData> result = new ArrayList<>();
        Data AINIFormData = inParameters.get("DATASERVICEPARAMETER");

        if (AINIFormData != null && AINIFormData.get("xidlog") != null)
            utilsService.xlogUpdate(AINIFormData.get("xidlog"), "AINII");

        AINI aINI = mapper.map(AINIFormData, AINIImpl.class);

        List<AINI> AINIList = new ArrayList<>();
        for (AINI AINIElement : AINIList)
        {
            if (AINIElement != null)
            {
                AINIData AINIData = mapper.map(AINIElement, AINIData.class);
                result.add(AINIData);
            }
        }
        return result;
    }
}