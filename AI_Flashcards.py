from tkinter import *
from tkinter import ttk
import PyPDF2
import pandas
import random
import openai
from playsound import playsound
import os


size = ""
input_file = ""
is_front = True


#GUI TO GET FILE AND SIZE

frame = Tk() 
frame.title("TextBox Input")
frame.geometry('600x400')

def end():
    global filename
    global flashcard_number
    filename = entry.get()
    flashcard_number = entry2.get()
    frame.destroy()

#Initialize a Label to display the User Input
label=Label(frame, text="Enter The Name of the File", font=("Courier 22"))
label.pack()

#Create an Entry widget to accept User Input
entry= Entry(frame, width= 40)
entry.focus_set()
entry.pack()

#Initialize a Label to display the User Input
label2=Label(frame, text="Enter How Many Flashcards", font=("Courier 22"))
label2.pack()

#Create an Entry widget to accept User Input
entry2= Entry(frame, width= 40)
entry2.pack()

ttk.Button(frame, text= "Generate Flashcards",width= 20, command=end).pack(pady=20)

frame.mainloop()

pdf_file_obj = open(filename, 'rb')
pdf_reader = PyPDF2.PdfReader(pdf_file_obj)
count = len(pdf_reader.pages)
input = ""
for i in range(count):
    page = pdf_reader.pages[i]
    input += page.extract_text()


pdf_file_obj.close()
size = flashcard_number




#START OPENAI

#load key
openai.api_key = 'enter-api-key-here'


def get_completion(prompt, model="gpt-3.5-turbo"):
    messages = [{"role": "user", "content": prompt}]
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=0, # this is the degree of randomness of the model's output
    )
    return response.choices[0].message["content"]

format = f""" 
terms on the front definition in the back. 
"""


# Define a test prompt
test_prompt = f"""
Create '''{size}''' flashcards on the following text: '''{input}'''
with the following format: '''{format}'''
Use labels "Front: " and "Back: "
Add a silly emoji that relates to the topic to each flashcard.
Add a joke at the end that relates to the topic. Label this as "Joke: ".
"""

front = []
back = []
joke = ""
# Call the get_completion function with the test prompt
response = get_completion(test_prompt)

#parser 
response_arr = response.strip().split('\n')
for line in response_arr:
    if "Front:" in line:
        front.append(line[7:])
    elif "Back:" in line:
        back.append(line[6:])
    elif "Joke:" in line:
        joke = line[6:]

# Display the completion
print(response)
df = pandas.DataFrame({'front' : front, 'back': back})
df.to_csv("./file.csv", sep='|', index=False)




#FLASHCARD CODE
BACKGROUND_COLOR = "#B1DDC6"
FILE_PATH = "file.csv"
current_card = {}
words_to_learn = {}
words_to_learn_copy = {}

sound_file = os.path.dirname(__file__) + '\mice.mp3'
sound_wrong_file = os.path.dirname(__file__) + '\womp-womp.mp3'

last_card = False

def import_words():
    global words_to_learn
    global words_to_learn_copy
    data_frame = pandas.read_csv(FILE_PATH, sep='|')
    words_to_learn = data_frame.to_dict(orient="records")
    words_to_learn_copy = words_to_learn.copy()

#If player gets it correct remove from deck
def word_known():
    global words_to_learn, current_card
    words_to_learn.remove(current_card)
    data = pandas.DataFrame(words_to_learn)
    data.to_csv("file.csv", sep='|', index=False)
    flashcard.tag_raise(gif_image)
    playsound(sound_file)

#If player gets it incorrect keep in deck
def word_unknown():
    flashcard.tag_raise(gif_wrong_image)
    playsound(sound_wrong_file)

def play_again():
    global words_to_learn, words_to_learn_copy
    words_to_learn = words_to_learn_copy.copy()
    print(words_to_learn)
    next_card()
    next_button.config(text="NEXT", command=next_card)

def next_card():
    global words_to_learn
    global current_card
    global is_front
    global last_card

    try:
        current_card = random.choice(words_to_learn)
    except IndexError:
        last_card = True
        current_card = {"front": "Flip this card for a joke!", "back": joke}
        flashcard.itemconfig(card_background, image=front_image)
        flashcard.itemconfig(language, text="Well done!", fill="black")
        flashcard.itemconfig(word, text="Flip this card for a prize!", fill="black", font=("Ariel", 40, "bold"))
        flashcard.tag_lower(gif_image)
        flashcard.tag_lower(gif_wrong_image)
        next_button.config(text = "PLAY AGAIN", command=play_again)
    else:
        flashcard.itemconfig(card_background, image=front_image)
        flashcard.itemconfig(word, text=current_card["front"], fill="black")
        flashcard.itemconfig(language, text="term", fill="black")
        flashcard.tag_lower(gif_image)
        flashcard.tag_lower(gif_wrong_image)
    is_front = True

def flip_card():
    global is_front
    if is_front:
        flashcard.itemconfig(card_background, image=back_image)
        flashcard.itemconfig(word, text=current_card["back"], fill="white")
        if (not last_card):
            flashcard.itemconfig(language, text="definition", fill="white")
        else:
            flashcard.itemconfig(language, text="", fill="white")
        flashcard.tag_lower(gif_image)
        flashcard.tag_lower(gif_wrong_image)
        is_front = False
    else:
        flashcard.itemconfig(card_background, image=front_image)
        flashcard.itemconfig(word, text=current_card["front"], fill="black")
        flashcard.itemconfig(language, text="term", fill="black")
        flashcard.tag_lower(gif_image)
        flashcard.tag_lower(gif_wrong_image)
        is_front = True

window = Tk()
window.minsize(height=526, width=800)
window.title("Flashcards")
window.config(padx=50, pady=50, bg=BACKGROUND_COLOR)

front_image = PhotoImage(file="assets/card_front.png")
back_image = PhotoImage(file="assets/card_back.png")

right_image = PhotoImage(file="assets/right.png")
wrong_image = PhotoImage(file="assets/wrong.png")
flip_image = PhotoImage(file="assets/flip.png")
next_image = PhotoImage(file="assets/next.png")
party_people_image = PhotoImage(file="assets/party_people.png")
crying_dog_image = PhotoImage(file="assets/crying_dog.gif")


flashcard = Canvas(width=800, height=526, bg=BACKGROUND_COLOR, highlightthickness=0)
card_background = flashcard.create_image(400, 263, image=front_image)
gif_image = flashcard.create_image(400, 263, image=party_people_image)
gif_wrong_image = flashcard.create_image(400, 263, image=crying_dog_image)
language = flashcard.create_text(400, 100, text="", fill="black", font=("Ariel", 30, "italic"), width=600)
word = flashcard.create_text(400, 263, text="", fill="black", font=("Ariel", 30, "bold"), width=600)
flashcard.grid(row=0, column=0, columnspan=3)

unknown_button = Button(image=wrong_image, highlightthickness=0, command=word_unknown)
unknown_button.grid(row=1, column=0)

known_button = Button(image=right_image, highlightthickness=0, command=word_known)
known_button.grid(row=1, column=2)

flip_button = Button(image=flip_image, highlightthickness=0, command=flip_card)
flip_button.grid(row=1, column=1)

next_button = Button(window, text = "NEXT", command=next_card)
next_button.grid(row=1, column=3)

import_words()
next_card()

window.mainloop()