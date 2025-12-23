from django.http.response import HttpResponse
from django.shortcuts import redirect, render, get_object_or_404
from .models import UserPoint, Quiz, MainCategory, SubCategory, UserExamRecord, Notice, WithdrawRecord, GiftRecord, UserProfile, UserBankInfo, ShortQuiz, OxQuiz
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.http import JsonResponse
from django.contrib.auth.decorators import user_passes_test
import uuid

# 메인 페이지
def main(request):

    user = request.user
    balance = None
    username = None

    if user.is_authenticated:
        username = user.username
        try:
            point = UserPoint.objects.get(user=user)
            balance = point.balance
        except UserPoint.DoesNotExist:
            balance = 0

    return render(request, "HTML/main.html", {
        "username": username,
        "balance": balance,
    })

# ------------------------------------
# 대분류 목록
# ------------------------------------
def main_category_list(request):
    main_categories = MainCategory.objects.all()
    sub_categories = SubCategory.objects.all()

    return render(request, "HTML/main_category_list.html", {
        "main_categories": main_categories,
        "sub_categories": sub_categories
    })


# ------------------------------------
# 소분류 목록
# ------------------------------------
def sub_category_list(request, main_id):
    main = MainCategory.objects.get(id=main_id)
    sub_categories = SubCategory.objects.filter(main=main)

    return render(request, "HTML/sub_category_list.html", {
        "main": main,
        "sub_categories": sub_categories
    })

# ------------------------------------
# 퀴즈 페이지(객관식/답답형/OX)
# ------------------------------------
@login_required
def quiz_view(request, sub_id):
    subcategory = SubCategory.objects.get(id=sub_id)
    questions = Quiz.objects.filter(subcategory=subcategory)
    
    # 시험 유형 체크
    if subcategory.quiz_type == "mcq":  # 객관식
        questions = Quiz.objects.filter(subcategory=subcategory)
        return render(request, "HTML/quiz.html", {
            "subcategory": subcategory,
            "questions": questions,
        })

    elif subcategory.quiz_type == "short":  # 단답형
        questions = ShortQuiz.objects.filter(subcategory=subcategory)
        return render(request, "HTML/short_quiz.html", {
            "subcategory": subcategory,
            "questions": questions,
        })

    elif subcategory.quiz_type == "ox":    # OX 퀴즈
        questions = OxQuiz.objects.filter(subcategory=subcategory)
        return render(request, "HTML/ox_quiz.html", {
            "subcategory": subcategory,
            "questions": questions,
        })

    return HttpResponse("시험 유형이 설정되지 않았습니다.", status=400)


# ------------------------------------
# 퀴즈 제출 & 채점(객관식)
# ------------------------------------
@login_required
def quiz_submit(request, sub_id):
    if request.method != "POST":
        return redirect(f"/quiz/{sub_id}/")

    user = request.user
    subcategory = SubCategory.objects.get(id=sub_id)
    questions = Quiz.objects.filter(subcategory=subcategory)

    # 유저 시험 기록 조회 (없으면 생성)
    user_exam, created = UserExamRecord.objects.get_or_create(
        user=user,
        subcategory=subcategory
    )

    # ----- 채점 시작 -----
    correct_count = 0
    question_count = questions.count()

    for quiz in questions:
        selected = request.POST.get(str(quiz.id))
        if selected and int(selected) == quiz.answer:
            correct_count += 1

    # 합격 기준 = 70%
    passed = correct_count >= (question_count * 0.7)

    # 합격 보상
    reward = 1000 if passed else 0

    # 이미 보상 받았는지 확인
    already_rewarded = user_exam.rewarded
    if already_rewarded:
        reward = 0

    # 결과 저장
    user_exam.score = correct_count
    user_exam.passed = passed

    # 새로 합격 → 보상 지급
    if passed and not user_exam.rewarded:
        user_exam.rewarded = True
        user_point, _ = UserPoint.objects.get_or_create(user=user)
        user_point.balance += reward
        user_point.save()

    user_exam.save()

    return render(request, "HTML/exam_result.html", {
        "subcategory": subcategory,
        "score": correct_count,
        "question_count": question_count,
        "passed": passed,
        "reward": reward,
        "already_rewarded": already_rewarded,
        "balance": UserPoint.objects.get(user=user).balance,
    })

# ------------------------------------
# 퀴즈 제출 & 채점(단답형)
# ------------------------------------
@login_required
def short_quiz_submit(request, sub_id):
    if request.method != "POST":
        return redirect(f"/quiz/short/{sub_id}/")

    user = request.user
    subcategory = SubCategory.objects.get(id=sub_id)
    questions = ShortQuiz.objects.filter(subcategory=subcategory)

    # 유저 시험 기록 조회 (없으면 생성)
    user_exam, created = UserExamRecord.objects.get_or_create(
        user=user,
        subcategory=subcategory
    )

    correct_count = 0
    question_count = questions.count()

    for quiz in questions:
        user_answer = request.POST.get(str(quiz.id), "").strip()

        if user_answer and user_answer.lower() == quiz.answer_text.lower():
            correct_count += 1

    # 합격 기준 = 70%
    passed = correct_count >= (question_count * 0.7)

    # 기본 보상 금액
    reward = 1000 if passed else 0

    # 이미 보상 받은 기록이 있으면 지급 불가
    already_rewarded = user_exam.rewarded
    if already_rewarded:
        reward = 0

    # 점수 저장
    user_exam.score = correct_count
    user_exam.passed = passed

    # 보상 지급 처리
    if passed and not user_exam.rewarded:
        user_exam.rewarded = True
        user_point, _ = UserPoint.objects.get_or_create(user=user)
        user_point.balance += reward
        user_point.save()

    user_exam.save()

    return render(request, "HTML/exam_result.html", {
        "subcategory": subcategory,
        "score": correct_count,
        "question_count": question_count,
        "passed": passed,
        "reward": reward,
        "already_rewarded": already_rewarded,
        "balance": UserPoint.objects.get(user=user).balance,
    })

# ------------------------------------
# 퀴즈 제출 & 채점(OX 퀴즈)
# ------------------------------------
@login_required
def ox_quiz_submit(request, sub_id):
    if request.method != "POST":
        return redirect(f"/quiz/ox/{sub_id}/")

    user = request.user
    subcategory = SubCategory.objects.get(id=sub_id)
    questions = OxQuiz.objects.filter(subcategory=subcategory)

    user_exam, created = UserExamRecord.objects.get_or_create(
        user=user,
        subcategory=subcategory
    )

    correct_count = 0
    for quiz in questions:
        selected = request.POST.get(str(quiz.id))
        if selected is not None:
            if (selected == "o" and quiz.answer == True) or \
               (selected == "x" and quiz.answer == False):
                correct_count += 1

    question_count = questions.count()
    passed = correct_count >= (question_count * 0.7)

    reward = 1000 if passed else 0
    already_rewarded = user_exam.rewarded
    if already_rewarded:
        reward = 0

    user_exam.score = correct_count
    user_exam.passed = passed

    if passed and not user_exam.rewarded:
        user_exam.rewarded = True
        user_point, _ = UserPoint.objects.get_or_create(user=user)
        user_point.balance += reward
        user_point.save()

    user_exam.save()

    return render(request, "HTML/exam_result.html", {
        "subcategory": subcategory,
        "score": correct_count,
        "question_count": question_count,
        "passed": passed,
        "reward": reward,
        "already_rewarded": already_rewarded,
        "balance": UserPoint.objects.get(user=user).balance,
    })


# ------------------------------------
# 퀴즈 제출 자동 라우팅 (객관/단답/ox 자동 선택)
# ------------------------------------
@login_required
def quiz_submit_router(request, sub_id):
    subcategory = SubCategory.objects.get(id=sub_id)

    # 시험 유형에 따라 올바른 채점 함수 호출
    if subcategory.quiz_type == "mcq":  # 객관식
        return quiz_submit(request, sub_id)

    elif subcategory.quiz_type == "short":  # 단답형
        return short_quiz_submit(request, sub_id)

    elif subcategory.quiz_type == "ox":
        return ox_quiz_submit(request, sub_id)

    return HttpResponse("시험 유형이 설정되지 않았습니다.", status=400)

# ------------------------------------
# 환급 페이지
# ------------------------------------
@login_required
def point(request):
    user_point, _ = UserPoint.objects.get_or_create(user=request.user)
    return render(request, "HTML/point.html", {"balance": user_point.balance})
    
@login_required
def withdraw_view(request):
    user = request.user
    user_point = UserPoint.objects.get(user=user)

    # 기존 계좌 정보(자동 입력용)
    bank_info = UserBankInfo.objects.filter(user=user).first()

    return render(request, "HTML/withdraw.html", {
        "balance": user_point.balance,
        "bank_info": bank_info,
    })

# ------------------------------------
# 계좌 관리
# ------------------------------------
@login_required
def bank_info_view(request):
    bank_info = UserBankInfo.objects.filter(user=request.user).first()

    bank_list = ["국민은행", "우리은행", "신한은행", "카카오뱅크", "토스뱅크", "농협은행"]

    return render(request, "HTML/bank_info.html", {
        "bank_info": bank_info,
        "bank_list": bank_list
    })

@login_required
def bank_info_save(request):
    if request.method != "POST":
        return redirect("bank_info")

    user = request.user
    bank_name = request.POST.get("bank_name")
    account_number = request.POST.get("account_number")
    account_holder = request.POST.get("account_holder")

    # 저장 or 업데이트
    bank_info, created = UserBankInfo.objects.get_or_create(user=user)
    bank_info.bank_name = bank_name
    bank_info.account_number = account_number
    bank_info.account_holder = account_holder
    bank_info.save()

    return redirect("bank_info")

# ------------------------------------
# 출금
# ------------------------------------
@login_required
def withdraw_process(request):
    if request.method != "POST":
        return redirect("withdraw")

    user = request.user
    user_point = UserPoint.objects.get(user=user)

    # 기존 계좌 정보 가져오기
    bank_info = UserBankInfo.objects.filter(user=user).first()
    if not bank_info:
        return render(request, "HTML/withdraw.html", {
            "balance": user_point.balance,
            "error": "계좌 정보가 등록되어 있지 않습니다. 먼저 계좌를 등록해주세요."
        })

    amount = int(request.POST.get("amount"))

    if amount < 1000:
        return render(request, "HTML/withdraw.html", {
            "balance": user_point.balance,
            "error": "최소 1000포인트부터 출금 가능합니다.",
            "bank_info": bank_info
        })

    if user_point.balance < amount:
        return render(request, "HTML/withdraw.html", {
            "balance": user_point.balance,
            "error": "포인트가 부족합니다.",
            "bank_info": bank_info
        })

    # 출금 처리
    user_point.balance -= amount
    user_point.save()

    # 출금 기록 저장
    WithdrawRecord.objects.create(
        user=user,
        bank_name=bank_info.bank_name,
        account_number=bank_info.account_number,
        amount=amount
    )

    return render(request, "HTML/withdraw_success.html", {
        "withdraw_amount": amount,
        "balance": user_point.balance,
        "bank_name": bank_info.bank_name,
        "account_number": bank_info.account_number,
    })

# ------------------------------------
# 출금 및 기프티콘 교환 내역 확인
# ------------------------------------
@login_required
def point_records(request):
    gift_records = GiftRecord.objects.filter(user=request.user).order_by('-created_at')
    withdraw_records = WithdrawRecord.objects.filter(user=request.user).order_by('-created_at')

    return render(request, "HTML/point_records.html", {
        "gift_records": gift_records,
        "withdraw_records": withdraw_records,
    })

# ------------------------------------
# 기프티콘 교환 페이지
# ------------------------------------
@login_required
def gift_view(request):
    user_point = UserPoint.objects.get(user=request.user)

    # 기프티콘 목록 샘플
    gifts = [
        {"name": "스타벅스 아메리카노", "cost": 4500},
        {"name": "배스킨라빈스 싱글", "cost": 3500},
        {"name": "GS25 5천원 쿠폰", "cost": 5000},
    ]

    return render(request, "HTML/gift.html", {
        "balance": user_point.balance,
        "gifts": gifts
    })

# ------------------------------------
# 기프티콘 구매 처리
# ------------------------------------
@login_required
def gift_buy(request):
    if request.method != "POST":
        return redirect("gift")

    gift_name = request.POST.get("gift_name")
    cost = int(request.POST.get("cost"))

    user = request.user
    user_point = UserPoint.objects.get(user=user)
    code = uuid.uuid4().hex[:12].upper()

    if user_point.balance < cost:
        return render(request, "HTML/gift.html", {
            "balance": user_point.balance,
            "error": "포인트가 부족합니다."
        })

    # 포인트 차감
    user_point.balance -= cost
    user_point.save()

    # 기록 생성
    gift = GiftRecord.objects.create(
        user=user,
        gift_name=gift_name,
        cost=cost,
        code=code
    )

    return render(request, "HTML/gift_success.html", {
        "gift": gift,
        "balance": user_point.balance
    })



# ------------------------------------
# 유저 정보
# ------------------------------------
@login_required
def user_info(request):
    user = request.user
    try:
        point = UserPoint.objects.get(user=user)
        balance = point.balance
    except UserPoint.DoesNotExist:
        balance = 0

    return render(request, "HTML/user_info.html", {
        "username": user.username,
        "balance": balance,
    })


# ------------------------------------
# 로그인
# ------------------------------------
def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("main")
        else:
            return render(request, "HTML/login.html", {"error": "로그인 실패"})

    return render(request, "HTML/login.html")


# ------------------------------------
# 아이디 중복 체크
# ------------------------------------
def check_username(request):
    username = request.GET.get("username")
    exists = User.objects.filter(username=username).exists()
    return JsonResponse({"exists": exists})


# ------------------------------------
# 로그아웃
# ------------------------------------
def logout_view(request):
    logout(request)
    return redirect("main")


# ------------------------------------
# 회원가입
# ------------------------------------
def signup(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        phone = request.POST.get("phone")

        # ID 중복 확인
        if User.objects.filter(username=username).exists():
            return render(request, "HTML/signup.html", {"error": "이미 존재하는 ID 입니다."})

        # 유저 생성
        user = User.objects.create(
            username=username,
            password=make_password(password),
        )

        # 프로필 생성 (전화번호 저장)
        UserProfile.objects.create(
            user=user,
            phone=phone
        )

        # 포인트 계정 생성
        UserPoint.objects.create(user=user, balance=0)

        return redirect("login")

    return render(request, "HTML/signup.html")


# ------------------------------------
# 관리자만 접근
# ------------------------------------
def admin_only(user):
    return user.is_superuser or user.is_staff


# ------------------------------------
# 공지 목록 페이지
# ------------------------------------
def notice_list(request):
    notices = Notice.objects.order_by('-created_at')
    return render(request, "HTML/notice_list.html", {
        "notices": notices
    })

# ------------------------------------
# 공지 생성
# ------------------------------------
@user_passes_test(admin_only)
def notice_create(request):
    if request.method == "POST":
        title = request.POST.get("title")
        content = request.POST.get("content")

        Notice.objects.create(
            title=title,
            content=content,
            author=request.user
        )
        return redirect("notice_list")

    return render(request, "HTML/notice_create.html")

# ------------------------------------
# 공지 삭제
# ------------------------------------
@user_passes_test(admin_only)
def notice_delete(request, notice_id):
    try:
        notice = Notice.objects.get(id=notice_id)
    except Notice.DoesNotExist:
        return redirect("notice_list")

    if request.method == "POST":
        notice.delete()
        return redirect("notice_list")

    return render(request, "HTML/notice_delete_confirm.html", {
        "notice": notice,
    })

# ------------------------------------
# 공지 확인 페이지
# ------------------------------------
def notice_detail(request, pk):
    notice = get_object_or_404(Notice, id=pk)
    return render(request, "HTML/notice_detail.html", {"notice": notice})




