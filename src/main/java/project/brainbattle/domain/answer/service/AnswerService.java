package project.brainbattle.domain.answer.service;


import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import project.brainbattle.domain.answer.dto.response.AnswerResponse;
import project.brainbattle.domain.answer.entity.Answer;
import project.brainbattle.domain.answer.repository.AnswerRepository;
import project.brainbattle.domain.question.entity.Question;
import project.brainbattle.domain.question.repository.QuestionRepository;
import project.brainbattle.domain.team.entity.Team;
import project.brainbattle.domain.team.repository.TeamRepository;

@Service
@RequiredArgsConstructor
public class AnswerService {

    private final AnswerRepository answerRepository;
    private final TeamRepository teamRepository;
    private final QuestionRepository questionRepository;

    // 모둠이 문제에 답을 제출
    @Transactional
    public AnswerResponse submitAnswer(
            Long teamId,
            Long questionId,
            String submittedAnswer
    ) {
        Team team = teamRepository.findById(teamId).orElseThrow(() -> new IllegalArgumentException("존재하지 않는 모둠입니다.")); // 답을 제출한 모둠 찾기

        // 게임이 아직 시작되지 않은 경우 제출 불가
        if (!team.getRoom().isStarted()) {
            throw new IllegalArgumentException("아직 게임이 시작되지 않았습니다.");
        }

        // 이미 모든 문제를 모두 맞힌 경우 제출 불가
        if (team.isFinished()) {
            throw new IllegalArgumentException("이미 모든 문제를 완료한 모둠입니다.");
        }

        Question question = questionRepository.findById(questionId).orElseThrow(() -> new IllegalArgumentException("존재하지 않는 문제입니다.")); // 답을 제출할 문제 찾기
        Answer answer = answerRepository.findByTeamIdAndQuestionId(teamId, questionId).orElse(null); // 해당 모둠이 해당 문제에 이미 답을 제출했는지 확인
        boolean wasCorrect = answer != null && answer.isCorrect();

        // 처음 제출하는 경우
        if(answer == null) {

            // 새로운 답 생성
            answer = new Answer(
                    team,
                    question,
                    submittedAnswer
            );
        } else {
            // 이미 정답을 맞힌 문제는 다시 제출할 수 없음
            if (answer.isCorrect()) {
                throw new IllegalArgumentException(
                        "이미 정답을 맞힌 문제입니다."
                );
            }
            // 제출 횟수 제한 확인
            if (answer.getSubmitCount() >= question.getMaxSubmitCount()) {
                throw new IllegalArgumentException(
                        "답안 제출 횟수를 초과했습니다."
                );
            }
            answer.modifyAnswer(submittedAnswer); // 기존 답 수정
        }
        boolean correct = question.getAnswer().equalsIgnoreCase(submittedAnswer.trim()); // 입력한 답과 실제 정답 비교
        answer.checkCorrect(correct); // 정답 여부 저장

        // 이전에는 오답이었는데 이번에 처음 정답이 된 경우
        if(!wasCorrect && correct) {

            team.increaseCorrectCount(); // 모둠의 정답 개수 증가

            int totalQuestionCount = questionRepository.findAllByOrderByQuestionNumber().size();

            // 모든 문제를 모두 맞혔고 아직 완료 처리되지 않은 경우
            if(team.getCurrentCount() >= totalQuestionCount && !team.isFinished()) {
                team.finish(); // 10문제 완료 처리 및 완료 시간 기록
            }
        }

        answerRepository.save(answer); // answer 저장

        return new AnswerResponse(
                answer.getId(),
                answer.getSubmittedAnswer(),
                answer.isCorrect(),
                answer.getSubmitCount(),
                answer.getModifyCount()
        );
    }
}
