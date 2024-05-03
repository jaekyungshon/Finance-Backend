package com.capstone.finance.DAO;
import com.capstone.finance.Entity.recommendEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface recommendDao extends JpaRepository<recommendEntity, String> {

}
