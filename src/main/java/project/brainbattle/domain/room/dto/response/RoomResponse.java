package project.brainbattle.domain.room.dto.response;


import lombok.Getter;
import lombok.RequiredArgsConstructor;

@Getter
@RequiredArgsConstructor
public class RoomResponse {

    private final Long id;
    private final String pin;
    private final boolean started;
}
