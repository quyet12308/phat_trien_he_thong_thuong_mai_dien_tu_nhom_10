from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Text,
    Boolean,
    DateTime,
    ForeignKey,
    Numeric,
    func,
    MetaData,
    Table,
    text,
    select,
)
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import func
from setting import DATA_BASE_PATH
from sqlalchemy.orm import sessionmaker
import json

from datetime import datetime


def convert_to_json(**kwargs):
    return json.dumps(kwargs)


####################################################
################ create database ###################
####################################################
# Tạo engine cho SQLite
engine = create_engine(f"sqlite:///{DATA_BASE_PATH}")

# Tạo Base class
Base = declarative_base()


# Định nghĩa các model
class User(Base):
    __tablename__ = "users"
    user_id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String)
    password = Column(String)
    email = Column(String)
    fullname = Column(String)
    phone_number = Column(String)
    address = Column(String)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    img = Column(String)
    is_admin = Column(Boolean, default=False)


class Product(Base):
    __tablename__ = "products"
    product_id = Column(Integer, primary_key=True, autoincrement=True)
    product_name = Column(String)
    price = Column(Numeric)
    description = Column(Text)
    category_id = Column(Integer, ForeignKey("categories.category_id"))
    brand_id = Column(Integer, ForeignKey("brands.brand_id"))
    quantity = Column(Integer)
    image = Column(String)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    img = Column(String)
    category = relationship("Category", backref="products")
    brand = relationship("Brand", backref="products")


class Category(Base):
    __tablename__ = "categories"
    category_id = Column(Integer, primary_key=True, autoincrement=True)
    category_name = Column(String)
    description = Column(Text)


class Brand(Base):
    __tablename__ = "brands"
    brand_id = Column(Integer, primary_key=True, autoincrement=True)
    brand_name = Column(String)
    description = Column(Text)
    img = Column(String)
    # url_web = Column(String)  # Thêm cột "url" vào bảng "brands"


class Order(Base):
    __tablename__ = "orders"
    order_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    order_date = Column(DateTime, server_default=func.now())
    order_status = Column(String)
    total_price = Column(Numeric)
    shipping_address = Column(String)
    payment_method = Column(String)
    user = relationship("User", backref="orders")


class OrderDetail(Base):
    __tablename__ = "order_details"
    order_detail_id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey("orders.order_id"))
    product_id = Column(Integer, ForeignKey("products.product_id"))
    quantity = Column(Integer)
    unit_price = Column(Numeric)
    order = relationship("Order", backref="order_details")
    product = relationship("Product", backref="order_details")


class Cart(Base):
    __tablename__ = "cart"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    total = Column(Integer)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    user = relationship("User", backref="cart")


class CartItem(Base):
    __tablename__ = "cart_item"
    id = Column(Integer, primary_key=True, autoincrement=True)
    cart_id = Column(Integer, ForeignKey("cart.id"))
    product_id = Column(Integer, ForeignKey("products.product_id"))
    quantity = Column(Integer)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    cart = relationship("Cart", backref="cart_items")
    product = relationship("Product", backref="cart_items")


class PaymentDetail(Base):
    __tablename__ = "payment_details"
    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey("orders.order_id"))
    amount = Column(Integer)
    provider = Column(String)
    status = Column(String)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    order = relationship("Order", backref="payment_details")


######################################################################
################ delete or clear table in database ###################
######################################################################


def delete_table_data(db_path, table_name):
    # Tạo engine và phiên làm việc
    engine = create_engine(f"sqlite:///{db_path}")
    Session = sessionmaker(bind=engine)
    session = Session()

    # Xóa sạch dữ liệu của bảng
    table = Base.metadata.tables[table_name]
    session.execute(table.delete())
    session.commit()

    message = f"Đã xóa sạch dữ liệu của bảng '{table_name}'."
    return {"status": True, "message": message}


######################################################################
################ display table in database ###########################
######################################################################


def display_table_data(db_path, table_name):
    engine = create_engine(f"sqlite:///{db_path}")
    metadata = MetaData()

    with engine.connect() as connection:
        metadata.reflect(bind=engine)
        table = metadata.tables[table_name]

        # Lấy toàn bộ dữ liệu từ bảng
        select_statement = select([table])
        result = connection.execute(select_statement)

        print(f"Nội dung của bảng '{table_name}':")
        for row in result:
            print(row)


# test
def test_alter_table_with_brand_table(db_path, table_name, operation, column):
    # Tạo engine và phiên làm việc
    engine = create_engine(f"sqlite:///{db_path}")
    Session = sessionmaker(bind=engine)
    session = Session()

    Base = declarative_base()

    # Định nghĩa lớp tạm thời để áp dụng thay đổi cấu trúc bảng
    class TempTable(Base):
        __tablename__ = table_name

        # Định nghĩa các cột hiện có trong bảng
        brand_id = Column(Integer, primary_key=True, autoincrement=True)
        brand_name = Column(String)
        description = Column(Text)
        img = Column(String)

    # Kiểm tra loại thao tác
    if operation == "add":
        # Thêm cột mới vào bảng
        setattr(TempTable, column, Column(String))

    elif operation == "drop":
        # Xóa cột khỏi bảng
        delattr(TempTable, column)

    # Tạo bảng tạm thời
    Base.metadata.create_all(bind=engine)

    # Thực hiện thay đổi cấu trúc bảng bằng cách tạo bảng mới và sao chép dữ liệu từ bảng cũ
    session.execute(f"INSERT INTO {TempTable.__tablename__} SELECT * FROM {table_name}")
    session.commit()

    # Xóa bảng cũ
    session.execute(f"DROP TABLE {table_name}")
    session.commit()

    # Đổi tên bảng tạm thời thành tên bảng gốc
    session.execute(f"ALTER TABLE {TempTable.__tablename__} RENAME TO {table_name}")
    session.commit()

    # Đóng phiên làm việc
    session.close()


# Tạo các bảng trong cơ sở dữ liệu
# Base.metadata.create_all(engine)


##################################################################
########## interact with the user table in database ##############
##################################################################


# check user is taken
def is_username_taken(username):
    # Tạo engine và phiên làm việc
    engine = create_engine(f"sqlite:///{DATA_BASE_PATH}")
    Session = sessionmaker(bind=engine)
    session = Session()

    # Kiểm tra xem tên người dùng đã tồn tại trong cơ sở dữ liệu hay chưa
    existing_user = session.query(User).filter_by(username=username).first()

    # Trả về True nếu tên người dùng đã được sử dụng, False nếu chưa
    return existing_user is not None


# add user
def add_user(
    username, password, email, fullname, phone_number, address, img, is_admin=False
):
    # Kiểm tra xem tên người dùng đã tồn tại hay chưa
    if is_username_taken(username):
        messgae = f"Tên người dùng đã tồn tại. Vui lòng chọn tên người dùng khác."
        return {"status": False, "messgae": messgae}
    else:
        # Tạo engine và phiên làm việc
        engine = create_engine(f"sqlite:///{DATA_BASE_PATH}")
        Session = sessionmaker(bind=engine)
        session = Session()

        # Tạo đối tượng User mới
        new_user = User(
            username=username,
            password=password,
            email=email,
            fullname=fullname,
            phone_number=phone_number,
            address=address,
            img=img,
            is_admin=is_admin,
        )

        # Thêm đối tượng User mới vào phiên làm việc và commit thay đổi
        session.add(new_user)
        session.commit()
        messgae = f"Thêm người dùng thành công"
        return {"status": True, "messgae": messgae}


# delete user
def delete_user(user_id):
    # Tạo engine và phiên làm việc
    engine = create_engine(f"sqlite:///{DATA_BASE_PATH}")
    Session = sessionmaker(bind=engine)
    session = Session()

    # Tìm người dùng dựa trên user_id
    user = session.query(User).filter_by(user_id=user_id).first()

    if user:
        # Xóa người dùng và commit thay đổi
        session.delete(user)
        session.commit()
        message = f"Người dùng với user_id {user_id} đã được xóa."
        return {"status": True, "message": message}
    else:
        message = f"Không tìm thấy người dùng với user_id {user_id}."
        return {"status": False, "message": message}


# update user
def update_user(user_id, new_data):
    # Tạo engine và phiên làm việc
    engine = create_engine(f"sqlite:///{DATA_BASE_PATH}")
    Session = sessionmaker(bind=engine)
    session = Session()

    # Tìm người dùng dựa trên user_id
    user = session.query(User).filter_by(user_id=user_id).first()

    if user:
        # Cập nhật thông tin người dùng với dữ liệu mới
        for key, value in new_data.items():
            setattr(user, key, value)

        # Commit thay đổi
        session.commit()
        message = f"Thông tin người dùng với user_id {user_id} đã được cập nhật."
        return {"status": True, "message": message}
    else:
        message = f"Không tìm thấy người dùng với user_id {user_id}."
        return {"status": False, "message": message}


def get_user(user_id):
    # Tạo engine và phiên làm việc
    engine = create_engine(f"sqlite:///{DATA_BASE_PATH}")
    Session = sessionmaker(bind=engine)
    session = Session()

    # Tìm người dùng dựa trên user_id
    user = session.query(User).filter_by(user_id=user_id).first()

    if user:
        # Trả về thông tin người dùng
        user_info = {
            "user_id": user.user_id,
            "username": user.username,
            "email": user.email,
            "fullname": user.fullname,
            "phone_number": user.phone_number,
            "address": user.address,
            "img": user.img,
            "is_admin": user.is_admin,
        }
        return {"status": True, "messgae": user_info}
    else:
        messgae = f"Không tìm thấy người dùng với user_id {user_id}."
        return {"status": False, "messgae": messgae}


##################################################################
########## interact with the brands table in database ############
##################################################################


# check brand is taken
def is_brand_taken(brand_name):
    # Tạo engine và phiên làm việc
    engine = create_engine(f"sqlite:///{DATA_BASE_PATH}")
    Session = sessionmaker(bind=engine)
    session = Session()

    existing_brand = session.query(Brand).filter_by(brand_name=brand_name).first()

    return existing_brand is not None


def create_brand_description(
    lich_su, san_pham, uu_diem, nhuoc_diem, dong_san_pham, website
):
    brand_description = {
        "lich_su": lich_su,
        "san_pham": san_pham,
        "uu_diem": uu_diem,
        "nhuoc_diem": nhuoc_diem,
        "dong_san_pham": dong_san_pham,
        "website": website,
    }
    return json.dumps(brand_description, ensure_ascii=False)


def add_brand(brand_name, description, img):
    # print(brand_name)
    # print(is_brand_taken(brand_name=brand_name))
    if is_brand_taken(brand_name):
        messgae = f"Tên thương hiệu đã tồn tại. Vui lòng chọn tên thương hiệu khác."
        return {"status": False, "messgae": messgae}
    else:
        # Tạo engine và phiên làm việc
        engine = create_engine(f"sqlite:///{DATA_BASE_PATH}")
        Session = sessionmaker(bind=engine)
        session = Session()

        # Tạo đối tượng Brand mới
        new_brand = Brand(brand_name=brand_name, description=description, img=img)

        # Thêm đối tượng Brand mới vào phiên làm việc và commit thay đổi
        session.add(new_brand)
        session.commit()
        messgae = f"Thêm thương hiệu thành công"
        return {"status": True, "messgae": messgae}


def edit_brand_data(brand_id, new_brand_name=None, new_description=None, new_img=None):
    # Tạo engine và phiên làm việc
    engine = create_engine(f"sqlite:///{DATA_BASE_PATH}")
    Session = sessionmaker(bind=engine)
    session = Session()

    # Lấy đối tượng Brand cần chỉnh sửa
    brand = session.query(Brand).filter_by(brand_id=brand_id).first()

    if not brand:
        message = f"Không tìm thấy thương hiệu với ID {brand_id}."
        return {"status": False, "message": message}

    # Cập nhật thông tin của thương hiệu
    if new_brand_name is not None:
        brand.brand_name = new_brand_name
    if new_description is not None:
        brand.description = new_description
    if new_img is not None:
        brand.img = new_img

    # Commit thay đổi
    session.commit()

    message = f"Đã chỉnh sửa thông tin thương hiệu với ID {brand_id}."
    return {"status": True, "message": message}


def delete_brand(brand_name):
    # Tạo engine và phiên làm việc
    engine = create_engine(f"sqlite:///{DATA_BASE_PATH}")
    Session = sessionmaker(bind=engine)
    session = Session()

    # Kiểm tra xem thương hiệu có tồn tại trong cơ sở dữ liệu hay không
    brand = session.query(Brand).filter_by(brand_name=brand_name).first()
    if brand is None:
        message = f"Thương hiệu '{brand_name}' không tồn tại trong cơ sở dữ liệu."
        return {"status": False, "message": message}

    # Xóa thương hiệu từ cơ sở dữ liệu
    session.delete(brand)
    session.commit()
    message = f"Đã xóa thương hiệu '{brand_name}' thành công."
    return {"status": True, "message": message}


##################################################################
########## interact with the categories table in database ########
##################################################################


def is_categorie_taken(category_name):
    # Tạo engine và phiên làm việc
    engine = create_engine(f"sqlite:///{DATA_BASE_PATH}")
    Session = sessionmaker(bind=engine)
    session = Session()

    existing_category = (
        session.query(Category).filter_by(category_name=category_name).first()
    )

    return existing_category is not None


def add_category(category_name, description):
    # print(brand_name)
    # print(is_brand_taken(brand_name=brand_name))
    if is_categorie_taken(category_name):
        messgae = f"Tên thể loại đã tồn tại. Vui lòng chọn tên thể loại khác."
        return {"status": False, "messgae": messgae}
    else:
        # Tạo engine và phiên làm việc
        engine = create_engine(f"sqlite:///{DATA_BASE_PATH}")
        Session = sessionmaker(bind=engine)
        session = Session()

        # Tạo đối tượng Brand mới
        new_category = Category(category_name=category_name, description=description)

        # Thêm đối tượng Brand mới vào phiên làm việc và commit thay đổi
        session.add(new_category)
        session.commit()
        messgae = f"Thêm thể loại thành công"
        return {"status": True, "messgae": messgae}


def edit_category_data(category_id, new_category_name=None, new_description=None):
    # Tạo engine và phiên làm việc
    engine = create_engine(f"sqlite:///{DATA_BASE_PATH}")
    Session = sessionmaker(bind=engine)
    session = Session()

    # Lấy đối tượng Brand cần chỉnh sửa
    category = session.query(Category).filter_by(category_id=category_id).first()

    if not category:
        message = f"Không tìm thấy thể loại với ID {category_id}."
        return {"status": False, "message": message}

    # Cập nhật thông tin của thương hiệu
    if new_category_name is not None:
        category.category_name = new_category_name
    if new_description is not None:
        category.description = new_description

    # Commit thay đổi
    session.commit()

    message = f"Đã chỉnh sửa thông tin thể loại với ID {category_id}."
    return {"status": True, "message": message}


def delete_category(category_name):
    # Tạo engine và phiên làm việc
    engine = create_engine(f"sqlite:///{DATA_BASE_PATH}")
    Session = sessionmaker(bind=engine)
    session = Session()

    # Kiểm tra xem thương hiệu có tồn tại trong cơ sở dữ liệu hay không
    category = session.query(Category).filter_by(category_name=category_name).first()
    if category is None:
        message = f"Thể loại '{category_name}' không tồn tại trong cơ sở dữ liệu."
        return {"status": False, "message": message}

    # Xóa thương hiệu từ cơ sở dữ liệu
    session.delete(category)
    session.commit()
    message = f"Đã xóa thể loại '{category_name}' thành công."
    return {"status": True, "message": message}


##################################################################
########## interact with the products table in database ##########
##################################################################


def is_product_taken(product_name):
    # Tạo engine và phiên làm việc
    engine = create_engine(f"sqlite:///{DATA_BASE_PATH}")
    Session = sessionmaker(bind=engine)
    session = Session()

    existing_product = (
        session.query(Product).filter_by(product_name=product_name).first()
    )

    return existing_product is not None


def add_product(
    product_name, price, description, category_id, brand_id, quantity, image
):
    if is_product_taken(product_name=product_name):
        messgae = f"Tên sản phẩm đã tồn tại. Vui lòng chọn tên sản phẩm khác."
        return {"status": False, "messgae": messgae}
    else:
        # Tạo engine và phiên làm việc
        engine = create_engine(f"sqlite:///{DATA_BASE_PATH}")
        Session = sessionmaker(bind=engine)
        session = Session()

        # Tạo đối tượng sản phẩm mới
        product = Product(
            product_name=product_name,
            price=price,
            description=description,
            category_id=category_id,
            brand_id=brand_id,
            quantity=quantity,
            img=image,
        )

        # Thêm sản phẩm vào phiên làm việc
        session.add(product)

        # Commit thay đổi
        session.commit()

        message = "Đã thêm sản phẩm thành công."
        return {"status": True, "message": message}


def edit_product_data(
    product_id,
    new_product_name=None,
    new_price=None,
    new_description=None,
    new_category_id=None,
    new_brand_id=None,
    new_quantity=None,
    new_image=None,
):
    # Tạo engine và phiên làm việc
    engine = create_engine(f"sqlite:///{DATA_BASE_PATH}")
    Session = sessionmaker(bind=engine)
    session = Session()

    # Lấy đối tượng sản phẩm cần chỉnh sửa
    product = session.query(Product).filter_by(product_id=product_id).first()

    if not product:
        message = f"Không tìm thấy sản phẩm với ID {product_id}."
        return {"status": False, "message": message}

    # Cập nhật thông tin của sản phẩm
    if new_product_name is not None:
        product.product_name = new_product_name
    if new_price is not None:
        product.price = new_price
    if new_description is not None:
        product.description = new_description
    if new_category_id is not None:
        product.category_id = new_category_id
    if new_brand_id is not None:
        product.brand_id = new_brand_id
    if new_quantity is not None:
        product.quantity = new_quantity
    if new_image is not None:
        product.img = new_image

    # Commit thay đổi
    session.commit()

    message = f"Đã chỉnh sửa thông tin sản phẩm với ID {product_id}."
    return {"status": True, "message": message}


def delete_product(product_id):
    # Tạo engine và phiên làm việc
    engine = create_engine(f"sqlite:///{DATA_BASE_PATH}")
    Session = sessionmaker(bind=engine)
    session = Session()

    # Lấy đối tượng sản phẩm cần xóa
    product = session.query(Product).filter_by(product_id=product_id).first()

    if not product:
        message = f"Không tìm thấy sản phẩm với ID {product_id}."
        return {"status": False, "message": message}

    # Xóa sản phẩm khỏi phiên làm việc
    session.delete(product)

    # Commit thay đổi
    session.commit()

    message = f"Đã xóa sản phẩm với ID {product_id}."
    return {"status": True, "message": message}


def get_product_details(product_id=None, product_name=None):
    # Tạo engine và phiên làm việc
    engine = create_engine(f"sqlite:///{DATA_BASE_PATH}")
    Session = sessionmaker(bind=engine)
    session = Session()

    query = session.query(Product, Category, Brand).join(Category).join(Brand)

    if product_id is not None:
        query = query.filter(Product.product_id == product_id)
    elif product_name is not None:
        query = query.filter(Product.product_name == product_name)
    else:
        message = "Vui lòng cung cấp ID hoặc tên sản phẩm."
        return {"status": False, "message": message}

    result = query.first()

    if not result:
        message = "Không tìm thấy sản phẩm."
        return {"status": False, "message": message}

    product, category, brand = result

    product_details = {
        "product_id": product.product_id,
        "product_name": product.product_name,
        "price": product.price,
        "description": product.description,
        "category": {
            "category_id": category.category_id,
            "category_name": category.category_name,
        },
        "brand": {"brand_id": brand.brand_id, "brand_name": brand.brand_name},
        "quantity": product.quantity,
        "image": product.image,
        "created_at": product.created_at,
        "updated_at": product.updated_at,
        "img": product.img,
    }

    return {"status": True, "product_details": product_details}


###################################################################################
########## interact with the order and order_detail table in database #############
###################################################################################


def compress_order_items(product_ids, quantities, unit_prices):
    compressed_items = []
    if len(product_ids) == len(quantities) and len(quantities) == len(unit_prices):
        for i in range(len(product_ids)):
            compressed_item = {
                "product_id": product_ids[i],
                "quantity": quantities[i],
                "unit_price": unit_prices[i],
            }
            compressed_items.append(compressed_item)
        return {"status": True, "message": compressed_items}
    else:
        message = f"Số lượng của các thông số truyền vào không bằng nhau"
        return {"status": False, "message": message}


def add_order(
    user_id, order_status, total_price, shipping_address, payment_method, order_items
):
    if order_items["status"] == False:
        return {"status": False, "message": order_items["message"]}
    else:
        # Tạo engine và phiên làm việc
        engine = create_engine(f"sqlite:///{DATA_BASE_PATH}")
        Session = sessionmaker(bind=engine)
        session = Session()

        # Tạo đối tượng đơn hàng mới
        order = Order(
            user_id=user_id,
            order_status=order_status,
            total_price=total_price,
            shipping_address=shipping_address,
            payment_method=payment_method,
        )

        # Thêm đơn hàng vào phiên làm việc
        session.add(order)

        # Commit thay đổi để lấy order_id mới được tạo
        session.commit()
        order_item_datas = order_items["message"]
        # Lặp qua các mục trong đơn hàng và tạo đối tượng chi tiết đơn hàng
        for item in order_item_datas:
            product_id = int(item["product_id"])
            quantity = int(item["quantity"])
            unit_price = int(item["unit_price"])

            # Tạo đối tượng chi tiết đơn hàng mới
            order_detail = OrderDetail(
                order_id=order.order_id,
                product_id=product_id,
                quantity=quantity,
                unit_price=unit_price,
            )

            # Thêm chi tiết đơn hàng vào phiên làm việc
            session.add(order_detail)

        # Commit thay đổi cuối cùng
        session.commit()

        message = "Đã thêm đơn hàng thành công."
        return {"status": True, "message": message}


def edit_order(
    order_id,
    user_id=None,
    order_status=None,
    total_price=None,
    shipping_address=None,
    payment_method=None,
    order_items=None,
):
    # Tạo engine và phiên làm việc
    engine = create_engine(f"sqlite:///{DATA_BASE_PATH}")
    Session = sessionmaker(bind=engine)
    session = Session()

    # Tìm đơn hàng cần chỉnh sửa
    order = session.query(Order).get(order_id)

    if not order:
        return {"status": False, "message": "Đơn hàng không tồn tại."}

    # Cập nhật thông tin đơn hàng
    if user_id is not None:
        order.user_id = user_id
    if order_status is not None:
        order.order_status = order_status
    if total_price is not None:
        order.total_price = total_price
    if shipping_address is not None:
        order.shipping_address = shipping_address
    if payment_method is not None:
        order.payment_method = payment_method

    # Thêm lại chi tiết đơn hàng mới
    if order_items is not None:
        # Xóa chi tiết đơn hàng cũ
        session.query(OrderDetail).filter(OrderDetail.order_id == order_id).delete()
        order_item_datas = order_items["message"]
        for item in order_item_datas:
            product_id = int(item["product_id"])
            quantity = int(item["quantity"])
            unit_price = int(item["unit_price"])

            order_detail = OrderDetail(
                order_id=order_id,
                product_id=product_id,
                quantity=quantity,
                unit_price=unit_price,
            )

            session.add(order_detail)

    # Commit thay đổi cuối cùng
    session.commit()

    message = "Đã chỉnh sửa đơn hàng thành công."
    return {"status": True, "message": message}


def delete_order(order_id):
    # Tạo engine và phiên làm việc
    engine = create_engine(f"sqlite:///{DATA_BASE_PATH}")
    Session = sessionmaker(bind=engine)
    session = Session()

    # Tìm đơn hàng theo order_id
    order = session.query(Order).filter(Order.order_id == order_id).first()

    if order:
        # Xóa các chi tiết đơn hàng liên quan
        session.query(OrderDetail).filter(OrderDetail.order_id == order_id).delete()

        # Xóa đơn hàng
        session.delete(order)
        session.commit()

        message = "Đã xóa đơn hàng thành công."
        return {"status": True, "message": message}
    else:
        message = "Không tìm thấy đơn hàng."
        return {"status": False, "message": message}


###################################################################################
########## interact with the cart and cart_item table in database #################
###################################################################################


def add_to_cart(user_id, product_id, quantity):
    # Tạo engine và phiên làm việc
    engine = create_engine(f"sqlite:///{DATA_BASE_PATH}")
    Session = sessionmaker(bind=engine)
    session = Session()

    # Kiểm tra xem giỏ hàng của người dùng đã tồn tại hay chưa
    cart = session.query(Cart).filter(Cart.user_id == user_id).first()

    if not cart:
        # Tạo giỏ hàng mới nếu chưa tồn tại
        cart = Cart(user_id=user_id, total=0)
        session.add(cart)
        session.commit()

    # Kiểm tra xem sản phẩm đã tồn tại trong giỏ hàng chưa
    cart_item = (
        session.query(CartItem)
        .filter(CartItem.cart_id == cart.id, CartItem.product_id == product_id)
        .first()
    )

    if cart_item:
        # Nếu sản phẩm đã tồn tại trong giỏ hàng, cập nhật số lượng
        cart_item.quantity += quantity
    else:
        # Nếu sản phẩm chưa tồn tại trong giỏ hàng, tạo mới
        cart_item = CartItem(cart_id=cart.id, product_id=product_id, quantity=quantity)
        session.add(cart_item)

    # Cập nhật tổng số lượng sản phẩm trong giỏ hàng
    cart.total += quantity

    session.commit()

    message = "Đã thêm sản phẩm vào giỏ hàng thành công."
    return {"status": True, "message": message}


###################################################################################
########## interact with the payment_details table in database ####################
###################################################################################


def add_payment(order_id, amount, provider, status):
    # Tạo engine và phiên làm việc
    engine = create_engine(f"sqlite:///{DATA_BASE_PATH}")
    Session = sessionmaker(bind=engine)
    session = Session()

    # Kiểm tra xem đơn hàng đã tồn tại hay chưa
    order = session.query(Order).filter(Order.order_id == order_id).first()

    if not order:
        # Nếu đơn hàng không tồn tại, trả về thông báo lỗi
        message = "Đơn hàng không tồn tại."
        return {"status": False, "message": message}

    # Tạo một payment detail mới
    payment_detail = PaymentDetail(
        order_id=order_id, amount=amount, provider=provider, status=status
    )
    session.add(payment_detail)
    session.commit()

    message = "Đã thêm thanh toán thành công."
    return {"status": True, "message": message}


def edit_payment(payment_id, amount=None, provider=None, status=None):
    # Tạo engine và phiên làm việc
    engine = create_engine(f"sqlite:///{DATA_BASE_PATH}")
    Session = sessionmaker(bind=engine)
    session = Session()

    # Kiểm tra xem thanh toán có tồn tại hay không
    payment = (
        session.query(PaymentDetail).filter(PaymentDetail.id == payment_id).first()
    )

    if not payment:
        # Nếu thanh toán không tồn tại, trả về thông báo lỗi
        message = "Thanh toán không tồn tại."
        return {"status": False, "message": message}

    # Cập nhật thông tin thanh toán nếu tham số được truyền vào
    if amount is not None:
        payment.amount = amount
    if provider is not None:
        payment.provider = provider
    if status is not None:
        payment.status = status

    session.commit()

    message = "Đã sửa thông tin thanh toán thành công."
    return {"status": True, "message": message}


def delete_payment(payment_id):
    # Tạo engine và phiên làm việc
    engine = create_engine(f"sqlite:///{DATA_BASE_PATH}")
    Session = sessionmaker(bind=engine)
    session = Session()

    # Kiểm tra xem thanh toán có tồn tại hay không
    payment = (
        session.query(PaymentDetail).filter(PaymentDetail.id == payment_id).first()
    )

    if not payment:
        # Nếu thanh toán không tồn tại, trả về thông báo lỗi
        message = "Thanh toán không tồn tại."
        return {"status": False, "message": message}

    # Xóa thanh toán
    session.delete(payment)
    session.commit()

    message = "Đã xóa thông tin thanh toán thành công."
    return {"status": True, "message": message}
