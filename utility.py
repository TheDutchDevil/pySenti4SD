import pandas as pd

from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn import metrics

import os
import sys
import subprocess
import argparse
import shutil

def get_models():
    '''
    Returns a list of all models that are currently present 
    on the local filesystem. For this we list all the filenames 
    in the models folder.
    '''
    
    models = []

    for file in os.listdir("/models"):
        if file.endswith(".model"):
            models.append(file.replace(".model", ""))
    
    print("Model available on the system:")

    for model in models:
        print(f"\t{model}")

 

def train_model(file_path, model_name, predictions_path = None, split = 0.3, random_state = None, text_column = "text", label_column = "label", seperator = "c"):
    '''
    Take a file, converts it to the pysenti4sd format and 
    then calls the pysenti4sd shell to train the model.  

    To train the model, we need the ground truth data, so 
    the format of the file should be id, text, label. 

    If predictions path is not none, then the resulting 
    predictions will be saved to that path, 
    
    split is the fraction in the train/test split and 
    random state is the random state for the train/test split
    '''

    if not Path(file_path).is_file():
        raise ValueError(f"{file_path} is not a valid file")

    if seperator == "c":
        df = pd.read_csv(file_path)
    elif seperator == "sc":
        df = pd.read_csv(file_path, sep=";")
    else:
        raise ValueError(f"Unknown seperator {seperator}")

    # If there is no column named id, we add one with row numbers
    if "id" not in df.columns:
        df["id"] = df.index

    df["text"] = df[text_column].apply(lambda x: x.replace("\n", " "))
    df["label"] = df[label_column]

    train_X, test_X, train_y, test_y = train_test_split(df[['text', 'id']], df['label'].values, test_size=split, random_state=random_state)

    df_train = pd.DataFrame(train_X)
    df_test = pd.DataFrame(test_X)

    df_train["polarity"] = train_y
    df_test["polarity"] = test_y

    df_train.to_csv(f"train.csv", index=False)
    df_test.to_csv(f"test.csv", index=False)

    command = f"bash train.sh -i train.csv -i test.csv -m {model_name}"

    # Path to classification task folder
    print(f"Executing '{command}'")
    
    run_result = subprocess.run(command, text=True, shell=True, stderr=sys.stdout, stdout=sys.stdout)

    run_result.check_returncode()

    # Move the trained model to the models folder
    shutil.move(os.path.join("/app", f"{model_name}.model"), os.path.join("/models", f"{model_name}.model"))
    shutil.move(os.path.join("/app", f"{model_name}.model_le"), os.path.join("/models", f"{model_name}.model_le"))
   


def predict(file, model_name = "Senti4SD", predictions_path = "out.csv", text_column = "text", seperator = "c"):

    if seperator == "c":
        df = pd.read_csv(file)
    elif seperator == "sc":
        df = pd.read_csv(file, sep=";")
    else:
        raise ValueError(f"Unknown seperator {seperator}")

    if "id" not in df.columns:
        df["Id"] = df.index

    df["Text"] = df[text_column].apply(lambda x: x.replace("\n", " "))

    df.to_csv(f"to_run.csv", index=False)

    command = f"bash classification.sh -i to_run.csv -m {model_name}.model -o test_preds.csv"

    run_result = subprocess.run(command, text=True, shell=True, stderr=sys.stdout, stdout=sys.stdout)

    run_result.check_returncode()

    predictions_senti4sd_path = os.path.join("predictions", "test_preds.csv")

    predictions = pd.read_csv(predictions_senti4sd_path)

    df_test = pd.read_csv(file)

    predictions["Text"] = df_test[text_column]
    predictions = predictions.rename(columns={'PREDICTED': 'Prediction', "ID": "Id"})
    
    if predictions_path is not None:
        predictions.to_csv(predictions_path, index=False)
        print(f"Wrote output file to {predictions_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("--train", dest="train", help="", action="store_true")

    parser.add_argument("--list", dest="list", help="", action="store_true")

    parser.add_argument("--predict", dest="predict", help="", action="store_true")

    parser.add_argument("--test-split", dest="test_split", help="", type=float, default=0.3)

    parser.add_argument("--model-name", dest="model_name", help="", type=str)

    parser.add_argument("--input", dest="input", help="", type=str)

    parser.add_argument("--output", dest="output", help="", type=str)

    # The two columns can be used to deal with non-standard dataset files. 

    parser.add_argument("--text-column", dest="text_column", help="", type=str, default="text")

    parser.add_argument("--label-column", dest="label_column", help="", type=str, default="label")

    # We should also take into account that the seperator might be different
    parser.add_argument("--sep", dest="sep", help="Seperator used in .csv, either c for comma or sc for semicolon", type=str, default="c")

    args = parser.parse_args()

    if sum([args.train, args.list, args.predict]) != 1:
        raise ValueError("You must specify either --train, --list or --predict")

    if args.list:
        get_models()

    if args.train:
        train_model(args.input, args.model_name, predictions_path = args.output, text_column=args.text_column, label_column=args.label_column, split=args.test_split, seperator=args.sep)

    if args.predict:
        predict(args.input, model_name = args.model_name, predictions_path = args.output, text_column=args.text_column, seperator=args.sep)



