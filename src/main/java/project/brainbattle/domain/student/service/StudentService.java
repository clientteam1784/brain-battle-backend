package project.brainbattle.domain.student.service;


import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import project.brainbattle.domain.student.entity.Student;
import project.brainbattle.domain.student.repository.StudentRepository;
import project.brainbattle.domain.team.entity.Team;
import project.brainbattle.domain.team.repository.TeamRepository;

@Service
@RequiredArgsConstructor
public class StudentService {

    private final StudentRepository studentRepository;
    private final TeamRepository teamRepository;

    // 학생을 특정 모둠에 등록
    @Transactional
    public Student joinTeam(Long teamId, String studentNumber) {

        // teamId를 이용해 모둠 찾기
        Team team = teamRepository.findById(teamId).orElseThrow(() -> new IllegalArgumentException("존재하지 않는 모둠입니다."));

        // 같은 모둠에 같은 학번이 이미 들어가 있는지 확인하기
        if(studentRepository.findByStudentNumberAndTeamId(studentNumber, teamId).isPresent()) {
            throw new IllegalArgumentException("이미 해당 모둠에 등록된 학번입니다.");
        }
        // 학생 객체 생성
        Student student = new Student(studentNumber, team);

        // DB 저장
        return studentRepository.save(student);
    }
}
