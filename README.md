# Charles the Chatbot
<h5>By Samual Finnigan-Griffin</h5>


This chatbot will initiate a conversation with the user, interacting with them like a friend. It will be able to understand the gist of what the user is saying, and (hopefully) respond in an appropriate way.


<h3>Features:</h3>
Uses NLTK (Natural Language Toolkit)
<ul>
	<li>POS tagging</li>
	<li>Synonym matching</li>
	<li>Lemmatizing (word stems)</li>
</ul>

Usable on public-facing web server (PHP backend)

HTML/CSS interface

Variety of topics

Handles small spelling mistakes

Many (5+) different responses to unknown user inputs

Can connect to other chatbots via sockets (with some tinkering of charles.py)


<h3>Usage:</h3>

This program is to be hosted on a Linux web server. It uses PHP to connect the Python backend script to a simple HTML frontend, which is visible to the user.

Note: `index.php` must be able to execute the Python script as sudo, in order for the script to execute sent_tokenizer.pickle; make sure your system allows this for your web server user. An easy way to accomplish this in Linux is by adding the following line to your `sudoers` file:

`www  ALL=(root) NOPASSWD: path/to/python`

Where `www` is your web server user.

Also, make sure you change the following line in `index.php` to point to your own Python installation location:

`shell_exec('/usr/bin/sudo /opt/rh/rh-python36/root/usr/bin/python charles.py '.$srcPort.' > /dev/null 2>&1 &');`

All conversation topics are handled dynamically in `convo.dat`. The first line of a topic is structured as follows:

<b>`. or ?` `keywords` (`^variable.wordType` OR `+`)</b>

The chatbot script will timeout after 120 seconds, to prevent abuse.


<h3>Dependencies:</h3>
The NLTK and Pattern Python libraries must first be downloaded. Installation instructions for each can be found here:

<a href="https://www.nltk.org/install.html">NLTK</a></br>
<a href="https://github.com/clips/pattern#installation">Pattern</a>

The simplest way is to run `python -m pip install nltk`, and then `python -m pip install pattern`
Then, a few NLTK modules must be downloaded. They can be downloaded by running Python in the command line and typing the following:

```
import nltk
nltk.download('punkt')
nltk.download('wordnet')
nltk.download('vader_lexicon')
nltk.download('averaged_perceptron_tagger')
```


<h3>Explanation:</h3>

`. or ?`: Depending on whether the topic expects a statement (.) or question (?) from the user (although currently unused).

`keywords`: When looking for only one of a multiple set of similar keywords, separate them with /'s (eg, hi/hey/hello). When looking for another set/single keyword, separate with &'s (eg, i&like&ham). Note that they must all be lowercase. Combined example: do&you/u&like/enjoy&soccer/football

`^variable`: Used when expecting to detect a single word from the user to save in memory, referenced by the give name ('variable' in this case)

`.wordType`: Dictates which word type (as defined by the NLTK library. eg, NNP = proper noun, VB = verb) to look for in the user's response, in order to help determine which word to save as the answer 'variable'.

`+`: Used when expecting to detect the positivity of the user's following response.
Note: Only one of `^variable.wordType` and `+` may be used at a time. In other words, the chatbot cannot handle both determining the positivity of the user's next response as well as saving a certain answer from it.

The rest of the topic is separated by newlines, with the bot waiting a response between each line before printing the next line.

In order to reference a saved answer from the user (`^variable` from before), simply put `$variable` in the bot's response, which will be replaced by the saved answer. Note that an answer must first be saved before it can be called like this. Otherwise, it will return "NaN" instead.

When using the `+` operator, the following 3 lines must start with `+` (positive), `-` (negative), and `0` (neutral), in any order. The positivity score of the user's last response will be used to determine which of these three responses to output.


<h3>Restrictions:</h3>

`convo.dat` file must begin with an empty line, and end with two empty lines.

First 5 topics of convo.dat must be default statement responses, followed by 5 default question responses.

Correlation algorithm likely won't scale well when many more topics are added.

Doesn't handle context well; user must explicitly mention what they're referring to each time they ask a question.

Can't both save an answer and determine the positivity of a single user response.

If the `+` operator is used, the next 3 lines MUST start with each one of `+`, `-`, and `0` (any order).


<h3>Potential Updates:</h3>

1. Take context into account

2. Create better correlation system

3. Make bot able to give some suggested topics/questions for the user to ask.

4. Make certain words weighted heavier (why, what, etc) when choosing topics

5. Use first character of topics (. or ?) to weight responses



<h1>Assignment Documentation</h1>


<h4>Feature List</h4>

<ul>
<li>GUI</li>
This allowed the chatbot system to look much more appealing to an average user, and further helped the 'friendly' aspect of the bot.
</br>
<img src="https://puu.sh/DaIWO/49d74d0fb4.jpg">
<li>Web Server Backend</li>
By allowing Charles to be hosted on a public-facing web server, it makes him much more accessible, as instead of having to give someone a program they have to set up and run in an interpreter, they can simply enter a web address into their browser.
</br>
<img src="http://puu.sh/DaIXI/9ae7c63e7f.png">
<li>Extra Topics</li>
Adding more topics makes the chatbot system more diverse, able to respond to users in a wider array of situations. This makes Charles seem more realistic
</br>
<img src="http://puu.sh/DaIYt/187353fa08.jpg">
</br>
<img src="http://puu.sh/DaIYA/bc54849887.jpg">
<li>5+ Reasonable Responses</li>
When Charles doesn't understand the user, it's more user-friendly for him to respond in a multitude of ways, instead of repeating "I didn't understand that" over and over. This also allows for a bit of personality to be added.
</br>
<img src="http://puu.sh/DaIZB/0417535bdb.jpg">
<li>Spelling Mistake Handling</li>
Allowing him to understand the user, even if words are slightly mispelled, goes a long way in reducing frustration and increasing believability.
</br>
<img src="http://puu.sh/DaIZS/d9d203100f.jpg">
<li>POS Tagging</li>
Using NLTK to handle POS tagging allows Charles to retrieve the appropriate piece of a user's response. When he uses parts of the user's response in return, this makes him seem even more real.
</br>
<img src="http://puu.sh/DaJ0k/ccbe541a2d.jpg">
<li>Synonym Recognition</li>
Similar to the spelling mistake handling, allowing Charles to understand words that aren't exactly what he expects makes him seem like he can understand real conversation.
</br>
<img src="https://puu.sh/DaJ3g/7e555345d9.jpg">
<li>Conversation with another agent</li>
Enabling Charles to be able to speak with another chatbot shows some interesting aspects of both bots, as well as potentially enabling easier, more dynamic testing to be done.
</br>
<img src="http://puu.sh/DaJ8W/301a4e8f76.png">
</br>
<img src="http://puu.sh/DaJ47/c8726330b7.png">
</ul>


<h4>Level 0 DFD</h4>
<img src="https://finnigan.me/chatbot/DFD0.png?1">

<h4>Level 1 DFD</h4>
<img src="https://finnigan.me/chatbot/DFD1.png?1">

<h4>GitHub Graphs</h4>
<img src="https://puu.sh/DaIam/57a58788b7.png">
<img src="https://puu.sh/DaIaL/b031f7c629.png">

<h4>Sample Output</h4>
<img src="https://puu.sh/DaIHR/540213dc2f.jpg">
<img src="https://puu.sh/DaIId/021ff1034e.jpg">
<img src="https://puu.sh/DaIIT/0bada56b53.jpg">
<img src="https://puu.sh/DaIJy/2d764faf2c.jpg">
<img src="https://puu.sh/DaIJU/4d8ed528c6.jpg">
<img src="https://puu.sh/DaISQ/c5a45c7878.jpg">



<h4>5 Extractable Features</h4>
As Charles was programmed to be as modular as possible, many of his functions can be reused:


<b>findAnswer(uIn, wordType):</b>
This function searches the user's sentence for a certain type of word (noun, verb, etc.), and returns the word best matching this type, if possible.

<b>posResponse(uIn):</b>
This function takes the user's response, and puts it through a language processor that gives it a positivity 'score'; how positive or negative it is in general.

<b>findWord(words, uIn):</b>
This function takes an array of words `words` and compares it to a string `uIn`. If any word in `uIn`, or any of their synonyms, match a word in `words`, the function returns `True`.

<b>spellCheck(uIn):</b>
This function spellchecks the user's sentence, and returns the corrected string.

<b>lemma(word):</b>
This function takes any word `word`, and lemmatizes it (gets its root word).