package project.brainbattle.domain.team.repository;


import org.springframework.data.jpa.repository.JpaRepository;
import project.brainbattle.domain.team.entity.Team;

import java.util.List;

public interface TeamRepository extends JpaRepository<Team, Long> {

    List<Team> findByRoomId(Long roomId); // 특정 방에 속한 모든 모둠 조회
    Team findByRoomIdAndName(Long roomId, String name); // 특정 방에서 모둠 이름으로 조회
}
