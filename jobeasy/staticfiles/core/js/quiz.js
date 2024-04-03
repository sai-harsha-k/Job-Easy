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
            <p style="color: red;">Please note both the answers should be more than or equal to 100 words</p>
                <div>
                    <label for="question1">How do you navigate challenges and setbacks in your journey?</label>
                    <br>
                    <textarea id="question1" rows="6" cols="50"></textarea>
                    <div id="wordCount1">Word Count: 0</div>
                </div>
                <div>
                    <label for="question2">In what ways do you seek to grow and evolve as an individual?</label>
                    <br>
                    <textarea id="question2" rows="6" cols="50"></textarea>
                    <div id="wordCount2">Word Count: 0</div>
                </div>
                <button id="finalSubmit" disabled>Submit Answers</button>
            </div>
        `;

        const finalSubmitButton = document.getElementById('finalSubmit');

        finalSubmitButton.addEventListener('click', () => {
            const answer1 = document.getElementById('question1').value;
            const answer2 = document.getElementById('question2').value;
            const combinedAnswers = `${answer1} ${answer2}`;

            // Check if both answers meet the minimum word count
            if (validateAnswers(answer1, answer2)) {
                // Hide additional questions
                document.getElementById('additional-questions').style.display = 'none';

                // Show and initialize the loading animation
                showLoadingAnimation(true);
                
                sendTextForFinalPrediction(initialMbtiType, combinedAnswers);
            } else {
                alert('Both answers must have at least 100 words.');
            }
        });

        // Enable/disable submit button based on input length
        const answerInputs = document.querySelectorAll('textarea');
        answerInputs.forEach((input, index) => {
            input.addEventListener('input', () => {
                const wordCount = input.value.trim().split(/\s+/).length;
                const wordCountElement = document.getElementById(`wordCount${index + 1}`);
                wordCountElement.textContent = `Word Count: ${wordCount}`;
                const answer1Length = document.getElementById('question1').value.trim().split(/\s+/).length;
                const answer2Length = document.getElementById('question2').value.trim().split(/\s+/).length;
                if (answer1Length >= 100 && answer2Length >= 100) {
                    finalSubmitButton.disabled = false;
                } else {
                    finalSubmitButton.disabled = true;
                }
            });
        });
    }

    function validateAnswers(answer1, answer2) {
        // Check if both answers have at least 100 words
        const words1 = answer1.trim().split(/\s+/).length;
        const words2 = answer2.trim().split(/\s+/).length;
        return words1 >= 100 && words2 >= 100;
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
            const finalMbtiType = data.final_mbti_type;
            const iComponent = finalMbtiType[0] === 'I' ? 'Introversion' : 'Extraversion';
            const sComponent = finalMbtiType[1] === 'S' ? 'Sensing' : 'Intuition';
            const tComponent = finalMbtiType[2] === 'T' ? 'Thinking' : 'Feeling';
            const jComponent = finalMbtiType[3] === 'J' ? 'Judging' : 'Perceiving';

            let baselineExplanation = '';
            switch (finalMbtiType) {
                case 'ISTJ':
                    baselineExplanation = 'ISTJs are responsible organizers, driven to create and enforce order within systems and institutions.';
                    break;
                case 'ISFJ':
                    baselineExplanation = 'ISFJs are industrious caretakers, loyal to traditions and organizations.';
                    break;
                case 'INFJ':
                    baselineExplanation = 'INFJs are empathetic visionaries, driven by their own personal values to create a better world.';
                    break;
                case 'INTJ':
                    baselineExplanation = 'INTJs are analytical problem-solvers, eager to improve systems and processes with their innovative ideas.';
                    break;
                case 'ISTP':
                    baselineExplanation = 'ISTPs are adaptable thrill-seekers, always looking for practical solutions to complex problems.';
                    break;
                case 'ISFP':
                    baselineExplanation = 'ISFPs are gentle caretakers, tuned into their inner values and committed to living in the present moment.';
                    break;
                case 'INFP':
                    baselineExplanation = 'INFPs are imaginative idealists, guided by their own core values and beliefs.';
                    break;
                case 'INTP':
                    baselineExplanation = 'INTPs are logical innovators, fascinated by theoretical possibilities and complex puzzles.';
                    break;
                case 'ESTP':
                    baselineExplanation = 'ESTPs are energetic problem-solvers, skilled in overcoming challenges and seizing opportunities.';
                    break;
                case 'ESFP':
                    baselineExplanation = 'ESFPs are vivacious entertainers, always ready to explore and experience something new.';
                    break;
                case 'ENFP':
                    baselineExplanation = 'ENFPs are enthusiastic innovators, always seeing new possibilities and following their inspirations.';
                    break;
                case 'ENTP':
                    baselineExplanation = 'ENTPs are imaginative thinkers, skilled in seeing new possibilities and coming up with innovative solutions.';
                    break;
                case 'ESTJ':
                    baselineExplanation = 'ESTJs are hardworking traditionalists, eager to take charge in organizing projects and people.';
                    break;
                case 'ESFJ':
                    baselineExplanation = 'ESFJs are conscientious helpers, sensitive to the needs of others and eager to contribute to their well-being.';
                    break;
                case 'ENFJ':
                    baselineExplanation = 'ENFJs are charismatic leaders, driven by their own personal values to help and inspire others.';
                    break;
                case 'ENTJ':
                    baselineExplanation = 'ENTJs are strategic organizers, motivated to bring order and efficiency to their environment.';
                    break;
                default:
                    baselineExplanation = 'Baseline explanation for the MBTI type could be added here.';
                    break;
            }

            document.getElementById('quiz').innerHTML = `
                <h2>Your personality type based on your answers is: ${finalMbtiType}</h2>
                <p> ${iComponent}</p>
                <p> ${sComponent}</p>
                <p> ${tComponent}</p>
                <p> ${jComponent}</p>
                <p>what it means: ${baselineExplanation}</p>
                <button id="restart">Restart</button>
            `;
            
            document.getElementById('restart').addEventListener('click', () => {
                location.reload();
            });
            saveMbtiTypeToProfile(finalMbtiType);
        })
        .catch(error => console.error('Failed to get the final MBTI prediction:', error));
    }

    function saveMbtiTypeToProfile(mbtiType) {
        fetch('/core/save-mbti-profile/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                'mbti_type': mbtiType
            }),
        })
        .then(response => response.json())
        .then(data => {
            console.log('MBTI type saved to profile:', data.status);
            // Optionally, you can perform further actions here
        })
        .catch(error => console.error('Failed to save MBTI type to profile:', error));
    }

    function calculatePersonalityType(selections) {
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
