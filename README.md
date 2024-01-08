
# Quiz

소스코드 다운로드

    git clone https://github.com/evadelzz1/experiment3.git

python 환경변수 및 가상환경 설정

    cd ./experiment3

    pyenv versions

    pyenv local 3.11.6

    pyenv versions

    echo '.env'  >> .gitignore
    echo '.venv' >> .gitignore

    echo 'OPENAI_API_KEY=sk-9jz....' >> .env

    ls -la

    python -m venv .venv

    source .venv/bin/activate

    python -V

프로젝트에 필요한 라이브러리 설치

    pip install -r requirements.txt

예제코드 테스트

    python -m streamlit run app.py

python 가상환경 deactivate

    deactivate
