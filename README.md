## Introduction

This repo contains a KNN model specifically trained on a dataset that is collected from large WiFi network devices. The model predicts the possible advisory class for the customer care representative. The model is wraped as a REST API so that application layer can call the endpoint, get the advisory class and render on application side. The data used to calculate the distance has been continuously ingested and processed using a separate data pipeline and made available on a `S3` storage bucket.

## Overall Architecture 


## Data 

A sample dataset has been given in 
