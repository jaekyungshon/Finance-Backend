package com.capstone.finance.DTO.Member;

import lombok.Builder;
import lombok.Getter;
import lombok.Setter;

@Getter
@Setter
public class MemberFindPwReqDto {
    private String username;
    private String nickname;

    @Builder
    public MemberFindPwReqDto(String username, String nickname) {
        this.username = username;
        this.nickname = nickname;
    }
}