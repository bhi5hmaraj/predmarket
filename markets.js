async function getQuestions() {
    let url = 'https://5fff1998a4a0dd001701b79f.mockapi.io/questions';
    try {
        let res = await fetch(url);
        return await res.json();
    } catch (error) {
        console.log(error);
    }
}

async function dateToDay(date) {
    let days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
    let dateSlice = new Date(date.slice(0,10));  
    let day = days[dateSlice.getDay()];
    return day
}

async function renderQuestions() {
    let questions = await getQuestions();
    let html = '';
    questions.forEach(question => {
        // console.log(dateToDay(question.creation_time))
        let htmlSegment = `<div class="well">
        <h3 id="question">${question.question_text}</h3> 
        <h6 id="explanation">${question.explanation_text}</h6>
        <p id="resolution" class="glyphicon glyphicon-time">Question created on:${question.resolution_rule}</p>
        <p id="time-created">Question created on: ${question.creation_time}</p>
        <p id="deadline-bet">Deadline for placing bets: ${question.deadline_for_betting}</p>
        <p id="deadline-resolve">Deadline for resolving question: ${question.deadline_for_resolving}</p>
        </div>`;

        html += htmlSegment;
    });

    let container = document.getElementById('marketList');
    container.innerHTML = html;
}

renderQuestions();
