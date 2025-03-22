function loadSubjectForm() {
    fetch('/quiz-master/add-subject')  // Fetch content from Flask route
    .then(response => response.text())  // Convert response to text (HTML)
    .then(html => {
        document.getElementById('modalContentSubject').innerHTML = html;  // Insert into modal
    })
    .catch(error => console.error('Error loading form:', error));
}


function loadChapterForm() {
    fetch('/quiz-master/add-chapter')  
    .then(response => response.text())  
    .then(html => {
        document.getElementById('modalContentChapter').innerHTML = html;  
    })
    .catch(error => console.error('Error loading form:', error));
}

function loadQuizForm() {
    fetch('/quiz-master/add-quiz')  
    .then(response => response.text())  
    .then(html => {
        document.getElementById('modalContentQuiz').innerHTML = html;  
    })
    .catch(error => console.error('Error loading form:', error));
}

function loadQuestionForm() {
    fetch('/quiz-master/add-question')  
    .then(response => response.text())  
    .then(html => {
        document.getElementById('modalContentQuestion').innerHTML = html;  
    })
    .catch(error => console.error('Error loading form:', error));
}


function deleteSubject(subjectId) {
    if (confirm('Are you sure you want to delete this subject?')) {
        fetch(`/quiz-master/subject/${subjectId}`, {
            method: 'DELETE'
        })
        .then(response => {
            if (!response.ok) {
                if (response.status === 400) {
                    return response.json().then(data => {
                        alert(`${data.message}`);
                });
                }
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            console.log('Subject deleted:', data);
            window.location.reload();
        })
        .catch(error => console.error('Error deleting subject:', error));
    }
}

function deleteChapter(chapterId) {
    if (confirm('Are you sure you want to delete this chapter?')) {
        fetch(`/quiz-master/chapter/${chapterId}`, {
            method: 'DELETE'
        })
        .then(response => {
            if (!response.ok) {
                if (response.status === 400) {
                    return response.json().then(data => {
                        alert(`${data.message}`);
                });
                }
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            console.log('Chapter deleted:', data);
            window.location.reload();
        })
        .catch(error => console.error('Error deleting chapter:', error));
    }
}

function deleteQuiz(quizId) {
    if (confirm('Are you sure you want to delete this quiz?')) {
        fetch(`/quiz-master/quiz/${quizId}`, {
            method: 'DELETE'
        })
        .then(response => {
            if (!response.ok) {
                if (response.status === 400) {
                    return response.json().then(data => {
                        alert(`${data.message}`);
                });
                }
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            console.log('Quiz deleted:', data);
            window.location.reload();
        })
        .catch(error => console.error('Error deleting quiz:', error));
    }
}

function deleteQuestion(questionId) {
    if (confirm('Are you sure you want to delete this question?')) {
        fetch(`/quiz-master/question/${questionId}`, {
            method: 'DELETE'
        })
        .then(response => {
            if (!response.ok) {
                if (response.status === 400) {
                    return response.json().then(data => {
                        alert(`${data.message}`);
                });
                }
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            console.log('Question deleted:', data);
            window.location.reload();
        })
        .catch(error => console.error('Error deleting question:', error));
    }
}

async function editQuestion(questionId) {
    await fetch(`/quiz-master/edit-question/${questionId}`) 
    .then(response => response.text())  
    .then(html => {
        document.getElementById('modalContentEditQuestion').innerHTML = html;  
    })
    .catch(error => console.error('Error loading form:', error));
}
async function editQuiz(quizId) {
    await fetch(`/quiz-master/edit-quiz/${quizId}`)  
    .then(response => response.text())  
    .then(html => {
        document.getElementById('modalContentEditQuiz').innerHTML = html;  
    })
    .catch(error => console.error('Error loading form:', error));
}

function deleteUser(userId) {
    if (confirm('Are you sure you want to delete this user?')) {
        fetch(`/quiz-master/user/${userId}`, {
            method: 'DELETE'
        })
        .then(response => {
            if (!response.ok) {
                if (response.status === 400) {
                    return response.json().then(data => {
                        alert(`${data.message}`);
                });
                }
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            console.log('User deleted:', data);
            window.location.reload();
        })
        .catch(error => console.error('Error deleting quiz:', error));
    }
}