
# coding: utf-8

# In[1]:

import sys
sys.path.append(r'T:\Departments\Informatics\LanguageEngineering')


#  # Introduction

# This report looks at opinion extraction of certain aspects in sentences of documents. Certain Natural Language Processing methods such as part of speech tagging and dependency parsing will be used to achieve the goal of extracting opinions. 
# 
# Part of speech tagging is labeling each word in a sentence with a specific part of speech(e.g. adjective, noun,adverb, etc.). This is important because we need to know which words are describing aspects in a document. For example, adjectives can directly describe a noun. This adjective can be extracted as an opinion of that noun(e.g. amazing game, amazing is an opinion on a game).
# 
# Dependency parsing is looking at the relations between words and what role each word has in a specific sentence(e.g. The plot is fun - the word "plot" is the subject of the sentence and it's relation is with the root- "fun" - of the sentence.

# # 1.Opinion Extractor Code

# The opinion extractor below has been implemented that when given an aspect_token, it will return a list of opinions on that aspect. The extractor is able to find adjectival modifiers(i.e. exciting plot), adjectives linked by copulae(i.e. the plot was fun), adverbial modifiers(i.e. incredibly fun), negations(i.e. the plot was not fun) and conjunctions(i.e. plot was fun and inspiring)
# 
# The way the opinion extractor works is that it firstly checks for words(or tokens) that are dependent on the aspect word. To find the dependants that describe the aspect token(which is what it's looking for), the opinion extractor must look for specific dependency relations such as adjectival and adverbial modifiers. If one is found, it is also necessary to look for words linked to these modifiers as these might also describe the aspect word(e.g. fun exciting plot). It also checks if any negations are dependent on the aspect word.
# 
# Secondly, the opinion extractor looks at modifiers linked by copulae. This works by looking at the head of the aspect word(the word that it is dependent on) and checks if it is a part of speech that describes the aspect word(i.e. adjective) and that the aspect word is in an "nsubj" relation with it's head. Same procedures as above apply when looking for words linked to these modifiers and negations. Although these negations should be dependent on the head, not the aspect token itself. 
# 
# 

# In[5]:

def opinion_extractor(aspect_token, parsed_sentence):
    
    opinions = []
  
    word=''
    word2=''
    #this for-loop structure looks for adjectival and adverbial modifiers to the aspect token
    for dependant in parsed_sentence.get_dependants(aspect_token):
        #if a dependant is found as and adjective or adverb
        if dependant.deprel =="amod" or dependant.deprel =="advmod":
            word = dependant.form                               
            for dep in parsed_sentence.get_dependants(dependant):
                #checks if the original modifier has an adjectival or adverbial modifier itself and add it to it
                if dep.deprel =="amod" or dep.deprel =="advmod":
                    word = " "+dep.form+"-" + word
                
            for dep in parsed_sentence.get_dependants(aspect_token):
                #if the aspect token has a negation modifier, add "not" to the opinion word to represent it
                if dep.deprel=="neg":
                    word="not " + word
                    break
            opinions+=[word]   
                 
   
    #this if-structure checks for words that the aspect token is in an "nsubj" relation(i.e. is the subject of the sentence)
    #this would mean that the word we're looking for is the head of the aspect token
    if (parsed_sentence.get_head(aspect_token).pos =="JJ" or parsed_sentence.get_head(aspect_token).pos =="VBG" or parsed_sentence.get_head(aspect_token).pos =="NN") and aspect_token.deprel=="nsubj":  
        word = parsed_sentence.get_head(aspect_token).form 
        #this looks at the dependants of the modifier above(i.e. the head of the aspect token)
        for de in parsed_sentence.get_dependants(parsed_sentence.get_head(aspect_token)):
            word2=''
            #if a conjunction is found, it means there is another adjective describing the aspect token
            if de.deprel=="conj":
                word2=de.form
                #checks if the conjunction has modifiers(adverbial or adjectival)
                for d in parsed_sentence.get_dependants(de):
                    #if one is found, add the modifier to the opinion word
                    if d.deprel=="amod" or d.deprel=="advmod":
                        word2=" "+d.form+"-"+word2
                #checks if the conjunction is negated            
                for d in parsed_sentence.get_dependants(de):
                    if d.deprel=="neg":
                        #adds the modifier to the opinion word
                        word2="not"+word2
                        break
                #adds the conjuction with any modifier to the opinions list       
                opinions+=[word2]
                          
        for dep in parsed_sentence:
            #checks if the word found has adverbial or adjectival modifiers
            if (dep.deprel == "advmod" or dep.deprel =="amod") and parsed_sentence.get_head(dep)==parsed_sentence.get_head(aspect_token):
                word=dep.form + "-"+word
        #checks if the head of the aspect token has a negation modifier         
        for dep in parsed_sentence.get_dependants(parsed_sentence.get_head(aspect_token)):
                if dep.deprel=="neg":
                    word="not " + word
                    break  
        opinions+=[word]
        
    return opinions


# # 2.Opinion Extractor tested on the example sentences

# In[6]:

from sussex_nltk.parse import load_parsed_dvd_sentences, load_parsed_example_sentences


# Here are the example sentences provided. There are a total of 16 sentences. They are meant to test the implementation of the extensions of the opinion extractor on the "plot" aspect.
# 
# Sentence 1 covers adjectival modification(i.e. fresh plot)
# 
# Sentence 2 covers adjectives linked by copulae(i.e. plot was bad)
# 
# Sentence 3 covers adverbial modifiers on adjectives linked by copulae(i.e. the plot was extremely bad)
# 
# Sentence 4 covers adverbial modifiers on adjectival modifiers of the aspect token(i.e. extremely bad plot)
# 
# Sentences 5,6 and 7 cover negations(i.e. not dull, not fresh)
# 
# Sentences 8 and 9 cover conjunctions(i.e.  plot was bad but interesting)
# 
# Sentences 10 to 16 cover the additional extensions of which only the extension tested in 12 was implemented. This one covers verbs with "-ing". (i.e. plot was lacking)

# In[7]:

#this piece of code prints out just the example sentences 
parsed_example_sentences = load_parsed_example_sentences()
for parsed_sentence in parsed_example_sentences:
    print "--- Sentence ---"
    print parsed_sentence


# In this section, the opinion extractor will be tested on the example sentences provided. Each
# sentence provided is meant to test one extension(i.e. Sentence 1 tests if the opinion extractor detects adjectival modifiers). Not all example sentences will have opinions of the plot that can be detected by the opinion extractor with just those 5 extensions. These sentences will be omitted when printing out the opinions below as we are not interested in those because they cover the additional extensions. 
# 
# A list of the sentences and their opinion of the plot that should come out of the opinion extracting process below has been created. This number is less than the total number of sentences as some of those cover the additional extensions that weren't implemented. 

# In[8]:

aspect = "plot"
i=0
#These are the opinions of the sentences that will be printed(i.e. sentences that will have  
#opinions detectable by the opinion extractor)
expected_opinions = ["exciting, fresh",
                     "dull", 
                     "excessively-dull",
                     "excessively-dull",
                     "not dull",
                     "not exciting, not fresh",
                     "not excessively-dull",
                     "fun,inspiring,cheesy",
                     "not particularly-special, really-cheesy",
                     "not lacking",
                     "full of holes",
                     "no logical plot"]    
#for each pre-parsed sentence, extract an opinion for the plot aspect  
for parsed_sentence in load_parsed_example_sentences(): 
    opinions=[]
    for aspect_token in parsed_sentence.get_query_tokens(aspect):
            opinions+=opinion_extractor(aspect_token,parsed_sentence)
    #if an opinion is found on a sentence, print the raw sentence, the parsed sentence
    #the expected opinion output and the actual opinion
    if opinions: 
        print "--- Sentence: %s ---\n" % parsed_sentence.raw()
        print "%s\n" % parsed_sentence  
        print "Expected Opinions - " +expected_opinions[i]
        i+=1
        print "Actual Opinions: %s\n" % opinions


# As expected, the opinion extractor produced the right output for the sentences that cover extensions 1 to 5. That is the first 9 sentences from the 16 provided. For the other 3 sentences printed out which are used to test the additional extensions, one of them was implemented and produces the right output(i.e. not lacking). 
# 
# In the sentence: "The plot is full of holes", the opinion "full" is found because it is an adjective and this relation between "plot" and "full" was covered in the second extension which looks for adjectives linked by copulae with the subject. What is omitted by the opinion extractor is "of holes" structure which is dependent on the "full" adjective. Because this wasn't implemented in the opinion extractor, it is not part of the opinion in that sentence. 
# 
# In the sentence: "There was no logical plot to this story.", the opinion "logical" is found because it is an adjectival modifier to the subject of the sentence. This is covered in the first extension. What is omitted by the opinion extractor is the "no" which should be a negation but because "no" has been parsed as a determiner and not as a negation which was covered in extension 4. Also, if the opinion extractor finds a negation, it will print out "not", instead of "no" as needed above. 

# # 3.Opinion Extractor tested on the example sentences

# ## I.Plot Aspect

# In[9]:

import random
aspect = "plot"
j =1;

#get a sample of 180 sentences from the parsed dvd sentences
#because not all senteces have opinions on the plot and these will not be printed off later on
parsed_dvd_sentences_sample = load_parsed_dvd_sentences(aspect)[:180]
#for each pre-parsed sentence, extract an opinion for the plot aspect 
for parsed_sentence in parsed_dvd_sentences_sample:    
    opinions=[]
    for aspect_token in parsed_sentence.get_query_tokens(aspect):
            opinions+=opinion_extractor(aspect_token,parsed_sentence)
   
    #if an opinion is found on a sentence, print the raw sentence, the parsed sentence
    #the opinion and the sentence number
    if opinions: 
        print "--- Sentence: %s ---\n" % parsed_sentence.raw()
        print "%s\n" % parsed_sentence  
        print "Opinions: %s\n" % opinions  
        print "Sentence Number: "+str(j)
        #when sentence number 36 is reached
        if j==36:
            #take sentence 36 as an example of a parse error
            parse_error_example = parsed_sentence
            parse_error_opinions_ex = opinions
        #when sentence number 18 is reached
        if j==18:
            #take sentence 18 as an example of a PoS tag error
            pos_error_example = parsed_sentence
            pos_error_opinions_ex = opinions
        if j==47:
            #take sentence 47 as an example of an ambiguity error
            ambiguity_example = parsed_sentence
            ambiguity_opinions_ex = opinions
        if j==28:
            #take sentence 28 as an example of a extractor defficiency
            defficiency_example = parsed_sentence
            defficiency_opinions_ex = opinions
        j+=1
        print "--------------------------------"


# Out of the 180 sentences, 58 had opinions about the plot. Out of those 58, 28 had correctly extracted opinions, 13 with parser errors, 3 with PoS tags errors, 9 sentences were ambiguous and 5 had extractor deficiencies. 

# ### Parse Error Example

# In the sentences with parsing errors, the most common problem was not matching a possible opinion with the aspect word because of wrong dependency relationships. An example of  this is sentence 36:"An original and timely plot." from the sample. 

# In[10]:

#this is the original parsing of the sentence
print "--- Sentence: %s ---\n" % parse_error_example.raw()
print "%s\n" % parse_error_example   
print "Opinions: %s\n" % parse_error_opinions_ex


# Correct Parsing Example
# <img src="./img/img1.png" alt="img1">
# <p><i><center><b>img1: Correct Parsing of: "An original and timely plot."</b><center></i></p>

# By comparing these parsing results from img1 and the output above, you can notice that because the sentence hasn't been parsed correctly originally, plot would have the wrong dependency relation and so would its opinion words so the extractor would produce the wrong output. The opinion extracted is 'timely' while it should be 'timely' and 'original'.

# ### PoS Tag Error Example

# With PoS tagging issues, the main problem was that certain adjectives were not tagged as "JJ" but as nouns(i.e. "NN")

# In[11]:

#this is the original parsing of the sentence with a PoS tag error
print "--- Sentence: %s ---\n" % pos_error_example.raw()
print "%s\n" % pos_error_example   
print "Opinions: %s\n" % pos_error_opinions_ex


# From the result above, you can see that only 'strong' is selected because 'fun' is tagged as a noun('NN') when it should be an adjective ('JJ') as shown below.

# Correct PoS Tag Example
# ![Parse Error Example](./img/img2.png)
# <p><i><center><b>img2: Correct PoS Tag of 'fun'</b><center></i></p>

# As you can see in img2, fun is an adjective('A')

# ### Ambiguity Example

# When a sentence is found as ambiguous, the opinion extraction is usually correct. The problem is that the output produced isn't clear or misleading. 

# In[12]:

#this is the original parsing of the ambiguous sentence
print "--- Sentence: %s ---\n" % ambiguity_example.raw()
print "%s\n" % ambiguity_example   
print "Opinions: %s\n" % ambiguity_opinions_ex


# Reading the above sentence, you notice that the word 'plot' doesn't refer to the plot of the movie. In this example. plot is a synonym of scheme but the extractor cannot detect that and produces the output 'sinister'.

# ### Extractor Deficiency

# Certain sentences might have complex opinions regarding the aspect word that the extractor wasn't implemented to find. 

# In[13]:

#this is the original parsing of the ambiguous sentence
print "--- Sentence: %s ---\n" % defficiency_example.raw()
print "%s\n" % defficiency_example   
print "Opinions: %s\n" % defficiency_opinions_ex


# The opinion extractor only produces 'nothing'. That doesn't make sense by itself. The output should've been "would've been nothing if not for the President" to give a good image of the opinion of the plot in that sentence. This opinion extractor, however, was not trained to deal with complex situations like this.

# ## II.Characters Aspect

# In[14]:

import random
aspect = "characters"
j =1;

#get a sample of 120 sentences from the parsed dvd sentences
#because not all senteces have opinions on the plot and these will not be printed off later on
parsed_dvd_sentences_sample = load_parsed_dvd_sentences(aspect)[:120]
#for each pre-parsed sentence, extract an opinion for the plot aspect 
for parsed_sentence in parsed_dvd_sentences_sample:    
    opinions=[]
    for aspect_token in parsed_sentence.get_query_tokens(aspect):
            opinions+=opinion_extractor(aspect_token,parsed_sentence)
   
    #if an opinion is found on a sentence, print the raw sentence, the parsed sentence
    #the opinion and the sentence number
    if opinions: 
        print "--- Sentence: %s ---\n" % parsed_sentence.raw()
        print "%s\n" % parsed_sentence  
        print "Opinions: %s\n" % opinions  
        print "Sentence Number: "+str(j)
        if j==45:
            #take sentence 45 as an example of a parse error
            parse_error_example = parsed_sentence
            parse_error_opinions_ex = opinions 
        if j==44:
            #take sentence 44 as an example of a PoS tag error
            pos_error_example = parsed_sentence
            pos_error_opinions_ex = opinions
        if j==23:
            #take sentence 23 as an example of an ambiguity error
            ambiguity_example = parsed_sentence
            ambiguity_opinions_ex = opinions
        if j==16:
            #take sentence 16 as an example of a extractor defficiency
            defficiency_example = parsed_sentence
            defficiency_opinions_ex = opinions
            
        j+=1
        print "--------------------------------"


# Out of the 120 sentences, 48 had opinions about the characters. Out of those 48, 17 had correctly extracted opinions, 3 with parser errors, 3 with PoS tags errors, 19 sentences were ambiguous and 6 had extractor deficiencies. 

# ### Parse Error Example

# In the sentences with parsing errors, the most common problem was not matching a possible opinion with the aspect word because of wrong dependency relationships. An example of  this is sentence 45:"The characters are psychedelic , psychotic , retro and bent ." from the sample where both psychedelic and psychotic are marked as the root.

# In[15]:

#this is the original parsing of the sentence
print "--- Sentence: %s ---\n" % parse_error_example.raw()
print "%s\n" % parse_error_example   
print "Opinions: %s\n" % parse_error_opinions_ex


# Correct Parsing Example
# ![Parse Error Example](./img/parseErrorChar.png)
# <p><i><center><b>img3: Correct Parsing of: "The characters are psychedelic , psychotic , retro and bent." </b><center></i></p>

# If the parsing was correct, the word "psychotic" would've been detected as adjectival modifier and "retro" and "bent" as a conjunction of "psychedelic" as seen in img3.

# ### PoS Error Example

# Like with the plot aspect, the most common problem was when adjectives were confused with nouns. Here is an example from the sample of reviews.

# In[16]:

#this is the original parsing of the sentence
print "--- Sentence: %s ---\n" % pos_error_example.raw()
print "%s\n" % pos_error_example   
print "Opinions: %s\n" % pos_error_opinions_ex


# Correct PoS Tag Example
# ![Parse Error Example](./img/posEC.png)
# <p><i><center><b>img4: Correct PoS Tag for "borderline"</b><center></i></p>

# If 'borderline' was found as an adjective, it would've been a modifier for the 'offensive' conjunction proven in the parsing from img4.

# ### Ambiguity Example

# When a sentence is found as ambiguous, the opinion extraction is usually correct. The problem is that the output produced doesn't clearly describe the characters. 

# In[17]:

#this is the original parsing of the ambiguous sentence
print "--- Sentence: %s ---\n" % ambiguity_example.raw()
print "%s\n" % ambiguity_example   
print "Opinions: %s\n" % ambiguity_opinions_ex


# In this example, there are no adjectives here that say anything about the characters(e.g. characters are good or bad). Although this can be avoided if the opinion extractor was edited to ignore instances of 'other', 'main',etc. This way it would only output meaningful opinions

# ### Extractor Deficiency

# In[18]:

#this is the original parsing of the deficiency sentence
print "--- Sentence: %s ---\n" % defficiency_example.raw()
print "%s\n" %  defficiency_example   
print "Opinions: %s\n" % defficiency_opinions_ex


# In this example, the output is incomplete. It should've been 'easy to like' but because the extractor only detects conjunctions, it wouldn't find 'like' or 'to' as they aren't conjunctions

# ## III. Dialogue Aspect

# In[19]:

import random
aspect = "dialogue"
j =1;

#get a sample of 120 sentences from the parsed dvd sentences
#because not all senteces have opinions on the plot and these will not be printed off later on
parsed_dvd_sentences_sample = load_parsed_dvd_sentences(aspect)[:130]
#for each pre-parsed sentence, extract an opinion for the plot aspect 
for parsed_sentence in parsed_dvd_sentences_sample:    
    opinions=[]
    for aspect_token in parsed_sentence.get_query_tokens(aspect):
            opinions+=opinion_extractor(aspect_token,parsed_sentence)
   
    #if an opinion is found on a sentence, print the raw sentence, the parsed sentence
    #the opinion and the sentence number
    if opinions: 
        print "--- Sentence: %s ---\n" % parsed_sentence.raw()
        print "%s\n" % parsed_sentence  
        print "Opinions: %s\n" % opinions  
        print "Sentence Number: "+str(j)
        if j==9:
            #take sentence 9 as an example of a parse error
            parse_error_example = parsed_sentence
            parse_error_opinions_ex = opinions 
        if j==10:
            #take sentence 10 as an example of a PoS tag error
            pos_error_example = parsed_sentence
            pos_error_opinions_ex = opinions
        if j==22:
            #take sentence 22 as an example of an ambiguity error
            ambiguity_example = parsed_sentence
            ambiguity_opinions_ex = opinions
        if j==20:
            #take sentence 20 as an example of a extractor defficiency
            defficiency_example = parsed_sentence
            defficiency_opinions_ex = opinions
            
        j+=1
        print "--------------------------------"


# Out of the 130 sentences, 46 had opinions about the dialogue. Out of those 46, 25 had correctly extracted opinions, 5 with parser errors, 2 with PoS tags errors, 6 sentences were ambiguous and 6 had extractor deficiencies. 

# ### Parse Error Example

# In[20]:

#this is the original parsing of the sentence
print "--- Sentence: %s ---\n" % parse_error_example.raw()
print "%s\n" % parse_error_example   
print "Opinions: %s\n" % parse_error_opinions_ex


# The problem with this sentence is that the root is wrong. 'Unbelievable' should've been the root and the correct output the reverse of the actual output. Img5 shows a correct parsing for the sentence.

# Correct Parsing Example
# ![Parse Error Example](./img/diaP.png)
# <p><i><center><b>img5: Correct parsing of: "The dialogue is completely unbelievable considering the age of these kids."</b><center></i></p>

# ### PoS Tag Error Example

# In[21]:

#this is the original parsing of the sentence with the PoS error
print "--- Sentence: %s ---\n" % pos_error_example.raw()
print "%s\n" % pos_error_example   
print "Opinions: %s\n" % pos_error_opinions_ex


# In this example, 'tangy' is tagged as a noun when it should've been an adjective.

# ### Ambiguity Example

# In[22]:

#this is the original parsing of the sentence with 
print "--- Sentence: %s ---\n" % ambiguity_example.raw()
print "%s\n" % ambiguity_example   
print "Opinions: %s\n" % ambiguity_opinions_ex


# The opinion extracted could be considered ambiguous as 'talking-to-himself' doesn't mean that the dialogue is either good or bad. This can be interpreted by whoever reads the review.

# ### Extractor Deficiency Example

# In[23]:

#this is the original parsing of the sentence with deficiencies
print "--- Sentence: %s ---\n" % defficiency_example.raw()
print "%s\n" % defficiency_example   
print "Opinions: %s\n" % defficiency_opinions_ex


# A problem with this sentence is that the opinion extractor has taken 'have' because it is a conjunction. This doesn't describe the aspect and because not only adjectives can be conjunctions, this would be a problem for the extractor that could be implemented. 

# ## IV. Cinematography Aspect

# In[24]:

import random
aspect = "cinematography"
j =1;

#get a sample of 120 sentences from the parsed dvd sentences
#because not all senteces have opinions on the plot and these will not be printed off later on
parsed_dvd_sentences_sample = load_parsed_dvd_sentences(aspect)[:90]
#for each pre-parsed sentence, extract an opinion for the plot aspect 
for parsed_sentence in parsed_dvd_sentences_sample:    
    opinions=[]
    for aspect_token in parsed_sentence.get_query_tokens(aspect):
            opinions+=opinion_extractor(aspect_token,parsed_sentence)
   
    #if an opinion is found on a sentence, print the raw sentence, the parsed sentence
    #the opinion and the sentence number
    if opinions: 
        print "--- Sentence: %s ---\n" % parsed_sentence.raw()
        print "%s\n" % parsed_sentence  
        print "Opinions: %s\n" % opinions  
        print "Sentence Number: "+str(j)
        if j==30:
            #take sentence 30 as an example of a parse error
            parse_error_example = parsed_sentence
            parse_error_opinions_ex = opinions 
        if j==6:
            #take sentence 6 as an example of a PoS tag error
            pos_error_example = parsed_sentence
            pos_error_opinions_ex = opinions
        if j==28:
            #take sentence 28 as an example of an ambiguity error
            ambiguity_example = parsed_sentence
            ambiguity_opinions_ex = opinions
        if j==8:
            #take sentence 8 as an example of a extractor defficiency
            defficiency_example = parsed_sentence
            defficiency_opinions_ex = opinions
            
        j+=1
        print "--------------------------------"


# Out of the 90 sentences, 53 had opinions about the dialogue. Out of those 53, 34 had correctly extracted opinions, 9 with parser errors, 4 with PoS tags errors, 1 sentence was ambiguous and 5 had extractor deficiencies. 

# ### Parse Error Example

# In[25]:

#this is the original parsing of the sentence with Parser error
print "--- Sentence: %s ---\n" % parse_error_example.raw()
print "%s\n" % parse_error_example   
print "Opinions: %s\n" % parse_error_opinions_ex


# The output produced here is wrong because 'see' is not meant to be an opinion. 'see' is wrongly linked as a dependant to 'amazing' which describes the aspect token. And because it is a conjunction, it is added to the output

# Correct Parsing Example
# ![Parse Error Example](./img/cineP.png)
# <p><i><center><b>img6: Correct Parsing of: "The cinematography in this movie is amazing ; the camera disappears and we see real life transpiring on screen."</b><center></i></p>

# ### PoS Error Example

# In[26]:

#this is the original parsing of the sentence with PoS error
print "--- Sentence: %s ---\n" % pos_error_example.raw()
print "%s\n" % pos_error_example   
print "Opinions: %s\n" % pos_error_opinions_ex


# In this example, 'music' is tagged as an adjective when clearly music is a noun. 

# ### Ambiguity Example

# In[27]:

#this is the original parsing of the sentence with ambiguity
print "--- Sentence: %s ---\n" % ambiguity_example.raw()
print "%s\n" % ambiguity_example   
print "Opinions: %s\n" % ambiguity_opinions_ex


# This example can be ambiguous as 'Russian' doesn't provide a clear description of the cinematography. The person that looks at the opinion wouldn't know what to make of it as 'Russian' doesn't mean if it's good or bad. 

# ### Extractor Deficiency Example

# In[28]:

#this is the original parsing of the sentence with deficiencies
print "--- Sentence: %s ---\n" % defficiency_example.raw()
print "%s\n" % defficiency_example   
print "Opinions: %s\n" % defficiency_opinions_ex


# In this example 'even' is an adverb modifier which the extractor was trained to find. Usually, adverb modifiers are descriptive but not in this case. The extractor doesn't know that, unfortunately unless it's clearly specified it should only look at adjectives.

# ## Opinion Extractor Analysis on DVD Reviews

# ### Plot Code

# In[78]:

#code used to plot a graph
from matplotlib import pylab as plt
get_ipython().magic('matplotlib inline')
# tweak figure appearance 
rc = {'xtick.labelsize': 16,
      'ytick.labelsize': 16,
      'axes.labelsize': 18,
      'axes.labelweight': '900',
      'legend.fontsize': 20,
      'font.family': 'cursive',
      'font.monospace': 'Nimbus Mono L',
      'lines.linewidth': 2,
      'lines.markersize': 9,
      'xtick.major.pad': 20}
plt.rc_context(rc=rc)
plt.rcParams['font.family'] = 'serif'
plt.rcParams['axes.labelsize'] = 22
plt.rcParams['figure.figsize'] = 9, 6  # make figures larger in notebook

def plot_results(results, title, xlabels, ylabel="Success Rate"):
    '''Plot a bar graph of results'''
    ind = np.arange(len(results))
    width = 0.4
    plt.bar(ind, results, width, color="#1AADA4")
    plt.ylabel(ylabel)
    plt.ylim(ymax=100)
    plt.xticks(ind+width/2.0, xlabels)
    plt.title(title)


# The success rates of all aspects have been calculated below and plotted on the graph.

# In[80]:


plot_total =58;
plot_correct =28;
plot_success_rate =28%(58%100);

char_total =48;
char_correct =17;
char_success_rate =17%(48%100);

dial_total =46;
dial_correct =25;
dial_success_rate =25%(46%100);

cinem_total =53;
cinem_correct =34;
cinem_success_rate =34%(53%100);


plot_results([plot_success_rate, char_success_rate, dial_success_rate, cinem_success_rate],"Aspect",['Plot', 'Characters', 'Dialogue', 'Cinematography'])


# <p><i><b>Graph1: Success Rate of Extraction on Aspects</b></i></p>

# In conclusion, we notice from graph1 that the extractor doesn't do a very good job in extracting the right opinions with the greatest percentage being just under 40% for cinematography. 
# 
# The reason why the cinematography aspect has the highest success rate is because most of the sentences with opinions found for cinematography didn't have a complex structure like for the previous aspects so it was easier for the extractor to find opinions.

# # 4.Proposal on the website

# A website that automatically extracts opinions of certain aspects of a DVD can be quite useful for people that might be interested in viewing that DVD. This would provide a quicker way of finding out what the idea behind the DVD's aspects is about without having to read through long reviews.
# 
# To create such a website, certain NLE tools are needed: a PoS tagger, a dependency parser and an opinion extractor. A large amount of reviews would also be needed to be able to cover a large amount of films that people might be interested in. 
# 
# Because the parser is quite slow, especially when dealing with a large amount of data, the tagging, parsing and opinion extracting should all be done offline, then on the website, for each movie reviewed, these opinions would be stored and could be retrieved when a user requests them with a name of a film. The website can also let the user provide an aspect such as the plot, characters, etc. or just display the opinions of all aspects of a movie that are available.
# 
# The accuracy of these opinions all depend on the back-end of the NLP system. Basically if the tagger gets something wrong then the parser will get something wrong then the extractor will get something wrong. The accuracy all depends on how well all of these are written. 

# # Conclusion

# To conclude, the 5 extensions have been implemented in the opinion extractor. This has been tested on a set of example sentences and has proven that the opinion extractor functioned accordingly(i.e. the correct opinions were extracted on each example sentence).
# 
# When tested on actual reviews, the opinion extracting process was successful but produced a lot of incorrect opinions due to PoS tagging error, parsing errors and opinion extractor defficiencies. 
# 
# To improve on the accuracy of the opinion extraction process, the extractor can be extended to support more complex sentence structures and find more complex opinions.
# 

# * (2191 words)

# 

# In[ ]:



