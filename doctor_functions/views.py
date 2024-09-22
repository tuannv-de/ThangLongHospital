from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib.auth.views import LoginView
from django.contrib.auth.models import User
from .models import UserProfileModel
from .forms import UserProfileForm 
from django.contrib.auth import logout
from appointment.models import Appointment
from django.shortcuts import get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt

from pyspark.sql import SparkSession
from pyspark.ml import Pipeline
from pyspark.sql.functions import col, explode, lit, array, udf
from pyspark.sql.types import DoubleType
from pyspark.ml.feature import MinMaxScaler, StringIndexer, VectorAssembler, PCA
from pyspark.ml.classification import RandomForestClassifier
from pyspark.ml.evaluation import MulticlassClassificationEvaluator


def signup(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES)  # Chú ý thêm request.FILES
        if form.is_valid():
            user = form.save()
            login(request, user)
            user_profile = UserProfileModel(
                user=user,
                name=form.cleaned_data['name'],
                speciality=form.cleaned_data['speciality'],
                picture=form.cleaned_data['picture'],
                details=form.cleaned_data['details'],
                experience=form.cleaned_data['experience'],
                twitter=form.cleaned_data['twitter'],
                facebook=form.cleaned_data['facebook'],
                instagram=form.cleaned_data['instagram'],
            )
            user_profile.save()  # Lưu đối tượng UserProfileModel
            return redirect('/doctor-functions/login')  # Điều hướng đến trang đăng nhập
    else:
        form = UserProfileForm()
    return render(request, 'doctor_functions/signup.html', {'form': form})

class CustomLoginView(LoginView):
    template_name = 'doctor_functions/login.html'
    
    def get_success_url(self):
        return '/doctor-functions/'

def logout_view(request):
    logout(request)
    return redirect('/doctor-functions/login')

@login_required
def dashboard(request):
    user_profile = request.user.userprofilemodel  # Lấy thông tin người dùng hiện tại
    appointments = Appointment.objects.filter(doctor=user_profile)  # Lọc lịch hẹn theo bác sĩ
    return render(request, 'dashboard.html', {'appointments': appointments})



@csrf_exempt  
@require_POST
def update_status(request):
    import json
    data = json.loads(request.body)
    appointment_id = data.get('appointment_id')
    new_status = data.get('status')

    try:
        appointment = Appointment.objects.get(id=appointment_id)
        appointment.status = new_status
        appointment.save()

        return JsonResponse({'success': True})
    except Appointment.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Appointment not found'})
    




def predict(request):
    spark = SparkSession.builder.master('local[*]').appName('Heart predict').getOrCreate()


    df = spark.read.csv('heart_2020_cleaned.csv', sep=',', header=True, inferSchema=True, nullValue='NA')

    df = df.dropDuplicates()

    if request.method == 'POST':
        # Get input values from the form
        bmi = float(request.POST.get('BMI'))
        smoking = request.POST.get('Smoking')
        alcohol_drinking = request.POST.get('AlcoholDrinking')
        stroke = request.POST.get('Stroke')
        physical_health = float(request.POST.get('PhysicalHealth'))
        mental_health = float(request.POST.get('MentalHealth'))
        diff_walking = request.POST.get('DiffWalking')
        sex = request.POST.get('Sex')
        age_category = request.POST.get('AgeCategory')
        race = request.POST.get('Race')
        diabetic = request.POST.get('Diabetic')
        physical_activity = request.POST.get('PhysicalActivity')
        gen_health = request.POST.get('GenHealth')
        sleep_time = float(request.POST.get('SleepTime'))
        asthma = request.POST.get('Asthma')
        kidney_disease = request.POST.get('KidneyDisease')
        skin_cancer = request.POST.get('SkinCancer')

        # Create a new DataFrame with the input values
        new_data = [('No', bmi, smoking, alcohol_drinking, stroke, physical_health,
                     mental_health, diff_walking, sex, age_category, race,
                     diabetic, physical_activity, gen_health, sleep_time,
                     asthma, kidney_disease, skin_cancer)]
        
        columns = ['HeartDisease', 'BMI', 'Smoking', 'AlcoholDrinking', 'Stroke', 
                   'PhysicalHealth', 'MentalHealth', 'DiffWalking', 'Sex', 
                   'AgeCategory', 'Race', 'Diabetic', 'PhysicalActivity', 
                   'GenHealth', 'SleepTime', 'Asthma', 'KidneyDisease', 'SkinCancer']

        new_df = spark.createDataFrame(new_data, columns)

        indexers = [
            StringIndexer(inputCol=column, outputCol=column + "_label")
            for column in df.columns
        ]

        # Tạo Pipeline với các StringIndexer
        pipeline = Pipeline(stages=indexers)

        # Áp dụng Pipeline để mã hóa các cột phân loại
        indexed_df_model = pipeline.fit(df)
        indexed_df = indexed_df_model.transform(df)
        test_df = indexed_df_model.transform(new_df)

        # Loại bỏ các cột gốc và đổi tên các cột _label thành tên cột gốc
        for column in df.columns:
            indexed_df = indexed_df.drop(column).withColumnRenamed(column + "_label", column)

        for column in df.columns:
            test_df = test_df.drop(column).withColumnRenamed(column + "_label", column)


        def resample(base_features, class_field, base_class):
            pos = base_features.filter(col(class_field) == base_class)
            neg = base_features.filter(col(class_field) != base_class)

            total_pos = pos.count()
            total_neg = neg.count()

            ratio = int(total_pos / total_neg)
            remainder = total_pos % total_neg

            oversampled_neg = neg.withColumn("dummy", explode(array([lit(x) for x in range(ratio)]))).drop("dummy")

            if remainder > 0:
                oversampled_neg = oversampled_neg.union(neg.sample(False, float(remainder) / total_neg))
            return pos.union(oversampled_neg)

        balanced_df = resample(indexed_df, "HeartDisease", 0)

        x = indexed_df.drop('HeartDisease')
        y = indexed_df.select('HeartDisease')

        x1 = test_df.drop('HeartDisease')

        feature_columns = [col for col in x.columns]
        assembler = VectorAssembler(inputCols=feature_columns, outputCol="features")

        df_features = assembler.transform(indexed_df)
        test_features = assembler.transform(test_df)

        scaler = MinMaxScaler(inputCol="features", outputCol="scaled_features")

        scaler_model = scaler.fit(df_features)
        scaled_x = scaler_model.transform(df_features)
        scaled_test_x = scaler_model.transform(test_features)

        pca = PCA(k=3, inputCol="scaled_features", outputCol="pca_features")
        pca_model = pca.fit(scaled_x)
        pca_df = pca_model.transform(scaled_x)

        pca_test_df = pca_model.transform(scaled_test_x)

        pca_df = pca_df.select("pca_features", "HeartDisease")

        pca_test_df = pca_test_df.select("pca_features", "HeartDisease")

        def extract_pca_features(pca_features):
            return [float(x) for x in pca_features]

        extract_pca_features_udf = udf(extract_pca_features, "array<double>")

        pca_df = pca_df.withColumn("pca1", extract_pca_features_udf(col("pca_features")).getItem(0))
        pca_df = pca_df.withColumn("pca2", extract_pca_features_udf(col("pca_features")).getItem(1))
        pca_df = pca_df.withColumn("pca3", extract_pca_features_udf(col("pca_features")).getItem(2))

        pca_test_df = pca_test_df.withColumn("pca1", extract_pca_features_udf(col("pca_features")).getItem(0))
        pca_test_df = pca_test_df.withColumn("pca2", extract_pca_features_udf(col("pca_features")).getItem(1))
        pca_test_df = pca_test_df.withColumn("pca3", extract_pca_features_udf(col("pca_features")).getItem(2))

        pca_df = pca_df.select("pca1", "pca2", "pca3", "HeartDisease")
        pca_test_df = pca_test_df.select("pca1", "pca2", "pca3", "HeartDisease")

        assembler = VectorAssembler(inputCols=["pca1", "pca2", "pca3"], outputCol="features")
        assembled_df = assembler.transform(pca_df)
        assembled_test_df = assembler.transform(pca_test_df)

        train_df, test_df = assembled_df.randomSplit([0.7, 0.3], seed=42)

        rf = RandomForestClassifier(featuresCol="features", labelCol="HeartDisease")
        rf_model = rf.fit(train_df)

        predictions = rf_model.transform(assembled_test_df)

        # Tạo UDF để trích xuất giá trị thứ hai
        get_second_value = udf(lambda vector: float(vector[1]))

        # Áp dụng UDF để tạo cột mới chứa giá trị thứ hai
        predictions_with_second_value = predictions.withColumn("second_value", get_second_value("probability"))

        # Hiển thị kết quả
        predictions_with_second_value.select("second_value").show(truncate=False)

        second_value_row = predictions_with_second_value.select("second_value").collect()[0][0]
        
        second_value_float = float(second_value_row) * 100
        second_value_str = str(second_value_float)

        return render(request, 'doctor_functions/prediction_result.html', {'prediction': second_value_str})

    # Render form dự đoán ban đầu nếu không phải là POST
    return render(request, 'doctor_functions/predict.html')