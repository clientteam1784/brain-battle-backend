package project.brainbattle.domain.student.repository;

import org.springframework.data.jpa.repository.JpaRepository;
import project.brainbattle.domain.student.entity.Student;

import java.util.Optional;

public interface StudentRepository extends JpaRepository<Student, Long> {

    Optional<Student> findByStudentNumber(String studentNumber); // 학번으로 학생들 찾기

    Optional<Student> findByStudentNumberAndTeamId(
            String studentNumber,
            Long teamId
    ); // 특정 모둠에 속한 학생들 찾기
}
