package project.brainbattle.domain.question.controller;


import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import project.brainbattle.domain.question.dto.request.QuestionRequest;
import project.brainbattle.domain.question.dto.response.QuestionResponse;
import project.brainbattle.domain.question.service.QuestionService;

import java.util.List;

@RestController
@RequiredArgsConstructor
@RequestMapping("/questions")
public class QuestionController {

    private final QuestionService questionService;

    @PostMapping
    public ResponseEntity<QuestionResponse> createQuestion(
            @Valid @RequestBody QuestionRequest request
            ) {
        // Service에 문제 생성 요청
        QuestionResponse question = questionService.createQuestion(
                request.getQuestionNumber(),
                request.getAnswer(),
                request.getMaxSubmitCount()
        );

        return ResponseEntity.ok(question); // 생성된 문제 반환
    }

    // 전체 문제 조회
    @GetMapping
    public ResponseEntity<List<QuestionResponse>> getQuestions() {
        List<QuestionResponse> questions = questionService.getQuestions();
        return ResponseEntity.ok(questions);
    }

    // 문제 수정
    @PatchMapping("/{questionId}")
    public ResponseEntity<QuestionResponse> updateQuestion(
            @PathVariable Long questionId,
            @Valid @RequestBody QuestionRequest request
    ) {
        // Service에 문제 수정 요청
        QuestionResponse question = questionService.updateQuestion(
                questionId,
                request.getQuestionNumber(),
                request.getAnswer(),
                request.getMaxSubmitCount()
        );

        return ResponseEntity.ok(question); // 수정된 문제 반환
    }
    // 문제 삭제
    @DeleteMapping("/{questionId}")
    public ResponseEntity<Void> deleteQuestion(
            @PathVariable Long questionId
    ) {
        // Service에 문제 삭제 요청
        questionService.deleteQuestion(questionId);

        return ResponseEntity.noContent().build();
    }
}
