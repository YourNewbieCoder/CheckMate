document.addEventListener("DOMContentLoaded", () => {
    const examNameForm = document.getElementById('examNameForm');
    const answerKeyForm = document.getElementById('answerKeyForm');
    const examTitle = document.getElementById('examTitle');
    const hiddenExamName = document.getElementById('hiddenExamName');
    const addQuestionButton = document.getElementById('addQuestionButton');

    examNameForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const examName = document.getElementById('examName').value;
        examTitle.textContent = `Answer Key for: ${examName}`;
        hiddenExamName.value = examName;
        examNameForm.style.display = 'none';
        answerKeyForm.style.display = 'block';
    });

    addQuestionButton.addEventListener('click', () => {
        const questionNumber = answerKeyForm.querySelectorAll('.form-group').length + 1;
        const newQuestion = document.createElement('div');
        newQuestion.classList.add('form-group');

        const newLabel = document.createElement('label');
        newLabel.setAttribute('for', `question${questionNumber}`);
        newLabel.textContent = `Question ${questionNumber}:`;

        const newInput = document.createElement('input');
        newInput.setAttribute('type', 'text');
        newInput.setAttribute('id', `question${questionNumber}`);
        newInput.setAttribute('name', `answers[]`);
        newInput.setAttribute('placeholder', `Answer for Question ${questionNumber}`);

        newQuestion.appendChild(newLabel);
        newQuestion.appendChild(newInput);

        answerKeyForm.insertBefore(newQuestion, addQuestionButton);
    });
});
