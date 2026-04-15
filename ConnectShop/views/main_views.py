from flask import Blueprint, render_template, request
from ConnectShop.models import FAQ

# 'main'이라는 이름의 블루프린트 생성 (기본 접속 주소 '/')
bp = Blueprint('main', __name__, url_prefix='/')

@bp.route('/')
def index():
    # 🌟 팀원이 만든 상품 메인 페이지로 연결
    return render_template('product/main_page.html')

# 회사 소개 페이지 라우트 함수
@bp.route('/company')
def company():
    return render_template('company.html')

# 이용약관 페이지
@bp.route('/terms')
def terms():
    return render_template('policy/terms.html')

# 개인정보처리방침 페이지
@bp.route('/privacy')
def privacy():
    return render_template('policy/privacy.html')

# 고객 지원 페이지 라우트 함수
@bp.route('/support')
def support():
    # DB에서 최신순으로 정렬해서 5개를 가져옵니다.
    faq_list = FAQ.query.order_by(FAQ.id.desc()).limit(5).all()
    # 가져온 데이터를 faq_list라는 이름으로 템플릿에 넘겨줍니다.
    return render_template('support.html', faq_list=faq_list)

@bp.route('/faq_board')
def faq_board():
    # 1. 사용자가 검색창에 입력한 단어(kw)를 가져옵니다. (기본값은 빈 문자열)
    kw = request.args.get('kw', type=str, default='')

    # 2. 검색어가 있으면 필터링, 없으면 전체 다 가져오기
    if kw:
        search = f"%%{kw}%%"  # 검색어를 포함하는지 확인하기 위한 와일드카드
        # 질문(question), 답변(answer), 카테고리(category) 중 하나라도 겹치면 검색됨
        faq_list = FAQ.query.filter(
            FAQ.question.ilike(search) | FAQ.answer.ilike(search) | FAQ.category.ilike(search)
        ).order_by(FAQ.id.desc()).all()
    else:
        faq_list = FAQ.query.order_by(FAQ.id.desc()).all()

    return render_template('support/faq_board.html', faq_list=faq_list, kw=kw)

# 준비 중 페이지 라우트 함수
@bp.route('/preparing')
def preparing():
    return render_template('preparing.html')
