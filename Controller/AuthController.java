package com.capstone.finance.Controller;

import com.capstone.finance.DTO.Member.LoginDto;
import com.capstone.finance.DTO.Member.MemberRequestDto;
import com.capstone.finance.DTO.Member.MemberResponseDto;
import com.capstone.finance.DTO.Token.TokenReqDto;
import com.capstone.finance.DTO.Token.TokenResDto;
import com.capstone.finance.JWT.TokenProvider;
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
    private final TokenProvider tokenProvider;
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

    @PostMapping("/chatbot")
    public ResponseEntity<?> accessSecureResource(@RequestHeader("Authorization") String authorizationHeader) {
        // 헤더에서 Authorization 값 파싱
        if (authorizationHeader != null && authorizationHeader.startsWith("Bearer ")) {
            String accessToken = authorizationHeader.substring(7); // "Bearer " 이후의 토큰 추출
            // 여기서 Access Token을 사용하여 작업 수행
            boolean isValid = tokenProvider.validateToken(accessToken);
            if (isValid) {
                return ResponseEntity.ok("Token is valid. Welcome to the chatbot!");
            } else {
                return ResponseEntity.status(401).body("Invalid token. Access denied.");
            }

        } else {
            return ResponseEntity.status(401).body("Invalid token. Access denied.");
        }
    }


    @PostMapping("/reissue")
    public ResponseEntity<?> reissue(@RequestHeader("Authorization") String authorizationHeader) {
        if (authorizationHeader != null && authorizationHeader.startsWith("Bearer ")) {
            String refreshToken = authorizationHeader.substring(7); // "Bearer " 이후의 토큰 추출

            return ResponseEntity.ok(authService.reissue(refreshToken));
        } else {
            return ResponseEntity.status(401).body("Invalid token. Access denied.");
        }
    }
}
