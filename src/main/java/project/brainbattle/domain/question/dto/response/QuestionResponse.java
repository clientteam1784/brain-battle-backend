package project.brainbattle.domain.question.dto.response;


import lombok.Getter;
import lombok.RequiredArgsConstructor;

@Getter
@RequiredArgsConstructor
public class QuestionResponse {

    private final Long id;
    private final int questionNumber;
    private final int maxSubmitCount;
}
