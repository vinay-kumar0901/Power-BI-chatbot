"""Per-dashboard retrieval. Prefer Ollama semantic embeddings; fall back to TF-IDF."""
import os, requests, numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from .config import OLLAMA_URL, RAG_MODE, OLLAMA_REQUEST_TIMEOUT, OLLAMA_CONNECT_TIMEOUT

class DashboardRAG:
    def __init__(self, docs):
        self.docs=docs or []; self.mode='none'; self.vectors=None
        self.vectorizer=None; self.matrix=None
        if not self.docs: return
        self.embed_model=os.getenv('OLLAMA_EMBED_MODEL','nomic-embed-text')
        # TF-IDF is the reliable default for Colab. It avoids a second Ollama call
        # and prevents embedding timeouts from blocking the first chat response.
        if RAG_MODE == 'ollama':
            try:
                vectors=self._ollama_embed([d['text'][:6000] for d in self.docs])
                self.vectors=self._normalize(vectors); self.mode='ollama-embeddings'
            except Exception:
                self._build_tfidf()
        else:
            self._build_tfidf()

    def _build_tfidf(self):
        self.vectorizer=TfidfVectorizer(ngram_range=(1,2),stop_words='english',max_features=30000)
        try:
            self.matrix=self.vectorizer.fit_transform([d['text'][:16000] for d in self.docs]); self.mode='tfidf'
        except ValueError:
            self.matrix=None; self.mode='empty'
    def _ollama_embed(self,texts):
        r=requests.post(f'{OLLAMA_URL}/api/embed',json={'model':self.embed_model,'input':texts},timeout=(OLLAMA_CONNECT_TIMEOUT, min(OLLAMA_REQUEST_TIMEOUT,300)))
        r.raise_for_status(); data=r.json().get('embeddings')
        if not data: raise RuntimeError('Ollama returned no embeddings')
        return np.asarray(data,dtype='float32')
    @staticmethod
    def _normalize(v):
        norms=np.linalg.norm(v,axis=1,keepdims=True); return v/np.maximum(norms,1e-12)
    def retrieve(self,q,k=6):
        if self.mode=='ollama-embeddings':
            try:
                qv=self._normalize(self._ollama_embed([q]))[0]
                scores=self.vectors @ qv
            except Exception: scores=None
        else: scores=None
        if scores is None:
            if self.matrix is None:return []
            scores=cosine_similarity(self.vectorizer.transform([q]),self.matrix)[0]
        ids=np.argsort(scores)[::-1][:k]
        return [{'source':self.docs[i]['source'],'text':self.docs[i]['text'][:6000],'score':float(scores[i])} for i in ids if scores[i]>0]
