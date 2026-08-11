

Search relevance is a key to modern digital infrastructure
 
Relevance is the  practice of improving search results for users by satisfying their information needs in the context of a praticular user experience while balancing how ranking impacts our business needs

Solve relevance:
 - identify salient features describing the content , the user and query,
 - find ways to tell the search engine about those features through extraction and enrichment
 - At search time measure waht's relevant to a user's search by crafting signals
 - carefully balances the influence of multiple signals to rank results by manipulating the ranking functions


 ## Search Under the hood
  during analysis 
 documenrs -> orginal text -> tokensization
 -> indexed -> search engine datastructure for document retrieval
 In additio original untokenzied text fields are stored to show in search results

 ### Search engine Data structure 
     Inverted Index  ~ physical index in back of the book
     Inverted iNdex composed of two main pieces dictionary and postings list
     term dictionart -> the sorted list of terms occur in the given field across a set of documets

    documents
    0 ....
    1 ...
    2...

    Dictionary 
    words -> term 

    postings list 
    term -> list of documents 

### Other Data structures in Lucene along with Inverted Index 
    Doc Frequency -> A count of Documents that contain a particulat term or length of postings associated with a particular term 
    Term Frequency -> NUmber of times a terms occur in a particular document.
    Term positions -> word position in the doc
    Term offsets   -> highlightes position of words in the doc by keeping track of start and end position of the terms during indexing
    Payloads    -> Each term -> arbitrary data leike relevancy scoiring 
    Stored fields -> Any fields are to be presents to user must be saved in stored fields.
    Doc Values -> incorporate auxillary values into relevenacy heuristic
    
###INdexing content:Extraction, Enrichment analysis and indexing
   Source -- Extraction --> Documents 
          -- Enrichment --> added information useful for relevance 
         -- analysis --> converts documents data into tokens that enable matching 
         -- indexing --> placiing data into data structures 
 Analysis has overiding importance to search relevance 
 Analysis transforms raw text and from documents into tokens  these tokens represent document features
Engineering to match these features from a user query is critical to satisfy user's information needs 
Extarction and enrichment are general
indexing concerns us to only pertain to enable and disabling features 

#### Component of Analysis
        three steps 
            - Character filtering
             - Tokenization 
             - Token filtering
####Document Search and retrieval
        Lucene has Boolean queru SHOULD , MUST and MUST_NOT 
            A clause of type MUST has to have a match inside a document; otherwise, the
            document isn’t considered a match.
            ■
            A clause of type SHOULD might or might not have a match in a given docu-
            ment, but documents that do have SHOULD clause matches are ranked higher
            than those that don’t.
            ■
            Any document that contains a match for a MUST_NOT clause won’t be con-
            sidered a match for the search results even if it does match a MUST or a
            SHOULD clause.

 Elasticsearch and Solr use this syntax to provide query
debug information, and we refer to this debug information throughout the book. In
Lucene query syntax, the MUST and MUST_NOT queries are preceded by a prefix.
The MUST clause is preceded by a +, and the MUST_NOT clause is preceded by a -.
The SHOULD clause isn’t prefixed. Consider a simple query and a set of documents:
Query:
black +cat –dog
Documents:
(a) my cat ran under the couch
(b) black cats are mysterious
(c) the dog scared the black cat

Ranking function determines relavnce of the results 
  -> based on term frequency , doc frequency (how common), how many term the field contaoms 

## Debugging the first relevance problem
  Take the movie database TMDB 
     when searching movies attributes include 
        * Prose Text (synopsis and user reviews)
        * Shorter Text (director, actor names and titles)
        * Numerical Attributes (ratings, revenue )
        * MOvie release dates 

  Alloperations indexing query validation uses Qury DSL
  Query Domain specific lanuguage

  use Lucene intenal vector multiplication model for scoring vector of documents vs queries
  
        Lucenes classic similarity measure 

        TFWeighted = sqrt(tf)
        IDF Weighted = log(numDocs/(df+1)) + 1
        filednorm = (1/sqrt(fieldlength))
        Simularity score = TFweighed * IDF weighted * Fieldnorm


        BM25 is advance simularity score and desfault

        ■
Not getting the expected search results requires debugging matching and ranking.
■
To debug matching, examine how your search engine interprets and executes
your query; with Elasticsearch, this corresponds to the query validation endpoint.
■
Search engines require exacting, byte-for-byte term matching to include a docu-
ment in the search results.
■
Search engines need your help to determine which matches to include/omit
(such as stop words) by choosing an appropriate analyzer.
■
Search engines use TF × IDF scoring to rank results. You can see the scoring by
using your search engine’s relevance explain output.
■
TF measures the term’s importance in the document’s text. IDF determines the
rareness/specialness of a term across the whole corpus. Field norms (norms)
bias scoring toward shorter text.
■
Debugging search engine ranking requires understanding fieldWeight (how
important search terms are in the text) and debugging queryWeight (how impor-
tant search terms are in the search query).
■
Relevance scores aren’t easily compared, nor are they normalized. A poor score
for a title field may be 10.0; a good search score for the overview field may be 0.01.
■
Boost factors aren’t field priorities. Instead, they let you rebalance relevance
scoring. When scoring is balanced, you can prioritize one field or another

## Taming Tokens 
With feature modeling you take into consideration of users intent as well as the ideas conveyed in documents.
Creation of tokens and thus creation of features happens to both the query and to the documents
when analysis done right it extracts the meaning of a documnet beyond the words 
analyse with intent + meaning in mind => improves search relavance
### Precision and recall
   - prcision -> percentage of documents in the result set that are relavnce 
   - Recall -? The precentage of relevant documents that are returned in the result set 

   A search engine is nothing more than a sophisticated token-matching
system and document-ranking system

Analysis Strategies :
  - > Delimiters - preserve_original
  -> Phone numbers last 10 digits filter / last 7 digits  type tokens 
    a user’s search for “800.867.5309” would get tokenized
as 8008675309,8675309 

  -> Capturing meaning with synonyms
  -> Modeling specificity in search

# BM25 Algorithm
  It is default in lucene/elastic search

 ## Saturating term Frequency 
    f * (k1 + 1)
    ---------
    f + k1

## Normalizing Document Length    
   f * (k1 + 1)
──────────────────────────────────────────────────
f + k1 * (1 - b + b * (|D| / avgdl))

BM25(D, Q) = sum over each query term qi of:

            [ f(qi, D) * (k1 + 1) ]
IDF(qi) * ------------------------------------------------- 
            [ f(qi, D) + k1 * (1 - b + b * |D| / avgdl) ]


  Score(D,Q) = Sum of all query terms relevance score of 

   ( IDF*TF* Document length normailzer)

   IDF = ln( (N-n(qi) + 0.5 /n(qi)+0.5 ) + 1)

    Term Frequency = f(qi, D).(k1+1) /(f(qi,D) + k1)
    
    Document length normailzer = 1/(1-b+b.(|D| / avgdl)

    Cleverness of BM25 and its precursors
We've just gone through the components of the BM25 equation, but I think it's worth pausing to emphasize two of its most ingenious aspects.

Ranking by probability without calculating probability
As mentioned earlier, BM25 is based on an idea called the Probability Ranking Principle. In short, it says:

If retrieved documents are ordered by decreasing probability of relevance on the data available, then the system’s effectiveness is the best that can be obtained for the data.

The Probabilistic Relevance Framework: BM25 and Beyond
