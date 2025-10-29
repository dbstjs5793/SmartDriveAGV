# SmartDriveAGV
Autonomous line-following AGV with traffic light detection and obstacle avoidance

## 프로젝트 소개
AGV(Automated Guided Vehicle)가 바닥에 임의로 그린 선을 따라 자율주행하며, 경로 상 신호등과 장애물을 감지하고 안전하게 목적지까지 이동하는 시스템.

AGV의 주행 성능을 최적화하기 위해 다양한 자율주행 접근법을 비교하고, 최적의 방법을 선정하여 구현함

## 자율주행 접근법 비교
1. **라인트레이싱 (채택)**
   - 장점: 구현 간단, 안정적
   - 단점: 고정된 경로만 주행 가능, 환경 변화 대응 어려움
   - 프로젝트 적용: 임의로 그린 선을 따라 안정적 주행, 1분 45초 만에 5분 내 주행 완료, 교육 내 1등 성과

2. **CNN 딥러닝**
   - 장점: 다양한 환경 대응 가능
   - 단점: 방향판별 기준 불분명, AGV 메모리 부족으로 학습 어려움, 임의로 그린 선에는 최적화 어려움

3. **SLAM**
   - 장점: 미지 환경 대응 우수, 실시간 위치 추정 가능
   - 단점: 계산 부하 높음, 센서 노이즈와 오차 문제, 환경 변화에 민감, 초기화 및 맵 관리 문제 발생

---

## 주요 기능
- 라인트레이싱 기반 자율주행
- ArUco 마커를 이용한:
  - 신호등 감지 및 정지
  - 장애물 회피
- 목표 지점 자동 도달
- 카메라 영상 기록 및 화면 출력

## 사용 기술
- Python
- OpenCV (라인 및 ArUco 마커 감지)
- `pymycobot` 라이브러리 (AGV 제어)
- 멀티스레딩(Threading) 기반 실시간 주행 처리


## 시연 영상
https://youtube.com/shorts/75yS-PwQebk?feature=share
