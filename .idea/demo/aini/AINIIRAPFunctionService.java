package com.linedata.chorus.std.gui.aini;

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
public class AINIIRAPFunctionService extends ScreenService
{
    private static final String BEANID = "AINIIRAPFunctionService";

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