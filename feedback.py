import sqlite3
import pandas as pd
from textblob import TextBlob
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.backends.backend_pdf import PdfPages

# Path to the database
db_path = "/Users/esmaf/OneDrive/Desktop/feedback.db"
conn = sqlite3.connect(db_path)

# Create a cursor object to interact with the database
cursor = conn.cursor()

# List all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print("Tables:", tables)

# Dictionary to store customer feedback by table
customer_feedback_dict = {}

# Fetch rows and columns from each table and store them in a dictionary
for table in tables:
    table_name = table[0]  # Extract the table name
    print(f"\nFetching rows from {table_name}:")

    # Fetch all rows and column names from the table
    cursor.execute(f"SELECT * FROM {table_name};")
    rows = cursor.fetchall()
    columns = [description[0] for description in cursor.description]  # Get column names

    # Store the data as a DataFrame
    customer_feedback_dict[table_name] = pd.DataFrame(rows, columns=columns)

# Close the connection
conn.close()

# Save each table's DataFrame to an Excel file
excel_path = "/Users/esmaf/OneDrive/Desktop/feedback.xlsx"
with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
    for table_name, df in customer_feedback_dict.items():
        df.to_excel(writer, sheet_name=table_name, index=False)

print(f"Customer feedback has been saved to {excel_path}")

# Load the Excel file
df = pd.read_excel(excel_path, sheet_name=0)  # Load the first sheet for analysis

# Ensure the 'comment' column exists
if 'comment' not in df.columns:
    raise ValueError("The 'comment' column is missing in the Excel file.")

# Function for sentiment analysis using TextBlob
def analyze_sentiment(text):
    analysis = TextBlob(text)
    return analysis.sentiment.polarity

# Apply the function to the 'comment' column
df['Sentiment Score'] = df['comment'].apply(analyze_sentiment)

# Categorize sentiment based on the score
def categorize_sentiment(score):
    if score > 0.1:
        return 'Positive'
    elif score < -0.1:
        return 'Negative'
    else:
        return 'Neutral'

df['Sentiment Category'] = df['Sentiment Score'].apply(categorize_sentiment)

# Save the results to a new Excel file
output_file = "/Users/esmaf/OneDrive/Desktop/feedbackresults.xlsx"
df.to_excel(output_file, index=False)
print(f"Sentiment analysis results saved to {output_file}")

# Custom color palette
sentiment_colors = {
    'Negative': '#FF0000',  # Red for negative
    'Neutral': '#A52A2A',   # Brown for neutral
    'Positive': '#00FF00'   # Green for positive
}

# Open a PDF file to save plots
pdf_path = "/Users/esmaf/OneDrive/Desktop/Visualizations.pdf"
with PdfPages(pdf_path) as pdf:
    # 1. Bar Chart for Sentiment Category Distribution
    plt.figure(figsize=(10, 6))
    sns.countplot(data=df, x='Sentiment Category',
                  palette=[sentiment_colors[cat] for cat in ['Negative', 'Neutral', 'Positive']])
    plt.title('Sentiment Distribution', fontsize=14)
    plt.xlabel('Sentiment Category', fontsize=12)
    plt.ylabel('Count', fontsize=12)
    pdf.savefig()
    plt.close()

    # 2. Enhanced Boxplot for Sentiment Scores
    plt.figure(figsize=(10, 6))
    sns.boxplot(data=df, x='Sentiment Category', y='Sentiment Score',
                palette=[sentiment_colors[cat] for cat in ['Negative', 'Neutral', 'Positive']])
    plt.title('Sentiment Score Distribution by Category', fontsize=14)
    plt.xlabel('Sentiment Category', fontsize=12)
    plt.ylabel('Sentiment Score', fontsize=12)
    plt.grid(True, axis='y', linestyle='--', alpha=0.7)
    pdf.savefig()
    plt.close()

    # 3. Pie Chart for Sentiment Distribution
    plt.figure(figsize=(10, 8))
    sentiment_counts = df['Sentiment Category'].value_counts()
    plt.pie(sentiment_counts,
            labels=sentiment_counts.index,
            colors=[sentiment_colors[cat] for cat in sentiment_counts.index],
            autopct='%1.1f%%',
            startangle=90,
            explode=(0.05, 0.05, 0.05))  # Add slight separation between segments
    plt.title('Sentiment Category Distribution', fontsize=14, pad=20)
    plt.axis('equal')
    pdf.savefig()
    plt.close()

print(f"Visualizations have been saved to {pdf_path}")
