from restaurantMenu.models.menu import Menu
from restaurantFood.models.food import RestaurantFood
from restaurantDrink.models.drink import RestaurantDrink
from restaurantFood.serializers.food import RestaurantFoodSerializer
from restaurantDrink.serializers.drink import RestaurantDrinkSerializer
from restaurantMenu.serializers.menu import MenuSerializer
from restaurantCommande.serializers.commande import CommandeSerializer
from accounts.serializers.user import UserSerializer
from accounts.serializers.client import ClientSerializer
from accounts.serializers.delivery import DeliverySerializer
from restaurantCommande.serializers.note import NoteSerializer
from restaurantCommande.models.note import Note
from datetime import datetime


def get_objets(commande):
    menus = []
    for elt in CommandeSerializer(commande).data['menu']:
        datax = {
            "menu": MenuSerializer(Menu.objects.get(pk=elt['menu'], is_active=True, is_deleted=False)).data,
            "quantity": elt['quantity']
        }
        menus.append(datax)
    foods = []
    for elt in CommandeSerializer(commande).data['food']:
        datax = {
            "food": RestaurantFoodSerializer(RestaurantFood.objects.get(pk=elt['food'], is_active=True, is_deleted=False)).data,
            "quantity": elt['quantity']
        }
        foods.append(datax)
    drinks = []
    for elt in CommandeSerializer(commande).data['drink']:
        datax = {
            "drink": RestaurantDrinkSerializer(RestaurantDrink.objects.get(pk=elt['drink'], is_active=True, is_deleted=False)).data,
            "quantity": elt['quantity']
        }
        drinks.append(datax)
    return menus, foods, drinks


def get_commande(commande, note, restaurant):
    menus, foods, drinks = get_objets(commande=commande)
    valeur = None
    if note is not None:
        if isinstance(note, Note):
            valeur = NoteSerializer(note).data
        else:
            valeur = NoteSerializer(note, many=True).data
    suggestions = None
    if commande.suggestion is not None:
        suggestions = {
            "foods": [],
            "drinks": []
        }
        for item in commande.suggestion['foods']:
            val = {'initial_food': RestaurantFoodSerializer(
                RestaurantFood.objects.get(pk=item['initial_food'], is_active=True, is_deleted=False)).data,
                   'suggest_food': RestaurantFoodSerializer(
                       RestaurantFood.objects.get(pk=item['suggest_food'], is_active=True, is_deleted=False)).data}
            suggestions['foods'].append(val)
        for item in commande.suggestion['drinks']:
            val = {'initial_drink': RestaurantDrinkSerializer(
                RestaurantDrink.objects.get(pk=item['initial_drink'], is_active=True, is_deleted=False)).data,
                   'suggest_drink': RestaurantDrinkSerializer(
                       RestaurantDrink.objects.get(pk=item['suggest_drink'], is_active=True, is_deleted=False)).data}
            suggestions['drinks'].append(val)

    data = {
        'id': commande.id,
        'reference': commande.reference,
        'is_active': commande.is_active,
        'food': foods,
        'drink': drinks,
        'menu': menus,
        'created_by': ClientSerializer(commande.created_by).data,
        'total_price': commande.total_price,
        'created_at': commande.created_at,
        'updated_at': commande.updated_at,
        'delivery_location': commande.delivery_location,
        'site_delivery': commande.site_delivery,
        'cooking_time': commande.cooking_time,
        'token': commande.token,
        'is_restaurant_valid': commande.is_restaurant_valid,
        'is_delivery_valid': commande.is_delivery_valid,
        'restaurant_validate_date': commande.restaurant_validate_date,
        'delivery_validate_date': commande.delivery_validate_date,
        'restaurant_cancel_validated_by': UserSerializer(commande.restaurant_cancel_validated_by).data,
        'delivery_cancel_validated_by': DeliverySerializer(commande.delivery_cancel_validated_by).data,
        'restaurant_validated_by': UserSerializer(commande.restaurant_validated_by).data,
        'delivery_validated_by': DeliverySerializer(commande.delivery_validated_by).data,
        'restaurant_cancel_date': commande.restaurant_cancel_date,
        'delivery_cancel_date': commande.delivery_cancel_date,
        'delivery_check_date': commande.delivery_cancel_date,
        'is_delivery_check': commande.is_delivery_check,
        'status': commande.get_status_display(),
        'delivery_date': commande.delivery_date,
        'suggestion': suggestions,
        'notes': valeur,
        'restaurant': {
            "id": restaurant.id,
            "name": restaurant.name,
            "location": restaurant.location
        }
    }
    return data


def get_total_price(commande):
    price = 0
    for f in CommandeSerializer(commande).data['menu']:
        menu = Menu.objects.get(pk=f['menu'], is_active=True, is_deleted=False)
        if menu.real_price is not None:
            price = price + (menu.real_price * f['quantity'])
    for f in CommandeSerializer(commande).data['food']:
        food = RestaurantFood.objects.get(pk=f['food'], is_active=True, is_deleted=False)
        price = price + (food.price * f['quantity'])
    for f in CommandeSerializer(commande).data['drink']:
        drink = RestaurantDrink.objects.get(pk=f['drink'], is_active=True, is_deleted=False)
        price = price + (drink.price * f['quantity'])
    return price


def get_max_time(commande):
    max_time = '00:00:00'
    max_time = datetime.strptime(max_time, "%H:%M:%S").time()
    menus, foods, drinks = get_objets(commande=commande)
    for menu in menus:
        for food in menu['menu']['foods']:
            x = RestaurantFood.objects.get(pk=food, is_active=True, is_deleted=False)
            if x.cooking_time is not None and x.cooking_time > max_time:
                max_time = x.cooking_time
    for food in foods:
        if food['food']['cooking_time'] is not None:
            f = datetime.strptime(str(food['food']['cooking_time']), "%H:%M:%S").time()
            if f > max_time:
                max_time = f

    return max_time


def get_all_foods(commande):
    results = []
    menus, foods, drinks = get_objets(commande=commande)
    for menu in menus:
        for food in menu['menu']['foods']:
            x = RestaurantFood.objects.get(pk=food, is_active=True, is_deleted=False)
            results.append(x)
    for food in foods:
        x = RestaurantFood.objects.get(pk=food['food']['id'], is_active=True, is_deleted=False)
        results.append(x)
    return results


def get_all_drinks(commande):
    results = []
    menus, foods, drinks = get_objets(commande=commande)
    for menu in menus:
        for drink in menu['menu']['drinks']:
            x = RestaurantDrink.objects.get(pk=drink, is_active=True, is_deleted=False)
            results.append(x)
    for drink in drinks:
        x = RestaurantDrink.objects.get(pk=drink['drink']['id'], is_active=True, is_deleted=False)
        results.append(x)
    return results


def check_foods(serializer):
    """Docstring for function."""
    foods = get_all_foods(serializer.validated_data['commande'])
    for food in serializer.validated_data['comments']['foods']:
        if food['food'] not in foods:
            return False


def check_drinks(serializer):
    """Docstring for function."""
    drinks = get_all_drinks(serializer.validated_data['commande'])
    for drink in serializer.validated_data['comments']['drinks']:
        if drink['drink'] not in drinks:
            return False


def check_foods_note(serializer):
    """Docstring for function."""
    foods = get_all_foods(serializer.validated_data['commande'])
    for food in serializer.validated_data['note_restaurant']['foods']:
        if food['food'] not in foods:
            return False


def check_drinks_note(serializer):
    """Docstring for function."""
    drinks = get_all_drinks(serializer.validated_data['commande'])
    for drink in serializer.validated_data['note_restaurant']['drinks']:
        if drink['drink'] not in drinks:
            return False


def check_foods_suggest(serializer):
    """Docstring for function."""
    foods = get_all_foods(serializer.validated_data['commande'])
    for food in serializer.validated_data['foods']:
        if food['initial_food'] not in foods:
            return False


def check_drinks_suggest(serializer):
    """Docstring for function."""
    drinks = get_all_drinks(serializer.validated_data['commande'])
    for drink in serializer.validated_data['drinks']:
        if drink['initial_drink'] not in drinks:
            return False


def get_food_same_price(commande):
    result = []
    foods = get_all_foods(commande)
    for food in foods:
        res = {
            "food_id": food.id
        }
        foo = RestaurantFood.objects.all().filter(price__gte=food.price, is_active=True, is_deleted=False)
        foo = list(foo)
        foo.remove(food)
        val = []
        for i in foo:
            val.append(RestaurantFoodSerializer(i).data)
        res['same_price'] = val
        result.append(res)
    return result


def get_drink_same_price(commande):
    result = []
    drinks = get_all_drinks(commande)
    for drink in drinks:
        res = {
            "drink_id": drink.id
        }
        foo = RestaurantDrink.objects.all().filter(price__gte=drink.price, is_active=True, is_deleted=False)
        foo = list(foo)
        foo.remove(drink)
        val = []
        for i in foo:
            val.append(RestaurantDrinkSerializer(i).data)
        res['same_price'] = val
        result.append(res)
    return result
