package project.brainbattle.domain.question.dto.request;

import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotBlank;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

@Getter
@Setter
@NoArgsConstructor
public class QuestionRequest {

    @Min(value = 1, message = "문제 번호는 1 이상이어야 합니다.")
    private int questionNumber; // 문제 번호

    @NotBlank(message = "정답은 필수입니다.")
    private String answer; // 정답

    @Min(value = 1, message = "최대 제출 횟수는 1회 이상이어야 합니다.")
    private int maxSubmitCount; // 최대 제출 횟수
}