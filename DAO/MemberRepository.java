package com.capstone.finance.DAO;

import com.capstone.finance.Entity.Member;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.Optional;

public interface MemberRepository extends JpaRepository<Member,Long> {
    Optional<Member> findByUsername(String username);
    boolean existsByUsername(String username);
    Optional<Member> findByNickname(String nickname);
}