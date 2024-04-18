package com.capstone.finance.DTO.Member;

import lombok.Builder;
import lombok.Getter;
import lombok.Setter;

@Getter
@Setter
public class MemberFindIdReqDto {
    private String nickname;
    private Integer findQuesNum;
    private String findAnswer;

    @Builder
    public MemberFindIdReqDto(String nickname, Integer findQuesNum, String findAnswer) {
        this.nickname = nickname;
        this.findQuesNum = findQuesNum;
        this.findAnswer = findAnswer;
    }
}