document.addEventListener("DOMContentLoaded", () => {
    const examNameForm = document.getElementById('examNameForm');
    const answerKeyForm = document.getElementById('answerKeyForm');
    const examTitle = document.getElementById('examTitle');
    const hiddenExamName = document.getElementById('hiddenExamName');
    const addQuestionButton = document.getElementById('addQuestionButton');
    const questionsContainer = document.getElementById('questionsContainer');

    examNameForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const examName = document.getElementById('examName').value;
        examTitle.textContent = `Answer Key for: ${examName}`;
        hiddenExamName.value = examName;
        examNameForm.style.display = 'none';
        answerKeyForm.style.display = 'block';
    });

    addQuestionButton.addEventListener('click', () => {
        const questionNumber = questionsContainer.querySelectorAll('.form-group').length + 1;
        const newQuestion = document.createElement('div');
        newQuestion.classList.add('form-group');

        newQuestion.innerHTML = `
            <label for="question${questionNumber}">Question ${questionNumber}:</label>
            <textarea id="question${questionNumber}" name="questions[]" placeholder="Enter Question ${questionNumber}"></textarea>

            <label for="question${questionNumber}_asked">What is asked?</label>
            <input type="text" id="question${questionNumber}_asked" name="answers[question${questionNumber}][asked]" placeholder="What is asked?">

            <label for="question${questionNumber}_given">What are given facts?</label>
            <input type="text" id="question${questionNumber}_given" name="answers[question${questionNumber}][given]" placeholder="What are given facts?">

            <label for="question${questionNumber}_operation">What operation will be used?</label>
            <input type="text" id="question${questionNumber}_operation" name="answers[question${questionNumber}][operation]" placeholder="What operation will be used?">

            <label for="question${questionNumber}_sentence">What is the number sentence?</label>
            <input type="text" id="question${questionNumber}_sentence" name="answers[question${questionNumber}][sentence]" placeholder="What is the number sentence?">

            <label for="question${questionNumber}_solution">Solution</label>
            <textarea id="question${questionNumber}_solution" name="answers[question${questionNumber}][solution]" placeholder="Solution"></textarea>

            <label for="question${questionNumber}_final_answer">What is the final answer?</label>
            <input type="text" id="question${questionNumber}_final_answer" name="answers[question${questionNumber}][final_answer]" placeholder="What is the final answer?">
        `;

        questionsContainer.appendChild(newQuestion);
    });
});