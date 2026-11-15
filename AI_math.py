import streamlit as st

st.set_page_config(page_title='경사하강법', page_icon='🧮')
st.title('🧮 경사하강법 기반 추세선 계산')

# 데이터 개수 입력
n = st.number_input(
    '데이터의 개수를 입력하시오:',
    min_value=1,
    value=3,
    step=1
)

data = []

# 데이터 입력
for i in range(n):
    x_value = st.number_input(
        f'{i+1}번째 데이터의 x값을 입력하시오:',
        min_value=0.0,
        value=0.0,
        format='%.2f',
    )

    y_value = st.number_input(
        f'{i+1}번째 데이터의 y값을 입력하시오:',
        min_value=0.0,
        value=0.0,
        format='%.2f',
    )

    data.append((x_value, y_value))

# 손실함수의 계수 계산
p = 0
q = 0
r = 0

for x_value, y_value in data:
    p += x_value ** 2
    q += -2 * x_value * y_value
    r += y_value ** 2

p = p / n
q = q / n
r = r / n

st.info(f'손실함수: E(a) = {p}a² - {-q}a + {r}')

# 학습 설정
a = st.number_input(
    '초깃값을 입력하시오:',
    value=0.0,
    format='%.2f'
)

eta = st.number_input(
    '학습률을 입력하시오:',
    min_value=0.0,
    value=0.01,
    format='%.2f'
)

if st.button('경사하강법 실행'):

    if p == 0:
        st.error('x값 중 적어도 하나는 0보다 커야 합니다.')

    elif eta == 0:
        st.error('학습률을 양수인 값으로 입력하시오.')

    elif eta >= 1 / p:
        st.error(f'학습률을 {1/p} 미만인 값으로 입력하시오.')

    else:
        cnt = 0
        converged = False

        # 초기 상태 기록: (반복 횟수, 기울기, 손실값)
        loss = sum((y - a * x) ** 2 for x, y in data) / n
        history = [(cnt, a, loss)]

        # 경사하강법
        while cnt < 100000:

            if abs(2 * p * a + q) < 0.00001:
                converged = True
                break

            a = a - eta * (2 * p * a + q)
            cnt += 1

            # 업데이트 이후의 상태 기록
            loss = sum((a * x - y) ** 2 for x, y in data) / n
            history.append((cnt, a, loss))

        # 마지막 업데이트 이후에도 수렴 여부 확인
        if abs(2 * p * a + q) < 0.00001:
            converged = True

        if converged:
            st.success('경사하강법이 종료 기준을 만족하여 수렴하였습니다.')
            st.success(f'총 업데이트 횟수: {cnt}번')
            st.success(f'최종 추세선: f(x) = {a}x')
            st.success(f'최종 손실함수 값: {loss}')
            st.success(f'최종 미분값의 절댓값: {abs(2 * p * a + q)}')
        else:
            st.warning('최대 반복 횟수에 도달했으나 종료 기준을 만족하지 못했습니다.')
