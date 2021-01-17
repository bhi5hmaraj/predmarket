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
        // let htmlSegment = `<div class="blog-post">
        // <h3 class="title" id="question">${question.question_text}</h3> 
        // <h6 class="text" id="explanation">${question.explanation_text}</h6>
        // <p class="user-info" id="resolution" class="glyphicon glyphicon-time">Resolution rule:${question.resolution_rule}</p>
        // <p class="user-info" id="time-created">Question created on: ${question.creation_time}</p>
        // <p class="user-info" id="deadline-bet">Deadline for placing bets: ${question.deadline_for_betting}</p>
        // <p class="user-info" id="deadline-resolve">Deadline for resolving question: ${question.deadline_for_resolving}</p>
        // </div>`;

        let htmlSegment = `<div class="blog-post">
        <h3 class="title" id="question">Who will win big boss season 4</h3> 

        <h6 class="text" id="explanation">Ipsum faucibus vitae aliquet nec ullamcorper sit. 
        Ac felis donec et odio pellentesque diam volutpat. Urna nunc id cursus metus aliquam. 
        Amet dictum sit amet justo. Sem viverra aliquet eget sit amet tellus cras adipiscing. 
        Urna nec tincidunt praesent semper. Integer enim neque volutpat ac. 
        Aliquet enim tortor at auctor urna.</h6>

        <p class="user-info" id="resolution" class="glyphicon glyphicon-time">Resolution rule:
        Ipsum faucibus vitae aliquet nec ullamcorper sit. 
        Ac felis donec et odio pellentesque diam volutpat. 
        Urna nunc id cursus metus aliquam. 
        Amet dictum sit amet justo.</p>

        <p class="user-info" id="time-created">Question created on: ${question.creation_time}</p>
        <p class="user-info" id="deadline-bet">Deadline for placing bets: ${question.deadline_for_betting}</p>
        <p class="user-info" id="deadline-resolve">Deadline for resolving question: ${question.deadline_for_resolving}</p>
        </div>`;

        html += htmlSegment;
    });

    let container = document.getElementById('marketList');
    container.innerHTML = html;
}

renderQuestions();
