package com.capstone.finance.Service;

import com.capstone.finance.DAO.MemberRepository;
import com.capstone.finance.Entity.Member;
import com.capstone.finance.DTO.Member.MemberResponseDto;
import lombok.RequiredArgsConstructor;
import org.springframework.security.core.userdetails.UsernameNotFoundException;
import org.springframework.stereotype.Service;
import jakarta.transaction.Transactional;

@Service
@RequiredArgsConstructor
@Transactional
public class MemberService {

    private final MemberRepository memberRepository;
    private final CustomUserDetailsService customUserDetailsService;

    public Member findMemberByUsername(String username) {
        return memberRepository.findByUsername(username)
                .orElseThrow(() -> new UsernameNotFoundException("User not found with username: " + username));
    }

    public MemberResponseDto findMemberInfoByUsername(String username) {
        return customUserDetailsService.findMemberInfoByUsername(username);
    }

    public boolean checkNickname(String nickname) {
        return memberRepository.findByNickname(nickname).isEmpty();
    }
}