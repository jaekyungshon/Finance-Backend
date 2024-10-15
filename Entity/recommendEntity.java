package com.capstone.finance.Entity;

import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.Table;

@Entity
@Table(name = "recommend")
public class recommendEntity {
    @Id
    private String code;
    private int last_pv;

    public String getCode(){
        return code;
    }
    public void setCode(String code){
        this.code = code;
    }

    public int getLast_pv(){
        return last_pv;
    }

    public void setLast_pv(int last_pv) {
        this.last_pv = last_pv;
    }
}
