package com.example.spring_ftl.dto;

import java.util.List;

public class ValuesListCallDTO {
    private String champ;
    private String methode;
    private List<String> parametres;

    public ValuesListCallDTO(String champ, String methode, List<String> parametres) {
        this.champ = champ;
        this.methode = methode;
        this.parametres = parametres;
    }

    public String getChamp() {
        return champ;
    }
    public ValuesListCallDTO() {
        // constructeur par défaut
    }


    public void setChamp(String champ) {
        this.champ = champ;
    }

    public void setMethode(String methode) {
        this.methode = methode;
    }

    public void setParametres(List<String> parametres) {
        this.parametres = parametres;
    }

    public String getMethode() {
        return methode;
    }



    public List<String> getParametres() {
        return parametres;
    }

private String type; // ou adapte selon la structure réelle
private List<?> filters; // adapte le type si besoin
private Boolean withParams;

// Getter/Setter pour type
public String getType() { return type; }
public void setType(String type) { this.type = type; }

// Getter/Setter pour filters
public List<?> getFilters() { return filters; }
public void setFilters(List<?> filters) { this.filters = filters; }

// Getter/Setter pour withParams
public Boolean getWithParams() { return withParams; }
public void setWithParams(Boolean withParams) { this.withParams = withParams; }
}
