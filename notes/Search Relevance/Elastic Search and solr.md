# Search Relevance: Elasticsearch and Solr

Search relevance is a key to modern digital infrastructure.

Relevance is the practice of improving search results for users by satisfying their information needs in the context of a particular user experience while balancing how ranking impacts our business needs.

## Solve Relevance

- Identify salient features describing the content, the user, and the query.
- Find ways to tell the search engine about those features through extraction and enrichment.
- At search time, measure what is relevant to a user's search by crafting signals.
- Carefully balance the influence of multiple signals to rank results by manipulating the ranking functions.

## Search Under the Hood

During analysis:

```
documents -> original text -> tokenization -> indexed -> search engine data structure for document retrieval
```

In addition, original untokenized text fields are stored to show in search results.

### Search Engine Data Structure

The **inverted index** is like the physical index in the back of a book. It is composed of two main pieces: the dictionary and the postings list.

- **Term dictionary** -> the sorted list of terms occurring in the given field across a set of documents

```
documents       Dictionary        Postings list
0 ...           words -> term     term -> list of documents
1 ...
2 ...
```

### Other Data Structures in Lucene Along with the Inverted Index

- **Doc frequency** -> a count of documents that contain a particular term, or the length of the postings associated with a particular term
- **Term frequency** -> number of times a term occurs in a particular document
- **Term positions** -> word position in the doc
- **Term offsets** -> highlight positions of words in the doc by keeping track of the start and end positions of the terms during indexing
- **Payloads** -> each term can carry arbitrary data, like relevancy scoring
- **Stored fields** -> any fields to be presented to the user must be saved in stored fields
- **Doc values** -> incorporate auxiliary values into relevance heuristics

### Indexing Content: Extraction, Enrichment, Analysis, and Indexing

```
Source -> Extraction -> Documents
       -> Enrichment -> added information useful for relevance
       -> Analysis   -> converts document data into tokens that enable matching
       -> Indexing   -> placing data into data structures
```

Analysis has overriding importance to search relevance. Analysis transforms raw text from documents into tokens; these tokens represent document features. Engineering to match these features from a user query is critical to satisfying the user's information needs. Extraction and enrichment are general; indexing concerns us only insofar as it pertains to enabling and disabling features.

#### Components of Analysis

Three steps:

1. Character filtering
2. Tokenization
3. Token filtering

#### Document Search and Retrieval

Lucene has Boolean queries: SHOULD, MUST, and MUST_NOT.

- A clause of type MUST has to have a match inside a document; otherwise, the document isn't considered a match.
- A clause of type SHOULD might or might not have a match in a given document, but documents that do have SHOULD clause matches are ranked higher than those that don't.
- Any document that contains a match for a MUST_NOT clause won't be considered a match for the search results, even if it does match a MUST or a SHOULD clause.

Elasticsearch and Solr use this syntax to provide query debug information. In Lucene query syntax, the MUST and MUST_NOT queries are preceded by a prefix: the MUST clause is preceded by a `+`, and the MUST_NOT clause is preceded by a `-`. The SHOULD clause isn't prefixed.

Consider a simple query and a set of documents:

Query: `black +cat -dog`

Documents:
- (a) my cat ran under the couch
- (b) black cats are mysterious
- (c) the dog scared the black cat

The ranking function determines the relevance of the results, based on term frequency, doc frequency (how common the term is), and how many terms the field contains.

## Debugging the First Relevance Problem

Take the movie database TMDB. When searching movies, attributes include:

- Prose text (synopsis and user reviews)
- Shorter text (director, actor names, and titles)
- Numerical attributes (ratings, revenue)
- Movie release dates

All operations - indexing and query validation - use Query DSL (query domain-specific language).

Use Lucene's internal vector multiplication model for scoring vectors of documents vs. queries.

Lucene's classic similarity measure:

```
TFWeighted = sqrt(tf)
IDFWeighted = log(numDocs / (df + 1)) + 1
fieldnorm = (1 / sqrt(fieldlength))
Similarity score = TFWeighted * IDFWeighted * Fieldnorm
```

BM25 is the advanced similarity measure and is the default.

### Key Takeaways

- Not getting the expected search results requires debugging matching and ranking.
- To debug matching, examine how your search engine interprets and executes your query; with Elasticsearch, this corresponds to the query validation endpoint.
- Search engines require exacting, byte-for-byte term matching to include a document in the search results.
- Search engines need your help to determine which matches to include/omit (such as stop words) by choosing an appropriate analyzer.
- Search engines use TF x IDF scoring to rank results. You can see the scoring by using your search engine's relevance explain output.
- TF measures the term's importance in the document's text. IDF determines the rareness/specialness of a term across the whole corpus. Field norms (norms) bias scoring toward shorter text.
- Debugging search engine ranking requires understanding fieldWeight (how important search terms are in the text) and queryWeight (how important search terms are in the search query).
- Relevance scores aren't easily compared, nor are they normalized. A poor score for a title field may be 10.0; a good search score for the overview field may be 0.01.
- Boost factors aren't field priorities. Instead, they let you rebalance relevance scoring. When scoring is balanced, you can prioritize one field or another.

## Taming Tokens

With feature modeling, you take into consideration the user's intent as well as the ideas conveyed in documents. Creation of tokens - and thus creation of features - happens for both the query and the documents. When analysis is done right, it extracts the meaning of a document beyond the words. Analyze with intent + meaning in mind => improves search relevance.

### Precision and Recall

- **Precision** -> percentage of documents in the result set that are relevant
- **Recall** -> the percentage of relevant documents that are returned in the result set

A search engine is nothing more than a sophisticated token-matching system and document-ranking system.

### Analysis Strategies

- Delimiters - preserve_original
- Phone numbers: last 10 digits filter / last 7 digits type tokens. A user's search for `800.867.5309` would get tokenized as `8008675309`, `8675309`
- Capturing meaning with synonyms
- Modeling specificity in search

## BM25 Algorithm

It is the default in Lucene/Elasticsearch.

### Saturating Term Frequency

```
f * (k1 + 1)
------------
f + k1
```

### Normalizing Document Length

```
f * (k1 + 1)
----------------------------------------
f + k1 * (1 - b + b * (|D| / avgdl))
```

BM25(D, Q) = sum over each query term qi of:

```
                  [ f(qi, D) * (k1 + 1) ]
IDF(qi) * ------------------------------------------------
                  [ f(qi, D) + k1 * (1 - b + b * |D| / avgdl) ]
```

Score(D, Q) = sum of all query terms' relevance scores:

```
IDF * TF * document length normalizer
```

- IDF = ln((N - n(qi) + 0.5) / (n(qi) + 0.5)) + 1
- Term frequency = f(qi, D) * (k1 + 1) / (f(qi, D) + k1)
- Document length normalizer = 1 / (1 - b + b * (|D| / avgdl))

### Cleverness of BM25 and Its Precursors

We've just gone through the components of the BM25 equation, but it's worth pausing to emphasize two of its most ingenious aspects.

#### Ranking by Probability Without Calculating Probability

As mentioned earlier, BM25 is based on an idea called the Probability Ranking Principle. In short, it says:

> If retrieved documents are ordered by decreasing probability of relevance on the data available, then the system's effectiveness is the best that can be obtained for the data.

The Probabilistic Relevance Framework: BM25 and Beyond.