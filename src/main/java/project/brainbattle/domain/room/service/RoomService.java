package project.brainbattle.domain.room.service;


import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import project.brainbattle.domain.room.dto.response.RoomResponse;
import project.brainbattle.domain.room.entity.Room;
import project.brainbattle.domain.room.repository.RoomRepository;

import java.util.Random;

@Service
@RequiredArgsConstructor
public class RoomService {

    private final RoomRepository roomRepository;

    // 방 생성
    @Transactional
    public RoomResponse createRoom() {

        String pin = createUniquePin(); // 중복되지 않는 6자리 pin 생성

        Room room = new Room(pin); // 새로운 room 객체 생성

        roomRepository.save(room); // DB 저장

        return new RoomResponse(
                room.getId(),
                room.getPin(),
                room.isStarted()
        );
    }

    // 방 찾기
    @Transactional
    public RoomResponse startRoom(Long roomId) {

        // 방 찾기
        Room room = roomRepository.findById(roomId).orElseThrow(() -> new IllegalArgumentException("존재하지 않는 방입니다."));

        room.start(); // 게임 시작

        // 변경된 방 정보 반환
        return new RoomResponse(
                room.getId(),
                room.getPin(),
                room.isStarted()
        );
    }

    // 중복되지 않는 6자리 pin 생성
    private String createUniquePin() {
        Random random = new Random();

        while (true) {
            int number = 100000 + random.nextInt(900000); // 100000 ~ 999999 사이의 숫자 생성

            String pin = String.valueOf(number); // 숫자를 문자열로 변환

            // 이미 사용중인 pin인지 확인
            if(!roomRepository.existsByPin(pin)) {
                return pin;
            }
        }
    }
}
