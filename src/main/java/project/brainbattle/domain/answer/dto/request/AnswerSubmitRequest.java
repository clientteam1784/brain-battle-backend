package project.brainbattle.domain.answer.dto.request;


import jakarta.validation.constraints.NotBlank;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

@Getter
@Setter
@NoArgsConstructor
public class AnswerSubmitRequest {

    @NotBlank(message = "답은 필수입니다.")
    private String submittedAnswer;
}
