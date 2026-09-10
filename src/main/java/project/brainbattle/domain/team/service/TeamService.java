package project.brainbattle.domain.team.service;


import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import project.brainbattle.domain.room.entity.Room;
import project.brainbattle.domain.room.repository.RoomRepository;
import project.brainbattle.domain.team.dto.response.TeamResponse;
import project.brainbattle.domain.team.entity.Team;
import project.brainbattle.domain.team.repository.TeamRepository;

@Service
@RequiredArgsConstructor
public class TeamService {

    private final TeamRepository teamRepository;
    private final RoomRepository roomRepository;

    // pin을 이용해 방에 모둠 참가
    @Transactional
    public TeamResponse joinRoom(String pin, String teamName) {

        // 입력받은 pin으로 방 찾기
        Room room = roomRepository.findByPin(pin).orElseThrow(() -> new IllegalArgumentException("존재하지 않는 pin입니다."));

        // 같은 방에 같은 이름있나 확인
        Team existingTeam = teamRepository.findByRoomIdAndName(
                room.getId(),
                teamName
        );

        // 이미 존재하면 참가 불가
        if(existingTeam != null) {
            throw new IllegalArgumentException("이미 존재하는 모둠 이름입니다.");
        }

        Team team = new Team(teamName, room); // 새로운 모둠 생성
        teamRepository.save(team);

        return new TeamResponse(
                team.getId(),
                team.getName(),
                team.getCurrentCount(),
                team.isFinished()
        );
    }
}
