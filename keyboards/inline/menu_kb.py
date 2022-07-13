import asyncio

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData
from db_api import *
# from utils.db_api.db_commands import get_subcategories, count_items, get_items, get_categories

# Создаем CallbackData-объекты, которые будут нужны для работы с менюшкой
# menu_cd = CallbackData("menu", "level", "category", "subcategory", "product_id")
# menu_cd = CallbackData("menu", "level", "category", "product")
menu_cd = CallbackData("menu", "category", "product")
buy_product = CallbackData("buy", "product")
basket_cd = CallbackData("pay", "status", "amount")


# С помощью этой функции будем формировать коллбек дату для каждого элемента меню, в зависимости от
# переданных параметров. Если Подкатегория, или айди товара не выбраны - они по умолчанию равны нулю
def make_callback_data(category=None, product=None):
    return menu_cd.new(
                       category=str(category or ""),
                       product=str(product or "")
                       )


# Создаем функцию, которая отдает клавиатуру с доступными категориями
async def categories_keyboard(category_id:int=None):
    # Создаем Клавиатуру
    markup = InlineKeyboardMarkup()

    # Забираем список товаров из базы данных с РАЗНЫМИ категориями и проходим по нему
    categories = await CategoryUtils.get_categories(category_id=category_id)
    if categories:
        for category in categories:
            button_text = category[1]
            callback_data = make_callback_data(category=category[0])
            markup.insert(
                InlineKeyboardButton(text=button_text, callback_data=callback_data)
            )
        if category_id:
            supercategory = await CategoryUtils.get_supercategory(category_id=category_id)
            if supercategory is None:
                # callback_data = make_callback_data(level=CURRENT_LEVEL-1, category=supercategory)
                callback_data = make_callback_data(category=supercategory)
            else:
                callback_data = make_callback_data(category=supercategory)
            markup.row(
                InlineKeyboardButton(
                    text="Назад",
                    callback_data=callback_data)
            )
    else:
        markup = await products_keyboard(category_id=category_id)
    # Возвращаем созданную клавиатуру в хендлер
    return markup


# Создаем функцию, которая отдает клавиатуру с доступными товарами, исходя из выбранной категории и подкатегории
async def products_keyboard(category_id):
    markup = InlineKeyboardMarkup(row_width=2)

    # Забираем список товаров из базы данных с выбранной категорией и подкатегорией, и проходим по нему
    products = await ProductUtils.get_products(category_id=category_id)
    for product in products:
        # Сформируем текст, который будет на кнопке
        button_text = f"{product[1]} - ${product[2]}"

        # Сформируем колбек дату, которая будет на кнопке
        callback_data = make_callback_data(
                                           category=category_id,
                                           product=product[0])
        markup.insert(
            InlineKeyboardButton(
                text=button_text, callback_data=callback_data)
        )

    # Создаем Кнопку "Назад", в которой прописываем колбек дату такую, которая возвращает
    markup.row(
        InlineKeyboardButton(
            text="Назад",
            # callback_data=make_callback_data(level=CURRENT_LEVEL - 1,
            callback_data=make_callback_data(
                                             category=await CategoryUtils.get_supercategory(category_id=category_id)
                                            )
                            )
            )
    return markup


# Создаем функцию, которая отдает клавиатуру с кнопками "купить" и "назад" для выбранного товара
def product_keyboard(category_id, product_id):
    markup = InlineKeyboardMarkup()
    markup.row(
        InlineKeyboardButton(
            text=f"Купить",
            callback_data=buy_product.new(product=product_id)
                            )
                )
    markup.row(
        InlineKeyboardButton(
            text="Назад",
            callback_data=make_callback_data(
                                             category=category_id)
                              )
                )
    return markup

def basket_keyboard(status: str, amount: str) -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup()
    if status == 'ref':
        markup.row(
            InlineKeyboardButton(
                text='Использовать баллы и оплатить',
                callback_data=basket_cd.new(status=status, amount=amount)))
        status = 'pay'
    markup.row(
        InlineKeyboardButton(
            text=f'Оплатить полностью',
            callback_data=basket_cd.new(status=status, amount=amount)))
    markup.row(
        InlineKeyboardButton(
            text="Отменить заказ",
            callback_data=basket_cd.new(status='cancel', amount=amount)))
    return markup


async def main():
    # result_cb = make_callback_data(level=0,category=None,product=None)
    result_cb = make_callback_data(0)
    print(result_cb)
    result_cat = await categories_keyboard()
    print(result_cat)
    # result_subcat = await CategoryUtils.get_subcategories(category_id=1)
    result_subcat = await categories_keyboard(category_id=1)
    print(result_subcat)
    result_subcat2 = await categories_keyboard(category_id=3)
    print(result_subcat2)
    result_subcat3 = await categories_keyboard(category_id=7)
    print(result_subcat3)
    result_prods = await product_keyboard(category_id=7, product_id=1)
    print(result_prods)


if __name__ == '__main__':
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(main())
