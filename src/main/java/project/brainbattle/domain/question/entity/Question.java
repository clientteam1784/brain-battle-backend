package project.brainbattle.domain.question.entity;


import jakarta.persistence.*;
import lombok.Getter;
import lombok.NoArgsConstructor;

@Entity
@Getter
@NoArgsConstructor
public class Question {

    // 문제 고유 Id
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false)
    private int questionNumber; // 문제 번호

    @Column(nullable = false)
    private String answer; // 정답

    @Column(nullable = false)
    private int maxSubmitCount; // 문제 답안 제출 최대 횟수

    // 문제 생성에 사용하는 생성자
    public Question(int questionNumber, String answer, int maxSubmitCount) {
        this.questionNumber = questionNumber;
        this.answer = answer;
        this.maxSubmitCount = maxSubmitCount;
    }
    // 문제 정보 수정
    public void update(int questionNumber, String answer, int maxSubmitCount) {
        this.questionNumber = questionNumber;
        this.answer = answer;
        this.maxSubmitCount = maxSubmitCount;
    }
}
