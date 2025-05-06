import os
import random
import tkinter as tk
from tkinter import messagebox
from collections import defaultdict

QUESTION_FILE = "OSE_Master_MCQ_QuestionBank.txt"

def load_questions(filename):
    with open(filename, "r") as f:
        raw = f.read().strip().split("\n\n")
    qs, chapter = [], "General"
    for block in raw:
        lines = block.strip().split("\n")
        # detect chapter headings like "--- CH10 ---"
        if lines and lines[0].startswith("---"):
            chapter = lines[0].strip("- ").strip()
            continue
        # now expects at least 8 lines: Q, A, B, C, D, Answer, Page, Source
        if len(lines) < 8:
            continue
        qs.append({
            "chapter": chapter,
            "question": lines[0][3:].strip(),
            "A": lines[1][3:].strip(),
            "B": lines[2][3:].strip(),
            "C": lines[3][3:].strip(),
            "D": lines[4][3:].strip(),
            "answer": lines[5][8:].strip().upper(),
            "page": lines[6][5:].strip(),
            "source": lines[7][8:].strip()
        })
    return qs

class QuizGUI(tk.Tk):
    def __init__(self, questions):
        super().__init__()
        self.title("OSE MCQ Quiz")
        self.questions = random.sample(questions, len(questions))
        self.idx = 0
        self.score = 0
        self.chapter_scores = defaultdict(lambda: {"correct":0, "total":0})

        # question label
        self.lbl_q = tk.Label(self, wraplength=500, font=("Helvetica", 14))
        self.lbl_q.pack(pady=20)

        # radio buttons for choices
        self.selected = tk.StringVar()
        self.opts = {}
        for choice in ("A","B","C","D"):
            rb = tk.Radiobutton(self, text="", variable=self.selected, value=choice, font=("Helvetica",12))
            rb.pack(anchor="w", padx=40, pady=2)
            self.opts[choice] = rb

        # feedback + source label
        self.lbl_feedback = tk.Label(self, text="", font=("Helvetica",12), justify="left")
        self.lbl_feedback.pack(pady=10)

        # submit/next button
        self.btn_next = tk.Button(self, text="Submit", command=self.submit_answer)
        self.btn_next.pack(pady=20)

        self.load_current()

    def load_current(self):
        q = self.questions[self.idx]
        self.lbl_q.config(text=f"Q{self.idx+1}: {q['question']}")
        for choice in ("A","B","C","D"):
            self.opts[choice].config(text=f"{choice}. {q[choice]}")
        self.selected.set(None)
        self.lbl_feedback.config(text="")
        self.btn_next.config(text="Submit")

    def submit_answer(self):
        q = self.questions[self.idx]
        ans = self.selected.get()
        if not ans:
            messagebox.showwarning("No selection","Please select A, B, C or D.")
            return

        # record total
        self.chapter_scores[q["chapter"]]["total"] += 1

        # build feedback text
        if ans == q["answer"]:
            self.score += 1
            self.chapter_scores[q["chapter"]]["correct"] += 1
            fb = "✅ Correct!"
            color = "green"
        else:
            fb = f"❌ Incorrect. Correct: {q['answer']}"
            color = "red"

        # append page and source
        fb += f"\n📄 Page: {q['page']}\n📂 Source: {q['source']}"
        self.lbl_feedback.config(text=fb, fg=color)

        # move to next
        self.idx += 1
        if self.idx < len(self.questions):
            self.btn_next.config(text="Next", command=self.next_question)
        else:
            self.btn_next.config(text="Show Results", command=self.show_results)

    def next_question(self):
        self.load_current()
        self.btn_next.config(command=self.submit_answer)

    def show_results(self):
        summary = [f"Total Score: {self.score}/{len(self.questions)}\n",
                   "Chapter-wise breakdown:"]
        for chap, sc in self.chapter_scores.items():
            summary.append(f"  {chap}: {sc['correct']}/{sc['total']}")
        messagebox.showinfo("Quiz Results", "\n".join(summary))
        self.destroy()

if __name__ == "__main__":
    if not os.path.exists(QUESTION_FILE):
        tk.messagebox.showerror("File not found", f"Could not find '{QUESTION_FILE}'.")
    else:
        qs = load_questions(QUESTION_FILE)
        app = QuizGUI(qs)
        app.mainloop()
