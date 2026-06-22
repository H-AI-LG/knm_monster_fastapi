from src.models import CustomModel


class QuizOption(CustomModel):
    index: int
    text: str


class ArtifactQuiz(CustomModel):
    question: str
    options: list[QuizOption]
    answer_index: int


class ArtifactResponse(CustomModel):
    id: str
    name: str
    era: str
    grade: str        # 일반 | 고급 | 전설 | 보스
    persona: str
    greeting: str
    description: str
    image_url: str
    quiz: ArtifactQuiz
