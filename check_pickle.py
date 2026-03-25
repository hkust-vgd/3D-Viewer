import pickle

with open(".\\predictions_\\vggt_predictions_0_torch_free.pkl", "rb") as f:
    obj = pickle.load(f)

print(type(obj))      # e.g., <class 'dict'>
print(obj.keys() if isinstance(obj, dict) else len(obj))