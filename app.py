import streamlit as st
import pymysql
from sqlalchemy import create_engine,text
import pandas as pd
st.title("图书管理系统")
# 页面布局
if "root" not in st.session_state:
    st.session_state["root"] = False
password = st.sidebar.text_input("管理员密码",type="password")
if password=='1958114514':
    st.session_state["root"] = True
else:
    st.error("user_mode,only borrow-return")
menu = st.sidebar.selectbox("功能选择", ["租借-归还","存储信息", "采购", "淘汰", "查询", "统计"])

refresh_button = st.sidebar.button("Refresh")
# 数据库连接 使用自己本地或云端数据库填写相关信息。
db_config = {
    "host": "localhost",
    "user": "root",
    "password": "1958114514",
    "database": "bk",
}
engine = create_engine(
    f"mysql+pymysql://{db_config['user']}:{db_config['password']}@{db_config['host']}/{db_config['database']}")


# 功能 1：存储图书信息
if menu == "存储信息" and st.session_state["root"]:
    st.header("存储图书信息")
    title = st.text_input("书名")
    author = st.text_input("作者")
    isbn = st.text_input("ISBN")
    publisher = st.text_input("出版社")
    publish_date = st.date_input("出版日期")
    stock = st.number_input("库存数量", min_value=0, step=1)

    if st.button("添加图书"):
        with engine.connect() as conn:
            conn.execute(text(f"INSERT INTO Books (Title, Author, ISBN, Publisher, PublishDate, Stock) VALUES ('{title}', '{author}', '{isbn}', '{publisher}', '{publish_date}', {stock});"))
            conn.commit()
            st.success("图书信息已存储！")

# 功能 2：采购
elif menu == "采购" and st.session_state["root"]:
    st.header("采购图书")
    with engine.connect() as conn:
        result = pd.read_sql(text("SELECT * FROM Books"), conn)
        st.dataframe(result)
    book_id = st.number_input("图书ID", min_value=1, step=1)
    quantity = st.number_input("采购数量", min_value=1, step=1)
    price = st.number_input("单价", min_value=0.0, step=0.01)
    purchase_date = st.date_input("采购日期")

    if st.button("确认采购"):
        with engine.connect() as conn:
            check = pd.read_sql(text(f"SELECT * FROM Books WHERE BookID = {book_id};"), conn)
            if not check.empty:
                conn.execute(text(f"""
                    INSERT INTO Procurement (BookID, Quantity, Price, PurchaseDate)
                    VALUES ({book_id}, {quantity}, {price}, '{purchase_date}');
                """))
                conn.execute(text(f"UPDATE Books SET Stock = Stock + {quantity} WHERE BookID = {book_id};"))
                conn.commit()
                st.success("采购成功！")
            else:
                st.error("该BookID不存在")

# 功能 3：淘汰
elif menu == "淘汰" and st.session_state["root"]:
    st.header("淘汰图书")
    with engine.connect() as conn:
        result = pd.read_sql(text("SELECT * FROM Books"), conn)
        st.dataframe(result)
    book_id = st.number_input("图书ID", min_value=1, step=1)
    quantity = st.number_input("淘汰数量", min_value=1, step=1)
    reason = st.text_area("淘汰原因")
    decommission_date = st.date_input("淘汰日期")

    if st.button("确认淘汰"):
        with engine.connect() as conn:
            check = pd.read_sql(text(f"SELECT * FROM Books WHERE BookID = {book_id};"), conn)
            if not check.empty:
                Max_quantity = conn.execute(text(f"SELECT Stock FROM Books WHERE BookID = {book_id}"))
                if quantity <= Max_quantity.scalar():
                    conn.execute(text(f"""
                        INSERT INTO Decommission (BookID, Quantity, Reason, DecommissionDate)
                        VALUES ({book_id}, {quantity}, '{reason}', '{decommission_date}');
                    """))
                    conn.execute(text(f"UPDATE Books SET Stock = Stock - {quantity} WHERE BookID = {book_id};"))
                    conn.commit()
                    st.success("淘汰成功！")
                else:
                    st.error("数量超过范围")
            else:
                st.error("该BookID不存在")

# 功能 4：租借
elif menu == "租借-归还":
    st.header("租借图书")
    with engine.connect() as conn:
        result = pd.read_sql(text("SELECT * FROM Books"), conn)
        st.dataframe(result)
    book_id = st.number_input("图书ID", min_value=1, step=1)
    borrower_name = st.text_input("租借人姓名")
    borrow_date = st.date_input("租借日期")
    if st.button("确认租借"):
        with engine.connect() as conn:
            check = pd.read_sql(text(f"SELECT * FROM Books WHERE BookID = {book_id};"), conn)
            print(check)
            if not check.empty:
                conn.execute(text(f"""
                    INSERT INTO Borrowing (BookID, BorrowerName, BorrowDate)
                    VALUES ({book_id}, '{borrower_name}', '{borrow_date}');
                """))
                conn.execute(text(f"UPDATE Books SET Stock = Stock - 1 WHERE BookID = {book_id};"))
                conn.commit()
                st.success("租借成功！")
            else:
                st.error("该BookID不存在")
    st.header("归还图书")
    return_name = st.text_input("租借人姓名",key='return')
    return_date = st.date_input("归还日期",key="returndate")


    if st.button("查询租借情况"):
        with engine.connect() as conn:
            borrow_pd = pd.read_sql(text(f"select borrowing.BorrowingID,borrowing.BookID,books.Title,borrowing.BorrowDate from books INNER JOIN Borrowing ON books.BookID = Borrowing.BookID WHERE Borrowing.BorrowerName = '{return_name}';"), conn)
            if not borrow_pd.empty:
                st.dataframe(borrow_pd)

            else:
                st.error("该用户不存在租借记录")
    bid = st.number_input("租借ID", min_value=1, step=1,key='Borrowing')
    if st.button("确认归还"):

        with engine.connect() as conn:
            check = pd.read_sql(text(f"SELECT * FROM borrowing WHERE BorrowingID = {bid};"), conn)
            if not check.empty:
                bkd = conn.execute(text(f"select BookID from borrowing WHERE BorrowingID = {bid};"))
                book_id = bkd.scalar()
                conn.execute(text(f"""UPDATE Borrowing SET ReturnDate = '{return_date}' WHERE BookID = {book_id};"""))
                conn.execute(text(f"UPDATE Books SET Stock = Stock + 1 WHERE BookID = {book_id};"))
                conn.commit()
                st.success("归还成功！")



# 功能 5：查询
elif menu == "查询" and st.session_state["root"]:
    st.header("查询图书信息")
    query_type = st.selectbox("查询类别", ["所有图书", "采购记录", "淘汰记录", "租借记录", "库存信息"])
    with engine.connect() as conn:
        if query_type == "所有图书":
            result = pd.read_sql(text("SELECT * FROM Books"), conn)
        elif query_type == "采购记录":
            result = pd.read_sql(text("SELECT * FROM Procurement"), conn)
        elif query_type == "淘汰记录":
            result = pd.read_sql(text("SELECT * FROM Decommission"), conn)
        elif query_type == "租借记录":
            result = pd.read_sql(text("SELECT * FROM Borrowing"), conn)
        else:
            result = pd.read_sql(text("SELECT BookID, Title, Stock FROM Books"), conn)

    st.dataframe(result)

# 功能 6：统计
elif menu == "统计" and st.session_state["root"]:
    st.header("统计信息")
    with engine.connect() as conn:
        total_books = conn.execute(text("SELECT COUNT(*) FROM Books")).fetchone()[0]
        total_stock = conn.execute(text("SELECT SUM(Stock) FROM Books")).fetchone()[0]
        total_borrowed = conn.execute(text("SELECT COUNT(*) FROM Borrowing WHERE ReturnDate IS NULL")).fetchone()[0]
        st.write(f"总图书种类：{total_books}")
        st.write(f"当前库存总量：{total_stock}")
        st.write(f"当前租借未归还：{total_borrowed}")
