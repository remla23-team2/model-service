import pandas as pd

def get_dataset(filename):
    dataset = pd.read_csv('data/input/a1_RestaurantReviews_HistoricDump.tsv', delimiter='\t', quoting=3)
    return dataset