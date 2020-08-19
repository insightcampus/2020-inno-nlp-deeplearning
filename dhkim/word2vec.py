import numpy as np
from collections import defaultdict
import matplotlib 

class OneHotEncoder():
    def __init__(self, tokenized_docs):
        self.w2i = defaultdict(lambda : len(self.w2i))      # 단어추가 될때마다 단어 인덱스부여
        [self.w2i[w] for d in tokenized_docs for w in d]
        self.i2w = {v : k for k, v in self.w2i.items()}
        self.n_word = len(self.w2i)
      

    def encode(self, tokenized_docs) :# 원핫인코딩 학습
        ret = []
        for d in tokenized_docs:
            for w in d :
                ret.append(self.get_onehot_vector(w))
        return ret        

    def get_onehot_vector(self,w): # 단어 -> 벡터
        v = [0] * len(self.w2i)
        v[self.w2i[w]] = 1
        return v

    def decode(self, v) : # 벡터 -> 단어
        pass

class Word2Vec():
    def __init__(self, docs, embedding_size, window = 1 ,learning_rate = 0.1, epoch = 100):
        # 받은 파라미터 변수에 저장
        self.docs = docs
        self.embedding_size = embedding_size
        self.window = window
        self.learning_rate = learning_rate
        self.epoch = epoch  

        self.tokenized_docs = [d.split() for d in docs]
        self.enc = OneHotEncoder(self.tokenized_docs)
        encoded_docs = self.enc.encode(self.tokenized_docs)

        W = self._init_weights(self.enc.n_word) # 아래서 두개를 리턴했는데 하나로 넣으면 리스트 형태로 들어옴
        X, Y = self._slide_window(encoded_docs)
        self._optimize(X, Y, W)

    def _init_weights(self, n_word) :
        W1 = np.random.rand(n_word, self.embedding_size)
        W2 = np.random.rand(n_word, self.embedding_size).T
        # W2 = np.random.rand(self.embedding_size, n_word)
        return W1, W2

    def _slide_window(self, encoded_docs) : 
        context, center = [], []# x,y 를 용도에 따라 다르게 쓰기 때문에 이처럼 설정
        
        for i, w in enumerate(encoded_docs) :
            # window 시작점 s ,끝점 e
            s = max(0, i - self.window) #i - self.window 마이너스가 나올 수 있으므로 0 이상이되게 max를 써줌 
            e = min(len(encoded_docs), i + self.window)


            tmp_context = encoded_docs[s:e+1]
            tmp_center = tmp_context.pop(i-s) # 이부분 다시 
            
            for c in tmp_context:
                center.append(tmp_center)
                context.append(c)


        return np.array(context), np.array(center)


    # feed forward => 인풋-> 히든(단어선택개념)  / 히든 -> 아웃풋(샘플링적용) 과정이 다르므로 두개로 나눠쓸 것 
    def _input_to_hidden(self, X, W):
        return np.dot(X, W)

    def _hidden_to_ouput(self, H, W):
        return self._softmax(np.dot(H, W))

    def _eval_loss(self, Y , Y_hat):
        return -1 / len(Y) * np.sum(Y*np.log(Y_hat))

    def _calc_gradients(self, X ,Y ,Y_hat, H, W2):
        err = Y_hat - Y
        
        dW2 = np.dot(H.T, err)
        dW1 = np.dot(np.dot(W2, err.T), X).T

        return dW1, dW2


    def _softmax(self, O):
        return np.exp(O)/np.sum(np.exp(O))

    def _optimize(self, X, Y, W): # 전체실행
        loss_trace = []

        for e in range(self.epoch):
            H = self._input_to_hidden(X, W[0])
            Y_hat = self._hidden_to_ouput(H, W[1])
            loss = self._eval_loss(Y, Y_hat)
            loss_trace.append(loss)
            gradients = self._calc_gradients(X, Y, Y_hat, H, W[1])
            
            # update weights
            for w, g in zip(W, gradients):
                w += -self.learning_rate * g

        self.WV = W[0]

    def wv(self, w):
        return self.WV[self.enc.w2i[w]]

    def most_similar(self, w, n = 3) : # 가장 유사한거 n 개 출력
        v = self.wv(w)

        np.dot(v, self.WV)

if __name__ == "__main__" :
    docs = ["you will never know until you try"]
    w2v = Word2Vec(docs = docs, embedding_size = 4)
    
    w2v.wv("you")
    w2v.most_similar("you")