package project.brainbattle.domain.team.controller;


import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import project.brainbattle.domain.team.dto.request.TeamJoinRequest;
import project.brainbattle.domain.team.dto.response.TeamResponse;
import project.brainbattle.domain.team.service.TeamService;

@RestController
@RequiredArgsConstructor
@RequestMapping("/rooms")
public class TeamController {

    private final TeamService teamService;

    // 모둠이 pin이 입력해 방에 참가
    @PostMapping("/{pin}/teams")
    public ResponseEntity<TeamResponse> joinRoom(
            @PathVariable String pin,
            @Valid @RequestBody TeamJoinRequest request
            ) {
        TeamResponse team = teamService.joinRoom(pin, request.getTeamName()); // 방 참가 요청

        return ResponseEntity.ok(team); // 모둠 정보 반환
    }
}
