package project.brainbattle.domain.question.service;


import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import project.brainbattle.domain.question.dto.response.QuestionResponse;
import project.brainbattle.domain.question.entity.Question;
import project.brainbattle.domain.question.repository.QuestionRepository;

import java.util.List;

@Service
@RequiredArgsConstructor
public class QuestionService {

    private final QuestionRepository questionRepository;

    // 새로운 문제 등록
    @Transactional
    public QuestionResponse createQuestion(
            int questionNumber,
            String answer,
            int maxSubmitCount
    ) {
        // 입력받은 정보로 새로운 문제 생성
        Question question = new Question(
                questionNumber,
                answer,
                maxSubmitCount
        );

        questionRepository.save(question); // 문제 저장

        return new QuestionResponse(
                question.getId(),
                question.getQuestionNumber(),
                question.getMaxSubmitCount()
        );
    }
    // 전체 문제 조회
    public List<QuestionResponse> getQuestions() {
        return questionRepository.findAllByOrderByQuestionNumber()
                .stream()
                .map(question -> new QuestionResponse(
                        question.getId(),
                        question.getQuestionNumber(),
                        question.getMaxSubmitCount()
                ))
                .toList();
    }
    // 문제 수정
    @Transactional
    public QuestionResponse updateQuestion(
            Long questionId,
            int questionNumber,
            String answer,
            int maxSubmitCount
    ) {
        Question question = questionRepository.findById(questionId)
                .orElseThrow(() -> new IllegalArgumentException("존재하지 않는 문제입니다."));

        question.update(questionNumber, answer, maxSubmitCount);

        return new QuestionResponse(
                question.getId(),
                question.getQuestionNumber(),
                question.getMaxSubmitCount()
        );
    }
    // 문제 삭제
    @Transactional
    public void deleteQuestion(Long questionId) {
        Question question = questionRepository.findById(questionId)
                .orElseThrow(() -> new IllegalArgumentException("존재하지 않는 문제입니다."));

        questionRepository.delete(question);
    }
}
