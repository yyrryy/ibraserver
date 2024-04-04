from django.db import models
from django.contrib.auth.models import User
import datetime
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
import uuid
import json
from django.db.models import Count, F, Sum, Q
import re
# Create your models here.

class Category(models.Model):
    name=models.CharField(max_length=150, default=None, null=True, blank=True)
    affichage=models.CharField(max_length=150, default=None, null=True, blank=True)
    code=models.CharField(max_length=150, default=None, null=True)
    masqueclients=models.BooleanField(default=False)
    excludedrep=models.ManyToManyField('Represent', default=None, blank=True)
    image=models.ImageField(upload_to='categories_images/', null=True, blank=True)
    def __str__(self) -> str:
        return self.name
    



class Mark(models.Model):
    name=models.CharField(max_length=20)
    image=models.ImageField(upload_to='marques_images/', null=True, blank=True, default=None)
    masqueclients=models.BooleanField(default=False)
    excludedrep=models.ManyToManyField('Represent', default=None, blank=True)
    def __str__(self) -> str:
        return self.name


class Carlogos(models.Model):
    name=models.CharField(max_length=20)
    image=models.ImageField(upload_to='carlogos_images/', null=True, blank=True, default=None)
    def __str__(self) -> str:
        return self.name


class Produit(models.Model):
    name=models.CharField(max_length=500, null=True)
    block=models.CharField(max_length=500, null=True, default=None)
    # code = classement
    code=models.CharField(max_length=500, null=True)
    coderef=models.CharField(max_length=500, null=True, default=None)
    #price
    buyprice= models.FloatField(default=None, null=True, blank=True)
    supplier=models.ForeignKey('Supplier', on_delete=models.CASCADE, default=None, null=True, blank=True, related_name='supplier')
    sellprice=models.FloatField(default=None, null=True, blank=True)
    sellpricebrut=models.FloatField(default=None, null=True, blank=True)
    coutmoyen=models.FloatField(default=None, null=True, blank=True)
    remise=models.IntegerField(default=35, null=True, blank=True)
    #checkprice= models.FloatField(default=None, null=True, blank=True)
    prixnet=models.FloatField(default=None, null=True, blank=True)
    devise=models.FloatField(default=None, null=True, blank=True)
    representprice=models.FloatField(default=None, null=True, blank=True)
    representremise=models.FloatField(default=0, null=True, blank=True)
    lastsellprice=models.FloatField(default=None, null=True, blank=True)
    #stock
    refeq1=models.CharField(max_length=500, default=None, null=True, blank=True)
    refeq2=models.CharField(max_length=500, default=None, null=True, blank=True)
    refeq3=models.CharField(max_length=500, default=None, null=True, blank=True)
    refeq4=models.CharField(max_length=500, default=None, null=True, blank=True)
    stockprincipal=models.IntegerField(default=None, null=True, blank=True)
    stockdepot=models.IntegerField(default=None, null=True, blank=True)
    stocktotal=models.IntegerField(default=None, null=True, blank=True)
    stockfacture=models.IntegerField(default=None, null=True, blank=True)
    stockbon=models.IntegerField(default=None, null=True, blank=True)
    # stock=models.BooleanField(default=True)
    # add equivalent in refs
    equivalent=models.TextField(default=None, null=True, blank=True)
    famille=models.CharField(max_length=500, default=None, null=True, blank=True)
    cars=models.TextField(default=None, null=True, blank=True)
    #ref
    ref=models.CharField(max_length=50)
    diametre=models.CharField(max_length=500, default=None, null=True, blank=True)

    # reps that will have the price applied
    repsprice=models.CharField(max_length=500, default=None, null=True, blank=True)
    #image
    image = models.ImageField(upload_to='products_imags/', null=True, blank=True)
    mark=models.ForeignKey(Mark, on_delete=models.CASCADE, default=None, null=True, blank=True)
    #cartgrise
    # n_chasis=models.CharField(max_length=50, null=True)
    minstock=models.IntegerField(default=None, null=True, blank=True)
    carlogos=models.ForeignKey(Carlogos, default=None, blank=True, null=True, on_delete=models.CASCADE)
    # min cmmand
    isnew=models.BooleanField(default=False)
    min=models.IntegerField(default=1, null=True, blank=True)
    isoffer=models.BooleanField(default=False)
    offre=models.CharField(max_length=500, default=None, null=True, blank=True)
    category=models.ForeignKey(Category,on_delete=models.CASCADE, default=None, null=True, blank=True)
    isactive=models.BooleanField(default=True)
    # commande
    iscommanded=models.BooleanField(default=False)
    suppliercommand=models.ForeignKey('Supplier', on_delete=models.CASCADE, default=None, null=True, blank=True, related_name='suppliercommand')
    # stock facture
    # stock bon
    def __str__(self) -> str:
        return self.ref
    def code_sort_key(self):
        # Custom sorting key function
        parts = [part.isdigit() and int(part) or part for part in re.split(r'(\d+)', self.code)]
        return parts
    
    def getprofit(self):
        try:
            # prix vente net - cout moyen
            # use Stockin model to get total quantity entered of this product
            entered=Stockin.objects.filter(product=self).aggregate(Sum('quantity'))['quantity__sum']
            cost=round(entered*self.coutmoyen,2)
            # use Orderitem model to get total quantity sold of this product
            sold=Livraisonitem.objects.filter(product=self).aggregate(Sum('total'))['total__sum']
            return round(sold-cost, 2)
        except:
            return 'NO DATA'
    def getpercentage(self):
        try:
            return 100*(self.prixnet-self.buyprice)/self.prixnet
        except:
            return 0
    def getequivalent(self):
        if self.equivalent:
            if '+' in self.equivalent:
                return self.equivalent.split('+')+['-', '-']
            return [self.equivalent, '-', '-']
    def getcommercialsprice(self):
        try:
            return json.loads(self.repsprice)
        except:
            return []
        
    def getcars(self):
        try:
            return json.loads(self.cars)
        except:
            return []
    # brand=models.CharField(max_length=25, default=None)
    # model=models.CharField(max_length=25, default=None)
    # mark=models.CharField(max_length=25, default=None)
    
# cupppon codes table



class Attribute(models.Model):
    product=models.ForeignKey(Produit, on_delete=models.CASCADE, default=None)
    name=models.CharField(max_length=50)
    value=models.CharField(max_length=50)
    

class Supplier(models.Model):
    name=models.CharField(max_length=500)
    address=models.CharField(max_length=500, default=None, null=True, blank=True)
    phone=models.CharField(max_length=500, default=None, null=True, blank=True)
    total=models.FloatField(default=0.00)
    rest=models.FloatField(default=0.00)




class Itemsbysupplier(models.Model):
    supplier= models.ForeignKey(Supplier, on_delete=models.CASCADE, default=None, null=True, blank=True, related_name='provider')
    date = models.DateTimeField(default=None)
    #date saisie
    dateentree=models.DateTimeField(default=datetime.datetime.now, blank=True, null=True)
    items = models.TextField(blank=True, null=True, help_text='Quantity and Product name would save in JSON format')
    total = models.FloatField(default=0.00)
    tva = models.FloatField(default=0.00, null=True, blank=True)
    rest = models.FloatField(default=0.00)
    nbon = models.CharField(max_length=100, blank=True, null=True)
    ispaid=models.BooleanField(default=False)
    isfacture=models.BooleanField(default=False)
    def __str__(self) -> str:
        return f'{self.nbon} - {self.id}'

class Stockin(models.Model):
    product=models.ForeignKey(Produit, on_delete=models.CASCADE, default=None)
    date=models.DateField()
    quantity=models.IntegerField()
    price=models.FloatField(default=0.00)
    devise=models.FloatField(default=0.00)
    # to delete stock facture is stock in is facture
    facture=models.BooleanField(default=False)
    # qtyofprice will be used to track qty of this price
    qtyofprice=models.IntegerField(default=0)
    remise=models.IntegerField(default=0)
    total=models.FloatField(default=0.00)
    supplier=models.ForeignKey(Supplier, on_delete=models.CASCADE, default=None)
    nbon=models.ForeignKey(Itemsbysupplier, on_delete=models.CASCADE, default=None, null=True, blank=True)
    isavoir=models.BooleanField(default=False)
    avoir=models.ForeignKey('Avoirclient', on_delete=models.CASCADE, default=None, null=True, blank=True)
class Pricehistory(models.Model):
    date=models.DateField()
    product=models.ForeignKey(Produit, on_delete=models.CASCADE, default=None)
    price=models.FloatField()

class Coupon(models.Model):
    code = models.CharField(max_length=50)
    amount = models.FloatField()

class Region(models.Model):
    name=models.CharField(max_length=500)
    def __str__(self) -> str:
        return self.name
# can command
class Client(models.Model):
    represent=models.ForeignKey('Represent', on_delete=models.CASCADE, default=None, null=True)
    user = models.OneToOneField(User, on_delete=models.SET_NULL, default=None, null=True)
    name=models.CharField(max_length=200)
    code=models.CharField(max_length=200, null=True, default=None)
    ice=models.CharField(max_length=200, null=True, default=None)
    city=models.CharField(max_length=200, null=True, default=None)
    region=models.CharField(max_length=200, null=True, default=None)
    total=models.FloatField(default=0.00, null=True, blank=True)
    soldtotal=models.FloatField(default=0.00, null=True, blank=True)
    soldbl=models.FloatField(default=0.00, null=True, blank=True)
    soldfacture=models.FloatField(default=0.00, null=True, blank=True)
    address=models.CharField(max_length=200)
    phone=models.CharField(max_length=200, default=None, null=True)
    def __str__(self) -> str:
        return self.name+'-'+str(self.city)

class Represent(models.Model):
    user = models.OneToOneField(User, on_delete=models.SET_NULL, default=None, null=True)
    name=models.CharField(max_length=50)
    phone=models.CharField(max_length=50, default=None, null=True)
    region=models.CharField(max_length=100, default=None, null=True)
    image = models.ImageField(upload_to='slasemen_imags/', null=True, blank=True)
    caneditprice=models.BooleanField(default=False)
    info=models.TextField(default=None, null=True, blank=True)
    # wether the products will be displaied in owlcarousel or not
    slides=models.BooleanField(default=True)
    def __str__(self) -> str:
        return self.name

# orders table
class Order(models.Model):
    date = models.DateTimeField(auto_now_add=True)
    code=models.CharField(max_length=50, null=True, default=None)
    # name will be a string
    # email will be a string and not requuired
    salseman=models.ForeignKey(Represent, on_delete=models.SET_NULL, default=None, null=True)
    modpymnt=models.CharField(max_length=50, null=True, default=None)
    modlvrsn=models.CharField(max_length=50, null=True, default=None)
    note=models.TextField(default=None, null=True, blank=True)
    total=models.DecimalField(default=0.00, decimal_places=2, max_digits=20)
    # totalremise will be there i ncase pymny is cash
    totalremise=models.DecimalField(default=0.00, decimal_places=2, max_digits=20)
    # true if its generated to be a bon livraison
    isdelivered = models.BooleanField(default=False)
    ispaied = models.BooleanField(default=False)
    isclientcommnd = models.BooleanField(default=False)
    clientname=models.CharField(max_length=500, null=True, default=None)
    clientphone=models.CharField(max_length=500, null=True, default=None)
    clientaddress=models.CharField(max_length=500, null=True, default=None)
    client=models.ForeignKey(Client, on_delete=models.CASCADE, default=None, null=True)
    order_no=models.CharField(max_length=500, null=True, default=None)
    # order by date
    class Meta:
        ordering = ['-date']
    # return the name and phone

    # methode to determine wether it's delivered or not
    def save(self, *args, **kwargs):
        self.code = str(uuid.uuid4())
        super().save(*args, **kwargs)  #


class Bonlivraison(models.Model):
    commande=models.ForeignKey(Order, on_delete=models.SET_NULL, default=None, null=True, blank=True)
    date = models.DateTimeField(default=datetime.datetime.now, blank=True, null=True)
    client=models.ForeignKey(Client, on_delete=models.SET_NULL, default=None, null=True, blank=True)
    salseman=models.ForeignKey(Represent, on_delete=models.SET_NULL, default=None, null=True, blank=True)
    total=models.FloatField(default=0.00)
    rest=models.FloatField(default=0.00)
    modlvrsn=models.CharField(max_length=50, null=True, default=None)
    code=models.CharField(max_length=50, null=True, default=None)
    bon_no=models.CharField(max_length=50, null=True, default=None)
    # true when the bon is generated to be a facture
    isfacture=models.BooleanField(default=False)
    # true when the bon is DELIVERED
    isdelivered=models.BooleanField(default=False)
    # true when its paid
    ispaid=models.BooleanField(default=False)
    note=models.TextField(default=None, null=True, blank=True)
    #statud if regl == r0
    statusreg=models.CharField(max_length=50, null=True, default='n1', blank=True)
    #statud if factur == f1
    statusfc=models.CharField(max_length=50, null=True, default='b1', blank=True)
    def save(self, *args, **kwargs):
        self.code = str(uuid.uuid4())
        super().save(*args, **kwargs)
    def __str__(self) -> str:
        return self.bon_no

class Facture(models.Model):
    bon=models.ForeignKey(Bonlivraison, on_delete=models.SET_NULL, default=None, blank=True, null=True)
    date = models.DateTimeField(default=datetime.datetime.now, blank=True, null=True)
    code=models.CharField(max_length=50, null=True, default=None)
    total=models.FloatField(default=0.00)
    tva=models.FloatField(default=0.00)
    rest=models.FloatField(default=0.00)
    ispaid=models.BooleanField(default=False)
    facture_no=models.CharField(max_length=50, null=True, default=None)
    client=models.ForeignKey(Client, on_delete=models.SET_NULL, default=None, null=True)
    salseman=models.ForeignKey(Represent, on_delete=models.SET_NULL, default=None, null=True, blank=True)
    # notes of fc
    transport=models.CharField(max_length=500, null=True, default=None)

    note=models.TextField(default=None, null=True, blank=True)
    # true if facture is accounting
    isaccount=models.BooleanField(default=False)
    statusreg=models.CharField(max_length=50, null=True, default='b1', blank=True)
    def save(self, *args, **kwargs):
        self.code = str(uuid.uuid4())
        super().save(*args, **kwargs)



class PaymentSupplier(models.Model):
    supplier=models.ForeignKey(Supplier, on_delete=models.CASCADE, default=None)
    date = models.DateTimeField(default=None)
    amount = models.FloatField(default=0.00)
    mode=models.CharField(max_length=10, default=None)
    echeance=models.DateField(default=None, null=True, blank=True)
    #factures reglé onetomanys
    bons=models.ManyToManyField(Itemsbysupplier, default=None, blank=True, related_name="reglementssupp")
    npiece=models.CharField(max_length=50, default=None, null=True, blank=True)





class PaymentClientbl(models.Model):
    client=models.ForeignKey(Client, on_delete=models.CASCADE, default=None, null=True, blank=True)
    date = models.DateTimeField(default=None)
    amount = models.FloatField(default=0.00)
    mode=models.CharField(max_length=10, default=None)
    amountofeachbon=models.CharField(max_length=100000, default=None, null=True, blank=True)
    bons=models.ManyToManyField(Bonlivraison, default=None, blank=True, related_name="reglements")
    # mode: 0 bl, 1 facture
    echance=models.DateField(default=None, null=True, blank=True)
    npiece=models.CharField(max_length=50, default=None, null=True, blank=True)
    # if the regelement is used to regle facture
    usedinfacture=models.BooleanField(default=False)
    # if regl is paid if it has echeaance
    ispaid=models.BooleanField(default=False)

class Bonsregle(models.Model):
    payment=models.ForeignKey(PaymentClientbl, on_delete=models.CASCADE, default=None, null=True, blank=True)
    bon=models.ForeignKey('Bonlivraison', on_delete=models.CASCADE, default=None, null=True, blank=True)
    amount=models.FloatField(default=0.00)



class PaymentClientfc(models.Model):
    client=models.ForeignKey(Client, on_delete=models.CASCADE, default=None, null=True, blank=True)
    date = models.DateTimeField(default=None)
    amount = models.FloatField(default=0.00)
    tva = models.FloatField(default=0.00)
    mode=models.CharField(max_length=10, default=None)
    factures=models.ManyToManyField(Facture, default=None, blank=True, related_name='reglementsfc')
    # mode: 0 bl, 1 facture
    echance=models.DateField(default=None, null=True, blank=True)
    npiece=models.CharField(max_length=50, default=None, null=True, blank=True)
    # if regl is paid if it has echeaance
    ispaid=models.BooleanField(default=False)

class Facturesregle(models.Model):
    payment=models.ForeignKey(PaymentClientfc, on_delete=models.CASCADE, default=None, null=True, blank=True)
    bon=models.ForeignKey(Facture, on_delete=models.CASCADE, default=None, null=True, blank=True)
    amount=models.FloatField(default=0.00)




# price of each product for each salesman
class Salesprice(models.Model):
    product=models.ForeignKey(Produit, on_delete=models.CASCADE, default=None)
    price=models.FloatField()
    salesman=models.ForeignKey(Represent, on_delete=models.CASCADE, default=None)
    date=models.DateField(auto_now_add=True)
    def __str__(self) -> str:
        return self.product.ref+'-'+self.id



# signal to set order_no when order is created to be in this format '23-09-00001'

@receiver(post_save, sender=Order)
def set_order_no(sender, instance, created, **kwargs):
    year_month = timezone.now().strftime("%y%m")

    if created:
        instance.order_no = f'{year_month}-{str(instance.id)}'
        instance.save()


# this class is the equivalnt of stockouts for each product
class Orderitem(models.Model):
    order=models.ForeignKey(Order, on_delete=models.CASCADE, default=None, null=True, blank=True)
    bonlivraison=models.ForeignKey('Bonlivraison', on_delete=models.CASCADE, default=None, null=True, blank=True)
    product=models.ForeignKey(Produit, on_delete=models.CASCADE, default=None, null=True)
    remise=models.CharField(max_length=100, null=True, default=None)
    ref=models.CharField(max_length=100, null=True, default=None)
    local=models.CharField(max_length=100, null=True, default=None)
    name=models.CharField(max_length=100, null=True, default=None)
    qty=models.IntegerField()
    # this total represents the revenue of this product
    total=models.FloatField(default=0.00)
    price=models.FloatField(default=0.00)
    date=models.DateTimeField(default=datetime.datetime.now, blank=True)
    outprincipal=models.IntegerField(default=0)
    outdepot=models.IntegerField(default=0)
    client=models.ForeignKey(Client, on_delete=models.CASCADE, default=None, null=True, blank=True)
    clientprice=models.FloatField(default=0.00)
    islivraison=models.BooleanField(default=False, null=True, blank=True)

class Shippingfees(models.Model):
    city=models.CharField(max_length=20)
    shippingfee=models.FloatField()
    def __str__(self) -> str:
        return f'{self.city} - {self.shippingfee}'




class Pairingcode(models.Model):
    code = models.CharField(max_length=50)
    amount = models.FloatField()




# this class is used to track client prices to be used in bon livraison, last proce the client bought the product with
class Clientprices(models.Model):
    client=models.ForeignKey(Client, on_delete=models.CASCADE, default=None, null=True, blank=True)
    product=models.ForeignKey(Produit, on_delete=models.CASCADE, default=None)
    price=models.FloatField()
    date=models.DateField(auto_now_add=True)




class Outfacture(models.Model):
    facture=models.ForeignKey(Facture, on_delete=models.CASCADE, default=None)
    total=models.FloatField(default=0.00)
    product=models.ForeignKey(Produit, on_delete=models.CASCADE, default=None, null=True)
    remise=models.CharField(max_length=100, null=True, default=None)
    ref=models.CharField(max_length=100, null=True, default=None)
    name=models.CharField(max_length=100, null=True, default=None)
    qty=models.IntegerField()
    # this total represents the revenue of this product
    price=models.FloatField(default=0.00)
    client=models.ForeignKey(Client, on_delete=models.CASCADE, default=None, null=True, blank=True)
    date=models.DateField(default=None, blank=True, null=True)
    
class Livraisonitem(models.Model):
    bon=models.ForeignKey(Bonlivraison, on_delete=models.CASCADE, default=None)
    total=models.FloatField(default=0.00)
    product=models.ForeignKey(Produit, on_delete=models.CASCADE, default=None, null=True)
    remise=models.CharField(max_length=100, null=True, default=None)
    ref=models.CharField(max_length=100, null=True, default=None)
    name=models.CharField(max_length=100, null=True, default=None)
    qty=models.IntegerField()
    # this total represents the revenue of this product
    price=models.FloatField(default=0.00)
    client=models.ForeignKey(Client, on_delete=models.CASCADE, default=None, null=True, blank=True)
    
    # to track ligns that are facture
    isfacture=models.BooleanField(default=False)
    isavoir=models.BooleanField(default=False)
    clientprice=models.FloatField(default=0.00)
    date=models.DateField(default=None, null=True, blank=True)
    def __str__(self) -> str:
        return f'{self.bon.bon_no} - {self.product.ref}'


class Avoirclient(models.Model):
    date=models.DateTimeField(default=datetime.datetime.now, blank=True, null=True)
    no = models.CharField(
        max_length=20, unique=True, blank=True, null=True
    )

    client = models.ForeignKey(
        Client,
        related_name='customer_avoir',
        blank=True, null=True,on_delete=models.CASCADE
    )
    representant= models.ForeignKey(Represent, on_delete=models.CASCADE, default=None, null=True)
    returneditems = models.ManyToManyField(
        'Returned',
        related_name='returned',
        max_length=100, blank=True, default=None
    )
    total = models.FloatField(default=0, blank=True, null=True)
    avoirbl=models.BooleanField(default=False)
    avoirfacture=models.BooleanField(default=False)



class Returned(models.Model):
    product=models.ForeignKey(Produit, on_delete=models.CASCADE, default=None)
    qty=models.IntegerField()
    remise=models.IntegerField(null=True, blank=True, default=None)
    total=models.FloatField(default=0.00)
    price=models.FloatField(default=0.00)
    avoir=models.ForeignKey(Avoirclient, related_name='returned_invoice', on_delete=models.CASCADE, default=None, null=True, blank=True)


class Avoirsupplier(models.Model):
    date=models.DateTimeField(default=datetime.datetime.now, blank=True, null=True)
    no = models.CharField(
        max_length=20, unique=True, blank=True, null=True
    )

    supplier = models.ForeignKey(
        Supplier,
        related_name='supplier_avoir',
        blank=True, null=True,on_delete=models.CASCADE
    )
    returneditems = models.ManyToManyField(
        'Returnedsupplier',
        related_name='returned_supplier',
        max_length=100, blank=True, default=None
    )
    total = models.FloatField(default=0, blank=True, null=True)
    avoirbl=models.BooleanField(default=False)
    avoirfacture=models.BooleanField(default=False)

class Returnedsupplier(models.Model):
    product=models.ForeignKey(Produit, on_delete=models.CASCADE, default=None)
    qty=models.IntegerField()
    total=models.FloatField(default=0.00)
    price=models.FloatField(default=0.00)
    avoir=models.ForeignKey(Avoirsupplier, related_name='avoir_supplier', on_delete=models.CASCADE, default=None, null=True, blank=True)


class Ordersnotif(models.Model):
    user=models.ForeignKey(User, on_delete=models.CASCADE, default=None)
    isread=models.BooleanField(default=False)

class Connectedusers(models.Model):
    user=models.ForeignKey(User, on_delete=models.CASCADE, default=None)
    activity=models.CharField(max_length=500, default=None, null=True, blank=True)
    lasttime=models.DateTimeField(auto_now_add=True)

# this class model for images carousel in catalog
class Promotion(models.Model):
    image=models.ImageField(upload_to='categories_images/', null=True, blank=True)
    info=models.CharField(max_length=500, default=None, null=True, blank=True)

class UserSession(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
# his will be refs that clients searched for
class Refstats(models.Model):
    ref=models.CharField(max_length=500, default=None, null=True, blank=True)
    times=models.IntegerField(default=1)
    lastdate=models.DateField(auto_now_add=True, blank=True, null=True)
    user=models.ForeignKey(User, on_delete=models.CASCADE, default=None, blank=True, null=True)
    def __str__(self) -> str:
        if self.user:
            return self.user.username
        return '--'

class Notavailable(models.Model):
    ref=models.CharField(max_length=500, default=None, null=True, blank=True)
    name=models.CharField(max_length=500, null=True)
    image = models.ImageField(upload_to='products_imags/', null=True, blank=True)
    sellprice=models.FloatField(default=0.00, null=True, blank=True)
    mark=models.ForeignKey(Mark, on_delete=models.CASCADE, default=None, null=True, blank=True)
    equiv=models.TextField(null=True, blank=True, default=None)

class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    total=models.FloatField(default=None, null=True, blank=True)

class Cartitems(models.Model):
    cart=models.ForeignKey(Cart, on_delete=models.CASCADE, default=None, null=True, blank=True)
    product=models.ForeignKey(Produit, on_delete=models.CASCADE, default=None)
    qty=models.IntegerField(default=None, null=True, blank=True)
    total=models.FloatField(default=None, null=True, blank=True)

class Wich(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    total=models.FloatField(default=None, null=True, blank=True)
    def __str__(self) -> str:
        if self.user:
            return self.user.username
#wishlist items
class Wishlist(models.Model):
    wich=models.ForeignKey(Wich, on_delete=models.CASCADE, default=None, null=True, blank=True)
    product=models.ForeignKey(Produit, on_delete=models.CASCADE, default=None)
    qty=models.IntegerField(default=None, null=True, blank=True)
    total=models.FloatField(default=None, null=True, blank=True)

class Notification(models.Model):
    notification=models.TextField()