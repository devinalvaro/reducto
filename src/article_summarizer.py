from operator import itemgetter

from tf_idf import term_frequency as tf, inverse_document_frequency as idf
from tokenizer import tokenize_word, tokenize_sentence


class ArticleSummarizer:
    """Summarize an article

    Rank sentences in the article with tf-idf scoring algorithm.
    """

    __sentence_scores = []
    __word_frequency = {}

    def __init__(self, article, document_number, document_frequency):
        """ Inits ArticleSummarizer

        Tokenize the article into sentences and words.
        Count term frequency and document frequency of each word.
        Score each sentence with tf-idf.
        Weigh each sentence relative to its position.
        Rank the sentences by the score in decreasing order.

        Args:
            article: A string of article text.
            document_number: Number of documents in dataset.
            document_frequency: Frequency of a word in documents dataset, i.e.
                 if a document has word, document_frequency[word] increase by 1.
        """

        self.sentences = tokenize_sentence(article)
        self.document_number = document_number + 1
        self.document_frequency = document_frequency

        word_set = set()

        for sentence in self.sentences:
            words = tokenize_word(sentence, only_noun=True)
            for word in words:
                if word not in self.__word_frequency:
                    self.__word_frequency[word] = 1
                else:
                    self.__word_frequency[word] += 1

                word_set.add(word)

        for word in word_set:
            if word not in self.document_frequency:
                self.document_frequency[word] = 1
            else:
                self.document_frequency[word] += 1

        for sentence in self.sentences:
            self.__sentence_scores.append(
                [self.__sentence_score(sentence), sentence])

        self.__weigh_sentences_by_position()

        self.__sentence_scores = sorted(
            self.__sentence_scores, key=itemgetter(0), reverse=True)
        self.ranked_sentences = [
            sentence[1] for sentence in self.__sentence_scores
        ]

    def __sentence_score(self, sentence):
        # return a sentence's average tf-idf score

        words = tokenize_word(sentence, only_noun=True)

        if not words:
            return 0

        total = 0
        for word in words:
            total += self.__word_score(word)

        return total / len(words)

    def __word_score(self, word):
        # return a word's tf-idf score

        return tf(word, self.__word_frequency) * idf(word, self.document_number,
                                                   self.document_frequency)

    def __weigh_sentences_by_position(self):
        # weigh each sentence relative to its position.

        # weight values are taken from a paper by Yohei Seki
        # http://research.nii.ac.jp/ntcir/workshop/OnlineProceedings3/NTCIR3-TSC-SekiY.pdf

        for index, __sentence_score in enumerate(self.__sentence_scores):
            distribution = index / len(self.__sentence_scores)

            if 0 <= distribution and distribution < 0.1:
                weight = 0.17
            elif 0.1 <= distribution and distribution < 0.2:
                weight = 0.23
            elif 0.2 <= distribution and distribution < 0.3:
                weight = 0.14
            elif 0.3 <= distribution and distribution < 0.4:
                weight = 0.08
            elif 0.4 <= distribution and distribution < 0.5:
                weight = 0.05
            elif 0.5 <= distribution and distribution < 0.6:
                weight = 0.04
            elif 0.6 <= distribution and distribution < 0.7:
                weight = 0.06
            elif 0.7 <= distribution and distribution < 0.8:
                weight = 0.04
            elif 0.8 <= distribution and distribution < 0.9:
                weight = 0.04
            else:
                weight = 0.15

            __sentence_score[0] *= weight

    def get_top_sentences(self, percentage):
        """Return top n% of the ranked sentences

        Args:
            percentage: A float representing the percentage, e.g. 56.8.

        Returns:
            A list of top n% sentences.
        """

        n = int(percentage / 100 * len(self.sentences))
        top_n_sentences = [
            sentence for sentence in self.sentences
            if sentence in self.ranked_sentences[0:n]
        ]

        return top_n_sentences
