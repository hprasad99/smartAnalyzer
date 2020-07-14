import pandas as pd
import numpy as np
import sys, math, openpyxl
import matplotlib.pyplot as plt
import io, urllib, base64

from sklearn import linear_model, svm
from sklearn.cluster import KMeans, DBSCAN
from sklearn.preprocessing import StandardScaler

from django.contrib import messages

from firebase import firebase
firebase = firebase.FirebaseApplication(
    'https://smartanalyzer-s3hp.firebaseio.com/')


class ERA:
    @staticmethod
    def count(nx, low=0, high=0, max_score=50):
        p = 0
        if (low == 0 and high == 0):
            for x in np.nditer(nx):
                if not x == 0:
                    p += 1
        else:
            for x in np.nditer(nx):
                if low <= x * 100 / max_score < high:
                    p += 1
        return p

    @staticmethod
    def evaluate_era_output(excel_file, e_name, max_score, q_count):
        passing_marks = max_score * 35 / 100
        wb = openpyxl.load_workbook(excel_file)
        sheets = wb.sheetnames
        worksheet = wb["Sheet1"]
        active_sheet = wb.active
        excel_data = list()
        for row in worksheet.iter_rows():
            row_data = list()
            for cell in row:
                row_data.append((cell.value))
            excel_data.append(row_data)

        categories = excel_data[0]
        excel_data = excel_data[1:]

        data = pd.DataFrame(excel_data, columns=categories)
        #dropping absent entries with NaN values
        data = data.dropna(
            subset=['Q' + str(x) for x in range(1, q_count + 1)], thresh=1)
        #replacing remaining NaN values with zeroes
        data.fillna(0, inplace=True)

        data.Total = data.Total.astype('int64')
        print(data.head())
        failed_students = data[data['Total'] < passing_marks]
        passed_students = data[data['Total'] >= passing_marks]
        c_fail = failed_students.shape[0]
        pass_pert = round(((passed_students.shape[0] * 100) / data.shape[0]),
                          2)

        x_p = []
        y_p = []
        regr_output = list()
        minimum_pref = max_score * 2 / q_count
        q = 0
        for i in range(1, q_count + 1):
            for x1, y1 in zip(data['ID'], data['Q' + str(i)]):
                if (y1 == 0):
                    continue
                x_p.append([x1])
                y_p.append(y1)

            #regr = linear_model.LinearRegression()
            regr = linear_model.LinearRegression()
            regr.fit(x_p, y_p)
            y_pred = regr.predict([[data['ID'].median()]])
            regr_output.append("Q" + str(i) + ": {:05.2f}".format(float(y_pred)))
            if y_pred < minimum_pref:
                minimum_pref = y_pred
                q = i

        regr_output_l1 = "Syllabus covered in Q" + str(
            q) + " requires most revision"

        rep = pd.DataFrame(data, columns=['ID'])
        rep['ID'] = round(rep['ID'], 0)
        rep['Marks Obtained out of ' + str(max_score)] = data['Total']
        rep["Percentage"] = round((data['Total'] * 100 / max_score), 2)
        rep['Remark'] = np.where(data['Total'] < passing_marks, "Fail", "Pass")
        rep['Class'] = np.where(
            75 <= rep["Percentage"], "Distinction",
            np.where(65 <= rep["Percentage"], "First Class",
                     np.where(35 <= rep["Percentage"], "Second Class", "-")))

        print(rep.head())
        rep_data = rep.values.tolist()
        rep_head = rep.columns.values.tolist()
        toppers = rep.nlargest(5, ['Percentage'])
        toppers_data = toppers.values.tolist()

        ###############################################################
        buf = io.BytesIO()
        plt.clf()
        xAxis = ['Q' + str(x) for x in range(1, q_count + 1)]
        max_scores = [data['Q' + str(x)].max() for x in range(1, q_count + 1)]
        mean_scores = [
            data.loc[:, "Q" + str(x)].sum() /
            ERA.count(data["Q" + str(x)], max_score=max_score)
            for x in range(1, q_count + 1)
        ]
        #plt.fill_between( x, y, color="skyblue", alpha=0.2)
        #plt.plot(x, y, color="Slateblue", alpha=0.6)
        plt.fill_between(xAxis, max_scores, color="yellow", alpha=0.2)
        plt.fill_between(xAxis, mean_scores, color="skyblue", alpha=0.2)

        plt.plot(xAxis,
                 max_scores,
                 label="Obtained (Maximum)",
                 marker="o",
                 color="orange",
                 alpha=0.6)
        plt.plot(xAxis,
                 mean_scores,
                 label="Obtained (Average)",
                 marker="o",
                 color="skyblue",
                 alpha=0.6)
        plt.ylabel("Marks")
        plt.xlabel("Questions")
        plt.legend()
        

        avg_chart = plt.gcf()
        avg_chart.savefig(buf, format='png')
        buf.seek(0)
        string = base64.b64encode(buf.read())
        avg_chart_uri = 'data:image/png;base64,' + urllib.parse.quote(string)

        plt.clf()
        attempts = [
            ERA.count(data["Q" + str(x)]) for x in range(1, q_count + 1)
        ]
        plt.bar(xAxis,
                attempts,
                label="No. of attempts",
                width=.5,
                color="skyblue",
                alpha=0.5)
        plt.plot(xAxis, attempts, marker="o", color="skyblue", alpha=0.6)
        plt.legend()

        buf = io.BytesIO()
        attempt_chart = plt.gcf()
        attempt_chart.savefig(buf, format='png')
        buf.seek(0)
        string = base64.b64encode(buf.read())
        attempt_chart_uri = 'data:image/png;base64,' + urllib.parse.quote(
            string)

        plt.clf()
        tags = ['0% - 35%', '35% - 55%', '55% - 75%', 'Above 75%']
        totals = data["Total"]
        slices = [
            ERA.count(totals, 0, 35, max_score),
            ERA.count(totals, 35, 55, max_score),
            ERA.count(totals, 55, 75, max_score),
            ERA.count(totals, 75, 101, max_score)
        ]
        colors = ['red', 'orange', 'green', 'blue']
        plt.pie(slices,
                labels=tags,
                colors=colors,
                explode=(0, 0, 0, 0.1),
                autopct='%1.1f%%',
                shadow=True,
                startangle=90)
        plt.axis('equal')

        buf = io.BytesIO()
        pie_chart = plt.gcf()
        pie_chart.savefig(buf, format='png')
        buf.seek(0)
        string = base64.b64encode(buf.read())
        pie_chart_uri = 'data:image/png;base64,' + urllib.parse.quote(string)

        plt.clf()
        plt.scatter(data['ID'], data['Total'], marker='o', s=50, alpha=0.5)
        plt.ylabel("Marks obtained")
        plt.xlabel("Student ID")

        buf = io.BytesIO()
        scatter = plt.gcf()
        scatter.savefig(buf, format='png')
        buf.seek(0)
        string = base64.b64encode(buf.read())
        scatter_uri = 'data:image/png;base64,' + urllib.parse.quote(string)

        plt.clf()
        xy = pd.DataFrame(data, columns=['ID', 'Total'])
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(xy)
        dbscan = DBSCAN(eps=0.5, min_samples=2)
        clusters = dbscan.fit_predict(X_scaled)
        plt.bar(xy['ID'], xy['Total'], alpha=0.1)
        plt.scatter(xy['ID'],
                    xy['Total'],
                    c=clusters,
                    cmap="plasma",
                    s=50,
                    alpha=0.8)
        plt.xlabel("Student ID")
        plt.ylabel("Marks Obtained")

        buf = io.BytesIO()
        dbscan = plt.gcf()
        dbscan.savefig(buf, format='png')
        buf.seek(0)
        string = base64.b64encode(buf.read())
        dbscan_uri = 'data:image/png;base64,' + urllib.parse.quote(string)

        #excel_file, e_name, max_score, q_count
        return ({
            'title': 'Exam Result Analysis',
            'e_name': e_name,
            'max_score': max_score,
            'q_count': q_count,
            'rep_head': rep_head,
            "toppers": toppers_data,
            "pass_pert": pass_pert,
            "failed_students": failed_students,
            "regr_output": regr_output,
            "regr_output_l1": regr_output_l1,
            "report": rep_data,
            "avg_chart": avg_chart_uri,
            "attempt_chart": attempt_chart_uri,
            "pie_chart": pie_chart_uri,
            "scatter": scatter_uri,
            "dbscan": dbscan_uri,
        })


class SAA:
    @staticmethod
    def se_a():
        n_days = 15
        data = pd.read_csv('blog/att_data_days.csv')
        df = pd.DataFrame(
            data, columns=["Day" + str(i) for i in range(1, n_days + 1)])
        l1 = df.sum(axis=0)

        buf = io.BytesIO()
        plt.figure(figsize=(10,6))
        plt.clf()
        
        xAxis = ["Day" + str(i) for i in range(1, n_days + 1)]
        plt.fill_between(xAxis, l1, color="yellow", alpha=0.2)
        plt.plot(xAxis, l1, marker='o', color="orange")
        plt.xlabel("Days")
        
        plt.ylabel("No. of present students")
        #plt.title("Day-wise Attendance")
        
        daywise_chart = plt.gcf()
        daywise_chart.savefig(buf, format='png')
        buf.seek(0)
        string = base64.b64encode(buf.read())
        daywise_chart_uri = 'data:image/png;base64,' + urllib.parse.quote(
            string)


        rep = pd.DataFrame(data, columns=['ID'])
        rep["Total"] = sum(
            [data["Day" + str(i)] for i in range(1, n_days + 1)])
        rep["Pert"] = round((rep['Total'] * 100 / n_days), 2)
        rep["isDefaulter"] = np.where(rep["Pert"] < 75, 'Y', 'N')
        rep_data_header = rep.columns.values.tolist()
        rep_data = rep.values.tolist()

        print(rep.head())

        plt.clf()
        #plt.scatter(rep['ID'], rep['Total'], marker='o', )

        xy = pd.DataFrame(rep, columns=['ID', 'Total'])
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(xy)
        dbscan = DBSCAN(eps=0.4, min_samples=2)
        clusters = dbscan.fit_predict(X_scaled)
        plt.scatter(xy['ID'],
                    xy['Total'],
                    c=clusters,
                    cmap="plasma",
                    s=50,
                    alpha=0.5)
        plt.ylabel("Current Attendance")
        plt.xlabel("Student ID")
        plt.bar(xy['ID'],
                    xy['Total'], color="skyblue", alpha=0.2
                    )
        buf = io.BytesIO()
        scatter = plt.gcf()
        scatter.savefig(buf, format='png')
        buf.seek(0)
        string = base64.b64encode(buf.read())
        scatter_uri = 'data:image/png;base64,' + urllib.parse.quote(string)

        #totals = pd.DataFrame(data, columns=["Day"+str(i) for i in range(1, n_days+1)]).sum(axis = 0)
        #print("Subject Avg Attendance:", sum(totals)/len(totals))

        return ({
            'title': 'Student Attendance Analysis - SE A',
            'daywise_chart': daywise_chart_uri,
            'detailed_report': rep_data,
            'detailed_report_head': rep_data_header,
            'scatter': scatter_uri,
        })


class SM:
    @staticmethod
    def fetch_sched(query):
        x = pd.DataFrame(firebase.get(query, None))
        y = pd.DataFrame(index=[1, 2, 3, 4, 5, 6, 7])
        y['Time Slot'] = [
            '1 [08:30 - 09:30]', '2 [09:30 - 10:30]', '3 [10:45 - 11:45]',
            '4 [11:45 - 12:45]', '5 [13:30 - 14:30]', '6 [14:30 - 15:30]',
            '7 [15:30 - 16:30]'
        ]
        days = ['MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT']
        for d in days:
            y[d] = x[d]
        sched_data_head = y.columns.values.tolist()
        sched_data = y.values.tolist()
        return sched_data_head, sched_data

    @staticmethod
    def display_schedule(request):
        classes = firebase.get('classes/', None)
        class_name = str(request.POST.get('class', None))
        print(class_name)
        query = 'class_details/' + class_name + '/schedule/'
        sched_data_head, sched_data = SM.fetch_sched(query)
        return {
            'classes': classes,
            'title': 'Schedule Manager',
            'sched_head': sched_data_head,
            'sched': sched_data,
        }

    @staticmethod
    def manage_schedule(request):
        classes = firebase.get('classes/', None)
        days = ['MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT']
        slots = [1, 2, 3, 4, 5, 6, 7]

        class_name = str(request.POST.get('class', None))
        day_mod = str(request.POST.get('day', None))
        slot_mod = int(request.POST.get('slot', None))
        new_val = str(request.POST.get('new_name', None))

        org = firebase.get(('class_details/' + class_name + '/schedule/' +
                            day_mod + '/' + str(slot_mod)), None)
        result = firebase.put(
            'class_details/' + class_name + '/schedule/' + day_mod + '/',
            str(slot_mod), str(new_val))
        if result == None:
            messages.success(request, 'Schedule update failed!')
            return {
                'title': 'Schedule Manager',
                'days': days,
                'classes': classes,
                'slots': slots,
            }
        else:
            messages.success(request, 'Schedule updated successfully!')
            query = 'class_details/' + class_name + '/schedule/'
            sched_data_head, sched_data = SM.fetch_sched(query)
            update_comment = "Slot " + str(slot_mod) + " of Class " + str(
                class_name) + " for " + str((day_mod)).capitalize() + "day" + " changed from " + str(
                    org) + " to " + str(new_val)
            return {
                'title': 'Schedule Manager',
                'days': days,
                'classes': classes,
                'slots': slots,
                'sched_head': sched_data_head,
                'sched': sched_data,
                'update_comment': update_comment,
            }