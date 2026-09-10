package project.brainbattle.domain.ranking.service;


import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import project.brainbattle.domain.ranking.dto.response.RankingResponse;
import project.brainbattle.domain.team.entity.Team;
import project.brainbattle.domain.team.repository.TeamRepository;

import java.util.Comparator;
import java.util.List;

@Service
@RequiredArgsConstructor
public class RankingService {

    private final TeamRepository teamRepository;

    // 특정 방에 참가한 모둠들의 현재 순위 조회
    public List<RankingResponse> getRanking(Long roomId) {
        List<Team> teams = teamRepository.findByRoomId(roomId); // 해당 방에 참가한 모든 모둠 조회

        // 순위 기준에 따라 모둠 정렬
        teams.sort(
                Comparator.comparing(Team::isFinished).reversed() // 1. 먼저 10문제를 모두 맞힌 모둠을 우선
                        .thenComparing(Team::getFinishedAt, Comparator.nullsLast(Comparator.naturalOrder())) // 2. 완료한 모둠끼리는 완료 시간이 빠른 순서
                        .thenComparing(Team::getCurrentCount, Comparator.reverseOrder()) // 3. 아직 완료하지 못한 모둠끼리는 맞힌 문제 수가 많은 순서
        );

        // Team -> RankingResponse 변환
        return java.util.stream.IntStream.range(0, teams.size())
                .mapToObj(i -> {
                    Team team = teams.get(i);

                    return new RankingResponse(
                            i + 1,
                            team.getName(),
                            team.getCurrentCount(),
                            team.isFinished(),
                            team.getFinishedAt()
                    );
                })
                .toList();
    }
}