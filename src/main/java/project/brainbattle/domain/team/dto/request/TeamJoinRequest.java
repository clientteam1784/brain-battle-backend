package project.brainbattle.domain.team.dto.request;


import jakarta.validation.constraints.NotBlank;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

@Getter
@Setter
@NoArgsConstructor
public class TeamJoinRequest {

    @NotBlank(message = "모둠 이름은 필수입니다.")
    private String teamName;
}
