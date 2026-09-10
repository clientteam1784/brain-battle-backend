package project.brainbattle.domain.student.entity;


import jakarta.persistence.*;
import lombok.Getter;
import lombok.NoArgsConstructor;
import project.brainbattle.domain.team.entity.Team;

@Entity
@Getter
@NoArgsConstructor
public class Student {

    // 학생 고유 Id
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    // 학번
    @Column(nullable = false)
    private String studentNumber;

    // 학생이 속한 모둠
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "team_id", nullable = false)
    private Team team;

    // 학생 등록 시 사용할 생성자
    public Student(String studentNumber, Team team) {
        this.studentNumber = studentNumber;
        this.team = team;
    }
}
