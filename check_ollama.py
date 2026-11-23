from app.rag import generate_answer

context = "Employees are entitled to 12 casual leave days per year."
question = "How many casual leave days are employees entitled to?"

answer = generate_answer(question,context)

print("Quesion:", question)
print("Answer:", answer)