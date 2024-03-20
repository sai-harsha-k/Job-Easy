document.addEventListener('DOMContentLoaded', () => {
    const questionElement = document.getElementById('question');
    const optionAElement = document.getElementById('a_text');
    const optionBElement = document.getElementById('b_text');
    const submitButton = document.getElementById('submit');
    let currentQuestionIndex = 0;
    let selections = [];

    // Fetch questions from the server
    fetch('/core/quiz-questions/')
        .then(response => response.json())
        .then(questions => {
            displayQuestion(questions[currentQuestionIndex]);

            submitButton.addEventListener('click', () => {
                const selectedOption = document.querySelector('input[name="answer"]:checked');
                if (selectedOption) {
                    const selectedTrait = selectedOption.getAttribute('data-trait');
                    selections.push(selectedTrait);
                    selectedOption.checked = false; // Deselect current selection

                    currentQuestionIndex++;
                    if (currentQuestionIndex < questions.length) {
                        displayQuestion(questions[currentQuestionIndex]);
                    } else {
                        displayResult(selections);
                    }
                } else {
                    alert('Please select an option before proceeding.');
                }
            });

            function displayQuestion(question) {
                questionElement.textContent = "Choose which option describes you more:";
                optionAElement.textContent = question.optionA;
                optionBElement.textContent = question.optionB;
                document.getElementById('a').setAttribute('data-trait', question.traitA);
                document.getElementById('b').setAttribute('data-trait', question.traitB);
            }

            function displayResult(selections) {
                const personalityType = calculatePersonalityType(selections);
                document.getElementById('quiz').innerHTML = `<h2>Your personality type is: ${personalityType}</h2> <button onclick="location.reload()">Restart</button>`;
            }

            function calculatePersonalityType(selections) {
                const counts = { I: 0, E: 0, S: 0, N: 0, T: 0, F: 0, J: 0, P: 0 };
            
                // Increment the count for each selected trait
                selections.forEach(trait => {
                    counts[trait]++;
                });
                //Choosing the trait
                let personalityType = '';
                personalityType += counts['I'] > counts['E'] ? 'I' : 'E';
                personalityType += counts['S'] > counts['N'] ? 'S' : 'N';
                personalityType += counts['T'] > counts['F'] ? 'T' : 'F';
                personalityType += counts['J'] > counts['P'] ? 'J' : 'P';
            
                return personalityType;
            }
        })
        .catch(error => console.error('Failed to load quiz questions:', error));
});
