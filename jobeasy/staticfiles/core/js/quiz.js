document.addEventListener('DOMContentLoaded', () => {
    const quizContainer = document.getElementById('quiz');
    const questionElement = document.getElementById('question');
    const optionsElements = document.querySelectorAll('.options');
    const submitButton = document.getElementById('submit');
    let currentQuestionIndex = 0;
    let selections = [];

    function fetchQuestions() {
        fetch('/core/quiz-questions/')
            .then(response => response.json())
            .then(questions => {
                displayQuestion(questions[currentQuestionIndex]);

                submitButton.addEventListener('click', () => {
                    const selectedOption = document.querySelector('input[name="answer"]:checked');
                    if (selectedOption) {
                        const selectedTrait = selectedOption.getAttribute('data-trait');
                        selections.push(selectedTrait);
                        selectedOption.checked = false;

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
            })
            .catch(error => console.error('Failed to load quiz questions:', error));
    }

    function displayQuestion(question) {
        questionElement.textContent = "Choose which option describes you more:";
        optionsElements[0].querySelector('label').textContent = question.optionA;
        optionsElements[0].querySelector('input').setAttribute('data-trait', question.traitA);
        optionsElements[1].querySelector('label').textContent = question.optionB;
        optionsElements[1].querySelector('input').setAttribute('data-trait', question.traitB);
    }

    function displayResult(selections) {
        questionElement.style.display = 'none';
        optionsElements.forEach(option => option.style.display = 'none');
        submitButton.style.display = 'none';

        const personalityType = calculatePersonalityType(selections);
        displayAdditionalQuestions(personalityType);
    }

    function displayAdditionalQuestions(initialMbtiType) {
        quizContainer.innerHTML += `
            <div id="additional-questions">
                <div>
                    <label for="question1">How do you navigate challenges and setbacks in your journey?</label>
                    <textarea id="question1"></textarea>
                </div>
                <div>
                    <label for="question2">In what ways do you seek to grow and evolve as an individual?</label>
                    <textarea id="question2"></textarea>
                </div>
                <button id="finalSubmit">Submit Answers</button>
            </div>
        `;

        document.getElementById('finalSubmit').addEventListener('click', () => {
            const answer1 = document.getElementById('question1').value;
            const answer2 = document.getElementById('question2').value;
            const combinedAnswers = `${answer1} ${answer2}`;

            // Hide additional questions
            document.getElementById('additional-questions').style.display = 'none';

            // Show and initialize the loading animation
            showLoadingAnimation(true);
            
            sendTextForFinalPrediction(initialMbtiType, combinedAnswers);
        });
    }

    function sendTextForFinalPrediction(initialMbtiType, textAnswers) {
        fetch('/core/final-mbti-prediction/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                'initial_mbti_type': initialMbtiType,
                'text_answers': textAnswers
            }),
        })
        .then(response => response.json())
        .then(data => {
            document.getElementById('quiz').innerHTML = `<h2>Your refined personality type is: ${data.final_mbti_type}</h2> <button id="restart">Restart</button>`;
            document.getElementById('restart').addEventListener('click', () => {
                location.reload();
            });
        })
        .catch(error => console.error('Failed to get the final MBTI prediction:', error));
    }

    function calculatePersonalityType(selections) {
        // Placeholder for your calculatePersonalityType function
        // Replace this with your actual logic
        const counts = { I: 0, E: 0, S: 0, N: 0, T: 0, F: 0, J: 0, P: 0 };
        selections.forEach(trait => counts[trait]++);
        let personalityType = '';
        personalityType += counts['I'] > counts['E'] ? 'I' : 'E';
        personalityType += counts['S'] > counts['N'] ? 'S' : 'N';
        personalityType += counts['T'] > counts['F'] ? 'T' : 'F';
        personalityType += counts['J'] > counts['P'] ? 'J' : 'P';
        return personalityType;
    }

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    function showLoadingAnimation(show) {
        const loadingAnimationElement = document.getElementById('loadingAnimation');
        if (loadingAnimationElement) { // Check if the element exists
            if (show) {
                loadingAnimationElement.style.display = 'block';
                const animationPath = loadingAnimationElement.getAttribute('data-animation-url');
                lottie.loadAnimation({
                    container: loadingAnimationElement,
                    renderer: 'svg',
                    loop: true,
                    autoplay: true,
                    path: animationPath,
                    rendererSettings: {
                        preserveAspectRatio: 'xMidYMid meet'
                    }
                });
            } else {
                loadingAnimationElement.style.display = 'none';
                lottie.stop();
            }
        } else {
            console.warn('loadingAnimationElement not found in the DOM.');
        }
    }

    // Start the quiz by fetching questions
    fetchQuestions();
});
