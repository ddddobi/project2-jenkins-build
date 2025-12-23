from django.db import models
from django.contrib.auth.models import User


# -----------------------
# 유저 포인트
# -----------------------
class UserPoint(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.user.username} - {self.balance}P"


# -----------------------
# 로그인한 유저 정보
# -----------------------
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        db_table = "user_profile"


# -----------------------
# 출금 신청 내역
# -----------------------
class WithdrawRecord(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    bank_name = models.CharField(max_length=50)
    account_number = models.CharField(max_length=50)
    amount = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "withdraw_record"

    def __str__(self):
        return f"{self.user.username} - {self.amount}P 출금"


# -----------------------
# 계좌 정보
# -----------------------
class UserBankInfo(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bank_name = models.CharField(max_length=50)
    account_number = models.CharField(max_length=50)
    account_holder = models.CharField(max_length=50)

    class Meta:
        db_table = "user_bank_info"

    def __str__(self):
        return f"{self.user.username} - {self.bank_name} / {self.account_number}"


# -----------------------
# 기프티콘 구매 내역
# -----------------------
class GiftRecord(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    gift_name = models.CharField(max_length=100)
    cost = models.IntegerField()
    code = models.CharField(max_length=50, default="", unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "gift_record"

    def __str__(self):
        return f"{self.user.username} - {self.gift_name} ({self.code})"


# -----------------------
# 대분류 카테고리
# -----------------------
class MainCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        db_table = "quiz_main_category"

    def __str__(self):
        return self.name


# -----------------------
# 소분류 카테고리
# -----------------------
class SubCategory(models.Model):
    main = models.ForeignKey(MainCategory, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    quiz_type = models.CharField(
        max_length=10,
        choices=[("mcq", "객관식"), ("short", "단답형"), ("ox", "OX")],
        default="mcq"
    )

    class Meta:
        db_table = "quiz_sub_category"
        unique_together = ('main', 'name')

    def __str__(self):
        return f"{self.main.name} - {self.name}"


# -----------------------
# 문제 테이블(객관식)
# -----------------------
class Quiz(models.Model):
    subcategory = models.ForeignKey(SubCategory, on_delete=models.CASCADE)
    question = models.CharField(max_length=255)
    choice1 = models.CharField(max_length=100)
    choice2 = models.CharField(max_length=100)
    choice3 = models.CharField(max_length=100)
    choice4 = models.CharField(max_length=100)
    answer = models.IntegerField()  # 1~4 정답 번호

    class Meta:
        db_table = 'quiz_question'

    def __str__(self):
        return f"[{self.subcategory.name}] {self.question}"

# -----------------------
# 문제 테이블(단답식)
# -----------------------
class ShortQuiz(models.Model):
    subcategory = models.ForeignKey(SubCategory, on_delete=models.CASCADE)
    question = models.CharField(max_length=255)
    answer_text = models.CharField(max_length=255)  # 정답 문자열 저장

    class Meta:
        db_table = 'quiz_short_question'

    def __str__(self):
        return f"[{self.subcategory.name}] {self.question}"


class OxQuiz(models.Model):
    subcategory = models.ForeignKey(SubCategory, on_delete=models.CASCADE)
    question = models.TextField()
    answer = models.BooleanField()   # True = O, False = X

    class Meta:
        db_table = 'ox_question'

    def __str__(self):
        return f"[{self.subcategory.name}] {self.question}"


# -----------------------z
# 유저 모의고사 기록 (소분류 단위로 저장)
# -----------------------
class UserExamRecord(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    subcategory = models.ForeignKey(SubCategory, on_delete=models.CASCADE)
    passed = models.BooleanField(default=False)
    score = models.IntegerField(default=0)
    rewarded = models.BooleanField(default=False)  

    class Meta:
        db_table = "user_exam_record"
        unique_together = ('user', 'subcategory')  # 동일 소분류 재보상 방지

    def __str__(self):
        return f"{self.user.username} - {self.subcategory.name}: {'통과' if self.passed else '미통과'}"


# -----------------------
# 공지 사항(admin만 작성)
# -----------------------
class Notice(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        db_table = "notice"

    def __str__(self):
        return self.title\

