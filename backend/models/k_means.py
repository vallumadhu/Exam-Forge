from sklearn.cluster import KMeans
import numpy as np
from models.embedding_model import embeddings

def gen_difference_array(arr):
    diff_arr = [arr[i+1] - arr[i] for i in range(len(arr)-1)]
    diff_arr.append(diff_arr[-1])
    return diff_arr


class K_means:
    def __init__(self,questions:list):
        self.questions = questions
        self.embedded_questions = embeddings(questions)

    def get_clustors(self,start=3,end=10):
        totoal_questions = len(self.questions)
        if end>totoal_questions:
            end = totoal_questions
            if end<start:
                start-=1
        
        intertia = []
        all_labels = []

        for k in range(start,end+1):
            kmeans = KMeans(n_clusters=k,random_state=42)
            kmeans.fit(self.embedded_questions)

            intertia.append(kmeans.inertia_)
            all_labels.append(kmeans.labels_)
        
        diff_arr1 = gen_difference_array(intertia)
        diff_arr2 = gen_difference_array(diff_arr1)
        correct_k_index = np.argmax(diff_arr2)

        labels = all_labels[correct_k_index]
        total_labels = len(set(labels))

        clusters = [[] for _ in range(total_labels)]
        for label,question in zip(labels,self.questions):
            clusters[label].append(question)

        return clusters