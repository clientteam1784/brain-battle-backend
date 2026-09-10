package project.brainbattle.domain.answer.entity;


import jakarta.persistence.*;
import lombok.Getter;
import lombok.NoArgsConstructor;
import project.brainbattle.domain.question.entity.Question;
import project.brainbattle.domain.team.entity.Team;

@Entity
@Getter
@NoArgsConstructor
public class Answer {

    // 답 고유 Id
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    // 답을 제출한 모둠
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "team_id", nullable = false)
    private Team team;

    // 답을 제출한 문제
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "question_id", nullable = false)
    private Question question;

    // 모둠이 현재 제출한 답
    @Column(nullable = false)
    private String submittedAnswer;

    private boolean correct = false; // 현재 제출한 답이 정답인지 여부
    private int submitCount = 0; // 이 문제에서 제출한 횟수
    private int modifyCount = 0; // 기존 답을 수정해서 다시 제출한 횟수

    // 처음 답을 제출할 때 사용하는 생성자
    public Answer(Team team, Question question, String submittedAnswer){
        this.team = team;
        this.question = question;
        this.submittedAnswer = submittedAnswer;
        this.submitCount = 1;
    }

    // 답을 다시 제출할 때 사용하는 메서드
    public void modifyAnswer(String submittedAnswer) {
        this.submittedAnswer = submittedAnswer;
        this.submitCount++;
        this.modifyCount++;
    }

    // 정답 여부 저장하는 메서드
    public void checkCorrect(boolean correct){
        this.correct = correct;
    }
}
