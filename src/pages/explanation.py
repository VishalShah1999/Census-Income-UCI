from app import *
import streamlit as st
import matplotlib
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
import numpy as np
import xgboost as xgb
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier 
import pandas as pd
import lime
import shap 
from lime import lime_tabular
import seaborn as sns
from src.get_data import dataframe
import streamlit.components.v1 as components
st.set_option('deprecation.showPyplotGlobalUse', False)
matplotlib.use('Agg')

columns = ['weeks_worked_in_year', 'num_persons_worked_for_employer', 'capital_gains','dividends_from_stocks', 'family_members_under_18', 'veterans_benefits']

def create_model(data,Xdata,model):
    #Train_test_split
    X = Xdata
    Y = data['under_50k_over_50k']
    X_train, X_test, Y_train, Y_test = train_test_split(X.values,Y.values, test_size=0.2, random_state=40)
    data_fit = (X,Y,X_train,Y_train,X_test,Y_test)

    #Models    
    if model=="xgboost":
        xgb_model = xgb.XGBClassifier(objective="binary:logistic", random_state=42)
        xgb_model.fit(X_train, Y_train)
        y_pred = xgb_model.predict(X_test)
        return data_fit,xgb_model
    
    elif model== "logistic":
        log_model = LogisticRegression(random_state=42)
        log_model.fit(X_train, Y_train)
        y_pred = log_model.predict(X_test)
        return data_fit,log_model

    elif model== "decision":
        tree_model = DecisionTreeClassifier(random_state=42)
        tree_model.fit(X_train, Y_train)
        y_pred = tree_model.predict(X_test)
        return data_fit,tree_model

    #Passing data to lime/shap
    
def create_model_synthetic(data,Xdata,model):
    #Train_test_split
    X = Xdata
    Y = data['target']
    X_train, X_test, Y_train, Y_test = train_test_split(X.values,Y.values, test_size=0.2, random_state=40)
    data_fit = (X,Y,X_train,Y_train,X_test,Y_test)

    #Models    
    if model=="xgboost":
        xgb_model = xgb.XGBClassifier(objective="binary:logistic", random_state=42)
        xgb_model.fit(X_train, Y_train)
        y_pred = xgb_model.predict(X_test)
        return data_fit,xgb_model
    
    elif model== "logistic":
        log_model = LogisticRegression(random_state=42)
        log_model.fit(X_train, Y_train)
        y_pred = log_model.predict(X_test)
        return data_fit,log_model

    elif model== "decision":
        tree_model = DecisionTreeClassifier(random_state=42)
        tree_model.fit(X_train, Y_train)
        y_pred = tree_model.predict(X_test)
        return data_fit,tree_model

    
def lime_explanation(data_fit,model):
    lime_explainer = lime_tabular.LimeTabularExplainer(
    training_data=np.array(data_fit[2]),
    feature_names=data_fit[0].columns,
    class_names=[0, 1],
    mode='classification')

    lime_exp = lime_explainer.explain_instance(
        data_row=data_fit[4][1],
        predict_fn=model.predict_proba
    )
    return lime_exp

def shap_explanation(data_fit,model):
        explainer_shap = shap.TreeExplainer(model)
        shap_values = explainer_shap.shap_values(data_fit[4][:100])
        return shap_values,explainer_shap
        
def write():
    with st.spinner("Loading ..."):
        st.title('ML Explanations')
        col1, col2, col3 = st.columns(3)
     
        with col1:
            data_select = st.selectbox('Data source',["US Census Data","Synthetic Data without Noise"])
        with col2:
            ex_select = st.selectbox('Explanation type',["Lime","Shapely"])
        with col3:
            model_select = st.selectbox('Model',["xgboost","decision","logistic"])
        try:
            
            data = dataframe(str(data_select)) 
            if data_select == "US Census Data":
                st.markdown("### US Census Data (Real-World Data)", unsafe_allow_html=True) 
        
                if ex_select=="Lime":
                    col4, col5 = st.columns(2)
                    with col4:
                        feature_1 = st.selectbox('Feature1',columns)
                    with col5:
                        feature_2 = st.selectbox('Feature2',columns)
   
                    formatted_data,model = create_model(data,data[[feature_1,feature_2]], model_select)
                    fig, ax = plt.subplots(figsize=(5,3))
                    st.write(sns.heatmap(data[columns].corr(), annot=True))
                    st.pyplot()
                    instance = lime_explanation(formatted_data, model)
                    components.html(instance.as_html())
                    
                    
                else:
                    ##Summary plot
                    formatted_data,model = create_model(data,data[columns], model_select)
                    shap_values,explainer = shap_explanation(formatted_data, model)
                    #st_shap(shap.force_plot(explainer.expected_values, shap_values[0], X_test[:100], plot_cmap=["#FF5733","#335BFF"]))
                    #st.pyplot()
                    shap.summary_plot(shap_values,formatted_data[2],feature_names=columns,plot_type="bar",show=False)
                    st.pyplot(bbox_inches='tight')
                    plt.clf()
    
                    ##Dependence plot
                    feature_select = st.selectbox('Feature',columns)
                    inds = shap.approximate_interactions(feature_select, shap_values, formatted_data[4][:100])
                    for i in range(4):
                        shap.dependence_plot(feature_select,shap_values,formatted_data[4][:100],interaction_index=inds[i],show=False)
                        st.pyplot()
                        plt.clf()
            else:
                st.markdown("## Synthetic Data without noise")
                
                
                if ex_select=="Lime":
                    syn_columns = ['Feature1','Feature2','Feature3']
                    col4, col5 = st.columns(2)     
                    with col4:
                        feature_1 = st.selectbox('Feature1',syn_columns)
                    with col5:
                        feature_2 = st.selectbox('Feature2',syn_columns)
                    formatted_data,model = create_model_synthetic(data,data[[feature_1,feature_2]], model_select)
                    fig, ax = plt.subplots(figsize=(5,3))
                    st.write(sns.heatmap(data[columns].corr(), annot=True))
                    st.pyplot()
                    instance = lime_explanation(formatted_data, model)
                    components.html(instance.as_html(), height=800)
                   
                else:
                    ##Summary plot
                    formatted_data,model = create_model_synthetic(data,data[columns], model_select)
                    shap_values,explainer = shap_explanation(formatted_data, model)
                    #st_shap(shap.force_plot(explainer.expected_values, shap_values[0], X_test[:100], plot_cmap=["#FF5733","#335BFF"]))
                    #st.pyplot()
                    shap.summary_plot(shap_values,formatted_data[2],feature_names=data.drop('target', axis=1).columns,plot_type="bar",show=False)
                    st.pyplot(bbox_inches='tight')
                    plt.clf()
    
                    ##Dependence plot
                    st.write('In the slider below, select the number of features to inspect for possible interaction effects.'
                            'These are ordered based on feature importance in the model.')
                    ranges = st.slider('Please select the number of features',min_value=min(range(len(data.drop('target', axis=1).columns)))+1, max_value=max(range(len(data.drop('target', axis=1).columns)))+1,value=1)
                    if ranges-1 == 0:
                        st.write('you have selected the most importance feature')
                    elif ranges == len(data.drop('target', axis=1).columns):
                            st.write('you have selected all possible features')
                    else:
                        st.write('you have selected the top:',ranges,'important features')
                    for rank in range(ranges):
                        ingest=('rank('+str(rank)+')')
                        shap.dependence_plot(ingest,shap_values,formatted_data[:100],show=False)
                        st.pyplot()
                        plt.clf()
                
        except Exception as e:
            st.write(e)
        
