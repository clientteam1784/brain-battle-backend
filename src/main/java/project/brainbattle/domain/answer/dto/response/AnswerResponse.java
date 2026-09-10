package project.brainbattle.domain.answer.dto.response;


import lombok.Getter;
import lombok.RequiredArgsConstructor;

@Getter
@RequiredArgsConstructor
public class AnswerResponse {

    private final Long id;
    private final String submittedAnswer;
    private final boolean correct;
    private final int submitCount;
    private final int modifyCount;
}
