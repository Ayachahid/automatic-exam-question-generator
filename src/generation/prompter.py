class Prompter:
    def build_prompt(self, chunk: str, question_type:str,
                     difficulty: str, num_questions: int) -> str:
        return f"""You are an expert exam question generator.

Given the following course material, generate {num_questions} {question_type} questions at {difficulty} difficulty.

Rules:
- Base questions ONLY on the provided text
- Return a valid JSON array
- Each object must have: question, options (if MCQ)

Text:
{chunk}

Return JSON only, no explanation:"""