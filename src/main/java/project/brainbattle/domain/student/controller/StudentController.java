package project.brainbattle.domain.student.controller;


import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import project.brainbattle.domain.student.entity.Student;
import project.brainbattle.domain.student.service.StudentService;

@RestController
@RequiredArgsConstructor
@RequestMapping("/teams")
public class StudentController {

    private final StudentService studentService;

    // 특정 모둠에 학생 등록
    @PostMapping("/{teamId}/students")
    public ResponseEntity<Student> joinTeam(
            @PathVariable Long teamId,
            @RequestParam String studentNumber
    ) {
        // Service에게 학생 등록 요청
        Student student = studentService.joinTeam(
                teamId,
                studentNumber
        );

        return ResponseEntity.ok(student); // 등록된 학생 정보 반환
    }
}