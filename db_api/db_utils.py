import asyncio

from sqlalchemy import select, update, delete
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from db_api import *
from db_api.models import Orders, Basket


class CategoryUtils(object):
    @staticmethod
    @create_session
    async def get_categories(category_id: int=None, session: AsyncSession = None) -> list | None:
        categories = await session.execute(select(Category).where(Category.parent_id == category_id))
        if categories := categories.all():
            return [(category[0].id, category[0].name) for category in categories]
        # print(categories.all())
        # res = {category[0].id:category[0].name for category in categories}
        # for category in categories.all():
        #     print(category)
        #     res.append(category.name)
        # return res

    @staticmethod
    @create_session
    async def get_supercategory(category_id: int, session: AsyncSession = None) -> int | None:
        supercategory = await session.execute(select(Category).where(Category.id == category_id))
        if supercategory := supercategory.first():
            return supercategory[0].parent_id
        # res = {subcategory[0].id:subcategory[0].name for subcategory in subcategories}
        # return res


class ProductUtils(object):
    @staticmethod
    @create_session
    async def get_products(category_id: int, session: AsyncSession = None) -> list | None:
        products = await session.execute(select(Product).where(Product.category_id == category_id))
        if products := products.all():
            return [(product[0].id, product[0].name, product[0].price) for product in products]
        # res = {product[0].id:product[0].name for product in products}
        # return res

    @staticmethod
    @create_session
    async def get_product(product_id: int, session: AsyncSession = None) -> Product | None:
        product = await session.execute(select(Product).where(Product.id == product_id))
        if product := product.first():
            return product[0]


class UserUtils(object):
    @staticmethod
    @create_session
    async def add_user(id:int,
                       username: str,
                       first_name: str,
                       last_name: str,
                       referrer: int,
                       ref_score: float = 0,
                       session: AsyncSession = None) -> int | None:
        user = Users(id=id,
                     username=username if username else f'User{id}',
                     first_name=first_name,
                     last_name=last_name,
                     referrer=referrer,
                     ref_score=ref_score)
        session.add(user)
        try:
            await session.commit()
        except IntegrityError:
            return None
        await session.refresh(user)
        return user.id

    @staticmethod
    @create_session
    async def get_user(id:int, session: AsyncSession = None) -> Users | None:
        user = await session.execute(select(Users).where(Users.id == id))
        if user := user.first():
            return user[0]
        else:
            return None


    @staticmethod
    @create_session
    async def ref_count(referrer_id:int, session: AsyncSession = None) -> int:
        users = await session.execute(select(Users).where(Users.referrer == referrer_id))
        return len(users.all())
        # if users := users.all():
        #     return len(users)
        # else:
        #     return 0


    @staticmethod
    @create_session
    async def update_user(id:int,
                        username: str = None,
                        first_name: str = None,
                        last_name: str = None,
                        referrer: int = None,
                        ref_score: float = None,
                        session: AsyncSession = None):
        await session.execute(update(Users).where(Users.id == id).values(
            username=username if username else Users.username,
            first_name=first_name if first_name else Users.first_name,
            last_name=last_name if last_name else Users.last_name,
            referrer=referrer if referrer else Users.referrer,
            ref_score=ref_score if ref_score  is not None else Users.ref_score)
                            )
        await session.commit()

    @staticmethod
    @create_session
    async def delete_user(id:int, session: AsyncSession = None):
        await session.execute(delete(Users).where(Users.id == id))


class OrderUtils(object):
    @staticmethod
    @create_session
    async def add_order(user_id: int,
                        # status: str = 'ordered',
                        amount: float,
                        session: AsyncSession = None) -> int | None:
        order = Orders(user_id=user_id,
                       status='ordered',
                       amount=amount)
        session.add(order)
        try:
            await session.commit()
        except IntegrityError:
            return None
        await session.refresh(order)
        return order.id

    @staticmethod
    @create_session
    async def get_ordered(user_id: int, status: str ='ordered', session: AsyncSession = None) -> Orders | None:
        order = await session.execute(select(Orders).where(Orders.user_id == user_id, Orders.status == status))
        if order := order.first():
            return order[0]
        else:
            return None

    @staticmethod
    @create_session
    async def update_order(id: int,
                           user_id: int =None,
                           status: str = None,
                           amount: float = None,
                           session: AsyncSession = None):
        await session.execute(update(Orders).where(Orders.id == id).values(
            user_id=user_id if user_id else Orders.user_id,
            status=status if status else Orders.status,
            amount=amount if amount else Orders.amount)
                            )
        await session.commit()

    @staticmethod
    @create_session
    async def delete_order(id:int, session: AsyncSession = None):
        await session.execute(delete(Orders).where(Orders.id == id))
        await session.commit()

    @staticmethod
    @create_session
    async def add_product(order_id:int,
                          product_id: int,
                          session: AsyncSession = None) -> bool:
        basket = Basket(order_id=order_id,
                        product_id=product_id)
        session.add(basket)
        try:
            await session.commit()
        except IntegrityError:
            return False
        await session.refresh(basket)
        return True

    @staticmethod
    @create_session
    async def get_products(order_id:int, session: AsyncSession = None) -> list | None:
        products = await session.execute(select(Basket).where(Basket.order_id == order_id))
        if products := products.all():
            print(*products)
            return [product[0].product_id for product in products]
        else:
            return None


async def main():
    # result = await CategoryCRUD.get(category_id=1)
    result_cat = await CategoryUtils.get_categories()
    print(result_cat)
    # result_subcat = await CategoryUtils.get_subcategories(category_id=1)
    result_subcat = await CategoryUtils.get_categories(category_id=result_cat[0][0])
    print(result_subcat)
    result_subcat2 = await CategoryUtils.get_categories(category_id=result_subcat[0][0])
    print(result_subcat2)
    result_subcat3 = await CategoryUtils.get_categories(category_id=result_subcat2[0][0])
    print(result_subcat3)
    # result_supcat = await CategoryUtils.get_supercategory(category_id=result_subcat2[0][0])
    result_supcat = await CategoryUtils.get_supercategory(category_id=1)
    print(result_supcat)
    result_prods = await ProductUtils.get_products(category_id=result_subcat2[0][0])
    print(result_prods)
    result_prod = await ProductUtils.get_product(product_id=result_prods[0][0])
    print(result_prod.name)
    user = await UserUtils.get_user(id=681824226)
    print(user.id)
    # user_append = await UserUtils.add_user(id=5097779417,
    #                                        username="Iryne",
    #                                        first_name='',
    #                                        last_name='',
    #                                        referrer=681824226)
    # print(user_append)
    referals = await UserUtils.ref_count(referrer_id=681824226)
    print(referals)


if __name__ == '__main__':
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(main())
