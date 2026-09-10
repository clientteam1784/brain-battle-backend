package project.brainbattle.domain.room.controller;


import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import project.brainbattle.domain.room.dto.response.RoomResponse;
import project.brainbattle.domain.room.service.RoomService;

@RestController
@RequiredArgsConstructor
@RequestMapping("/rooms")
public class RoomController {

    private final RoomService roomService;

    // 방 생성
    @PostMapping
    public ResponseEntity<RoomResponse> createRoom() {

        RoomResponse room = roomService.createRoom(); // 방 생성 요청

        return ResponseEntity.ok(room); // 생성된 방 정보 클라이언트에게 반환
    }

    // 게임 시작
    @PatchMapping("/{roomId}/start")
    public ResponseEntity<RoomResponse> startRoom(
            @PathVariable Long roomId
    ) {
        RoomResponse room = roomService.startRoom(roomId);
        return ResponseEntity.ok(room);
    }
}
