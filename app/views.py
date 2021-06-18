
from re import M
import re
from django.core import serializers
from django.http.response import JsonResponse
from django.shortcuts import render_to_response
from django.template import RequestContext, context
from django.contrib import messages
import io
import codecs
import csv,json
from django.template import loader
from django.template.loader import get_template
from django.db.models import Q, query
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django import template
from .models import TestBale, Bale
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.db.models import Sum
from datetime import datetime
from django.views.decorators.csrf import csrf_exempt
from django.core.serializers import serialize
from rest_framework.decorators import api_view
from django.views.decorators.csrf import csrf_exempt
import json
from django.core.serializers import serialize
from django.db.models import Avg, Max, Min, Sum
from .serializers import BalesSerializer
# @login_required(login_url="/login/")
# def index(request):
#     context = {}
#     context['segment'] = 'dashboard'

#     html_template = loader.get_template( 'dashboard.html' )
#     return HttpResponse(html_template.render(context, request))

@login_required(login_url="/login/")
def pages(request):
    context = {}
    # All resource paths end in .html.
    # Pick out the html file name from the url. And load that template.
    try:
        
        load_template      = request.path.split('/')[-1]
        context['segment'] = load_template
        
        html_template = loader.get_template( load_template )
        return HttpResponse(html_template.render(context, request))
        
    except template.TemplateDoesNotExist:

        html_template = loader.get_template( 'page-404.html' )
        return HttpResponse(html_template.render(context, request))

    except:
    
        html_template = loader.get_template( 'page-500.html' )
        return HttpResponse(html_template.render(context, request))

@login_required(login_url="/login/")
def dashboard(request):
    User = get_user_model()
    users = len(User.objects.all())
    bales = len(Bale.objects.all())
    lots = len(Bale.objects.values_list('Lot_ID', flat=True).distinct())
    Station = len(Bale.objects.values_list('Station', flat=True).distinct())
    test = len(TestBale.objects.all())
    
    context = {
    'users':users,
    'bales':bales,
    'lots':lots,
    'Station':Station,
    'test':test,
    }
    return render(request,"dashboard.html",context)


@login_required(login_url="/login/")
def settings(request):
    return render(request,'settings.html')


@login_required(login_url="/login/")
@csrf_exempt
def viewmybales(request):
    User = get_user_model()
    users = User.objects.all()
    data = TestBale.objects.all()
    query = request.user
    if request.user.is_superuser:
        bales = Bale.objects.all()
    else:
       bales = Bale.objects.filter(Q(user__exact=query))
    # rbales = Bale.objects.filter(Q(user__exact=query))
    # bales = Bale.objects.all()
    newdata = []
    # bales = Bale.objects.raw("SELECT id, Bale_ID, COUNT(Bale_ID) as count_of_bales, Station, variety, weightinkg, MAX(Staple_length) as max_sl, min(Staple_length) as min_sl, max(Micronaire), min(Micronaire), max(Rd), min(Rd), "
                            #  "Organic, BCI FROM app_bale GROUP BY Station")
    new_data = []
    unique_station = {}
    for j,i in enumerate(bales):
        bales_count = Bale.objects.filter(Lot_ID=i.Lot_ID).filter().count()
        if i.Lot_ID in unique_station:
            continue
        else:
            unique_station[i.Lot_ID] = True
            new_data.append({
                'Station': i.Station,
                'variety': i.variety,
                'Bale_ID': bales_count,
                'Lot_ID':i.Lot_ID,
                'Micronaire': i.Micronaire,
                'Staple_length': i.Staple_length ,
                'Rd':i.Rd,
                'Available_For_Sale':i.Available_For_Sale,
                'Spot_Price': i.Spot_Price,
                'weightinkg': i.weightinkg,
                'Organic': i.Organic,
                'BCI': i.BCI,
                'GTex': i.GTex,
                'user': i.user
            })
    print("🚀 ~ file: views.py ~ line 375 ~ new_data", new_data)
    # if request.method == 'POST':
    #     arr = json.loads(request.body)
    #     newlist = arr['arr']
    #     for i in newlist:
            
    #         multi = Bale.objects.filter(Q(user__username__exact=str(i)))
    #         print("multi",multi)
    #     if len(multi) > 0:
    #         new = serialize('json', multi)
    #         newdata.append(new)
    #     else:
    #         print("*************** ")
    #     print(newdata)
    #     return JsonResponse(newdata,safe=False)
    return render(request,'viewmybales.html',{'data':data,'users':users,'bales':new_data,'rbales':new_data})

@login_required(login_url="/login/")
@csrf_exempt
def available_for_sale(request):
    data= json.loads(request.body)
    sale_id = data['id']
    sale_value =  data['value']
    bales = Bale.objects.filter(Lot_ID=sale_id)
    for bale in bales:

        if sale_value == "True":
            bale.Available_For_Sale = False
        else:
            bale.Available_For_Sale = True
        bale.save()
    return JsonResponse({"msg": "success"},safe=False)

@login_required(login_url="/login/")
def addbales(request):
    data = TestBale.objects.all()
    User = get_user_model()
    users = User.objects.all()
    if request.method == "POST":
        csv_file = request.FILES['formFile']
        task = request.POST.get('country')
        print("🚀 ~ file: views.py ~ line 136 ~ task", task)
        if not csv_file.name.endswith('.csv'):
            messages.error(request, 'THIS IS NOT A CSV FILE')
        common_header =  ['\ufeffginnerid', 'baleid', 'lotid', 'variety', 'station ', 'crop year', 'staple ', 'micronaire', 'Rd', ' Gtex', 'spot_price', 'weightinkg', 'for_sale', 'organic', 'BCI']
        # common_header = ['ginnerid,baleid,lotid,variety,station,crop year,staple,micronaire,Rd,Gtex,spot_price,weightinkg,for_sale,organic,BCI\r\n']
        # for index,row in enumerate(csv_file):
        #     data = row.decode('utf-8')
        #     if data:
        #         line = data.split('","')
        #         # print("🚀 ~ file: views.py ~ line 125 ~ line", line)
        #     if index == 0:
        #         if (line != common_header):
        #             messages.error(request, 'THIS IS NOT SAME HEADER CSV FILE')
        #         else:
        #             messages.success(request, 'THIS IS SAME HEADER CSV FILE')
        # data_set = csv_file.read().decode('UTF-8')
        # io_string = io.StringIO(data_set)
        # next(io_string)
        # for column in csv.reader(data_set, delimiter=',', quotechar="|"):
                    # print("🚀 ~ file: views.py ~ line 152 ~ column",  row[0],row[1])
            # _, created = Bale.objects.update_or_create(
            #     ginnerid = column[0],
            #     Bale_ID=column[1],
            #     Lot_ID=column[2],
            #     variety = column[3],
            #     Station=column[4],
            #     Crop_Year=column[5],
            #     Staple_length=column[6],
            #     Micronaire=column[7],
            #     Rd= column[8],
            #     GTex= column[9],
            #     Spot_Price=column[10],
            #     weightinkg= column[11],
            #     Available_For_Sale= column[12],
            #     Organic=column[13],
            #     BCI=column[14],
            #     user = User.objects.get(id=request.user.id)
            # )
        reader = csv.reader(codecs.iterdecode(csv_file, 'utf-8'))
        for j,column in enumerate(reader):
            if j == 0:
                print("🚀 ~ file: views.py ~ line 441 ~ i", column)
                # print("🚀 ~ file: views.py ~ line 430 ~ common_header != i", common_header != i)
                if common_header != column:
                    messages.error(request, 'THIS IS NOT SAME HEADER CSV FILE')
                    break
                else:
                    messages.success(request, 'THIS IS SAME HEADER CSV FILE')
            if j != 0:
                
                # print("🚀 ~ file: views.py ~ line 186 ~ column", column[0],column[1])

                print("🚀 ~ file: views.py ~ line 441 ~ i")
                For_Sale = column[12]
                org = column[13]
                bci = column[14]
                if For_Sale == "TRUE":
                    sale = True
                else:
                    sale = False
                if org == "TRUE":
                    org_up = True
                else:
                    org_up = False
                if bci == "TRUE":
                    bci_up = True
                else:
                    bci_up = False
                created = Bale(
                    ginnerid = column[0],
                    Bale_ID=column[1],
                    Lot_ID=column[2],
                    variety = column[3],
                    Station=column[4],
                    Crop_Year=column[5],
                    Staple_length=column[6],
                    Micronaire=column[7],
                    Rd= column[8],
                    GTex= column[9],
                    Spot_Price=column[10],
                    weightinkg= column[11],
                    Available_For_Sale= sale,
                    Organic=org_up,
                    BCI=bci_up,
                    user = User.objects.get(id=request.user.id)
                )
                created.save()
              
        return render(request,'addbales.html',{"users":users})
    return render(request,'addbales.html',{"users":users})

# from .models import Bale
# Create your views here.
@login_required(login_url="/login/")
def addtestdata(request):
    data = TestBale.objects.all()
    if request.method == "POST":
        # csv_file = request.FILES['formFile']
        # if not csv_file.name.endswith('.csv'):
        #     messages.error(request, 'THIS IS NOT A CSV FILE')
        # data_set = csv_file.read().decode('UTF-8')
        # io_string = io.StringIO(data_set)
        # next(io_string)
        # for column in csv.reader(io_string, delimiter=',', quotechar="|"):
        #     _, created = TestBale.objects.update_or_create(
        #         Bale_ID=column[0],
        #         Staple_length=column[1],
        #         Trash=column[2],
        #         Bundle_Strength=column[3],
        #         Micronaire=column[4],
        #         Rd=column[5],
        #         b=column[6],
        #     )
        csv_file = request.FILES['formFile']
        common_header = ['Bale ID,Staple length,Trash,Bundle Strength,Micronaire,Rd,+b,test by fc,test_report\r\n']
        if not csv_file.name.endswith('.csv'):
            messages.error(request, 'THIS IS NOT A CSV FILE')
        for index,row in enumerate(csv_file):
            data = row.decode('utf-8')
            if data:
                line = data.split('","')
                print("🚀 ~ file: views.py ~ line 180 ~ line", line)
            if index == 0:
                if (line != common_header):
                    messages.error(request, 'THIS IS NOT SAME HEADER CSV FILE')
                else:
                    messages.success(request, 'THIS IS SAME HEADER CSV FILE')
        return render(request,'addtestdata.html',{'data':data})
    return render(request,'addtestdata.html')

@login_required(login_url="/login/")
@csrf_exempt
def searchbales(request):
    # request.body
   
    bales = Bale.objects.raw("SELECT id, Bale_ID, COUNT(Bale_ID) as count_of_bales, Station, variety, weightinkg, MAX(Staple_length) as max_sl, min(Staple_length) as min_sl, max(Micronaire), min(Micronaire), max(Rd), min(Rd), "
                            "Organic, BCI FROM app_bale GROUP BY Station")
    new_data = []
    for i in bales:

        LOt_id = Bale.objects.get(Bale_ID=i.Bale_ID,Lot_ID=i.Lot_ID,Station=i.Station,variety=i.variety)
        print("🚀 ~ file: views.py ~ line 310 ~ bale_id", LOt_id.Lot_ID)
        
        for_sale_count = Bale.objects.filter(Station=i.Station).filter(Available_For_Sale=True).count()

        max_staple = Bale.objects.filter(Station=i.Station).filter(variety=i.variety).aggregate(Max('Staple_length'))[
            'Staple_length__max']
        min_staple = Bale.objects.filter(Station=i.Station).filter(variety=i.variety).aggregate(Min('Staple_length'))[
            'Staple_length__min']

        max_mic = Bale.objects.filter(Station=i.Station).filter(variety=i.variety).aggregate(Max('Micronaire'))[
            'Micronaire__max']
        min_mic = Bale.objects.filter(Station=i.Station).filter(variety=i.variety).aggregate(Min('Micronaire'))[
            'Micronaire__min']

        max_rd = Bale.objects.filter(Station=i.Station).filter(variety=i.variety).aggregate(Max('Rd'))['Rd__max']
        min_rd = Bale.objects.filter(Station=i.Station).filter(variety=i.variety).aggregate(Min('Rd'))['Rd__min']

        max_price = Bale.objects.filter(Station=i.Station).filter(variety=i.variety).aggregate(Max('Spot_Price'))['Spot_Price__max']
        min_price = Bale.objects.filter(Station=i.Station).filter(variety=i.variety).aggregate(Min('Spot_Price'))['Spot_Price__min']

        organic_count = Bale.objects.filter(Station=i.Station).filter(variety=i.variety).filter(Organic=True).count()
        bci_count = Bale.objects.filter(Station=i.Station).filter(variety=i.variety).filter(BCI=True).count()

        max_gtex = Bale.objects.filter(Station=i.Station).filter(variety=i.variety).aggregate(Max('GTex'))['GTex__max']
        min_gtex = Bale.objects.filter(Station=i.Station).filter(variety=i.variety).aggregate(Min('GTex'))['GTex__min']
        
            # bales_count = Bale.objects.filter(Lot_ID=i.Lot_ID).filter().count()

        new_data.append({
            'Lot_ID':i.Lot_ID,
            'station': i.Station,
            'variety': i.variety,
            'total_bales': i.count_of_bales,
            'for_sale': for_sale_count,
            'mic_range': str(min_mic) + " - " + str(max_mic),
            'staple_range': str(min_staple) + " - " + str(max_staple),
            'rd_range': str(min_rd) + " - " + str(max_rd),
            'price_range': str(min_price) + " - " + str(max_price),
            'organic_count': str(organic_count),
            'bci_count': str(bci_count),
            'gtex_range': str(min_gtex) + " - " + str(max_gtex),
        })
    print("🚀 ~ file: views.py ~ line 375 ~ new_data", new_data)
    return render(request,"searchbales.html",{"list_data":new_data})
        # return HttpResponse(
        #     json.dumps(new_data),
        #     content_type="application/json"
        # )
    # bales = Bale.objects.all()
    # if request.method == 'GET':
    #     query= request.GET.get('q')
    #     submitbutton= request.GET.get('submit')
    #     if query is not None:
    #         lookups= Q(Bale_ID__icontains=query) | Q(Lot_ID__icontains=query) | Q(Station__icontains=query) | Q(Crop_Year__icontains=query) | Q(Pick__icontains=query) | Q(Staple_Type__icontains=query) | Q(Staple_length__icontains=query) | Q(Trash__icontains=query) | Q(Bundle_Strength__icontains=query) | Q(Micronaire__icontains=query) | Q(Moisture__icontains=query) | Q(Asking_Price__icontains=query)
    #         results= Bale.objects.filter(lookups).distinct()
    #         context={'results': results,
    #                  'submitbutton': submitbutton}
    #         return render(request, 'searchbales.html', context)
    return render(request,"searchbales.html")

@login_required(login_url="/login/")
@csrf_exempt
def searchbalesdata(request):
    # user = request.user
    bales = Bale.objects.raw("SELECT id, Bale_ID, COUNT(Bale_ID) as count_of_bales, Station, variety, weightinkg, MAX(Staple_length) as max_sl, min(Staple_length) as min_sl, max(Micronaire), min(Micronaire), max(Rd), min(Rd), "
                             "Organic, BCI FROM app_bale GROUP BY Station")
    new_data = []
    for i in bales:

        
        for_sale_count = Bale.objects.filter(Station=i.Station).filter(Available_For_Sale=True).count()

        max_staple = Bale.objects.filter(Station=i.Station).filter(variety=i.variety).aggregate(Max('Staple_length'))[
            'Staple_length__max']
        min_staple = Bale.objects.filter(Station=i.Station).filter(variety=i.variety).aggregate(Min('Staple_length'))[
            'Staple_length__min']

        max_mic = Bale.objects.filter(Station=i.Station).filter(variety=i.variety).aggregate(Max('Micronaire'))[
            'Micronaire__max']
        min_mic = Bale.objects.filter(Station=i.Station).filter(variety=i.variety).aggregate(Min('Micronaire'))[
            'Micronaire__min']

        max_rd = Bale.objects.filter(Station=i.Station).filter(variety=i.variety).aggregate(Max('Rd'))['Rd__max']
        min_rd = Bale.objects.filter(Station=i.Station).filter(variety=i.variety).aggregate(Min('Rd'))['Rd__min']

        max_price = Bale.objects.filter(Station=i.Station).filter(variety=i.variety).aggregate(Max('Spot_Price'))['Spot_Price__max']
        min_price = Bale.objects.filter(Station=i.Station).filter(variety=i.variety).aggregate(Min('Spot_Price'))['Spot_Price__min']

        organic_count = Bale.objects.filter(Station=i.Station).filter(variety=i.variety).filter(Organic=True).count()
        bci_count = Bale.objects.filter(Station=i.Station).filter(variety=i.variety).filter(BCI=True).count()

        max_gtex = Bale.objects.filter(Station=i.Station).filter(variety=i.variety).aggregate(Max('GTex'))['GTex__max']
        min_gtex = Bale.objects.filter(Station=i.Station).filter(variety=i.variety).aggregate(Min('GTex'))['GTex__min']


        new_data.append({
            'Lot_ID':i.Lot_ID,
            'station': i.Station,
            'variety': i.variety,
            'total_bales': i.count_of_bales,
            'for_sale': for_sale_count,
            'mic_range': str(min_mic) + " - " + str(max_mic),
            'staple_range': str(min_staple) + " - " + str(max_staple),
            'rd_range': str(min_rd) + " - " + str(max_rd),
            'price_range': str(min_price) + " - " + str(max_price),
            'organic_count': str(organic_count),
            'bci_count': str(bci_count),
            'gtex_range': str(min_gtex) + " - " + str(max_gtex),
        })
    print("🚀 ~ file: views.py ~ line 375 ~ new_data", new_data)
    return HttpResponse(
        json.dumps(new_data),
        content_type="application/json"
    )

# @login_required(login_url="/login/")
# @csrf_exempt
# def searchbales(request):
#     bales = Bale.objects.raw("SELECT id, Bale_ID, COUNT(Bale_ID) as count_of_bales, Station, variety, weightinkg, MAX(Staple_length) as max_sl, min(Staple_length) as min_sl, max(Micronaire), min(Micronaire), max(Rd), min(Rd), "
#                              "Organic, BCI FROM app_bale GROUP BY Station, variety")
#     new_data = []
#     for i in bales:

#         for_sale_count = Bale.objects.filter(Station=i.Station).filter(variety=i.variety).filter(Available_For_Sale=True).count()

#         max_staple = Bale.objects.filter(Station=i.Station).filter(variety=i.variety).aggregate(Max('Staple_length'))[
#             'Staple_length__max']
#         min_staple = Bale.objects.filter(Station=i.Station).filter(variety=i.variety).aggregate(Min('Staple_length'))[
#             'Staple_length__min']

#         max_mic = Bale.objects.filter(Station=i.Station).filter(variety=i.variety).aggregate(Max('Micronaire'))[
#             'Micronaire__max']
#         min_mic = Bale.objects.filter(Station=i.Station).filter(variety=i.variety).aggregate(Min('Micronaire'))[
#             'Micronaire__min']

#         max_rd = Bale.objects.filter(Station=i.Station).filter(variety=i.variety).aggregate(Max('Rd'))['Rd__max']
#         min_rd = Bale.objects.filter(Station=i.Station).filter(variety=i.variety).aggregate(Min('Rd'))['Rd__min']

#         max_price = Bale.objects.filter(Station=i.Station).filter(variety=i.variety).aggregate(Max('Spot_Price'))['Spot_Price__max']
#         min_price = Bale.objects.filter(Station=i.Station).filter(variety=i.variety).aggregate(Min('Spot_Price'))['Spot_Price__min']

#         organic_count = Bale.objects.filter(Station=i.Station).filter(variety=i.variety).filter(Organic=True).count()
#         bci_count = Bale.objects.filter(Station=i.Station).filter(variety=i.variety).filter(BCI=True).count()

#         max_gtex = Bale.objects.filter(Station=i.Station).filter(variety=i.variety).aggregate(Max('GTex'))['GTex__max']
#         min_gtex = Bale.objects.filter(Station=i.Station).filter(variety=i.variety).aggregate(Min('GTex'))['GTex__min']

#         new_data.append({
#             'station': i.Station,
#             'variety': i.variety,
#             'total_bales': i.count_of_bales,
#             'for_sale': for_sale_count,
#             'mic_range': str(min_mic) + " - " + str(max_mic),
#             'staple_range': str(min_staple) + " - " + str(max_staple),
#             'rd_range': str(min_rd) + " - " + str(max_rd),
#             'price_range': str(min_price) + " - " + str(max_price),
#             'organic_count': str(organic_count),
#             'bci_count': str(bci_count),
#             'gtex_range': str(min_gtex) + " - " + str(max_gtex),
#         })
#     return render(request,"searchbales.html",{"list_data":new_data})



def handler404(request,exception):
    return render(request, '404.html', status=404)
def handler500(request):
    return render(request, '500.html', status=500)

def handler403(request,exception):
    return render(request, '403.html', status=403)

@login_required(login_url="/login/")
@csrf_exempt
def auction_my_bales(request):
    User = get_user_model()
    users = User.objects.all()
    query = request.user
    rbales = Bale.objects.filter(Q(user__exact=query))
    bales = Bale.objects.all()
    return render(request,'auction_my_bales.html',{'users':users,'bales':bales,'rbales':rbales})

@login_required(login_url="/login/")
@csrf_exempt
def seeks_bids_to_supply(request):
    return render(request,'seeks_bids_to_supply.html')


@login_required(login_url="/login/")
@csrf_exempt
def live_auction(request):
    return render(request,'live_auction.html')

@csrf_exempt
def all_bales(request,lotID):
    print("🚀 ~ file: views.py ~ line 434 ~ lotID", lotID)
    data = Bale.objects.filter(Lot_ID=lotID)
    print("🚀 ~ file: views.py ~ line 435 ~ data", data)
    # return HttpResponse(
    #     json.dumps(data),
    #     content_type="application/json"
    # )
    data1 = BalesSerializer(data,many=True)
    return render(request,'all_bales.html',{"data":data1.data})
    # return JsonResponse(data1.data,safe=False)



@login_required(login_url="/login/")
@csrf_exempt
def searchform(request):
    if request.method == 'POST':
        data = request.POST
        bales = Bale.objects.filter(Q(Station=data.get("Station","")) | Q(Lot_ID=data.get("Lot_ID","")) | Q(variety=data.get("variety","")) | Q(Bale_ID=data.get("Bale_ID",""))
                                    # | Q(Micronaire=data["Micronaire"]) | Q(Rd=data["Rd"]) | Q(GTex=data["GTex"]) | Q(Spot_Price=data["Spot_Price"])
                                    # | Q(weightinkg__exact=data["weightinkg"]) | Q(Available_For_Sale=data.get("Available_For_Sale",None)) | Q(Organic=data.get("Organic",None))
                                    # | Q(BCI__icontains=data.get("BCI",None)) | Q(Moisture=data["Trash"]) | Q(Pick=data["Pick"]) | Q(Crop_Year=data['Crop_Year'])
                                    )
        ser_data = BalesSerializer(bales,many=True)
        return render(request,'searchform.html',{"data":ser_data.data})
    return render(request,'searchform.html')