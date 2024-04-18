package com.capstone.finance.Controller;

import com.capstone.finance.DTO.Member.MemberResponseDto;
import com.capstone.finance.Entity.Member;
import com.capstone.finance.Service.MemberService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.*;

import java.security.Principal;

@RestController
@RequiredArgsConstructor
@RequestMapping("/api/member")
public class MemberController {
    private final MemberService memberService;

    @GetMapping("/my")
    public ResponseEntity<MemberResponseDto> getMemberInfoByUsername(Principal principal) {
        String username = principal.getName();
        return ResponseEntity.ok(memberService.findMemberInfoByUsername(username));
    }

    @GetMapping("/nickname")
    public String getUsernickname(Principal principal){
        Member member = (Member) ((Authentication) principal).getPrincipal();
        return  member.getNickname();
    }
}
