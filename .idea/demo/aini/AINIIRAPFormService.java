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
public class AINIIRAPFormService implements FormService
{
    public static final String BEANID = "AINIIRAPFormService";

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
            inParameters.get("SCREENID").equals("AINIIRAP"))
        {
            Data data = new Data();
            String xidlog = utilsService.xlogCreate("AINIC");
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