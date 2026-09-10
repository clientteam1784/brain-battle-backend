package project.brainbattle.domain.room.repository;

import project.brainbattle.domain.room.entity.Room;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.Optional;

public interface RoomRepository extends JpaRepository<Room, Long> {

    Optional<Room> findByPin(String pin); // pin으로 방을 찾기 위한 메서드

    boolean existsByPin(String pin); // 이미 사용중인 pin 있는지 확인
}
