import sqlite3
import pandas as pd
import io
import base64
import matplotlib
matplotlib.use('Agg')  # Use a non-GUI backend
import matplotlib.pyplot as plt
def stats_master_fun():
    # Connect to the SQLite database
    conn = sqlite3.connect("instance\\quiz_master.db") 
    cursor = conn.cursor()

    # Read data into a Pandas DataFrame
    # Query to get the number of subjects, chapters, quizzes, and users
    num_subjects_query = "SELECT COUNT(*) as num_subjects FROM subjects"
    num_chapters_query = "SELECT COUNT(*) as num_chapters FROM chapters"
    num_quizzes_query = "SELECT COUNT(*) as num_quizzes FROM quizzes"
    num_users_query = "SELECT COUNT(*) as num_users FROM users where role='user'"
    num_questions_query = "SELECT COUNT(*) as num_questions FROM questions"

    # Execute the queries and fetch the results
    num_subjects = cursor.execute(num_subjects_query).fetchone()[0]
    num_chapters = cursor.execute(num_chapters_query).fetchone()[0]
    num_quizzes = cursor.execute(num_quizzes_query).fetchone()[0]
    num_users = cursor.execute(num_users_query).fetchone()[0]
    num_questions = cursor.execute(num_questions_query).fetchone()[0]

    stats_master = {
        "num_subjects": num_subjects,
        "num_chapters": num_chapters,
        "num_quizzes": num_quizzes,
        "num_users": num_users,
        "num_questions": num_questions
    }

    query = "SELECT full_name as user_name, quizzes.title as quiz_title, chapters.name as chapter_name, subjects.name as subject_name, total_scored from users, quizzes, chapters, subjects, scores where users.id=scores.user_id and quizzes.id=scores.quiz_id and quizzes.chapter_id = chapters.id and chapters.subject_id=subjects.id"
    df = pd.read_sql_query(query, conn)

    user_subject_wise_no_q = "SELECT full_name as user_name, subjects.name as subject_name, total_scored from users, chapters, scores, quizzes, subjects where users.id=scores.user_id and quizzes.id=scores.quiz_id and quizzes.id=scores.quiz_id and quizzes.chapter_id = chapters.id and chapters.subject_id=subjects.id"
    df2 = pd.read_sql_query(user_subject_wise_no_q, conn)

    # Check if there is any data in the DataFrame
    if not df.empty and not df2.empty:
        # Group by chapter_id and sum the total_scored
        grouped_df = df.groupby('chapter_name')['total_scored'].sum().reset_index()
        # Group by subject_name and get the highest and lowest scores
        subject_scores = df2.groupby('subject_name')['total_scored'].agg(['max', 'min']).reset_index()

        # Plot bar chart for highest and lowest scores by subject
        subject_scores.plot(kind='bar', x='subject_name', y=['max', 'min'], figsize=(10, 6))
        plt.title('Highest and Lowest Scores by Subject')
        plt.xlabel('Subject')
        plt.ylabel('Scores')
        plt.legend(['Highest Score', 'Lowest Score'])
        # Save the plot as an image file in the static/images directory
        plt.savefig('static/images/subject_scores_bar_chart.png')

        # Clear the current figure
        plt.clf()
        # Plot pie chart
        plt.pie(grouped_df['total_scored'], labels=grouped_df['chapter_name'], autopct='%1.1f%%')
        plt.title('Chapter vs Score Plot')
        # Save the plot as an image file in the static/images directory
        plt.savefig('static/images/quiz_scores_pie_chart.png')

        # Query to get the number of users who attempted quizzes for each subject
        user_attempts_query = """
        SELECT subjects.name as subject_name, COUNT(DISTINCT scores.user_id) as num_users
        FROM subjects
        JOIN chapters ON subjects.id = chapters.subject_id
        JOIN quizzes ON chapters.id = quizzes.chapter_id
        JOIN scores ON quizzes.id = scores.quiz_id
        GROUP BY subjects.name
        """
        user_attempts_df = pd.read_sql_query(user_attempts_query, conn)

        # Plot bar chart for number of users who attempted quizzes by subject
        user_attempts_df.plot(kind='bar', x='subject_name', y='num_users', figsize=(10, 6))
        plt.title('Number of Users Who Attempted Quizzes by Subject')
        plt.xlabel('Subject')
        plt.ylabel('Number of Users')
        # Save the plot as an image file in the static/images directory
        plt.savefig('static/images/user_attempts_bar_chart.png')

    conn.close()
    # return the update value
    return stats_master




def user_stats(user_id):
    conn = sqlite3.connect("instance\\quiz_master.db")  
    cursor = conn.cursor()
    # Query to get the highest and lowest scores for each subject for the given user_id
    user_subject_scores_query = """
    SELECT subjects.name as subject_name, MAX(scores.total_scored) as max_score, MIN(scores.total_scored) as min_score
    FROM subjects
    JOIN chapters ON subjects.id = chapters.subject_id
    JOIN quizzes ON chapters.id = quizzes.chapter_id
    JOIN scores ON quizzes.id = scores.quiz_id
    WHERE scores.user_id = ?
    GROUP BY subjects.name
    """
    user_subject_scores_df = pd.read_sql_query(user_subject_scores_query, conn, params=(user_id,))

    # Check if there is any data in the DataFrame
    if not user_subject_scores_df.empty:
        # Plot bar chart for highest and lowest scores by subject for the given user
        user_subject_scores_df.plot(kind='bar', x='subject_name', y=['max_score', 'min_score'], figsize=(10, 6))
        plt.title(f'Highest and Lowest Scores by Subject for User ID {user_id}')
        plt.xlabel('Subject')
        plt.ylabel('Scores')
        plt.legend(['Highest Score', 'Lowest Score'])
        # Save the plot to a BytesIO object
        img = io.BytesIO()
        plt.savefig(img, format='png')
        img.seek(0)  # Move the pointer to the beginning
        plt.close()
        # Encode the image to base64
        graph_url = base64.b64encode(img.getvalue()).decode()
    else:
        graph_url = None

    # Query to get the total number of questions attempted by the user
    total_quiz_attempted_query = """
    SELECT COUNT(*) as total_quiz_attempted
    FROM scores
    WHERE user_id = ?
    """
    total_quiz_attempted = cursor.execute(total_quiz_attempted_query, (user_id,)).fetchone()[0]

    conn.close()

    # Add the total number of questions attempted to the return value
    return {
        "graph_url": f"data:image/png;base64,{graph_url}" if graph_url else None,
        "total_quiz_attempted": total_quiz_attempted
    }

    



