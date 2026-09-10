package project.brainbattle.domain.answer.controller;


import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import project.brainbattle.domain.answer.dto.request.AnswerSubmitRequest;
import project.brainbattle.domain.answer.dto.response.AnswerResponse;
import project.brainbattle.domain.answer.service.AnswerService;

@RestController
@RequiredArgsConstructor
@RequestMapping("/teams")
public class AnswerController {

    private final AnswerService answerService;

    // 모둠이 문제에 답을 제출
    @PostMapping("/{teamId}/answers/{questionId}")
    public ResponseEntity<AnswerResponse> submitAnswer(
            @PathVariable Long teamId,
            @PathVariable Long questionId,
            @Valid @RequestBody AnswerSubmitRequest request
            ) {
        // Service에게 답안 제출 요청
        AnswerResponse answer = answerService.submitAnswer(
                teamId,
                questionId,
                request.getSubmittedAnswer()
        );

        return ResponseEntity.ok(answer); // 답안 dto 반환
    }
}
