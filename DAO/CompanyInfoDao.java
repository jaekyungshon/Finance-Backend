package com.capstone.finance.DAO;

import com.capstone.finance.Entity.CompanyInfoEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface CompanyInfoDao extends JpaRepository<CompanyInfoEntity, String> {

}
