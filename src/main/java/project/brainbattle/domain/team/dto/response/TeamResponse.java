package project.brainbattle.domain.team.dto.response;


import lombok.Getter;
import lombok.RequiredArgsConstructor;

@Getter
@RequiredArgsConstructor
public class TeamResponse {

    private final Long id;
    private final String name;
    private final int currentCount;
    private final boolean finished;
}
