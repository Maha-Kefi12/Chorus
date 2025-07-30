<#-- Generic FTL Template -->
<form id="GenericForm" beanId="GenericService">
  <graphic>
    <headerVisible>false</headerVisible>
  </graphic>
  <areas>
  {% for area in areas %}
    <area id="${area.id}" sortNumber="${area.sortNumber!''}">
      <graphic>
        <headerVisible>false</headerVisible>
      </graphic>
      <fields>
        <#assign sort = 1>
        <#list area.fields as field>
          <field
            <#if field.id??>id="${field.id}"</#if>
            <#if field.nature??>nature="${field.nature}"</#if>
            <#if field.editable?has_content>editable="${field.editable}"</#if>
            columnNumber="1"
            sortNumber="${sort}"
            <#if field.maxLength??>maxLength="${field.maxLength}"</#if>
            <#if field.readOnly??>readOnly="${field.readOnly}"</#if>
            <#if field.hidden??>hidden="${field.hidden}"</#if>
            <#if field.lov??>lov="${field.lov}"</#if>
            <#if field.valueField??>valueField="${field.valueField}"</#if>
          />
          <#assign sort = sort + 1>
        </#list>
      </fields>
    </area>
  {% endfor %}
  </areas>
</form>
