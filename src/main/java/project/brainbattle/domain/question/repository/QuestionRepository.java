package project.brainbattle.domain.question.repository;

import org.springframework.data.jpa.repository.JpaRepository;
import project.brainbattle.domain.question.entity.Question;

import java.util.List;
import java.util.Optional;

public interface QuestionRepository extends JpaRepository<Question, Long> {

    List<Question> findAllByOrderByQuestionNumber(); // 문제 번호 순서대로 전체 문제 조회

    Optional<Question> findByQuestionNumber(int questionNumber); // 문제 번호로 문제 조회
}
