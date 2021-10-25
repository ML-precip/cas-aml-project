from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.metrics import precision_score, recall_score, roc_auc_score, roc_curve
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os

def split_data(df, yy_train, yy_test, attributes, ylabel):
    """"Split the data into train and test
         df is the data\n",
         attributes are the covariates,
         ylabel is the target variable"""
    train_dataset = df[(df.date.dt.year >= yy_train[0]) & (df.date.dt.year <= yy_train[1])]
    test_dataset = df[(df.date.dt.year >= yy_test[0]) & (df.date.dt.year <= yy_test[1])]
    # extract the dates for each datasets
    train_dates = train_dataset['date']
    test_dates = test_dataset['date']
    # extract labels
    train_labels = train_dataset[ylabel].copy()
    test_labels = test_dataset[ylabel].copy()
    # extract predictors\n",
    train_dataset = train_dataset[attributes]
    test_dataset = test_dataset[attributes]

    return(train_dataset, train_labels, test_dataset, test_labels, train_dates, test_dates)


def create_pipeline(data, cat_var):
    """Prepare the data in the right format for the model"""

    num_attribs = list(data)
    num_pipeline = Pipeline([
        ('imputer', SimpleImputer(strategy="median")),
        ('std_scaler', StandardScaler()),
    ])

    if (cat_var != None):
        num_attribs.remove(cat_var)
        cat_attribs = [cat_var]
        full_pipeline = ColumnTransformer([
            ("num", num_pipeline, num_attribs),
            ("cat", OneHotEncoder(), cat_attribs),
        ])
    else:
        full_pipeline = ColumnTransformer([
            ("num", num_pipeline, num_attribs),
        ])

    return(full_pipeline)





def evaluate_model(test_labels, train_labels, predictions, probs, train_predictions, train_probs):
    """Compare machine learning model to baseline performance.
    Computes statistics and shows ROC curve."""
    
    baseline = {}
    
    baseline['recall'] = recall_score(test_labels, [1 for _ in range(len(test_labels))])
    baseline['precision'] = precision_score(test_labels, [1 for _ in range(len(test_labels))])
    baseline['roc'] = 0.5
    
    results = {}
    
    results['recall'] = recall_score(test_labels, predictions)
    results['precision'] = precision_score(test_labels, predictions)
    results['roc'] = roc_auc_score(test_labels, probs)
    
    train_results = {}
    train_results['recall'] = recall_score(train_labels, train_predictions)
    train_results['precision'] = precision_score(train_labels, train_predictions)
    train_results['roc'] = roc_auc_score(train_labels, train_probs)
    
    for metric in ['recall', 'precision', 'roc']:
        print(f'{metric.capitalize()} Baseline: {round(baseline[metric], 2)} Test: {round(results[metric], 2)} Train: {round(train_results[metric], 2)}')
    
    # Calculate false positive rates and true positive rates
    base_fpr, base_tpr, _ = roc_curve(test_labels, [1 for _ in range(len(test_labels))])
    model_fpr, model_tpr, _ = roc_curve(test_labels, probs)

    plt.figure(figsize = (8, 6))
    plt.rcParams['font.size'] = 16
    
    # Plot both curves
    plt.plot(base_fpr, base_tpr, 'b', label = 'baseline')
    plt.plot(model_fpr, model_tpr, 'r', label = 'model')
    plt.legend();
    plt.xlabel('False Positive Rate'); plt.ylabel('True Positive Rate'); plt.title('ROC Curves');



def plotprediction_TS(test_dates, final_predictions, test_labels):
    import seaborn as sns
    df_to_compare = pd.DataFrame({'date': test_dates, 'Actual': test_labels, 'Predicted': final_predictions})
    dfm = pd.melt(df_to_compare, id_vars=['date'], value_vars=['Actual', 'Predicted'], var_name='data', value_name='precip')
    f, axs = plt.subplots(1,2,
                      figsize=(12,5),
                      sharey=True)

    sns.regplot(data= df_to_compare,
                x="Actual",
                y="Predicted",
                ax=axs[0],
                )
    sns.lineplot(x='date', y='precip', hue = 'data', data=dfm, ax=axs[1])

    
    
    
def plot_Importance(features_importance, attributes, IMAGES_PATH):
    indices = np.argsort(features_importance)
    plt.barh(range(len(attributes)), features_importance[indices], color='b', align='center')
    plt.yticks(range(len(indices)), [attributes[i] for i in indices])
    plt.xlabel('Relative Importance')
    save_fig("Rela_Importance", IMAGES_PATH)
    plt.show()
    
    
def save_fig(fig_id,IMAGES_PATH, tight_layout=True, fig_extension="png", resolution=300):
    path = os.path.join(IMAGES_PATH, fig_id + "." + fig_extension)
    print("Saving figure", fig_id)
    if tight_layout:
        plt.tight_layout()
    plt.savefig(path, format=fig_extension, dpi=resolution)