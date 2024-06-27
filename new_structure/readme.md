한국 기준으로 서버 시간 설정
sudo ln -sf /usr/share/zoneinfo/Asia/Seoul /etc/localtime

패키지 목록 업데이트
sudo apt update

패키지 목록 업그레이드
sudo apt upgrade

pip3 설치
sudo apt install python3-pip

distutils 설치
python3-distutils

레포지토리 가져오기
git clone https://github.com/pakkee73/gpt-bitcoin.git

서버에서 라이브러리 설치
pip3 install -r requirements.txt

.env 파일 만들고 API KEY 넣기
vim .env

명령어
현재 경로 상세 출력
ls -al