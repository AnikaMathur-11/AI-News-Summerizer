# 📰 AI-News-Summarizer
An **AI-powered web application** that summarizes top news from major Indian newspapers in real-time.

Built using **Flask**, **Hugging Face Transformers**, and **BeautifulSoup**.

---

## 🚀 Features

### 🔍 Smart News Filtering
* **Select Newspaper:**
    * The Hindu
    * Times of India
    * Hindustan Times
* **Select Category:**
    * India
    * World
    * Sports
    * Tech

### 🤖 AI Summarization
* Uses the **`facebook/bart-large-cnn`** model (an open-source Hugging Face model).
* Generates **compact, readable summaries** for each article, providing quick insights.

---

## 🔧 Installation

**(Requires Python 3.8+)**

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/YOUR_USERNAME/ai-news-summarizer.git](https://github.com/YOUR_USERNAME/ai-news-summarizer.git)
    cd ai-news-summarizer
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the application:**
    ```bash
    python app.py
    ```

Now open your web browser and navigate to:

👉 **http://127.0.0.1:5000/**

---

## 🧠 Tech Stack

| Component | Choice |
| :--- | :--- |
| **Backend** | Flask |
| **Summarizer** | Hugging Face ($\rightarrow$ `facebook/bart-large-cnn$) |
| **Parsing** | BeautifulSoup4 |
| **Frontend/UI** | Custom HTML + CSS |
| **Deployment** | Works locally & on Hugging Face Spaces |

---

## 🌐 How It Works (Flow)

1.  **User Selects** $\rightarrow$ Newspaper and Category on the UI.
2.  **Backend Fetches** $\rightarrow$ Corresponding RSS feed.
3.  **Parser Extracts** $\rightarrow$ Article content (title + description/text).
4.  **Summarizer Generates** $\rightarrow$ The final compact summary for each article.
5.  **UI Displays** $\rightarrow$ Top 5 clickable articles with their new summaries.

---

## 📁 Project Structure

```
AI-News-Summarizer/
├── app.py                      → Main Flask backend (AI, RSS, and routing logic)
├── requirements.txt            → Python dependencies for the project
│
├── templates/                  → Frontend HTML files (used by Flask)
│   ├── base.html
│   └── index.html
│
└── static/                     → Static assets (CSS, images, JS)
    └── custom.css
```
