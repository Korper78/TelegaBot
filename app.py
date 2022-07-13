from decimal import Decimal
from os import getenv
from sys import exit

from aiogram import Bot, Dispatcher, executor, types
from aiogram.utils.deep_linking import get_start_link

from db_api.db_utils import OrderUtils
from keyboards.inline.menu_kb import *

bot_token = getenv("BOT_TOKEN")
if not bot_token:
    exit("Error: no token provided")

bot = Bot(token=bot_token)
dp = Dispatcher(bot)


@dp.message_handler(commands="start", state='*')
async def cmd_start(message: types.Message):
    await message.answer("Налетай, торопись,\nпокупай котопись!!! ")
    await message.answer_dice(emoji='🎰')
    referrer_id = int(message.text.split()[1] or 0) if len(message.text.split()) > 1 else 0
    if referrer := await UserUtils.get_user(id=referrer_id):
        ref_score = referrer.ref_score
        await UserUtils.update_user(id=referrer_id, ref_score=(ref_score + 100))
    else:
        referrer_id = None
    print(f'Referrer - {referrer_id}, user - {message.from_user.id},'
          f' {message.from_user.username}, {message.from_user.first_name}, '
          f'{message.from_user.last_name}')
    user_append = await UserUtils.add_user(id=message.from_user.id,
                                           username=message.from_user.username,
                                           first_name=message.from_user.first_name,
                                           last_name=message.from_user.last_name,
                                           referrer=referrer_id
                                           )
    print(f'Referral - {user_append}')
    # if user_append and (referrer := await UserUtils.get_user(id=referrer_id)):
    #     ref_score = referrer.ref_score
    #     await UserUtils.update_user(id=referrer_id, ref_score=(ref_score+100))
    await show_menu(message)


async def show_menu(message: types.CallbackQuery | types.Message, category_id: int = None, product_id: int = None):
    if product_id:
        await show_product(callback=message, category_id=category_id, product_id=product_id)
    else:
        # Клавиатуру формируем с помощью следующей функции (где делается запрос в базу данных)
        k_board = await categories_keyboard(category_id=category_id)

        # Проверяем, что за тип апдейта. Если Message - отправляем новое сообщение
        if isinstance(message, types.Message):
            await message.answer("Выбери себе))):", reply_markup=k_board)

        # Если CallbackQuery - изменяем это сообщение
        elif isinstance(message, types.CallbackQuery):
            call = message
            # await call.message.edit_reply_markup(k_board)
            await call.message.edit_text(text="Выбери себе))):", reply_markup=k_board)
            await call.answer()


async def show_product(callback: types.CallbackQuery, category_id, product_id):
    k_board = product_keyboard(category_id=category_id, product_id=product_id)

    # Берем запись о нашем товаре из базы данных
    product = await ProductUtils.get_product(product_id=product_id)
    text = f"Купи {product.name}\nпо цене {product.price}$"
    await callback.message.edit_text(text=text, reply_markup=k_board)
    await callback.answer()


@dp.callback_query_handler(menu_cd.filter())
async def navigate(callback: types.CallbackQuery, callback_data: dict):
    """
    :param call: Тип объекта CallbackQuery, который прилетает в хендлер
    :param callback_data: Словарь с данными, которые хранятся в нажатой кнопке
    """

    # Получаем категорию, которую выбрал пользователь (Передается всегда)
    category_id = int(callback_data.get("category")) if callback_data.get("category") else None

    # Получаем айди товара, который выбрал пользователь (Передается НЕ ВСЕГДА - может быть 0)
    product_id = int(callback_data.get("product")) if callback_data.get("product") else None

    await show_menu(callback, category_id, product_id)

    # Прописываем "уровни" в которых будут отправляться новые кнопки пользователю
    # levels = {
    #     "0": show_menu,  # Отдаем категории
    #     "1": show_menu,  # Отдаем подкатегории
    #     "2": show_menu,  # Отдаем товары
    #     "3": show_product  # Предлагаем купить товар
    # }
    #
    # # Забираем нужную функцию для выбранного уровня
    # current_level_function = levels[current_level]

    # Выполняем нужную функцию и передаем туда параметры, полученные из кнопки
    # await current_level_function(
    #     call,
    #     category_id=category_id,
    #     product_id=product_id
    # )


@dp.callback_query_handler(buy_product.filter())
async def purchase(callback: types.CallbackQuery, callback_data: dict):
    product_id = int(callback_data.get("product"))
    product = await ProductUtils.get_product(product_id=product_id)
    k_board = await categories_keyboard(category_id=product.category_id)
    if order := await OrderUtils.get_ordered(user_id=callback.from_user.id):
        order_id = order.id
        await OrderUtils.update_order(id=order.id, amount=(order.amount + product.price))
    else:
        order_id = await OrderUtils.add_order(user_id=callback.from_user.id, amount=product.price)
    basket_res = await OrderUtils.add_product(order_id=order_id, product_id=product.id)
    print(basket_res)
    text = f"Товар {product.name}\nдобавлен в корзину\nВыбери еще:)))"
    await callback.message.edit_text(text=text, reply_markup=k_board)
    await callback.answer()



@dp.message_handler(commands="ref")
async def cmd_ref(message: types.Message):
    ref_link = await get_start_link(payload=message.from_user.id)
    await message.answer(f'Ваша реферальная ссылка:\n<code>{ref_link}</code>', parse_mode='html')


@dp.message_handler(commands="account")
async def cmd_account(message: types.Message):
    await message.answer('Личный кабинет')
    # await account_menu(message,)
    user = await UserUtils.get_user(id=message.from_user.id)
    referals = await UserUtils.ref_count(referrer_id=user.id)
    await message.answer(f'Здравствуйте, {user.username}\nУ вас {referals} присоединившихся приглашенных\n'
                         f'У вас на счету {user.ref_score} баллов')
    if order := await OrderUtils.get_ordered(user_id=user.id):
        # products = [await ProductUtils.get_product(product_id=product.product_id) for product in await OrderUtils.get_products(order_id=order.id)]
        products = [await ProductUtils.get_product(product_id=product) for product in await OrderUtils.get_products(order_id=order.id)]
        # await message.answer(f'У вас в корзине есть товары на сумму {order.amount}$:')
        # for product in products:
        #     await message.answer(f'{product.name} по цене {product.price}$')
        text = f'У вас в корзине есть товары на сумму {order.amount}$:'
        # if (user.ref_score / 60) >= order.amount:
        amount = order.amount
        if user.ref_score:
            amount = min(round(order.amount * Decimal(0.6),2), round(user.ref_score / 100,2))
            # amount = order.amount * 0.6 if (order.amount * 0.6) < (user.ref_score / 100) else user.ref_score / 100
            text += f'\n{amount}$ можно оплатить баллами'
            status = 'ref'
        else:
            status = 'pay'
        for product in products:
            text += f'\n{product.name} по цене {product.price}$'
        k_board = basket_keyboard(status=status, amount=amount)
        await message.answer(text=text, reply_markup=k_board)


@dp.callback_query_handler(basket_cd.filter())
async def payment(callback: types.CallbackQuery, callback_data: dict):
    status = callback_data.get("status")
    amount = Decimal(callback_data.get("amount"))
    user = await UserUtils.get_user(id=callback.from_user.id)
    print(user.id)
    order = await OrderUtils.get_ordered(user_id=user.id)
    await OrderUtils.update_order(id=order.id, status='payed')
    text = f'Заказ отменен'
    match status:
        case 'ref':
            text = f'{order.amount - amount}$ оплачено\n{amount * 100} баллов списано'
            # await OrderUtils.update_order(id=order.id, status='payed')
            user.ref_score -= amount * 100
            await UserUtils.update_user(id=user.id, ref_score=user.ref_score)
            print(f'ref score={user.ref_score}')
        case 'pay':
            text = f'{order.amount}$ оплачено'
            # await OrderUtils.update_order(id=order.id, status='payed')
        case 'cancel':
            await OrderUtils.delete_order(id=order.id)
    await callback.message.edit_text(text=text, reply_markup=None)
    await callback.answer()



if __name__ == "__main__":
    # Запуск бота
    executor.start_polling(dp, skip_updates=True)
