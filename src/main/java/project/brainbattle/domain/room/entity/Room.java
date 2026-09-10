package project.brainbattle.domain.room.entity;

import jakarta.persistence.*;
import lombok.Getter;
import lombok.NoArgsConstructor;

@Entity
@Getter
@NoArgsConstructor
public class Room {

    // 고유 Id
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    // 6자리 pin
    @Column(nullable = false, unique = true)
    private String pin;

    private boolean started = false; // 현재 진행 중인지 여부

    // 방 생성 시 사용할 생성자
    public Room(String pin) {
        this.pin = pin;
    }

    // 게임 시작
    public void start() {
        this.started = true;
    }
}
