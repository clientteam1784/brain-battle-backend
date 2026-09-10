package project.brainbattle.domain.ranking.dto.response;


import lombok.Getter;
import lombok.RequiredArgsConstructor;

import java.time.LocalDateTime;

@Getter
@RequiredArgsConstructor
public class RankingResponse {

    private final int rank;
    private final String teamName;
    private final int currentCount;
    private final boolean finished;
    private final LocalDateTime finishedAt;
}
