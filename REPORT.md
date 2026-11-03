# Report: A Sustainable Malware Detection System (one page)

Written by the student, using your own results from docs/.

## Problem

The dataset had drift from year to year with the drift compounding with the increasing size of the gap between the years. Every year had drifted further and further from the original dataset. This presented an issue that needed to be addressed in the program. In order to create a machine learning program that could flag malicious software, it was neccessary to first identify and address the drift that was present in the data. In doing so, the program is able to adjust and still identify malware in programs created outside the years of the training set. While the data drift did still affect the model's preformance on other years, it did not stop the program from correctly flagging many malicious applications. The greatest drift occured from 2014 to 2024, with an average KS statistic of 0.0524 and a maximum KS statistic of 0.693. Additionally, the API calls that were most affected by drift were ContentResolver, process, oower-management, and notification calls. Overall, the drift is the primary cause of poorer preformance on the newer data.

## What we tried

The AI agent decided to utilize Logistic Regression and Random Forest models to predict the class of each query. The logistical regression model served as a linear baseline to the random forest model's nonlinear approach. The project also uses retraining to help build the models, continuously expanding the available dataset. 

## Results

Over all the years, the static logistical regression models scored an average accuracy of 0.6166, while the static random forest model recieved a modest five point bump to 0.6603. This means that over half of the classifications were correct. Before the preformance drop-off due to increasing data drift, 2018 queries scored around 0.95, roughly thirty points ahead of the average. The drop-off in the static models is most evident in the 2021 years with scores of 0.3910 and 0.5497 for the logistical regression and random forest models respectively. However, when the models used retraining, the score is bosted by over forty points in the most dramatic case, with logistic regression scorring 0.8369 comppared to random forest scoring 0.8542. These most dramatic improvements from the retraining aproach were seen in 2020 and 2021.

## Recommendation

Overall, the best approach to creating a preformant model to classify applications would use a periodic retraining approach and a random forest. This approach to machine learning proved to yield the most reliable results based on the data. The models should be retrained as soon as new yearly data becomes available so that the models can be the most reliable. Drift can be most accurately measured through KS statistics monitoring. Drift can also be monitored by observing key statistics such as accuracy, precision, and recall. As they begin to dip, it is reasonable to assume that the models are experiencing drift and may signify that the models should be retrained. 
