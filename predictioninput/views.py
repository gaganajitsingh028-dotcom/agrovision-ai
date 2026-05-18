from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache

from .models import YieldPrediction, DiseasePrediction
from .forms import RegisterForm

import os
import uuid
import pickle
import numpy as np
import tensorflow as tf

from tensorflow.keras.preprocessing import image


# =========================
# HOME PAGES
# =========================

@never_cache
def landing_page(request):
    return render(request, "landing.html")


@never_cache
def home(request):
    return render(request, "home.html")


# =========================
# LOAD YIELD MODEL
# =========================

yield_model_path = os.path.join(
    settings.BASE_DIR,
    "ml_models",
    "yield_model.pkl"
)




# =========================
# LOAD AREA ENCODER
# =========================

area_encoder_path = os.path.join(
    settings.BASE_DIR,
    "ml_models",
    "area_encoder.pkl"
)




# =========================
# LOAD ITEM ENCODER
# =========================

item_encoder_path = os.path.join(
    settings.BASE_DIR,
    "ml_models",
    "item_encoder.pkl"
)



area_list = list(le_area.classes_)
item_list = list(le_item.classes_)
# =========================
# YIELD PREDICTION VIEW
# =========================

@never_cache
@login_required
def yield_view(request):
    le_area = pickle.load(open(area_encoder_path, "rb"))  
    yield_model = pickle.load(open(yield_model_path, "rb"))
    le_item = pickle.load(open(item_encoder_path, "rb"))
    result = None
    
    if request.method == "POST":

        try:

            rainfall = float(request.POST.get("rainfall"))
            temp = float(request.POST.get("temp"))
            pesticides = float(request.POST.get("pesticides"))
            year = int(request.POST.get("year"))

            area = request.POST.get("area")
            item = request.POST.get("item")

            # Encode values
            area_encoded = le_area.transform([area])[0]
            item_encoded = le_item.transform([item])[0]

            # Predict yield
            prediction = yield_model.predict([[
                area_encoded,
                item_encoded,
                year,
                rainfall,
                pesticides,
                temp
            ]])

            result = str(round(prediction[0], 2)) + " hg/ha yield"

            # Save yield prediction
            YieldPrediction.objects.create(
                rainfall=rainfall,
                temperature=temp,
                pesticides=pesticides,
                area=area,
                item=item,
                year=year,
                result=result
            )

        except Exception as e:
            result = str(e)

    return render(
        request,
        "yield.html",
        {
            "result": result,
            "area_list": area_list,
            "item_list": item_list,
        }
    )

# =========================
DISEASE_MODELS = {
    "appleandmaize_model": {
        "path": "appleandmaize_model.keras",
        "classes": [
            "Apple___Apple_scab",
            "Apple___Black_rot",
            "Apple___Cedar_apple_rust",
            "Apple___healthy",
            "Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot",
            "Corn_(maize)___Common_rust_",
            "Corn_(maize)___healthy",
            "Corn_(maize)___Northern_Leaf_Blight",
        ]
    },

    "potatotomato_model": {
        "path": "potatotomato_model.keras",
        "classes": [
            "Potato___Early_blight",
            "Potato___healthy",
            "Potato___Late_blight",
            "Tomato___Bacterial_spot",
            "Tomato___Early_blight",
            "Tomato___healthy",
            "Tomato___Late_blight",
            "Tomato___Leaf_Mold",
            "Tomato___Septoria_leaf_spot",
            "Tomato___Spider_mites Two-spotted_spider_mite",
            "Tomato___Target_Spot",
            "Tomato___Tomato_mosaic_virus",
            "Tomato___Tomato_Yellow_Leaf_Curl_Virus",
        ]
    },

    "wheatandrice_model": {
        "path": "wheatandrice_model.keras",
        "classes": [
            "Bacterial Leaf Blight",
            "Brown Spot",
            "Crown and Root Rot",
            "Healthy Rice Leaf",
            "Healthy Wheat",
            "Leaf Blast",
            "Leaf Rust",
            "Leaf scald",
            "Sheath Blight",
            "Wheat Loose Smut",
        ]
    }

    }

# =========================
# DISEASE PREDICTION VIEW
# =========================

@never_cache
@login_required
def disease_view(request):

    result = None
    uploaded_image_url = None

    model_choices = [
        ("appleandmaize_model", "Apple + Maize Model"),
        ("potatotomato_model", "Potato + Tomato Model"),
        ("wheatandrice_model", "Wheat + Rice Model"),
    ]

    if request.method == "POST":

        selected_model = request.POST.get("model_choice")

        if selected_model not in DISEASE_MODELS:
            result = "Please select a valid model"

        elif not request.FILES.get("image"):
            result = "Please upload an image"

        else:
            try:
                uploaded_file = request.FILES["image"]

                filename = str(uuid.uuid4()) + "_" + uploaded_file.name

                upload_dir = os.path.join(settings.MEDIA_ROOT, "uploads")
                os.makedirs(upload_dir, exist_ok=True)

                file_path = os.path.join(upload_dir, filename)

                with open(file_path, "wb+") as destination:
                    for chunk in uploaded_file.chunks():
                        destination.write(chunk)

                uploaded_image_url = settings.MEDIA_URL + "uploads/" + filename

                # Load selected model
                model_info = DISEASE_MODELS[selected_model]

                model_path = os.path.join(
                    settings.BASE_DIR,
                    "ml_models",
                    model_info["path"]
                )

                disease_model = tf.keras.models.load_model(
                    model_path,
                    compile=False
                )

                class_names = model_info["classes"]

                # Load image
                img = image.load_img(
                    file_path,
                    target_size=(128, 128)
                )

                img_array = image.img_to_array(img)
                img_array = img_array / 255.0
                img_array = np.expand_dims(img_array, axis=0)

                predictions = []

                predictions.append(
                    disease_model.predict(img_array, verbose=0)
                )

                predictions.append(
                    disease_model.predict(np.fliplr(img_array), verbose=0)
                )

                predictions.append(
                    disease_model.predict(np.flipud(img_array), verbose=0)
                )

                avg_prediction = np.mean(predictions, axis=0)[0]

                top_3_idx = np.argsort(avg_prediction)[-3:][::-1]

                top_3 = [
                    (
                        class_names[i],
                        float(avg_prediction[i]) * 100
                    )
                    for i in top_3_idx
                ]

                main_result = f"{top_3[0][0]} ({top_3[0][1]:.1f}%)"

                extra = "<br><small>Top 3 Predictions:<br>"

                for i, (name, conf) in enumerate(top_3):
                    extra += f"{i+1}. {name} ({conf:.1f}%)<br>"

                extra += "</small>"

                result = main_result + extra

                DiseasePrediction.objects.create(
                    image="uploads/" + filename,
                    result=main_result
                )

            except Exception as e:
                result = f"Error: {str(e)}"

    return render(
        request,
        "disease.html",
        {
            "result": result,
            "uploaded_image_url": uploaded_image_url,
            "model_choices": model_choices
        }
    )




@never_cache
@login_required
def dashboard_view(request):
    return render(request, "dashboard.html")




def register_view(request):

    if request.method == "POST":

        form = RegisterForm(request.POST)

        if form.is_valid():

            form.save()

            return redirect("login")

    else:

        form = RegisterForm()

    return render(
        request,
        "register.html",
        {
            "form": form
        }
    )


