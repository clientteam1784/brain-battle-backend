package project.brainbattle.domain.team.entity;

import jakarta.persistence.*;
import lombok.Getter;
import lombok.NoArgsConstructor;
import project.brainbattle.domain.room.entity.Room;

import java.time.LocalDateTime;

@Entity
@Getter
@NoArgsConstructor
public class Team {

    // 모둠 고유 Id
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    // 모둠 이름
    @Column(nullable = false)
    private String name;

    private int currentCount = 0; // 현재 모둠 정답 개수
    private boolean finished = false; // 모든 문제를 맞췄는지 여부
    private LocalDateTime finishedAt; // 문제를 모두 맞힌시간


    // 이 모둠이 참가한 방 / 여러 모둠이 하나의 Room에 들어갈 수 있음
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "room_id", nullable = false)
    private Room room;

    // 모둠 생성 시 사용할 생성자
    public Team(String name, Room room) {
        this.name = name;
        this.room = room;
    }
    // 문제를 하나 맞췄을 때 정답 개수 증가
    public void increaseCorrectCount() {
        this.currentCount++;
    }

    // 모든 문제를 다 맞췄을 때 완료 처리
    public void finish() {
        this.finished = true;
        this.finishedAt = LocalDateTime.now();
    }
}
