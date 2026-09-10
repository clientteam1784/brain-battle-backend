package project.brainbattle.domain.answer.repository;

import org.springframework.data.jpa.repository.JpaRepository;
import project.brainbattle.domain.answer.entity.Answer;

import java.util.Optional;

public interface AnswerRepository extends JpaRepository<Answer, Long> {

    Optional<Answer> findByTeamIdAndQuestionId(
            Long teamId,
            Long questionId
    );
}
