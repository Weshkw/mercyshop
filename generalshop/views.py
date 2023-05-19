import requests
from django.shortcuts import render, redirect
from django.shortcuts import render,redirect,get_object_or_404
from django.db.models import Q, Sum
from django.contrib.auth import authenticate,login,logout,get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from . models import InventoryProducts,MoreImages,PettyCosts,OtherPettyCosts,FeaturedVideo,Order,OrderedProduct
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
import json





# Create your views here.

def login_user(request):
    Page= 'login'

    if request.method=='POST':
        usernm = request.POST.get('username')
        passwd = request.POST.get('password')

        # authenticate user using custom user model
        user = authenticate(request, id_number=usernm, password=passwd)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password')

    return render(request, 'generalshop/management.html', {'page': Page})



def logout_user(request):
    logout(request)
    return redirect('home')


@login_required(login_url=('login'))
def create_product(request):
    if request.method == 'POST':
        # Create a new instance of the InventoryProducts model
        product = InventoryProducts()

        # Populate the new instance with data from the form
        product.product_name = request.POST['product_name']
        product.description = request.POST['description']
        product.home_image = request.FILES.get('home_image')
        product.buying_price = request.POST['buying_price']
        product.selling_price = request.POST['selling_price']
        product.unit_amount = request.POST['unit_amount']
        product.unit_type = request.POST['unit_type']

        # Save the new instance to the database
        product.save()

        # Create MoreImages instances for each additional image uploaded
        for image in request.FILES.getlist('more_images'):
            MoreImages.objects.create(name=product, more_images=image)

    
            

        # Redirect to home page after all images are saved
        
    
    return render(request, 'generalshop/create_product.html')


#featured video
@login_required(login_url='login')
def addvideo(request):
    if request.method == 'POST':
        video_file = request.FILES.get('video')
        if video_file:
            featured_video = FeaturedVideo(video=video_file)
            featured_video.save()

    return render(request, 'generalshop/addvideo.html')


@login_required(login_url=('login'))
def petty_costs(request):
    # Get the current user
    employee = request.user

    if request.method == 'POST':
        # Extract form data
        activity = request.POST.get('activity')
        transport_cost = request.POST.get('transport_cost')
        lunch_cost = request.POST.get('lunch_cost')
        airtime_cost = request.POST.get('airtime_cost')
        others = request.POST.get('others')
        expense = request.POST.get('expense')

        if transport_cost == '':
            transport_cost = 0.00
        if lunch_cost == '':
            lunch_cost = 0.00
        if airtime_cost == '':
            airtime_cost = 0.00
        if others=='':
            others = None
        if expense=='':
            expense = 0.00
        
        

        # Create a new PettyCosts object for the current user
        petty_costs = PettyCosts.objects.create(employee=employee, activity=activity, 
                                                 transport_cost=transport_cost, 
                                                 lunch_cost=lunch_cost, 
                                                 airtime_cost=airtime_cost)
        
        # Create a new OtherPettyCosts object for the current user
        other_petty_costs = OtherPettyCosts.objects.create(pettycosts=petty_costs, others=others, 
                                                            expense=expense)

        # Set the user for the other petty costs object
        other_petty_costs.employee = request.user
        other_petty_costs.save()

        # Redirect to the same page to prevent resubmitting the form
        return redirect('pettycosts')
    
    
    


    # Get all PettyCosts and OtherPettyCosts objects for the current user
    petty_costs_list = PettyCosts.objects.filter(employee=employee).order_by('-date_created')
    other_petty_costs_list = OtherPettyCosts.objects.filter(pettycosts__employee=employee).order_by('-date_created')

        # Calculate the totals of all attributes
    transport_cost_total = sum(p.transport_cost for p in petty_costs_list)
    lunch_cost_total = sum(p.lunch_cost for p in petty_costs_list)
    airtime_cost_total = sum(p.airtime_cost for p in petty_costs_list)
    others_total = sum(o.expense for o in other_petty_costs_list if o.others is not None)
    expense_total = sum(o.expense for o in other_petty_costs_list)

    context = {
        'petty_costs_list': petty_costs_list,
        'other_petty_costs_list': other_petty_costs_list,
        'transport_cost_total': transport_cost_total,
        'lunch_cost_total': lunch_cost_total,
        'airtime_cost_total': airtime_cost_total,
        'others_total': others_total,
        'expense_total': expense_total,
    }

    # Render the form
    return render(request, 'generalshop/petty_costs.html', context)


def homepage(request):
    products = InventoryProducts.objects.all()
    videoss= FeaturedVideo.objects.all()
    context = {'products': products, 'videoss':videoss}
    
    
    return render(request, 'generalshop/home.html', context)


def search(request):
    search_term = request.GET.get('query')
    results = []

    if search_term:
        # Filter the InventoryProducts model to get the searched item
        products = InventoryProducts.objects.filter(
            Q(product_name__icontains=search_term) |
            Q(description__icontains=search_term) |
            Q(selling_price__icontains=search_term)
        )

        # Loop through each product and get all associated images
        for product in products:
            images = product.moreimages.all()
            result = {'product': product, 'images': images}
            # Add each product and its images to the results list
            results.append(result)

    context = {'results': results, 'search_term': search_term}
    return render(request, 'generalshop/home.html', context)


def moreinfo(request, pk):
    # get the product with the given ID
    product = get_object_or_404(InventoryProducts, pk=pk)
    more_images = MoreImages.objects.filter(name=product)
    return render(request, 'generalshop/moreinfo.html', {'more_images': more_images, 'product': product})

def cart(request):
    
   order, created = Order.objects.get_or_create(complete=False)
   items=order.ordered_products.all()

   context={'items':items, 'order':order}
   return render(request, 'generalshop/cart.html',context)

def add_to_cart(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']

    product = InventoryProducts.objects.get(id=productId)
    order, created = Order.objects.get_or_create(complete=False)

    item, created = OrderedProduct.objects.get_or_create(product=product, order=order)
    if action == 'add':
      item.quantity += 1
    

    item.save()

    return JsonResponse('successifully added', safe=False)



def increaseQuantityOfCartProduct(request):
  data = json.loads(request.body)
  productId = data['productId']
  action = data['action']
  product = InventoryProducts.objects.get(id=productId)
  order, created = Order.objects.get_or_create(complete=False)
  item, created = OrderedProduct.objects.get_or_create(product=product, order=order)
  if action == 'add':
    item.quantity += 1
    item.save()
    return JsonResponse({
      'success': True,
      'message': f'Successfully increased the quantity of {item}',
      'quantity': item.quantity,
      'total': item.get_total,
      'order_total': order.get_order_total
    })
  else:
    return JsonResponse({
      'success': False,
      'message': 'Invalid action'
    })
  


def decreaseQuantityOfCartProduct(request):
  data = json.loads(request.body)
  productId = data['productId']
  action = data['action']
  product = InventoryProducts.objects.get(id=productId)
  order, created = Order.objects.get_or_create(complete=False)
  item, created = OrderedProduct.objects.get_or_create(product=product, order=order)
  if action == 'subtract':
    item.quantity -= 1
    item.save()


 # check if the quantity is zero and delete the item
  if item.quantity < 1:
     
     item.delete()

     return JsonResponse({
     'success': True,
     'message': f'Successfully deleted {item}',
     'order_total': order.get_order_total
     })
  
  else:
  
    return JsonResponse({
      'success': True,
      'message': f'Successfully decreased the quantity of {item}',
      'quantity': item.quantity,
      'total': item.get_total,
      'order_total': order.get_order_total
    })
   

def deleteCartItem(request):
 data = json.loads(request.body)
 productId = data['productId']
 product = InventoryProducts.objects.get(id=productId)
 order, created = Order.objects.get_or_create(complete=False)
 item, created = OrderedProduct.objects.get_or_create(product=product, order=order)

 # delete the item from the order
 item.delete()

 return JsonResponse({
 'success': True,
 'message': f'Successfully deleted {item}',
 'order_total': order.get_order_total
 })


 

 
 
def checkout(request):
    context={}
    return render(request, 'generalshop/checkout.html',context)