## 소개
Quiz App은 Django 기반 웹 퀴즈 애플리케이션입니다.

사용자는 웹 화면에서 퀴즈 문제를 풀고 결과를 확인할 수 있으며,

Docker로 컨테이너화되어 있고 Jenkins를 통해 CI 파이프라인을 구성합니다.

## 주요 기능
Django 기반 웹 퀴즈 서비스

퀴즈 문제 및 정답 로직 처리

Django Template을 활용한 화면 렌더링

Docker를 통한 컨테이너 실행

Jenkins 파이프라인을 통한 자동 빌드

## 실행 방법
$ git clone https://github.com/OhseungKeun/Quiz_app.git

$ cd Quiz_app

$ python -m venv venv

$ source venv/bin/activate

$ pip install -r requirements.txt

$ python manage.py migrate

$ python manage.py runserver 0.0.0.0:8000

## 배포
https://github.com/OhseungKeun/manifests 참고

## 작성자
GitHub: OhseungKeun
