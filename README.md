# word-memo-app

This is a Word memorizing quiz app built using flask and sqlite.

Using the interface, you can:
* Sign Up, Sign In
* Search for word definitions
* Save any word and its definition to your personal dictionary
* See all of the words in your personal dictionary
* Search for words
* Practice(quiz) your words

## Searching
With a very basic UI, you will be able to search for definition of any words. 
To fetch definitions to the words, app uses wordsapi.com 
 
If the definition for searched term does not exist in the api, a message will flash to notify you. 
If the searched word exist in your personal dictionary, then api will not be called. Instead the definition will be shown to you from your personal dictionary. 


## Adding Words to Your Dictionary
Using very similiar interface with search, you will be able to add new words to your personal dictionary. 
 
## List your Words
You are able to see a list containing all your words, their definition, power attribute for words and a delete option to delete the word from your personal dictionary. 
 
## Practicing
Practicing will only be available after you have at least 10 words in your dictionary 

A random word definition from your dictionary will appear together with 3 options. 
After you answer the question, your words will get plus or minus practice points depending on your answer's beign correct. 
 
## Power Attribute for Words
All words have power attribute that is calculated using below formula:  
Power = # of Times Word is searched / 2  +  # of Times Word is Showed Up in Practice / 4  + Practice Point  
