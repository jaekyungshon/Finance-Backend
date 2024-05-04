package com.capstone.finance.Controller;

import com.capstone.finance.DTO.Member.*;
import com.capstone.finance.DTO.Token.TokenReqDto;
import com.capstone.finance.DTO.Token.TokenResDto;
import com.capstone.finance.Service.AuthService;
import com.capstone.finance.Service.VerificationTokenService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/auth")
@RequiredArgsConstructor
public  class AuthController {
    private final AuthService authService;
    private final VerificationTokenService verificationTokenService;

    @PostMapping("/signup")
    public ResponseEntity<MemberResponseDto> signup(@RequestBody MemberRequestDto memberRequestDto) {

        return ResponseEntity.ok(authService.signup(memberRequestDto));
    }

    @PostMapping("/login")
    public ResponseEntity<TokenResDto> login(@RequestBody LoginDto loginDto) {
        return ResponseEntity.ok(authService.login(loginDto));
    }

    @PostMapping("/logout")
    public ResponseEntity<?> logout(@RequestBody TokenReqDto requestDto) {
        authService.logout(requestDto);
        return ResponseEntity.ok().build();
    }

    @PostMapping("/reissue")
    public ResponseEntity<TokenResDto> reissue(@RequestBody TokenReqDto tokenReqDto) {
        return ResponseEntity.ok(authService.reissue(tokenReqDto));
    }
}
