package project.brainbattle.domain.ranking.controller;


import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import project.brainbattle.domain.ranking.service.RankingService;
import project.brainbattle.domain.ranking.dto.response.RankingResponse;

import java.util.List;

@RestController
@RequiredArgsConstructor
@RequestMapping("/rooms")
public class RankingController {

    private final RankingService rankingService;

    @GetMapping("/{roomId}/ranking")
    public ResponseEntity<List<RankingResponse>> getRanking(
            @PathVariable Long roomId
    ) {
        List<RankingResponse> ranking = rankingService.getRanking(roomId); // service에서 순위 조회

        return ResponseEntity.ok(ranking); // 정렬된 모둠 목록 반환
    }
}
