import os.pathimport pickleimport reALPHABETS= "([A-Z a-z])"PREFIXES="(my great|fair|virtuous|valiant|vile|king|queen|count|princess|prince|lord|lady|sir|mistress|duke|worthy|my noble|noblelroyal|highness)[' ']" SUFFIXES="(Inc|Ltd|Jr|Sr|Co)"STARTERS="(Methinks|Doth|Thine|Thy|Who\s|The|I|This|Not|Hast|Haveth|Makest|Tis|Twas|Thou|He\s|She\s|It\s|They\s|Their\s|Our\s|We\s|But\s|However\s|That\s|This\s|Wherever|Why|If)"   ACRONYMS = "([A-Z][.][A-Z][.](?:[A-Z][.])?)"WEBSITES = "[.](com|net|org|io|gov)"PUNCS = ",'.?!:;"  MODEL_NAME="model.pkl"TRAINING_DATA = "modified_shakespeare.txt"class FrequencyGram(dict):    from random import randint, choices    def __init__(self, iterable=None):        super(FrequencyGram, self)        self.tokens = 0         self.types = 0         if iterable:            self.update(iterable)        def update(self, iterable):        if iterable in self:            self[iterable] += 1            self.tokens += 1        else:            self[iterable] = 1            self.tokens += 1            self.types += 1    def count(self, item):        if item in self:            return self[item]        return 0    def return_rand_word(self):        return self.keys()[randint(0, self.types - 1)]    def return_weighted_rand_word(self):            weights = self.create_probability_distribution()        return choices(list(self.keys()), weights)[0]    def create_probability_distribution(self):        occurences = self.values()        distribution = []        total = sum(occurences)        for occurence in occurences:                distribution.append(occurence / total)        return distributionclass Gen(markov_model):    def get_data(path):        with open(path) as file:            data = file.read()        file.close()        return data    def split_into_sentences(text):        text = " " + text + " "        text = text.replace("\n","  ").replace("\r", " ")        text = re.sub(' +',' ',text)        text = re.sub(PREFIXES,"\\1<prd>",text)        text = re.sub(WEBSITES,"<prd>\\1",text)        if "Ph.D" in text: text = text.replace("Ph.D.","Ph<prd>D<prd>")        text = re.sub("\s" + ALPHABETS + "[.] "," \\1<prd>\\n ",text)        text = re.sub(ACRONYMS+" "+STARTERS,"\\1<stop> \\2",text)        text = re.sub(ALPHABETS + "[.] " + ALPHABETS + "[.] " + ALPHABETS + "[.] ","\\1<prd>\\2<prd>\\3<prd>",text)        text = re.sub(ALPHABETS + "[.] " + ALPHABETS + "[.] ","\\1<prd>\\2<prd>",text)        text = re.sub(" "+SUFFIXES+"[.] "+STARTERS," \\1<stop> \\2",text)        text = re.sub(" "+SUFFIXES+"[.] "," \\1<prd>",text)        text = re.sub(" " + ALPHABETS + "[.] "," \\1<prd>",text)        if "'" in text: text = text.replace("'\'","\''")        if "”" in text: text = text.replace(".”","”.")        if "\"" in text: text = text.replace(".\"","\".")        if "!" in text: text = text.replace("!\"","\"!")        if "?" in text: text = text.replace("?\"","\"?")        if "," in text: text = text.replace(",\"","\",")        if ";" in text: text = text.replace(";\"","\";")        if ":" in text: text = text.replace(":\"","\":")        text = text.replace(",",",<stop>")        text = text.replace(";",";<stop>")        text = text.replace(":",":<stop>")        text = text.replace(".",".<stop>")        text = text.replace("?","?<stop>")        text = text.replace("!","!<stop>")        text = text.replace("<prd>",".")         sentences = text.split("<stop>")        sentences = sentences[:-1]        sentences = [s.strip() for s in sentences]        for i in range(0, len(sentences)):            sentences[i] = re.findall(r"[\w']+|[.,!?;]", sentences[i])                return sentences    def make_markov_model(corpus):        markov_model = dict()        corpus_size = 0        for sentence in corpus:            if "START" in markov_model:                markov_model["START"].update(sentence[0])            else:                markov_model["START"] = FrequencyGram(sentence[0])            if sentence[-1] in markov_model:                 markov_model[sentence[-1]].update("END")            else:                markov_model[sentence[-1]] = FrequencyGram("END")            corpus_size += len(sentence)            for i in range(0, len(sentence)-1):                 if sentence[i] in markov_model: markov_model[sentence[i]].update(sentence[i+1])                else:                    markov_model[sentence[i]] = FrequencyGram(sentence[i+1])        markov_model["END"] = FrequencyGram("START")         print("Corpus: {0} words".format(corpus_size))##PPL        return markov_model    def existing_model():        return os.path.isfile(MODEL_NAME)            def load_model():        with open('model.pkl', 'rb') as f:            markov_model = pickle.load(f)        return markov_model        def load_data(file_path):        if isinstance(file_path, list):            for path in file_path:                corpus = []                raw_data = get_data(path)                corpus += split_into_sentences(raw_data)                markov_model = make_markov_model(corpus)        else:            raw_data = get_data(file_path)            corpus = split_into_sentences(raw_data)            markov_model = make_markov_model(corpus)        return markov_model        def generate_random_start(markov_model):        sentence_starter = markov_model["START"].return_weighted_rand_word()        return sentence_starter        def generate_n_length_sentence(length, markov_model):        sentence=["" for x in range(length)]        start_word = generate_random_start(markov_model)        for i in range(0, len(sentence[::4])-1):            if start_word =="START" or start_word =="END":continue            elif start_word not in PUNCS:                current_frequencygram=markov_model[start_word]                current_word=current_frequencygram.return_weighted_rand_word()            if current_word =="START" or current_word =="END":continue            elif current_word not in PUNCS:                sentence[i]+= current_word+' '                 current_frequencygram=markov_model[current_word]                next_word=current_frequencygram.return_weighted_rand_word()            if next_word =="START" or current_word =="END":continue            elif next_word not in PUNCS:                current_word=next_word                sentence[i]+= current_word+' '                 current_frequencygram=markov_model[next_word]                next_after=current_frequencygram.return_weighted_rand_word()            if next_after =="START" or next_after =="END":continue            elif next_after not in PUNCS:                current_word=next_after                sentence[i]+= current_word+' '                 current_frequencygram=markov_model[next_after]                word_after=current_frequencygram.return_weighted_rand_word()            if word_after =="START" or word_after =="END":continue            elif word_after not in PUNCS:                current_word=word_after                sentence[i]+= current_word+' '                current_frequencygram=markov_model[word_after]                current_after=current_frequencygram.return_weighted_rand_word()            if current_after =="START" or current_after =="END":continue            elif current_after not in PUNCS:                current_word=current_after                sentence[i]+= current_word+' '                 current_frequencygram=markov_model[current_after]                next2_last = current_frequencygram.return_weighted_rand_word()             if next2_last =="START" or next2_last =="END":continue            elif next2_last not in PUNCS:                current_word=next2_last                sentence[i]+= current_word+' '                current_frequencygram=markov_model[next2_last]                last_word = current_frequencygram.return_weighted_rand_word()            if last_word =="START" or last_word =="END":continue            elif last_word not in PUNCS:                current_word=last_word                sentence[i]+= current_word+' '        print("".join(sentence))        def generate_n_sentences(length, markov_model):        sentences = ["" for x in range(length)]        current_word = generate_random_start(markov_model)        current_frequencygram = markov_model[current_word]        for i in range(0, length):                    next_word = current_frequencygram.return_weighted_rand_word()            if next_word == "END":continue            current_word = next_word            if current_word not in PUNCS:                sentences[i] += " " + current_word            else:                sentences[i] += current_word        print(" ".join(sentences))class Scraper:    from bs4 import BeautifulSoup    from js import document    from pyodide.http import open_url        #Use the follow to get another page's content synchronously;otherwise we will use the current page    #page_html = open_url('hello_world.html')        page_html = document.documentElement.innerHTML    soup = BeautifulSoup(page_html, 'html.parser')        def print_self_and_children(tag, indent = 0):        print("_" * indent + str(tag.name))        if hasattr(tag, 'children'):            for child in tag.children:                if hasattr(child, 'name') and child.name is not None: print_self_and_children(child, indent = indent + 2)        print_self_and_children(soup)