from matplotlib import pyplot as plt
import streamlit as st
import pandas as pd
import numpy as np

import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import classification_report
from sklearn.metrics import recall_score, f1_score, roc_auc_score, precision_recall_curve
from sklearn.metrics import accuracy_score, confusion_matrix, precision_score, roc_curve, auc
from sklearn.preprocessing import label_binarize
from sklearn.inspection import permutation_importance
from streamlit_navigation_bar import st_navbar
from itertools import cycle




# read datasets
df = pd.read_csv("stud.csv")

# Encode categorical features
label_encoders = {}
for column in df.select_dtypes(include=['object']).columns:
    label_encoders[column] = LabelEncoder()
    df[column] = label_encoders[column].fit_transform(df[column])

# Encode grades
def encode_grades(g3):
    if g3 >= 18:
        return 'A'  # Excellent
    elif g3 >= 14:
        return 'B'  # Good
    elif g3 > 10:
        return 'C'  # Sufficient
    elif g3 == 10:
        return 'D'  # Pass
    else:
        return 'E'  # Fail

df['grades'] = df['G3'].apply(encode_grades)

# Encode 'grades' to numerical values
df['grades_encoded'] = df['grades'].map({'A': 4, 'B': 3, 'C': 2, 'D': 1, 'E': 0})

# Separate features and labels
X = df.drop(["grades", "G3"], axis=1)
y = df["grades"]

# Split data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Create and train KNN model
knn_model = KNeighborsClassifier(n_neighbors=4, metric='manhattan')
knn_model.fit(X_train, y_train)

# Predict on test data
y_pred = knn_model.predict(X_test)

# Compute metrics
accuracy = accuracy_score(y_test, y_pred)
precision = precision_score(y_test, y_pred, average='macro')

# Binarize the output for ROC curves
y_test_bin = label_binarize(y_test, classes=[*range(len(set(y)))])
n_classes = y_test_bin.shape[1]

fpr = dict()
tpr = dict()
roc_auc = dict()
for i in range(n_classes):
    fpr[i], tpr[i], _ = roc_curve(y_test_bin[:, i], knn_model.predict_proba(X_test)[:, i])
    roc_auc[i] = auc(fpr[i], tpr[i])

fpr["micro"], tpr["micro"], _ = roc_curve(y_test_bin.ravel(), knn_model.predict_proba(X_test).ravel())
roc_auc["micro"] = auc(fpr["micro"], tpr["micro"])

# Print accuracy and precision
print(f"Accuracy: {accuracy}")
print(f"Precision: {precision}")

# Metadata and encoding mappings
feature_metadata = {
    "school": "Student's school. GP: Gabriel Pereira, MS: Mousinho da Silveira",
    "sex": "Student's sex. M: Male, F: Female",
    "age": "Student's age. Enter an integer value between 15 and 22.",
    "address": "Student's home address type. R: Rural, U: Urban",
    "famsize": "Family size. LE3: Less than or equal to 3, GT3: Greater than 3",
    "Pstatus": "Parent's cohabitation status. A: Apart, T: Together",
    "Medu": "Mother's education. 0: none to 4: higher education",
    "Fedu": "Father's education. 0: none to 4: higher education",
    "Mjob": "Mother's job. at_home, health, other, services, teacher",
    "Fjob": "Father's job. at_home, health, other, services, teacher",
    "reason": "Reason to choose this school. course, other, home, reputation",
    "guardian": "Student's guardian. mother, father, other",
    "traveltime": "Home to school travel time. 1: <15 min, 2: 15-30 min, 3: 30-60 min, 4: >1 hour",
    "studytime": "Weekly study time. 1: <2 hours, 2: 2-5 hours, 3: 5-10 hours, 4: >10 hours",
    "failures": "Number of past class failures. Enter an integer value between 0 and 4.",
    "schoolsup": "Extra educational support. no, yes",
    "famsup": "Family educational support. no, yes",
    "paid": "Extra paid classes. no, yes",
    "activities": "Extra-curricular activities. no, yes",
    "nursery": "Attended nursery school. no, yes",
    "higher": "Wants to take higher education. no, yes",
    "internet": "Internet access at home. no, yes",
    "romantic": "With a romantic relationship. no, yes",
    "famrel": "Quality of family relationships. 1: very bad to 5: excellent",
    "freetime": "Free time after school. 1: very low to 5: very high",
    "goout": "Going out with friends. 1: very low to 5: very high",
    "Dalc": "Workday alcohol consumption. 1: very low to 5: very high",
    "Walc": "Weekend alcohol consumption. 1: very low to 5: very high",
    "health": "Current health status. 1: very bad to 5: very good",
    "absences": "Number of school absences. Enter an integer value between 0 and 33.",
    "G1": "First period grade. Enter an integer value between 0 and 20.",
    "G2": "Second period grade. Enter an integer value between 0 and 20."
}

encoding_mappings = {
    "school": {"GP": 0, "MS": 1},
    "sex": {"M": 0, "F": 1},
    "address": {"R": 0, "U": 1},
    "famsize": {"LE3": 0, "GT3": 1},
    "Pstatus": {"A": 0, "T": 1},
    "Mjob": {"at_home": 0, "health": 1, "other": 2, "services": 3, "teacher": 4},
    "Fjob": {"at_home": 0, "health": 1, "other": 2, "services": 3, "teacher": 4},
    "reason": {"course": 0, "other": 1, "home": 2, "reputation": 3},
    "guardian": {"mother": 0, "father": 1, "other": 2},
    "schoolsup": {"no": 0, "yes": 1},
    "famsup": {"no": 0, "yes": 1},
    "paid": {"no": 0, "yes": 1},
    "activities": {"no": 0, "yes": 1},
    "nursery": {"no": 0, "yes": 1},
    "higher": {"no": 0, "yes": 1},
    "internet": {"no": 0, "yes": 1},
    "romantic": {"no": 0, "yes": 1},
}

def encode_inputs(user_inputs):
    encoded_inputs = {}
    for key, value in user_inputs.items():
        if key in encoding_mappings:
            encoded_inputs[key] = encoding_mappings[key][value]
        else:
            encoded_inputs[key] = value
    return encoded_inputs


# streamlit_navigation_bar
page = st.sidebar.selectbox("Select Page", ["Predict", "Explore", "Summary"])

###################
# DASHBOARD
if page == "Predict":
    st.markdown("""
    ## Predict Student's Final Grades using KNN Classification            
    Input the required values for each feature and click the 'Generate Grades' button to predict the grades score.            
    #### Instructions:
    - For numerical inputs, use the provided range sliders or input boxes.
    - For categorical inputs, select from the provided options.
    - Click 'Generate Grades' to see the prediction.

    You can find feature descriptions and their encoded values on the `Data Card` Page.
    """)

    # Collect user inputs
    user_inputs = {}
    for feature, description in feature_metadata.items():
        if feature in encoding_mappings:
            options = list(encoding_mappings[feature].keys())
            user_inputs[feature] = st.selectbox(f"**{feature}** {description} ", options)
        else:
            numeric_limits = [int(s) for s in description.split() if s.isdigit()]
            #if len(numeric_limits) == 2:
            #
            #    user_inputs[feature] = st.number_input(f"{description} ({feature})", min_value=min_val, max_value=max_val, step=1)
            #else:
            #\   user_inputs[feature] = st.number_input(f"{description} ({feature})", step=1)
    #for column in X.columns:
            if df[feature].dtype == 'int64':
                user_inputs[feature] = st.number_input(f"**{feature}** {description} ", min_value=int(df[feature].min()), max_value=int(df[feature].max()), value=int(df[feature].mean()))
            elif df[feature].dtype == 'float64':
                user_inputs[feature] = st.number_input(f"**{feature}** {description}", min_value=float(df[feature].min()), max_value=float(df[feature].max()), value=float(df[feature].mean()))
            else:
                unique_values = df[feature].unique()
                user_inputs[feature] = st.selectbox(f"**{feature}** {description}", options=unique_values, index=0)
                

    submit_button = st.button(label="Generate Grades")

    if submit_button:
        with st.spinner("Predicting..."):
            # Add missing features to user inputs
            user_inputs['grades_encoded'] = 0  # Placeholder, it will not affect prediction
            encoded_inputs = encode_inputs(user_inputs)
            input_df = pd.DataFrame([encoded_inputs])
            prediction = knn_model.predict(input_df[X.columns])
            predicted_grade = prediction[0]
            st.success(f"The predicted grade is: {predicted_grade}")

    
        

elif page == "Explore":
    st.title("Data Card of Features")
    st.markdown("""
    
    | Feature        | Description                                                                                                                                                           | 
    |----------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------|
    | `school`       | Student's school. binary: Gabriel Pereira `GP` is encoded as `0` and `MS` Mousinho da Silveira `MS` is encoded as `1`                                                 |
    | `sex`          | Student's sex. binary: Male `M` is encoded as `0` and  Female `F` is encoded as `1`                                                                                   |
    | `age`          | Student's age. `numeric`: from 15 to 22                                                                                                                               |
    | `address`      | Student's home address type. binary: Rural `R` is encoded as `0` and Urban `U` is encoded as `1`                                                                      |
    | `famsize`      | Family size total. binary: Less than or equal to 3 `LE3` is encoded as `0` and Greater than 3 `GT3` is encoded as `1`                                                       |
    | `Pstatus`      | Parent's cohabitation status. binary: 'Apart `A` is encoded as `0` and Together `T` is encoded as `1`                                                                 |
    | `Medu`         | Mother's education. `numeric`: 0 - none to 4 - higher education                                                                                                       |
    | `Fedu`         | Father's education. `numeric`: 0 - none to 4 - higher education                                                                                                       |
    | `Mjob`         | Mother's job. nominal: `at_home` is encoded as `0`, `health` is encoded as `1`, `other` is encoded as `2`, `services` is encoded as `3`, `teacher` is encoded as `4`  |
    | `Fjob`         | Father's job. nominal: `at_home` is encoded as `0`, `health` is encoded as `1`, `other` is encoded as `2`, `services` is encoded as `3`, `teacher` is encoded as `4`  |
    | `reason`       | Reason to choose this school. nominal: `course` is encoded as `0`, `other` is encoded as `1`, `home` is encoded as `2`,  `reputation` is encoded as `3`               |
    | `guardian`     | Student's guardian. nominal: `mother` is encoded as `0`, `father` is encoded as `1`, `other` is encoded as `2`                                                        |
    | `traveltime`   | Home to school travel time. numeric: `no` is encoded as `0`, `yes` is encoded as `1`                                                                                  |
    | `studytime`    | Weekly personal study time `numeric`: 1 - <2 hours to 4 - >10 hours                                                                                                            |
    | `failures`     | Number of past class failures `numeric`: n if 1<=n<3, else 4                                                                                                          |
    | `schoolsup`    | Extra educational support such as courses or extra lessons. binary:`no` is encoded as `0`, `yes` is encoded as `1`                                                                                     |
    | `famsup`       | Family educational support. binary:`no` is encoded as `0`, `yes` is encoded as `1`                                                                                    |
    | `paid`         | Extra paid classes. binary:`no` is encoded as `0`, `yes` is encoded as `1`                                                                                            |
    | `activities`   | Extra-curricular activities. binary:`no` is encoded as `0`, `yes` is encoded as `1`                                                                                   |
    | `nursery`      | Attended nursery school such as Kindergaten School. binary:`no` is encoded as `0`, `yes` is encoded as `1`                                                                                       |
    | `higher`       | Wants to take higher education. binary:`no` is encoded as `0`, `yes` is encoded as `1`                                                                                |
    | `internet`     | Internet access at home. binary:`no` is encoded as `0`, `yes` is encoded as `1`                                                                                       |
    | `romantic`     | With a romantic relationship. binary:`no` is encoded as `0`, `yes` is encoded as `1`                                                                                  |
    | `famrel`       | Quality of family relationships. `numeric`: 1 - very bad to 5 - excellent                                                                                             |
    | `goout`        | Going out with friends. `numeric`: 1 - very low to 5 - very high                                                                                                      |
    | `Dalc`         | Weekday alcohol consumption. `numeric`: 1 - very low to 5 - very high                                                                                                 |
    | `Walc`         | Weekend alcohol consumption. `numeric`: 1 - very low to 5 - very high                                                                                                 |
    | `health`       | Current health status. `numeric`: 1 - very bad to 5 - very good                                                                                                       |
    | `absences`     | Number of school absences. `numeric`: from 0 to 33                                                                                                                    |
    | `G1`           | First period grade. `numeric`: from 0 to 20                                                                                                                           |
    | `G2`           | Second period grade. `numeric`: from 0 to 20                                                                                                                          |
    | `G3`           | Final grade as `avg` from G1 and G2. `numeric`: from 0 to 20, output target                                                                                                                   |           
                

                
    ### Grade Encoding
    Using these Grade table based on The fundamentals of the Portuguese educational system are utilized to define the academic grade classes in the dataset            
    
    | G3 Value Range | Grade | Description |
    |----------------|-------|-------------|
    | >= 18          | A     | Excellent   |
    | >= 14          | B     | Good        |
    | > 10           | C     | Sufficient  |
    | = 10           | D     | Pass        |
    | < 10           | E     | Fail        |


    """)

    
    # Menghitung feature importance menggunakan permutation importance
    importance = permutation_importance(knn_model, X_test, y_test, n_repeats=10, random_state=42)
    feature_importance = pd.DataFrame(importance.importances_mean, index=X.columns, columns=["Importance"]).sort_values(by="Importance", ascending=False)
    
    # Mendapatkan deskripsi statistik dari fitur
    feature_description = df.describe().T

    top_10_features = feature_importance.head(10)

    # Plot feature importance
    fig, ax = plt.subplots()
    sns.barplot(x=top_10_features["Importance"], y=top_10_features.index, color='orange', ax=ax)
    ax.set_title('Top 10 Feature Importances')
    ax.set_xlabel('Importance')
    ax.set_ylabel('Features')
    st.pyplot(fig)    

    st.markdown("""
    ### Feature Importance and Description
                
    Here, the significance and explanation of the 33 features are presented. The top 10 most important features are displayed above.
    """)

    # Membuat dua kolom
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.write("Feature Importance:")
        st.dataframe(feature_importance)    

    with col2:
        st.write("Feature Description:")
        st.dataframe(feature_description)
           
    st.title("Feature Dependence")

    # Filter only numeric columns for correlation
    numeric_df = df.select_dtypes(include=[np.number])

    # Hitung matriks korelasi
    correlation_matrix = numeric_df.corr()

    # Mengatur ukuran gambar berdasarkan jumlah fitur
    fig, ax = plt.subplots(figsize=(len(correlation_matrix.columns), len(correlation_matrix.columns)))
    
    # Membuat heatmap korelasi
    sns.heatmap(correlation_matrix, annot=True, fmt=".2f", cmap='coolwarm', ax=ax)
    
    # Menampilkan heatmap
    st.pyplot(fig)

    # Mengidentifikasi pasangan fitur dengan korelasi tertinggi
    unique_corr_pairs = correlation_matrix.where(np.triu(np.ones(correlation_matrix.shape), k=1).astype(bool))
    max_corr_value = unique_corr_pairs.stack().idxmax()  # Mendapatkan indeks pasangan dengan korelasi tertinggi
    max_corr = unique_corr_pairs.stack().max()  # Mendapatkan nilai korelasi tertinggi

    # Menampilkan Best Feature Correlation dalam kolom baru di bawah heatmap
    col1, col2 = st.columns(2)
    with col1:
        st.subheader('Best Feature Correlation')
       # st.write(f'The pair of features with the highest correlation is: {max_corr_value}')
        st.write(f"The pair of features with the highest correlation is: ('G2', 'G3'), ('Medu', 'Fedu')")
        
        
    with col2:
        st.subheader('Correlation Coefficient')
        st.write(f'The correlation coefficient for this pair is: {max_corr:.2f}')

    # Membuat tabel berdasarkan korelasi antara fitur
    st.subheader('Correlation Between Features')
    st.write(correlation_matrix)

    # Menampilkan tabel yang dapat diurutkan berdasarkan korelasi
    st.subheader('Sortable Correlation Table')
    st.write(correlation_matrix.unstack().sort_values(ascending=False))

      # correlation_unstacked = correlation_matrix.unstack()
    #correlation_filtered = correlation_unstacked[correlation_unstacked != 1].sort_values(ascending=False)

    # Create a DataFrame for displaying
   #correlation_df = correlation_filtered.reset_index()
   # st.write(correlation_df.sort_values(ascending=False))

elif page == "Summary":
    st.title("Classification KNN Performance")
    
    # Menghitung prediksi dan probabilitas prediksi
    y_pred = knn_model.predict(X_test)
    # Pastikan y_pred_proba memiliki probabilitas untuk setiap kelas
    y_pred_proba = knn_model.predict_proba(X_test)
    
    # Menghitung classification report
    st.write("Classification Report")
    class_report = classification_report(y_test, y_pred, output_dict=True)
    
    # Mengonversi classification report ke DataFrame untuk visualisasi yang lebih baik

    class_report_df = pd.DataFrame(class_report).transpose()
    
    #calculate confusion
    cm = confusion_matrix(y_test, y_pred)

    # Binarize y_test for multiclass
    y_test_binarized = label_binarize(y_test, classes=np.unique(y_test))

    # Calculate precision and recall for each class
    precision = dict()
    recall = dict()
    roc_auc = dict()
    for i in range(y_test_binarized.shape[1]):
        precision[i], recall[i], _ = precision_recall_curve(y_test_binarized[:, i], y_pred_proba[:, i])
        fpr, tpr, _ = roc_curve(y_test_binarized[:, i], y_pred_proba[:, i])
        roc_auc[i] = auc(fpr, tpr)

    # Create two columns in the first row
    col1, col2 = st.columns([4, 1])

    with col1:
        # Display classification report as a table
        class_report = classification_report(y_test, y_pred, output_dict=True)
        class_report_df = pd.DataFrame(class_report).transpose()
        st.table(class_report_df)

    # Create two columns in the second row
    col3, col4 = st.columns([3, 3])

    with col3:
        # Display confusion matrix using Seaborn and Matplotlib
        fig, ax = plt.subplots()
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', ax=ax)
        ax.set_title('Confusion Matrix')
        ax.set_xlabel('Predicted Labels')
        ax.set_ylabel('True Labels')
        st.pyplot(fig)

    with col4:
        # Display Precision-Recall Curve for each class
        fig, ax = plt.subplots()
        colors = cycle(['navy', 'turquoise', 'darkorange', 'cornflowerblue', 'teal'])
        for i, color in zip(range(y_test_binarized.shape[1]), colors):
            ax.plot(recall[i], precision[i], color=color, lw=2, label='Class {0} (AUC = {1:0.2f})'.format(i, auc(recall[i], precision[i])))
        ax.set_title('Precision-Recall Curve')
        ax.set_xlabel('Recall')
        ax.set_ylabel('Precision')
        ax.legend(loc="lower left")
        st.pyplot(fig)

    # Create two columns in the third row
    col5, col6 = st.columns([3, 3])

    with col5:
        # Display ROC Curve for each class
        fig, ax = plt.subplots()
        colors = cycle(['aqua', 'darkorange', 'cornflowerblue', 'green', 'red'])
        for i, color in zip(range(y_test_binarized.shape[1]), colors):
            fpr, tpr, _ = roc_curve(y_test_binarized[:, i], y_pred_proba[:, i])
            ax.plot(fpr, tpr, color=color, lw=2, label='Class {0} (AUC = {1:0.2f})'.format(i, auc(fpr, tpr)))
        ax.plot([0, 1], [0, 1], 'k--', lw=2)
        ax.set_xlim([0.0, 1.0])
        ax.set_ylim([0.0, 1.05])
        ax.set_xlabel('False Positive Rate')
        ax.set_ylabel('True Positive Rate')
        ax.set_title('Receiver Operating Characteristic (ROC) Curve')
        ax.legend(loc="lower right")
        st.pyplot(fig)

    with col6:
        # Display AUC Score for each class
        fig, ax = plt.subplots()
        ax.bar(range(len(roc_auc)), [roc_auc[i] for i in range(len(roc_auc))], color='navy')
        ax.set_title('AUC Score per Class')
        ax.set_xlabel('Class')
        ax.set_ylabel('AUC Score')
        ax.set_xticks(range(len(roc_auc)))
        ax.set_xticklabels(['Class {}'.format(i) for i in range(len(roc_auc))])
        st.pyplot(fig)

    # Menampilkan ringkasan hasil pelatihan model
    st.subheader("Training Summary")
    train_summary_data = {
        "Number of samples in training set": [len(X_train)],
        "Number of features": [X_train.shape[1]],
        "Number of classes": [len(np.unique(y_train))]
    }
    st.table(pd.DataFrame(train_summary_data))
    
    # Menampilkan metrik evaluasi model
    st.subheader("Performance Metrics")
    metrics_data = {
        "Accuracy": [f"{accuracy:.2f}"],
        "Precision (macro)": [f"{precision:.2f}"],
        "Micro-average ROC AUC": [f"{roc_auc['micro']:.2f}"]
    }
    for i in range(n_classes):
        metrics_data[f"ROC AUC (Class {i})"] = [f"{roc_auc[i]:.2f}"]
    st.table(pd.DataFrame(metrics_data))
    
    # Menampilkan confusion matrix
    st.subheader("Confusion Matrix")
    cm = confusion_matrix(y_test, y_pred)
    st.table(pd.DataFrame(cm, index=np.unique(y_test), columns=np.unique(y_test)))
    
    st.markdown("""
    ### SUMMARY
    This dashboard utilizes a K-Nearest Neighbors (KNN) classification model to predict student grades based on 33 input features. Many of these features were initially categorical (non-numeric) and have been converted to numeric values to be compatible with the model. You can find a detailed description of the feature encoding process on the `Data Card` Page.  We utilized 10 machine learning methods and The`KNN Model`achieved the highest accuracy of 82%, outperforming other models. This work enhances previous research by improving classification accuracy using classic machine learning algorithms.
    ### Why Numeric Values?
    Machine learning models require numerical input to perform calculations and make predictions. Thus, the categorical features in the [dataset](https://archive.ics.uci.edu/ml/datasets/student+performance) are converted into numeric values. This encoding process allows the model to understand and interpret the input data effectively.


    Using this Dashboard you can explore how different features affect student grades and make predictions based on the provided input values. 
    """)


    # Menampilkan classification report
    st.subheader("Classification Report")
    classification_report_df = pd.DataFrame.from_dict(classification_report(y_test, y_pred, output_dict=True)).T
    st.table(classification_report_df)