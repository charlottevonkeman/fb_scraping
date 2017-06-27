import sys
reload(sys)
sys.setdefaultencoding("utf-8")
import json
import time
import pandas as pd
import nltk
from nltk.corpus import stopwords
from nltk.stem.wordnet import WordNetLemmatizer
import string
import glob
import os
import gensim
from gensim import corpora
from nltk import pos_tag, word_tokenize
import csv
import datetime
from nltk.probability import FreqDist

def read_status(fbid):
	"""
	INPUT: None
	OUTPUT: pandas data frame from file
	"""
	return pd.read_csv("%s_facebook_statuses.csv" %fbid)

def read_comments(fbid):

	return pd.read_csv("%s_facebook_comments.csv" %fbid)


def filter_date (start_date, end_date, df, c_name):

	df[c_name] = pd.to_datetime(df[c_name])  
	mask = (df[c_name] > start_date) & (df[c_name] <= end_date)
	df = df.loc[mask]

	return df

def filter_language (df):
	df['lang'] = ''
	df['prob'] = ''

	for index, row in df.iterrows():
		df['lang'][index], df['prob'][index] = langid.classify(row['text'])

	return df[df.lang == 'en']

def topic_detection(df_column):
	stop = set(stopwords.words('english'))
	exclude = set(string.punctuation) 
	lemma = WordNetLemmatizer()

	def clean(doc):
		stop_free = " ".join([i for i in str(doc).lower().split() if i not in stop])
		punc_free = ''.join(ch for ch in stop_free if ch not in exclude)
		normalized = " ".join(lemma.lemmatize(word) for word in punc_free.decode('utf-8').split())
		return normalized

	reviews_clean = [clean(reviews).split() for reviews in df_column]

	# Creating the term dictionary of our courpus, where every unique term is assigned an index. 
	dictionary = corpora.Dictionary(reviews_clean)

	# Converting list of documents (corpus) into Document Term Matrix using dictionary prepared above.
	doc_term_matrix = [dictionary.doc2bow(review) for review in reviews_clean]

	# Creating the object for LDA model using gensim library
	Lda = gensim.models.ldamodel.LdaModel

	# Running and Trainign LDA model on the document term matrix.
	ldamodel = Lda(doc_term_matrix, num_topics=5, id2word = dictionary, passes=50)

	return ldamodel.print_topics(num_topics=5, num_words=5)

def most_engaging_content(df_status):

	df_status['engagement'] = df_status['num_reactions'] + df_status['num_comments'] + df_status['num_shares']
	i = pd.Index(df_status["engagement"]).get_loc(df_status.engagement.max())

	return df_status["status_message"][i]


def freq_words(df_comments):
	fdist1 = FreqDist(df_comments['comment_message'])
	fdist1.most_common(10) 

	return fdist1.most_common(10) 

def replies(df_comments):
	return df_comments.parent_id.count()

def avg_com_len (df_comments):
	text = df_comments['comment_message']
	df_comments['com_len'] = [len(word_tokenize(str(sent).decode('utf-8'))) for sent in text]
	
	return df_comments['com_len'].mean()

def super_users(df_comments):
	superusers = df_comments['comment_author'].value_counts()
	return superusers[:5]

def run_analysis(fbid, start_date, end_date): 

	df_status = filter_date(start_date, end_date, read_status(fbid), "status_published")
	print "Done importing statuses."

	num_status = df_status['status_id'].count()

	status_topics = topic_detection(df_status['status_message'])
	print "Done topic detection on statuses."

	df_comments = filter_date(start_date, end_date, read_comments(fbid), "comment_published")
	print "Done importing comments."

	print "Calculating engagement."
	df_status['engagement'] = df_status['num_reactions'] + df_status['num_comments'] + df_status['num_shares']
	print "Calculating daily engagement."
	start = datetime.datetime.strptime(start_date, "%Y-%m-%d")
	end = datetime.datetime.strptime(end_date, "%Y-%m-%d")
	eng = df_status['engagement'].sum()/(end-start).days
	frequent_words = freq_words(df_comments)
	print "Done analyzing frequent adjectives"
	num_discussion = replies(df_comments)
	print "Done analyzing number of discussions."

	comments_topics = topic_detection(df_comments['comment_message'])
	print "Done topic detection in comments"

	avg_comment_len = avg_com_len(df_comments)
	print "Done analyzing average comments length"
	superusers = super_users(df_comments)
	print "Done analyzing superusers"

	time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
	period = str(start_date) + " - " + str(end_date)

	with open('%s_facebook_analysis.csv' % fbid, 'wb') as file:
		print "Opening new files to write."
		w = csv.writer(file)
		w.writerow(["fb_id","time_of_analysis", "period_selected", "num_of_status", "daily_engagement", 
			"frequently_used_words", "number_of_discussion", "superusers", "avg_comment_len", "status_topics", "comments_topics"])
		w.writerow([fbid, time, period, num_status, eng,
			frequent_words, num_discussion, superusers, avg_comment_len, status_topics, comments_topics])


if __name__ == "__main__":
	run_analysis(fbid, start_date, end_date)