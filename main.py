# PROJECT NAME: Text permutation over constrained computational algorithms.

# COURSE: Introduction to Computer Programming (Python). University of Trento.
# Course Project Evaluation Submission. Summer Session 2022/23.

# DESCRIPTION: The project deals with text manipulation over constrained computational algorithms. We are doing word
# replacement on specific word categories in both user-written texts and external data, mainly literacy material. We
# aim to provide a little interactive game through which one can observe a little text manipulation.

# AUTHORS: Emma Angela Montecchiari, Juliette Napoli-Jacob
# Date: June 16, 2023


# Import necessary libraries and modules
import os
import re
from spacy.cli import download
from spacy.util import get_installed_models
import tkinter as tk
from PIL import ImageTk
from wordcloud import WordCloud
from colorama import Fore, Style
from textblob import TextBlob

# Import NLTK and download required resources
import nltk
from nltk.corpus import brown, stopwords
nltk.download('brown')
nltk.download('stopwords')

# Import and configure SpaCy
import spacy
spacy_model_name = 'en_core_web_sm'
if spacy_model_name not in get_installed_models():
    download(spacy_model_name)

stopwords = set(stopwords.words('english')) # Set up stopwords

# Load SpaCy model
nlp = spacy.load("en_core_web_md", disable=['ner', 'parser', 'textcat'])
nlp.max_length = 30000000


print(Style.BRIGHT, Fore.BLUE + "\nINSTRUCTIONS" + Style.RESET_ALL) # Print instructions to the user in the terminal with the desired style
print("\nHello user! This is a little game for you to try out some text manipulation over constrained computational algorithms.")
print("Altered and constrained composition has been used throughout literary history to achieve greater ideas and improve creativity.")
print("Here we start from this idea to create a simple game of replacement on specific word categories in both user-written texts and external data, mainly literary material.")
print("\nYou can choose between two techniques:")
print("- Noun Switch:")
print("   Switch all the nouns from one text with the nouns from another text.")
print("   Select two texts, and the algorithm will interchange the nouns between them.")
print("   Explore the impact of nouns on the overall composition.")
print()
print("- Dictionary Technique (Oulipo-inspired):")
print("   Alter the text based on a dictionary of nouns.")
print("   Provide a text and choose a specific position for the algorithm to modify the nouns.")
print("   The algorithm will replace the nouns at the chosen position with alternative nouns from the dictionary.")
print("\nEnjoy the game!")


def retrieve_local_text(text_number):  # Function to retrieve texts from local files, depending on the text_number chosen by the user.
    dir_name = 'Gutenberg'  # Directory path of the corpus folder in the project folder.
    sorted_files = sorted(filter(lambda x: os.path.isfile(os.path.join(dir_name, x)), os.listdir(dir_name)))  # Retrieve a list of sorted files from the directory, filtered to include only regular files.
    sorted_files = sorted(sorted_files, key=lambda x: int(x.split(']')[0][1:])) # Sorted again through file names numbers extraction

    if 0 <= text_number < len(sorted_files):  # Check if the text_number chosen by the user is inside the files range
        file_name = sorted_files[text_number]  # Retrieve the file, based on the chosen text_number
        file_path = os.path.join(dir_name, file_name)  # Construct the full file path
        with open(file_path, 'r', encoding='utf-8') as file: # Open the file, read its contents into the text variable.
            text = file.read()
        starting_sentences = { # Define a dictionary that maps text numbers to specific starting sentences, manually determined.
            0: 'Marley was dead, to begin with. There is no doubt whatever about that',
            1: '“The Signora had no business to do it,” said Miss Bartlett, “no',
            2: 'You don’t know about me without you have read a book by the name of The',
            3: 'In a castle of Westphalia, belonging to the Baron of',
            4: 'I had the story, bit by bit, from various people, and, as generally',
            5: 'One morning, when Gregor Samsa woke from troubled dreams, he found',
            6: 'A green and yellow parrot, which hung in a cage outside the door, kept',
            7: 'In my younger and more vulnerable years my father gave me some advice',
            8: 'Mr. Sherlock Holmes, who was usually very late in the mornings,',
            9: 'When Mary Lennox was sent to Misselthwaite Manor to live with her uncle',
            10: 'The Time Traveller (for so it will be convenient to speak of him) was'}
        starting_sentence = starting_sentences[text_number] # Retrieve the starting sentence based on the text_number from the starting_sentence dictionary.
        ending_sentence = r"\**\s*END OF (?:THE |THIS )?PROJECT GUTENBERG"  # Define the regular expression pattern to find the text footer. It mainly matches variation, with or without 'THE' or 'THIS'.
        ending_sentence = re.compile(ending_sentence, re.IGNORECASE)  # Ignore capital/low case sensitivity.

        starting_sentence_match = re.search(starting_sentence, text)  # Search for header and footer patterns in the text.
        ending_sentence_match = re.search(ending_sentence, text)

        if starting_sentence_match and ending_sentence_match: # If they are found:
            starting_sentence_index = starting_sentence_match.start()  # Retrieve their indices.
            ending_sentence_index = ending_sentence_match.start()
            text = text[starting_sentence_index:ending_sentence_index].strip()  # Cut the text removing the header and the footer. Then stripped of leading and trailing whitespace.
            return text
        else:
            print(Style.BRIGHT + "Starting or ending sentence not found." + Style.RESET_ALL) # If starting and ending sentences are not found, return None.
            return None
    else:
        print(Style.BRIGHT + "Invalid text number: out of range." + Style.RESET_ALL) # If text_number is out of range error message, return None.
        return None


def retrieve_local_corpus(dir_name, flagD):  # Function to retrieve the files titles inside a specific directory.
    try:
        file_names = os.listdir(dir_name)  # Get file names list from the specified dir_name
        if not file_names: # If file_names list is empty, raise error message.
            raise FileNotFoundError("No files found in the specified directory.")
        titles = [os.path.splitext(file_name)[0] for file_name in file_names]  # Retrieve titles list removing file extensions
        sorted_titles = sorted(titles, key=lambda x: int(''.join(filter(str.isdigit, x))))  # Sort the titles list based on numeric value extracted from each title. Through titles convertion to strings, filtering out of non-digits, joining of the filtered digits into a single string.
        if flagD:
            print(Style.BRIGHT + "\nCorpus:" + Style.RESET_ALL)
            for title in sorted_titles: # Iterate over the sorted titles and print.
                print(title)
        return sorted_titles  # Return the sorted list of titles
    except FileNotFoundError: # If directory does not exist or has no files, error raise.
        print(Style.BRIGHT + f"Directory '{dir_name}' does not exist or does not contain any files." + Style.RESET_ALL)
        return None


def extract_nouns(text):  # Function to extract a list of the nouns in the text parameter.
    textB = nlp(text)  # Tokenize the text using spacy nlp and assign to textB variable.
    noun_list = [a.text for a in textB if a.pos_ == 'NOUN']  # List comprehension iterating over each token of textB, appending it if it has 'NOUN' pos tag.
    return noun_list


def retrieve_brown_corpus(brown_dic=None): # Function to retrieve a corpus of nouns from the Brown corpus in NLTK.
    # Take an optional parameter which represents the dictionary of Brown Corpus noun.
    if brown_dic is None: # If none provided, retrieve and process the nouns (Caching and performance optimization)
        word_list = brown.words(categories=['humor', 'mystery']) # Retrieve the words from the selected categories of the corpus.
        word_list = ' '.join(f for f in word_list if not f.istitle()) # List comprehension to filter out capitalized words. Join them in a string object, assigned back to word_list.
        brown_dic = sorted(set(extract_nouns(word_list))) # Through the extract_nouns function returns a sorted list of the nouns in the list.
    return brown_dic


def texts_user_choice(flagB):  # Function to promt the user to select the texts for permutation.
    # Take boolean flag paramether, indicating the context of the user's choice.
    if flagB:  # If True, choose a text for modification.
        while True: # While loop for valid input for the user.
            text_number = input(Style.BRIGHT + "\nWhich is the text you want to " + Fore.BLUE + "modify?" + Style.RESET_ALL + "\nType its number: ") # Ask the user for the number of the text to modify.
            try:
                text_number = int(text_number)  # Convert to an integer
                if 0 <= text_number <= 10: # Check if inside the available range
                    return text_number
                else:
                    print(Style.BRIGHT + "Invalid input. Please enter a number inside the Corpus range." + Style.RESET_ALL)
            except ValueError: # If integer convertion fails, error message.
                print(Style.BRIGHT + "Invalid input: not an integer." + Style.RESET_ALL)
    else:  # Same logic for False flag. For the user to choose for the modifying text.
        while True:
            text_number = input(
                Style.BRIGHT + "\nWhich is the text you want to " + Fore.BLUE + "modify it with?" + Style.RESET_ALL + "\nType its number: ")
            try:
                text_number = int(text_number)
                if 0 <= text_number <= 10:
                    return text_number
                else:
                    print(
                        Style.BRIGHT + "Invalid input. Please enter a number inside the Corpus range." + Style.RESET_ALL)
            except ValueError:
                print(Style.BRIGHT + "Invalid input: not an integer." + Style.RESET_ALL)


def switch_nouns(textA, textB):  # Function to switch nouns between two texts.
    # Take two parameters, representing the text to be modified (textA) and the modifying one (textB)
    try:
        doc = nlp(textA)  # Text tokenization to a Spacy doc object with individual tokens.
        nouns_list = extract_nouns(textB)  # Through extract_nouns function, obtain a list of nouns from textB.
        bold_indices = []  # Initialize the empty list to store the indices of the modified words.
        textC = []  # To store the modified text.
        textA_tokens = []  # To store the textA tokens for output purposes.

        i = 0  # Set the counter to iterate though nouns_list to 0.
        for word in doc:  # Iterate through each token in doc using for loop
            if word.pos_ == 'NOUN':  # If the token has noun pos tag:
                bold_indices.append(len(textC))  # Append the lenght of textC to bold_indices (position of the modified words)
                textC.append(nouns_list[i])  # Append the corresponding noun from nouns_list at index i to textC (1:1, 2:2, 3:3).
                i = (i + 1) % len(nouns_list)  # Increment i, ensuring the counter wraps around when reaching the end of nouns_list.
            else: # If not a noun
                textC.append(word.text)  # Append the token's original text to textC
            textA_tokens.append(word.text)  # Append token's original text to textA_tokens (output purposes) (words position correspondant to textC)

        return textC, bold_indices, textA_tokens
    except Exception as e: # Exception print error message indication exeption occurrence and return None for the three.
        print("An error occurred during word switch nouns operation:", str(e))
        return None, None, None


def switch_Oulipo_technique(textA, dic):  # Function to switch nouns according to Oulipo technique.
    # Take two parameters, text to be modified and dictionary to be modified with.
    try:
        while True:  # Loop to input the instruction and responses to the user.
            try: # Loop to prompt the user for the positions number.
                n = int(input(Style.BRIGHT + "\nOn how many " + Fore.BLUE + "positions" + Style.RESET_ALL + Style.BRIGHT + ", in a range between 0 and 15, do you want to apply the permutation?" + Style.RESET_ALL + "\nN + "))
                if 0 <= n <= 15:  # Range of 'N + positions' the user can choose of.
                    break
                else:
                    print(Style.BRIGHT + "Invalid input. Please enter a number within the specified range." + Style.RESET_ALL)
            except ValueError:
                print(Style.BRIGHT + "Invalid input. Please enter a valid integer." + Style.RESET_ALL)

        mapping = {lemma: dic[i + n] for i, lemma in enumerate(dic) if i < len(dic) - n}  # Create a cammping dicionary where each word in dic is mapped to the corresponding word n positions ahead of it. Based on user's response.
        textC = []  # Store the empty list for the modified text.
        bold_indices = []  # To store the position of the modified words.
        words = textA.split()  # Split the textA into individual words and store them into a list.

        for i in range(len(words)):  # Iterate through each word in textA
            if words[i] in mapping and nlp(words[i])[0].pos_ == 'NOUN': # If word is found in the dic AND it's not ahead its lenght AND it's a noun:
                sub = mapping[words[i]]  # Assign the substituted word from the mapping dictionary to the variable sub.
                bold_indices.append(len(textC))  # Append the lenght of textC representing the position of the modified words.
            else: # If the word is not in mapping nore a noun:
                sub = words[i]  # Assign the original word to sub.
            textC.append(sub)  # Append the value of sub to textC.
        return textC, bold_indices, words
    except Exception as e:
        print("An error occurred during Oulipo technique operation:", str(e))
        return None, None, None


def word_cloud(text): # Function to create a word cloud of the input text.
    try:
        if not text or len(text) == 0: # Check if the text is empty
            raise ValueError("Cloud generation: Input text is empty")
        text = ' '.join(text) # Join the words in the text list into a single string.
        wordcloud = WordCloud(stopwords=stopwords).generate(text) # Generate the word cloud object by passing the 'stopword' parameter.
        image = wordcloud.to_image() # Convert the word cloud to an image.
        return image
    except ValueError as ve: # Handle empty text.
        print("ValueError during cloud generation:", str(ve))
    except Exception as e: # Handle exceptions.
        print("An error occurred during word cloud generation:", str(e))
    return None


def sentiment_analysis(text): # Function to implement sentiment analysis.
    try:
        if not text or len(text) == 0: # Check if text is empty
            raise ValueError("Sentiment Analysis: Input text is empty")
        text = ' '.join(text) # List object to string through join method.
        blob = TextBlob(text) # Create 'TextBlob' object by passing the text to it.
        sentiment = blob.sentiment.polarity # Calculate the sentiment polarity using the 'sentiment.polarity' attribute of 'TextBlob'.
        if sentiment > 0: # Based on sentiment polarity value, assign a sentiment label.
            sentiment_label = 'Positive'
        elif sentiment < 0:
            sentiment_label = 'Negative'
        else:
            sentiment_label = 'Neutral'
        return sentiment_label
    except Exception as e:
        print("An error occurred during sentiment analysis:", str(e))
        return None


def formatting(window, textC, textA, textB, modified_words_indices, file_title, flagA): # Function to format the outputs in both a graphical interface and terminal outputting.
    # Takes multiple parameters: window, activated each time; textC, permuted one; textA, original; textB, modifying one; modified_words_indices, of textC and textA; file title if retrieved from literature texts; flagA as an index to ouput three or two texts basing on the chosen technique.
    try:
        window.title(file_title) # Configure title and geometry of the window.
        window.geometry("1250x1000")
        frame_height = 1400
        if flagA: # Configure the width basing on if 2 or 3 texts are outputted.
            frame_width = 415
        else:
            frame_width = 625

        # Create two frames to hold the permuted text and the original one.
        frame2 = tk.Frame(window, width=frame_width, height=frame_height) # Frame2 = Permuted Text. Frame layout and stilying onfiguration.
        frame2.pack_propagate(False)
        frame2.pack(side=tk.LEFT)
        title_label2 = tk.Label(frame2, text="PERMUTED TEXT", font=("Baskerville", 16, "bold")) # Title configuration.
        title_label2.pack(side=tk.TOP)
        text_widget2 = tk.Text(frame2, font=("Baskerville", 16), wrap=tk.WORD) # Text widget configuration.
        text_widget2.pack(fill=tk.BOTH, expand=True)
        for i, word in enumerate(textC): # Iterate over the words and insert into the text widget.
            if i in modified_words_indices:
                text_widget2.insert(tk.END, word + ' ', "bold") # Bold tag to modified words.
            else:
                text_widget2.insert(tk.END, word + ' ')
        text_widget2.tag_configure("bold", font=("Baskerville", 16, "bold"))
        sentiment_label2 = tk.Label(frame2, text=f"Sentiment polarity: {sentiment_analysis(textC)}",font=("Baskerville", 16), fg="purple") # Perform sentiment analysis.
        textC_cloud = word_cloud(textC) # Generate word cloud.
        photo2 = ImageTk.PhotoImage(textC_cloud) # Display the image.
        image_label2 = tk.Label(frame2, image=photo2, width=frame_width, height=400)
        sentiment_label2.pack(side=tk.TOP)
        image_label2.pack()

        frame1 = tk.Frame(window, width=frame_width, height=frame_height) # Frame1 = Original text. Same operations for textC, here for textA in second position.
        frame1.pack_propagate(False)
        frame1.pack(side=tk.LEFT)
        title_label1 = tk.Label(frame1, text="ORIGINAL TEXT", font=("Baskerville", 16, "bold"))
        title_label1.pack(side=tk.TOP)
        text_widget1 = tk.Text(frame1, font=("Baskerville", 16), wrap=tk.WORD)
        text_widget1.pack(fill=tk.BOTH, expand=True)
        for i, word in enumerate(textA):
            if i in modified_words_indices:
                text_widget1.insert(tk.END, word + ' ', "bold")
            else:
                text_widget1.insert(tk.END, word + ' ')
        text_widget1.tag_configure("bold", font=("Baskerville", 16, "bold"))
        sentiment_label1 = tk.Label(frame1, text=f"Sentiment polarity: {sentiment_analysis(textA)}",
                                    font=("Baskerville", 16), fg="purple")
        textA_cloud = word_cloud(textA)
        photo1 = ImageTk.PhotoImage(textA_cloud)
        image_label1 = tk.Label(frame1, image=photo1, width=frame_width, height=400)
        sentiment_label1.pack(side=tk.TOP)
        image_label1.pack()

        if flagA: # If flag is True, create an additional frame to hold textB. Not always displayed, avoiding the displaying of the dictionary if Oulipo technique is chosen.
            frame3 = tk.Frame(window, width=frame_width, height=frame_height) # Frame3 = Modifying text. Same operations for the other two frames.
            frame3.pack_propagate(False)
            frame3.pack(side=tk.LEFT)

            title_label3 = tk.Label(frame3, text="MODIFYING TEXT", font=("Baskerville", 16, "bold"))
            title_label3.pack(side=tk.TOP)
            text_widget3 = tk.Text(frame3, font=("Baskerville", 16), wrap=tk.WORD)
            text_widget3.pack(fill=tk.BOTH, expand=True)
            textB_nouns = extract_nouns(textB)
            for i, word in enumerate(textB.split()):
                if word in textB_nouns:
                    text_widget3.insert(tk.END, word + ' ', 'bold')
                else:
                    text_widget3.insert(tk.END, word + ' ')
            text_widget3.tag_configure("bold", font=("Baskerville", 16, "bold"))
            sentiment_label3 = tk.Label(frame3, text=f"Sentiment polarity: {sentiment_analysis(textB)}",
                                        font=("Baskerville", 16), fg="purple")
            textB_cloud = word_cloud(textB.split())
            photo3 = ImageTk.PhotoImage(textB_cloud)
            image_label3 = tk.Label(frame3, image=photo3, width=frame_width, height=400)
            sentiment_label3.pack(side=tk.TOP)
            image_label3.pack()

        window.mainloop() # Enter the main event loop to display the GUI.

    except ValueError as ve:
        print("ValueError during formatting operation:", str(ve))
    except tk.TclError as te: # Specificallu check an exeption class to the Tkinter library.
        print("TclError during formatting operation:", str(te))
    except Exception as e:
        print("An error occurred during formatting:", str(e))
        return None

def terminal_printing(textC, textA, textB, modified_words_indices, flagA):  # Inner function that prints the texts to the terminal.
    def printing():
        original_text = ""  # Empty string initialisation to store the texts.
        for i, word in enumerate(textA):  # Iterate over the word in textA
            if i in modified_words_indices:
                original_text += f"{Style.BRIGHT}{word} "  # Append modified words in bold.
            else:
                original_text += f"{Style.RESET_ALL}{word} "  # And non-modified words in normal style.
        print(Fore.MAGENTA + Style.BRIGHT + "\nOriginal Text" + Style.RESET_ALL + " (up to 1500 characters):")  # Print the original text section heading and text.
        print(original_text[:1500])
        print()

        if flagA:  # If flag is true, performing for textB, modifying text. Same operations.
            second_text = ""
            textB_nouns = extract_nouns(textB)
            for i, word in enumerate(textB.split()):
                if word in textB_nouns:
                    second_text += f"{Style.BRIGHT}{word} "
                else:
                    second_text += f"{Style.RESET_ALL}{word} "
            print(Fore.MAGENTA + Style.BRIGHT + "Modifying Text" + Style.RESET_ALL + " (up to 1500 characters):")
            print(second_text[:1500])
            print()

        permuted_text = ""  # Same operations for textC, permuted one.
        for i, word in enumerate(textC):
            if i in modified_words_indices:
                permuted_text += f"{Style.BRIGHT}{word} "
            else:
                permuted_text += f"{Style.RESET_ALL}{word} "
        print(Fore.MAGENTA + Style.BRIGHT + "Permuted Text" + Style.RESET_ALL + " (up to 1500 characters):")
        print(permuted_text[:1500])
        print()

    print(Style.RESET_ALL)  # Reset the style for later operations.
    printing()  # Call the function.


def user_defining_functions(first_operation_num): # Function to provide interactive issues to the user
    def choosing_technique(flagC): # Inner function to define the techniques to be used.
        if flagC:  # Displaying if flag is True. Instructions displaying for permutations between retrieved existent texts
            while True: # Loop until a valid input is provided
                print(Style.BRIGHT + "\nWhich " + Fore.BLUE + "technique" + Style.RESET_ALL + Style.BRIGHT + " do you want to perform?" + Style.RESET_ALL)
                print("[0] Nouns switch between different texts.\n[1] N + n (Oulipo).")
                try:
                    operation_num = int(input(" "))
                    if 0 <= operation_num <= 1:
                        break
                    else:
                        print(
                            Style.BRIGHT + "Invalid input. Invalid input. Please enter a number between 0 and 1." + Style.RESET_ALL)
                except ValueError:
                    print(Style.BRIGHT + "Invalid input: not an integer." + Style.RESET_ALL)
            return operation_num
        else: # Displaying if flag is False. Instructions displaying for permutations between texts created by the user. 3 options.
            while True:
                print(
                    Style.BRIGHT + "\nWhich " + Fore.BLUE + "technique" + Style.RESET_ALL + Style.BRIGHT + " do you want to perform?" + Style.RESET_ALL)
                print(
                    "[0] Nouns switch between your texts.\n[1] Nouns switch between your text and a literature text.\n[2] N + n (Oulipo) with external dictionary.")
                try:
                    operation_num = int(input(" "))
                    if 0 <= operation_num <= 2:
                        break
                    else:
                        print(
                            Style.BRIGHT + "Invalid input. Please enter a number between 0 and 2." + Style.RESET_ALL)
                except ValueError:
                    print(Style.BRIGHT + "Invalid input: not an integer." + Style.RESET_ALL)
            return operation_num

    flagA = True # Flag initialized as True.
    flagD = True
    if first_operation_num == 0:  # If first_operation_num to 0 enters the instructions block for the USER texts.
        flagC = False # Flag set to False.
        second_operation_numA = choosing_technique(flagC) # Operation number from the choosing technique function.

        if second_operation_numA == 0:  # Instructions for permutations between two texts created by the user.
            while True:
                textA = input(
                    Style.BRIGHT + "\nPlease " + Fore.BLUE + "write the first text " + Style.RESET_ALL + "(to be modified):\n ")
                textB = input(
                    Style.BRIGHT + "\nPlease write the " + Fore.BLUE + "second text " + Style.RESET_ALL + "(modifying one):\n ")
                file_title = ''
                try:
                    textC, modified_words_indices, textA = switch_nouns(textA, textB) # Perform the switch nouns operation with the provided texts.
                    window = tk.Tk()  # Every time create a new window
                    return terminal_printing(textC, textA, textB, modified_words_indices, flagA), formatting(window, textC, textA, textB, modified_words_indices, file_title, flagA) # Raise the formatting and terminal printing for 3 windows.
                except ValueError:
                    print(Style.BRIGHT + "Invalid input: re-type please." + Style.RESET_ALL)

        elif second_operation_numA == 1:  # Instructions for permutations between one user's text and one pre-existing one.
            while True:
                textA = input(Style.BRIGHT + '\nPlease write ' + Fore.BLUE + 'your text ' + Style.RESET_ALL + "(to be modified):\n ")
                dir_name = 'Gutenberg'
                retrieve_local_corpus(dir_name, flagD)
                flagB = False
                text_number = texts_user_choice(flagB)
                modifying_text_choice = retrieve_local_text(text_number) # Retrieve the modifying text from the Gutenberg corpus based on user choices.
                flagD = False
                sorted_titles = retrieve_local_corpus(dir_name, flagD)
                file_title = 'Modified from ' + sorted_titles[text_number]
                modifying_data = modifying_text_choice.replace('\n', ' ')
                try:
                    textC, modified_words_indices, textA = switch_nouns(textA, modifying_data)
                    window = tk.Tk()
                    return terminal_printing(textC, textA, modifying_data, modified_words_indices, flagA), formatting(window, textC, textA, modifying_data, modified_words_indices, file_title, flagA)
                except ValueError:
                    print(Style.BRIGHT + "Invalid input: re-type please." + Style.RESET_ALL)

        elif second_operation_numA == 2:  # Instructions for permutations between one user's text and the Brown dictionary.
            flagA = False
            while True:
                textA = input(
                    Style.BRIGHT + '\nPlease write ' + Fore.BLUE + 'your text ' + Style.RESET_ALL + "(to be modified):\n ")
                brown_dic = retrieve_brown_corpus()
                file_title = ''
                try:
                    textC, modified_words_indices, textA = switch_Oulipo_technique(textA, brown_dic)
                    window = tk.Tk()
                    return terminal_printing(textC, textA, brown_dic, modified_words_indices, flagA), formatting(window, textC, textA, brown_dic, modified_words_indices, file_title, flagA) # Raise the formatting and terminal printing for 2 windows
                except ValueError:
                    print(Style.BRIGHT + "Invalid input: re-type please." + Style.RESET_ALL)

    elif first_operation_num == 1:  # If first_operation_num to 0 enters the instructions block for the PRE-EXISTING texts.
        flagC = True # FlagC set to True
        second_operation_numA = choosing_technique(flagC) # Operation number from the choosing technique function.

        if second_operation_numA == 0:  # Instructions for permutations between pre-existing texts.
            while True:
                dir_name = 'Gutenberg'
                sorted_titles = retrieve_local_corpus(dir_name, flagD)
                flagB = True
                text_number = texts_user_choice(flagB)
                while True:  # Loop to make the user choose which modifying_text
                    dic_num = input(
                        Style.BRIGHT + "\nOut of the same list, which is the text you would like to " + Fore.BLUE + "extract the new nouns " + Style.RESET_ALL + Style.BRIGHT + "from?" + Style.RESET_ALL + "\nType its number: ")
                    try:
                        dic_num = int(dic_num)
                        if 0 <= dic_num <= 10:
                            print('Warning: this operation might require some time due to the dimension of the texts.')
                            break
                        else:
                            print(
                                Style.BRIGHT + "Invalid input. Please enter a number inside the Corpus range." + Style.RESET_ALL)
                    except ValueError:
                        print(Style.BRIGHT + "Invalid input: not an integer." + Style.RESET_ALL)

                textA_choice = retrieve_local_text(text_number)  # Fetch the desired text based on the given number
                textB_choice = retrieve_local_text(dic_num)

                file_title = sorted_titles[text_number]  # Extract the single title
                data_to_modify = textA_choice.replace('\n', ' ')  # Replace with whitespace for better performance
                modifying_data = textB_choice.replace('\n', ' ')
                try:
                    textC, modified_words_indices, textA = switch_nouns(data_to_modify, modifying_data)
                    window = tk.Tk()  # Create a new window
                    return terminal_printing(textC, textA, modifying_data, modified_words_indices, flagA), formatting(window, textC, textA, modifying_data, modified_words_indices, file_title, flagA)
                except ValueError:
                    print(Style.BRIGHT + "Invalid input: re-type please." + Style.RESET_ALL)

        elif second_operation_numA == 1:  # Instructions for permutations between pre-existing text and Brown dictionary.
            while True:
                flagA = False
                dir_name = 'Gutenberg'
                sorted_titles = retrieve_local_corpus(dir_name, flagD)
                flagB = True
                text_number = texts_user_choice(flagB)
                text_choice = retrieve_local_text(text_number)
                file_title = sorted_titles[text_number]
                data_to_modify = text_choice.replace('\n', ' ')
                brown_dic = retrieve_brown_corpus()
                print('Warning: this operation might require a little time more due to texts lenght.')
                try:
                    textC, modified_words_indices, textA = switch_Oulipo_technique(data_to_modify, brown_dic)
                    window = tk.Tk()
                    return terminal_printing(textC, textA, brown_dic, modified_words_indices, flagA), formatting(window, textC, textA, brown_dic, modified_words_indices, file_title, flagA)
                except ValueError:
                    print(Style.BRIGHT + "Invalid input: re-type please." + Style.RESET_ALL)

while True:  # Loop to make the user choose if to perform between texts to write or pre-existing ones.
    print(Style.BRIGHT + "\n\nWhich " + Fore.BLUE + "operation" + Style.RESET_ALL + Style.BRIGHT + " do you want to perform?" + Style.RESET_ALL)
    print("[0] Permutation within texts written by you.\n[1] Permutation between literature texts.")
    try:
        first_operation_num = int(input(" "))
        if 0 <= first_operation_num <= 1:
            break
        else:
            print(
                Style.BRIGHT + "Invalid input. Please enter 0 or 1 depending on one of the two operations you want to perform." + Style.RESET_ALL)
    except ValueError:
        print(Style.BRIGHT + "Invalid input: not an integer." + Style.RESET_ALL)

user_defining_functions(first_operation_num) # Retrieving the all process.
