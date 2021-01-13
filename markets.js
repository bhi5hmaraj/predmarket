async function getQuestions() {
    let url = 'https://5ff305db28c3980017b18e2a.mockapi.io/dummy/questions';
    try {
        let res = await fetch(url);
        return await res.json();
    } catch (error) {
        console.log(error);
    }
}

async function renderQuestions() {
    let questions = await getQuestions();
    let html = '';
    questions.forEach(question => {
        let htmlSegment = `<div class="question">
        <p id="question-text">${question.question_text}</p>
        <p id="question-text">${question.explanation_text}</p>
        <p id="question-text">${question.resolution_rule_text}</p>
        <p id="question-text">${question.creation_time}</p>
        <p id="question-text">${question.deadline_for_betting}</p>
        <p id="question-text">${question.deadline_for_resolving}</p>
        </div>`;

        html += htmlSegment;
    });

    let container = document.querySelector('marketList');
    container.innerHTML = html;
}

renderUsers();