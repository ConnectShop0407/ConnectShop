from types import SimpleNamespace

from flask import Blueprint, render_template, redirect, url_for, session, g, flash
from ConnectShop import db
from ConnectShop.models import Cart, Product


bp = Blueprint('order', __name__, url_prefix='/order')

# --- Helper Functions (정석: 반복되는 세션 로직 분리) ---
def get_guest_cart():
    return session.get('guest_cart', [])

def save_guest_cart(cart):
    session['guest_cart'] = cart
    session.modified = True


@bp.route('/list')
def _list():
    if g.user:
        cart_list = Cart.query.filter_by(user_id=g.user.id).all()
    else:
        guest_cart = session.get('guest_cart', [])
        cart_list = []
        for item in guest_cart:
            product = db.session.get(Product, item['product_id'])
            if product:
                cart_list.append(SimpleNamespace(product=product, quantity=item['quantity']))

    total_price = sum(item.product.price * item.quantity for item in cart_list)

    return render_template('order/cart_list.html', cart_list=cart_list, total_price=total_price)


@bp.route('/add/<int:product_id>')
def add(product_id):
    if g.user:
        cart = Cart.query.filter_by(user_id=g.user.id, product_id=product_id).first()
        if cart:
            cart.quantity += 1
        else:
            cart = Cart(user_id=g.user.id, product_id=product_id, quantity=1)
            db.session.add(cart)
        db.session.commit()
    else:
        # 비회원 로직
        guest_cart = session.get('guest_cart', [])
        found = False
        for item in guest_cart:
            if item['product_id'] == product_id:
                item['quantity'] += 1
                found = True
                break
        if not found:
            guest_cart.append({'product_id': product_id, 'quantity': 1})

        session['guest_cart'] = guest_cart
        session.modified = True

    return redirect(url_for('order._list'))


@bp.route('/delete/<int:product_id>')
def delete(product_id):
    if g.user:
        cart_item = Cart.query.filter_by(user_id=g.user.id, product_id=product_id).first()
        if cart_item:
            db.session.delete(cart_item)
            db.session.commit()
    else:
        guest_cart = session.get('guest_cart', [])
        guest_cart = [item for item in guest_cart if item['product_id'] != product_id]

        session['guest_cart'] = guest_cart
        session.modified = True

    return redirect(url_for('order._list'))


@bp.route('/modify/<int:product_id>/<string:action>')
def modify(product_id, action):
    product = db.session.get(Product, product_id)
    if not product:
        flash('장바구니가 비어 있습니다.')

    if g.user:
        # --- 회원 로직 ---
        cart_item = Cart.query.filter_by(user_id=g.user.id, product_id=product_id).first()
        if not cart_item:
            flash('장바구니가 비어 있습니다.')

        if action == 'inc':
            cart_item.quantity += 1
        elif action == 'dec':
            cart_item.quantity -= 1
            if cart_item.quantity <= 0:
                db.session.delete(cart_item)

        db.session.commit()
    else:
        # --- 비회원 로직 ---
        guest_cart = get_guest_cart()
        target_item = next((item for item in guest_cart if item['product_id'] == product_id), None)

        if not target_item:
            flash('장바구니가 비어 있습니다.')

        if action == 'inc':
            target_item['quantity'] += 1
        elif action == 'dec':
            target_item['quantity'] -= 1
            if target_item['quantity'] <= 0:
                guest_cart = [i for i in guest_cart if i['product_id'] != product_id]

        save_guest_cart(guest_cart)

    return redirect(url_for('order._list'))